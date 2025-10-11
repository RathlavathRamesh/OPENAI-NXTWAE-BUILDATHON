# asr_openai.py
import os
import tempfile
from typing import Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_bytes_gpt4o(audio_bytes: bytes, filename: str, timeout: Optional[float]=180.0) -> str:
    # If the input is a video, pass the whole bytes; server handles decoding when supported.
    # For very large files, pre-trim or chunk before sending to avoid timeouts/limits.
    with tempfile.NamedTemporaryFile(delete=True, suffix=os.path.splitext(filename)[18]) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",  # hosted ASR endpoint
                file=f,
                # response_format="verbose_json",  # optional
                # temperature=0.0,               # optional
                timeout=timeout,
            )
    # Most responses expose .text; adjust if you requested verbose_json
    return getattr(resp, "text", str(resp))
