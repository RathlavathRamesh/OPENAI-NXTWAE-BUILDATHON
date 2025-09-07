# ai_core/multimodal_inference_gateway.py
from typing import Dict, Any, List
from shared.models import NormalizedIncident
from asr_openai import transcribe_bytes_gpt4o
from multimodal_openai import infer_situation_with_gpt

def multimodal_infer_openai(incident: NormalizedIncident) -> Dict[str, Any]:
    # Prepare transcripts: reuse existing transcripts if present,
    # else transcribe audio/video media now via endpoint.
    transcripts: List[str] = [t.text for t in incident.transcripts if t.text]

    for m in incident.media:
        if m.modality in ("audio", "video"):
            try:
                # Decode base64 back to bytes and transcribe
                import base64
                audio_bytes = base64.b64decode(m.bytes_b64)
                txt = transcribe_bytes_gpt4o(audio_bytes, m.filename)
                if txt:
                    transcripts.append(txt)
            except Exception:
                pass  # continue gracefully

    # Prepare images
    images_b64: List[tuple[str, str]] = []
    for m in incident.media:
        if m.modality == "image":
            images_b64.append((m.mime_type, m.bytes_b64))

    # Call GPT multimodal once with everything
    result = infer_situation_with_gpt(
        text_report=incident.text or "",
        transcripts=transcripts,
        images_b64=images_b64,
        lat=incident.lat,
        lon=incident.lon,
    )

    # Diagnostics
    result["evidence_used"] = {
        "text_present": bool((incident.text or "").strip()),
        "transcript_present": any(len(t.strip()) > 0 for t in transcripts),
        "images_count": len(images_b64),
    }
    return result
