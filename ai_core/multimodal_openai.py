# multimodal_openai.py
import os
import re 
import json
from typing import Dict, Any, List
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"  # vision-capable chat model [19]

def _data_url(mime: str, b64: str) -> str:
    return f"data:{mime};base64,{b64}"

def infer_situation_with_gpt(
    text_report: str,
    transcripts: List[str],
    images_b64: List[tuple[str, str]],  # list of (mime, b64)
    lat: float | None,
    lon: float | None,
    max_images: int = 4,
) -> Dict[str, Any]:

    content = []

    # Instruction and explicit schema
    content.append({
        "type": "text",
        "text": ("You are a disaster analyst. From the evidence below, output strict JSON with keys: "
                 "situation_summary (string), hazards (array of strings), severity (Low|Medium|High|Severe), "
                 "location_hint (string), evidence_notes (string). Return only JSON.")
    })

    if text_report and text_report.strip():
        content.append({"type": "text", "text": f"TEXT REPORT:\n{text_report.strip()}"})

    if transcripts:
        joined = " ".join([t for t in transcripts if t])[:3000]
        if joined:
            content.append({"type": "text", "text": f"AUDIO/VIDEO TRANSCRIPT:\n{joined}"})

    # Images (data URLs or https URLs). Base64 data URLs are standard for dev flows. [8][11][6]
    for i, (mime, b64) in enumerate(images_b64[:max_images]):
        content.append({"type": "image_url", "image_url": {"url": _data_url(mime, b64)}})

    if lat is not None and lon is not None:
        content.append({"type": "text", "text": f"LOCATION: {lat},{lon}"})

    # Call the chat completions endpoint
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=600,
    )
    raw = resp.choices.message.content or "{}"

    # Parse JSON (strip code fences if present)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    try:
        data = json.loads(cleaned)
    except Exception:
        # Fallback if model didn't obey
        data = {
            "situation_summary": cleaned[:500],
            "hazards": [],
            "severity": "Medium",
            "location_hint": f"{lat},{lon}" if lat is not None and lon is not None else "unknown",
            "evidence_notes": "Model returned non-JSON; fallback applied."
        }

    # Basic defaults
    data.setdefault("situation_summary", "No summary")
    data.setdefault("hazards", [])
    data.setdefault("severity", "Medium")
    data.setdefault("location_hint", f"{lat},{lon}" if lat is not None and lon is not None else "unknown")
    data.setdefault("evidence_notes", "")

    return data
