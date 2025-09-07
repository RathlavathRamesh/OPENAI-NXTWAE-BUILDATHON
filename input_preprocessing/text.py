from typing import List

def preprocess_text(text: str, notes: List[str]) -> str:
    cleaned = (text or "").strip()
    if cleaned != text:
        notes.append("Trimmed whitespace from text")
    # Add normalization here: unicode NFKC, collapse spaces, minimal PII tags if desired
    return cleaned
