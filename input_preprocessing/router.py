from typing import List
from shared.models import NormalizedIncident, ImageMeta, Transcript
from .text import preprocess_text
from .images import analyze_image
from .audio_video import transcribe_av
from .normalize import normalize_inputs

def preprocess_request(
    source: str,
    raw_text: str,
    latlon_str: str | None,
    uploads: list[tuple[str, bytes, str]],  # (filename, bytes, mime)
) -> NormalizedIncident:
    notes: List[str] = []
    cleaned_text = preprocess_text(raw_text, notes)
    print("Raw Text:", raw_text)
    print("Cleaned Text:", cleaned_text)
    incident = normalize_inputs(source, cleaned_text, latlon_str, uploads, notes)
    print("Normalized Incident:", incident)
    images_meta: List[ImageMeta] = []
    transcripts: List[Transcript] = []

    for (filename, file_bytes, mime) in uploads:
        print(f"Processing upload: {filename} ({mime}), size={len(file_bytes)} bytes")
        if mime.startswith("image/"):
            print("this is the image data")
            images_meta.append(analyze_image(file_bytes, filename))
        elif mime.startswith("audio/") or mime.startswith("video/"):
            print("this is the audio or video data")
            transcripts.append(transcribe_av(file_bytes, filename, mime))

    incident.images_meta = images_meta
    incident.transcripts = transcripts

    if images_meta:
        notes.append(f"Processed {len(images_meta)} image(s) with EXIF and dimensions.")
    if transcripts:
        notes.append(f"Generated {len(transcripts)} transcript(s) from audio/video.")
  
    return incident
