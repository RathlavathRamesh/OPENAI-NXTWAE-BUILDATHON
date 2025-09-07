# ai_core/multimodal_inference.py
from typing import Dict, Any, List
import os 

from shared.models import NormalizedIncident
from openai import OpenAI
import  re, json 
# Configure once
CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"  # pick your multimodal capable model [8][1]

def _b64_url(mime: str, b64: str) -> str:
    # Build data URL: data:<mime>;base64,<payload>
    return f"data:{mime};base64,{b64}"

def _build_messages(incident: NormalizedIncident, image_limits: int = 4) -> List[Dict[str, Any]]:
    # Compose a single user message with text + up to N images + optional transcript text
    user_content: List[Dict[str, Any]] = []

    # 1) Instruction + schema hint
    instruction = (
        "You are a disaster analyst. Infer exactly what happened from the evidence. "
        "Return a strict JSON object with keys: situation_summary (string), "
        "hazards (array of strings), severity (Low|Medium|High|Severe), "
        "location_hint (string), evidence_notes (short string). "
        "Be concise and factual; do not invent details not visible or stated."
    )
    user_content.append({"type": "text", "text": instruction})

    # 2) Add raw text if present
    if (incident.text or "").strip():
        user_content.append({"type": "text", "text": f"TEXT REPORT:\n{incident.text.strip()}"})

    # 3) Add AV transcripts (already produced in preprocessing)
    if incident.transcripts:
        joined = " ".join([t.text for t in incident.transcripts if t.text])[:3000]
        if joined:
            user_content.append({"type": "text", "text": f"AUDIO/VIDEO TRANSCRIPT:\n{joined}"})

    # 4) Add images (as base64 data URLs). Limit to keep token/bandwidth sensible.
    img_count = 0
    for m in incident.media:
        if img_count >= image_limits:
            break
        if m.modality == "image":
            user_content.append({
                "type": "image_url",
                "image_url": {"url": _b64_url(m.mime_type, m.bytes_b64)}
            })
            img_count += 1

    # 5) Add location if provided
    if incident.lat is not None and incident.lon is not None:
        user_content.append({"type": "text", "text": f"LOCATION: {incident.lat},{incident.lon}"})

    # 6) Add explicit JSON-return instruction
    user_content.append({"type": "text", "text": "Return only the JSON object. No extra text."})

    return [{"role": "user", "content": user_content}]

def multimodal_infer(incident: NormalizedIncident) -> Dict[str, Any]:
    messages = _build_messages(incident)

    # Call the chat completions API
    # Tip: If your account supports structured outputs, you can also use response_format later [15][6]
    resp = CLIENT.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=500,
    )

    raw = resp.choices.message.content or "{}"
    # Attempt to parse JSON; if assistant returns code fences, strip them
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)

    try:
        data = json.loads(cleaned)
    except Exception:
        # Fallback: wrap as free-text summary if JSON parse fails
        data = {
            "situation_summary": cleaned[:400],
            "hazards": [],
            "severity": "Medium",
            "location_hint": f"{incident.lat},{incident.lon}" if (incident.lat and incident.lon) else "unknown",
            "evidence_notes": "Model returned non-JSON; fallback applied."
        }

    # Minimal post-validation
    data.setdefault("situation_summary", "No summary")
    data.setdefault("hazards", [])
    data.setdefault("severity", "Medium")
    data.setdefault("location_hint", f"{incident.lat},{incident.lon}" if (incident.lat and incident.lon) else "unknown")
    data.setdefault("evidence_notes", "")

    # Add diagnostics
    data["evidence_used"] = {
        "text_present": bool((incident.text or "").strip()),
        "transcript_present": any(bool(t.text) for t in incident.transcripts),
        "images_count": sum(1 for m in incident.media if m.modality == "image"),
    }
    return data