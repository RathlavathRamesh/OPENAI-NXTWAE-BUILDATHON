import os
import time
from typing import List, Optional, Tuple

import ffmpeg  # ffmpeg-python
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # Fallback for newer moviepy versions
    from moviepy import VideoFileClip
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_VIDEO_MODEL = os.getenv("GEMINI_VIDEO_MODEL", "gemini-2.5-flash")

# Fallback template (use a joint A/V prompt file in production)
FALLBACK_TEMPLATE = (
    "Role: Expert disaster-video analyst and transcriber.\n"
    "Segment window: {start_min}–{end_min} minutes (approx).\n"
    "Context from previous segments:\n"
    "{previous_context}\n\n"
    "Task:\n"
    "- From this video segment ONLY, do BOTH:\n"
    "  1) Speech transcript (verbatim).\n"
    "  2) Visual incident analysis (objects, hazards, counts, severity).\n\n"
    "Output format (plain text, no markdown, no JSON):\n"
    "Transcript:\n"
    "- One utterance per line. If speaker known: Speaker 1:, Speaker 2:. Otherwise omit label.\n"
    "- Prefer timestamps like [MM:SS] at the start of each line when possible.\n"
    "- Preserve numbers, places, times; use [inaudible] sparingly.\n\n"
    "Visual:\n"
    "- Hazards: flooding depth/flow, fire/smoke, building damage, landslide, downed lines.\n"
    "- People/vehicles/resources: counts or estimates (boats, ambulances, etc.).\n"
    "- Location hints: visible signage, landmarks, road names.\n"
    "- Blockages and accessibility issues (roads, bridges).\n"
    "- Severity: Low / Moderate / High (visible impact only).\n\n"
    "Rules:\n"
    "- If no speech, write one line: [no speech detected] under Transcript.\n"
    "- Do NOT summarize Transcript inside Visual; keep them separate.\n"
    "- No code fences, no markdown, no JSON—plain text only.\n"
)

_client: Optional[genai.Client] = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

def _duration_seconds(video_path: str) -> int:
    clip = VideoFileClip(video_path)
    try:
        return int(clip.duration or 0)
    finally:
        clip.close()

def _split_moviepy(input_video: str, out_dir: str, segment_seconds: int) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    clip = VideoFileClip(input_video)
    total = int(clip.duration or 0)
    parts: List[str] = []
    try:
        for i, start in enumerate(range(0, total, segment_seconds)):
            end = min(start + segment_seconds, total)
            out_path = os.path.join(out_dir, f"chunk{i:03d}.mp4")
            clip.subclip(start, end).write_videofile(out_path, codec="libx264", audio=True, logger=None)
            parts.append(out_path)
    finally:
        clip.close()
    return parts

def _split_ffmpeg(input_video: str, out_dir: str, segment_seconds: int) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    (
        ffmpeg
        .input(input_video)
        .output(os.path.join(out_dir, "chunk%03d.mp4"),
                f="segment",
                segment_time=segment_seconds)
        .run(quiet=True, overwrite_output=True)
    )
    return sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("chunk") and f.endswith(".mp4")
    )

def _load_template(prompt_file: Optional[str]) -> str:
    if prompt_file and os.path.isfile(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    return FALLBACK_TEMPLATE

def _wait_until_active(client, file_obj, timeout_sec: int = 300, poll_sec: float = 2.0):
    import time
    name = getattr(file_obj, "name", None)
    if not name:
        return file_obj
    start = time.time()

    def _state(v):
        if hasattr(v, "name"):
            return v.name
        return str(v or "").upper()

    state = getattr(file_obj, "state", None)
    while time.time() - start < timeout_sec:
        st = _state(state)
        if st == "ACTIVE":
            return file_obj
        if st == "FAILED":
            raise RuntimeError("File processing failed: FAILED")
        time.sleep(poll_sec)
        # FIX: use keyword argument for the file identifier
        file_obj = client.files.get(name=name)
        state = getattr(file_obj, "state", None)
    raise TimeoutError("File did not become ACTIVE in time")

def _upload_and_prepare_file(client: genai.Client, path: str):
    f = client.files.upload(file=path)
    f = _wait_until_active(client, f, timeout_sec=300, poll_sec=2.0)
    return f

def _generate_for_chunk(
    client: genai.Client,
    uploaded_file: object,
    final_prompt: str,
) -> str:
    resp = client.models.generate_content(
        model=GEMINI_VIDEO_MODEL,
        contents=[uploaded_file, final_prompt],
    )
    return (getattr(resp, "text", "") or "").strip()

def _postprocess_combined(text: str) -> str:
    """Light cleanup: collapse repetitive ambient-only lines, trim blanks."""
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]  # remove empty
    pruned: List[str] = []
    ambient_run = 0
    for ln in lines:
        if ln.startswith("[") and ln.endswith("]"):
            ambient_run += 1
            # keep at most 1 ambient line in a run
            if ambient_run == 1:
                pruned.append(ln)
            continue
        ambient_run = 0
        pruned.append(ln)
    if pruned and all(l.startswith("[") and l.endswith("]") for l in pruned):
        pruned = pruned[:3]  # cap if entirely ambient
    return "\n".join(pruned).strip()

