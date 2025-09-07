from shared.models import Transcript

def transcribe_audio_stub(file_bytes: bytes, filename: str) -> Transcript:
    # Replace with Whisper later
    return Transcript(text=f"[stub transcript for {filename}]", language="en", segments=[])

def extract_audio_from_video_stub(file_bytes: bytes, filename: str) -> bytes:
    # Replace with ffmpeg audio extraction if needed
    return file_bytes

def transcribe_av(file_bytes: bytes, filename: str, mime: str) -> Transcript:
    if mime.startswith("audio/"):
        return transcribe_audio_stub(file_bytes, filename)
    if mime.startswith("video/"):
        audio_bytes = extract_audio_from_video_stub(file_bytes, filename)
        return transcribe_audio_stub(audio_bytes, filename)
    return Transcript(text="", language=None, segments=[])
