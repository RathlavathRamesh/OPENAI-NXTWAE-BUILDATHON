# ai_core/multimodal_inference_gateway_groq.py
from typing import Dict, Any, List
import base64
from shared.models import NormalizedIncident
from .asr_groq import transcribe_bytes_groq
from .groq_multimodal import infer_situation_with_groq

def multimodal_infer_groq(incident: NormalizedIncident) -> Dict[str, Any]:
    transcripts: List[str] = [t.text for t in incident.transcripts if t.text]

    # Transcribe audio/video via Groq ASR
    for m in incident.media:
        if m.modality in ("audio", "video"):
            try:
                transcripts.append(transcribe_bytes_groq(base64.b64decode(m.bytes_b64), m.filename))
            except Exception:
                pass

    # Collect images
    images_b64: List[tuple[str, str]] = [
        (m.mime_type, m.bytes_b64) for m in incident.media if m.modality == "image"
    ]
    # Call Groq multimodal once with everything
    breakpoint()
    result = infer_situation_with_groq(
        text_report=incident.text or "",
        transcripts=transcripts,
        images_b64=images_b64,
        lat=incident.lat,
        lon=incident.lon,
    )
    result["evidence_used"] = {
        "text_present": bool((incident.text or "").strip()),
        "transcript_present": any(t.strip() for t in transcripts),
        "images_count": len(images_b64),
    }
    return result
