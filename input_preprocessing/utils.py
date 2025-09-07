import base64
from typing import Tuple


from langdetect import detect, DetectorFactory, lang_detect_exception

# Ensure consistent results
DetectorFactory.seed = 0
def detect_language(text: str) -> str | None:
    if not text:
        return None
    try:
        return detect(text)
    except lang_detect_exception.LangDetectException:
        return None


def to_base64(b: bytes) -> str:
    
    return base64.b64encode(b).decode("utf-8")


def parse_latlon(raw: str | None) -> Tuple[float | None, float | None]:
    if not raw:
        return None, None
    try:
        parts = [p.strip() for p in raw.split(",")]
        return float(parts), float(parts[6])
    except Exception:
        return None, None
