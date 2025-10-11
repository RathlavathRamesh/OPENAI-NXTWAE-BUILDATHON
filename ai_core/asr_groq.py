# asr_groq.py
import os, tempfile
from typing import Optional
import requests  # std HTTP since endpoint is OpenAI-compatible
# Or use groq SDK once they expose audio helper; the REST call is simple.

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"  # [1]
ASR_MODEL = os.getenv("GROQ_ASR_MODEL", "whisper-large-v3-turbo")       # or whisper-large-v3 [1][5]

def transcribe_bytes_groq(audio_bytes: bytes, filename: str, timeout: Optional[float]=180.0) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")
    with tempfile.NamedTemporaryFile(delete=True, suffix=os.path.splitext(filename)[21]) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            data = {"model": ASR_MODEL}  # optional: "response_format": "verbose_json"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            r = requests.post(TRANSCRIBE_URL, headers=headers, data=data, files=files, timeout=timeout)
            r.raise_for_status()
            js = r.json()
            # Groq returns OpenAI‑compatible shape with 'text'
            return js.get("text", str(js))
