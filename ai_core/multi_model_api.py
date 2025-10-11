# ai_core/multimodal_gemini.py
import os, json, re
from typing import Dict, Any, List, Tuple
from google import genai
from utils.load_utils import load_prompt_template

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_SITUATION_MODEL = os.getenv("GEMINI_SITUATION_MODEL", "gemini-2.5-flash")

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

def infer_situation_with_gemini(
    text_report: str,
    transcripts: List[str],
    images_b64: List[Tuple[str, str]],
    lat: float | None,
    lon: float | None,
    max_images: int = 4,
) -> Dict[str, Any]:
    try:
        client = _get_client()
        
        # Load strict situation-analysis prompt (JSON schema)
        system_prompt = load_prompt_template("prompts/incident_situation_analysis_gemini.txt")
        
        # Build text content first - COMBINE ALL TEXT INTO ONE STRING
        text_parts = [system_prompt]
        
        if text_report and text_report.strip():
            text_parts.append(f"TEXT REPORT:\n{text_report.strip()}")
        
        if transcripts:
            joined = " ".join([t for t in transcripts if t])[:6000]
            if joined:
                text_parts.append(f"AUDIO/VIDEO TRANSCRIPT:\n{joined}")
        
        if lat is not None and lon is not None:
            text_parts.append(f"LOCATION: {lat},{lon}")
        
        # COMBINE ALL TEXT INTO A SINGLE STRING
        combined_text = "\n\n".join(text_parts)
        
        # Build multimodal content - start with the text
        content: List[Any] = [combined_text]  # START WITH COMBINED TEXT
        
        # Add images using PIL Image objects (NOT dictionaries)
        for mime, b64 in images_b64[:max_images]:
            try:
                # ADD THESE IMPORTS AT TOP OF FILE IF NOT PRESENT:
                import base64
                from PIL import Image
                from io import BytesIO
                
                image_data = base64.b64decode(b64)
                pil_image = Image.open(BytesIO(image_data))
                
                # Add the PIL Image object directly
                content.append(pil_image)  # THIS IS THE KEY FIX
                
            except Exception as e:
                print(f"Error processing image: {e}")
                continue
        
        # Call Gemini
        resp = client.models.generate_content(
            model=GEMINI_SITUATION_MODEL,
            contents=content,  # This now has correct format
            config={"temperature": 0.2},
        )
        
        raw = (getattr(resp, "text", "") or "").strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(json)?\s*|\s*```$", "", raw, flags=re.DOTALL)

        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "situation_summary": raw[:500],
                "hazards": [],
                "severity": "Medium",
                "location_hint": f"{lat},{lon}" if lat is not None and lon is not None else "unknown",
                "evidence_notes": "Non-JSON response; fallback applied."
            }

    except Exception as e:
        print(f"Gemini API error: {e}")
        # Return mock response if API fails
        data = {
            "situation_summary": f"Mock analysis for: {text_report[:100]}...",
            "hazards": [{"type": "test", "severity": "Medium", "details": "Mock hazard"}],
            "people_affected": {"visible_count_estimate": 1, "injuries_visible": False},
            "infrastructure": {"blocked_roads": [], "power_lines_down": False, "critical_facilities_affected": []},
            "access_constraints": ["Mock constraint"],
            "severity": "Medium",
            "location_hint": f"{lat},{lon}" if lat is not None and lon is not None else "unknown",
            "evidence_notes": f"Mock response due to API error: {str(e)}"
        }

    # Ensure defaults
    for k, v in [("situation_summary","No summary"),("hazards",[]),("severity","Medium")]:
        data.setdefault(k, v)
    data.setdefault("location_hint", f"{lat},{lon}" if lat is not None and lon is not None else "unknown")
    data.setdefault("evidence_notes", "")
    return data