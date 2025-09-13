# ai_core/multimodal_inference_gateway_gemini.py
from typing import Dict, Any, List, Tuple
import base64
from shared.models import NormalizedIncident
from .multi_model_api import infer_situation_with_gemini

def multimodal_infer_gemini(incident: NormalizedIncident) -> Dict[str, Any]:
    transcripts: List[str] = [t.text for t in incident.transcripts if t.text]

    # Collect images (mime, b64)
    images_b64: List[Tuple[str, str]] = [
        (m.mime_type, m.bytes_b64) for m in incident.media if m.modality == "image"
    ]


    result = infer_situation_with_gemini(
        text_report=(incident.text or ""),
        transcripts=transcripts,
        images_b64=images_b64,
        lat=incident.lat,
        lon=incident.lon,
    )
    result["evidence_used"] = {
        "text_present": bool((incident.text or "").strip()),
        "transcript_present": any((t or "").strip() for t in transcripts),
        "images_count": len(images_b64),
    }
    return result
