import os
import uuid
from typing import List
from shared.models import NormalizedIncident, ImageMeta, Transcript
from .text import preprocess_text
from .images import analyze_image
from .audio_video import transcribe_av
from .normalize import normalize_inputs
from ai_core.video_analysis_script import process_video_to_transcript  # updated API


def preprocess_request(source: str, raw_text: str, latlon_str: str | None, uploads: list[tuple[str, bytes, str]]) -> NormalizedIncident:
    notes: List[str] = []
    cleaned_text = preprocess_text(raw_text, notes)
    incident = normalize_inputs(source, cleaned_text, latlon_str, uploads, notes)

    images_meta: List[ImageMeta] = []
    transcripts: List[Transcript] = []
    # Create per-incident dirs
    inc_id = uuid.uuid4().hex
    inc_base = os.path.join("request_videos", f"incident_{inc_id}")
    orig_dir = os.path.join(inc_base, "orig")
    processed_dir = os.path.join(inc_base, "processed")
    os.makedirs(orig_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    for i, (filename, file_bytes, mime) in enumerate(uploads):
        safe_name = os.path.basename(filename or f"upload_{i}.bin")
        mime_raw = mime
        mime = (mime or "").strip().lower()
        print(f"[preprocess] idx={i} name={safe_name} mime_raw={repr(mime_raw)} mime_norm={repr(mime)} size={len(file_bytes)}")

        # Force video first to eliminate any surprises
        if mime.startswith("video/"):
            print("[preprocess] -> video branch")
            save_path = os.path.join(orig_dir, safe_name if "." in safe_name else safe_name + ".mp4")
            with open(save_path, "wb") as f:
                f.write(file_bytes)
            try:
                txt = process_video_to_transcript(
                    input_video_path=save_path,
                    processed_dir=processed_dir,
                    segment_seconds=600,
                    use_ffmpeg_split=True,
                    prompt_file="prompts/video_analysis_prompt.txt",
                    previous_context_window=3,
                )
                transcripts.append(Transcript(text=txt))
                print(f"[preprocess] video transcribed: {os.path.basename(save_path)} -> {len(txt)} chars")
                notes.append(f"Video transcribed via Gemini: {os.path.basename(save_path)}")
            except Exception as e:
                print(f"[preprocess] video transcription error: {e}")
                notes.append(f"Video transcription failed: {e}")

        elif mime.startswith("image/"):
            print("[preprocess] -> image branch")
            if mime.startswith("image/"):
                print("this is the image data")
                images_meta.append(analyze_image(file_bytes, filename))
        elif mime.startswith("audio/"):
            print("[preprocess] -> audio branch")
            transcripts.append(transcribe_av(file_bytes, safe_name, mime))
        else:
            print("[preprocess] -> unknown branch")
            notes.append(f"Unknown MIME, skipping: {mime} ({safe_name})")

    incident.images_meta = images_meta
    incident.transcripts = transcripts
    if images_meta:
        notes.append(f"Processed {len(images_meta)} image(s) with EXIF and dimensions.")
    if transcripts:
        notes.append(f"Generated {len(transcripts)} transcript(s) from audio/video.")
    return incident
