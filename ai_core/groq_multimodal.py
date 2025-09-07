# multimodal_groq.py
import os, json, re
from typing import Dict, Any, List
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")  # [6]

def _data_url(mime: str, b64: str) -> str:
    return f"data:{mime};base64,{b64}"

def infer_situation_with_groq(
    text_report: str,
    transcripts: List[str],
    images_b64: List[tuple[str, str]],
    lat: float | None,
    lon: float | None,
    max_images: int = 4,
) -> Dict[str, Any]:
    content = []
    content.append({"type": "text", "text":
        ("You are a disaster analyst. Produce strict JSON with: "
         "situation_summary, hazards[], severity (Low|Medium|High|Severe), "
         "location_hint, evidence_notes. Return only JSON.")})

    if text_report and text_report.strip():
        content.append({"type": "text", "text": f"TEXT REPORT:\n{text_report.strip()}"})

    if transcripts:
        joined = " ".join([t for t in transcripts if t])[:3000]
        if joined:
            content.append({"type": "text", "text": f"AUDIO/VIDEO TRANSCRIPT:\n{joined}"})

    for mime, b64 in images_b64[:max_images]:
        content.append({"type": "image_url", "image_url": {"url": _data_url(mime, b64)}})

    if lat is not None and lon is not None:
        content.append({"type": "text", "text": f"LOCATION: {lat},{lon}"})

    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
    )
    # raw = resp.choices.message.content or "{}"
    choice = resp.choices[0] if getattr(resp, "choices", None) else None
    raw = (choice.message.content if (choice and getattr(choice, "message", None)) else "") or "{}"
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL)
    try:
        data = json.loads(cleaned)
    except Exception:
        data = {
            "situation_summary": cleaned[:500],
            "hazards": [],
            "severity": "Medium",
            "location_hint": f"{lat},{lon}" if lat is not None and lon is not None else "unknown",
            "evidence_notes": "Non-JSON response; fallback applied."
        }
    for k, v in [("situation_summary","No summary"),("hazards",[]),("severity","Medium")]:
        data.setdefault(k, v)
    data.setdefault("location_hint", f"{lat},{lon}" if lat is not None and lon is not None else "unknown")
    data.setdefault("evidence_notes", "")
    return data