def process_video_to_transcript(
    input_video_path: str,
    processed_dir: str,
    segment_seconds: int = 600,
    use_ffmpeg_split: bool = True,
    prompt_file: Optional[str] = None,
    previous_context_window: int = 3,  # last N chunk outputs
) -> str:
    """
    - Reads base prompt template from prompt_file (placeholders {previous_context}, {start_min}, {end_min}).
    - Splits video if large, keeps rolling previous_context, and generates per-chunk joint A/V outputs.
    - Saves per-chunk prompt and transcript files and a final combined transcript.
    - Returns combined transcript string.
    """
    if not os.path.isfile(input_video_path):
        raise FileNotFoundError(f"Video not found: {input_video_path}")

    os.makedirs(processed_dir, exist_ok=True)
    client = _get_client()

    base_name, _ext = os.path.splitext(os.path.basename(input_video_path))
    combined_out = os.path.join(processed_dir, f"{base_name}.transcript.txt")
    chunks_dir = os.path.join(processed_dir, f"{base_name}_chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    # Decide chunking
    try:
        size_mb = os.path.getsize(input_video_path) / (1024 * 1024)
    except Exception:
        size_mb = 0.0
    try:
        total_sec = _duration_seconds(input_video_path)
    except Exception:
        total_sec = 0

    do_chunk = (total_sec and total_sec > segment_seconds) or (size_mb and size_mb > 20)

    if do_chunk:
        splitter = _split_ffmpeg if use_ffmpeg_split else _split_moviepy
        chunk_paths = splitter(input_video_path, chunks_dir, segment_seconds)
    else:
        # uniform processing via a single chunk copy
        single = os.path.join(chunks_dir, "chunk000.mp4")
        if input_video_path != single:
            try:
                import shutil
                shutil.copy2(input_video_path, single)
            except Exception:
                with open(input_video_path, "rb") as src, open(single, "wb") as dst:
                    dst.write(src.read())
        chunk_paths = [single]
        total_sec = total_sec or 0

    template = _load_template(prompt_file)
    combined_parts: List[str] = []
    previous_context: str = ""

    for idx, path in enumerate(chunk_paths):
        start_sec = idx * segment_seconds
        end_sec = min((idx + 1) * segment_seconds, total_sec) if total_sec else (idx + 1) * segment_seconds
        start_min = start_sec // 60
        end_min = max(start_min + 1, end_sec // 60)

        final_prompt = template.format(
            previous_context=previous_context if previous_context else "None",
            start_min=start_min,
            end_min=end_min,
        )

        # Save the exact prompt (audit)
        with open(os.path.join(chunks_dir, f"chunk{idx:03d}.prompt.txt"), "w", encoding="utf-8") as pf:
            pf.write(final_prompt)

        # Upload + wait for ACTIVE
        uploaded = _upload_and_prepare_file(client, path)

        # Generate content
        chunk_text = _generate_for_chunk(client, uploaded, final_prompt)

        # Save per-chunk output
        with open(os.path.join(chunks_dir, f"chunk{idx:03d}.txt"), "w", encoding="utf-8") as tf:
            tf.write(chunk_text)

        combined_parts.append(chunk_text)
        if previous_context_window > 0:
            previous_context = "\n\n".join(combined_parts[-previous_context_window:])
        else:
            previous_context = ""

    combined = "\n\n".join(combined_parts).strip()
    combined = _postprocess_combined(combined)

    with open(combined_out, "w", encoding="utf-8") as f:
        f.write(combined)

    return combined
