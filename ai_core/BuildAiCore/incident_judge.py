import os, json
from typing import Dict, Any, List
import google.generativeai as genai

# ---------------------------------------------------------------------------
# ✅ Configuration
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_JUDGE_MODEL = os.getenv("GEMINI_JUDGE_MODEL", "gemini-2.5-flash")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(GEMINI_JUDGE_MODEL)
else:
    gemini_model = None
    print("⚠️ Warning: No Gemini API key found. Set GEMINI_API_KEY environment variable.")

# ---------------------------------------------------------------------------
# ✅ Judge schema and system prompt
# ---------------------------------------------------------------------------
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "criteria": {
            "type": "object",
            "properties": {
                "location": {"type": "number"},
                "hazard": {"type": "number"},
                "severity": {"type": "number"},
                "impact": {"type": "number"},
                "recency": {"type": "number"},
            },
            "required": ["location", "hazard", "severity", "impact", "recency"],
        },
        "verdict_score_0_10": {"type": "integer"},
        "real_incident": {"type": "boolean"},
        "final_severity": {"type": "string"},
        "explanation": {"type": "string"},
    },
    "required": [
        "criteria",
        "verdict_score_0_10",
        "real_incident",
        "final_severity",
        "explanation",
    ],
}

JUDGE_SYSTEM = (
    "You are an impartial disaster incident judge.\n"
    "Given two inputs — an ML-derived incident report and an external real-world context for the same coordinates — "
    "decide if the incident is REAL and CURRENT. Judge on: location proximity (~8km/same locality), hazard alignment "
    "(synonyms OK), severity plausibility (±1 level), impact evidence match, and recency.\n"
    "Return ONLY JSON using the provided schema; scores are 0..1 and verdict_score is 0..10."
)

# ---------------------------------------------------------------------------
# ✅ Core logic
# ---------------------------------------------------------------------------
def judge_incident_with_gemini(
    incident_request: Dict[str, Any],
    realworld_context: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        if not gemini_model:
            raise RuntimeError("Gemini model not initialized (missing API key).")

        contents: List[Any] = [
            JUDGE_SYSTEM,
            f"INCIDENT_REQUEST_JSON:\n{json.dumps(incident_request, ensure_ascii=False)}",
            f"REALWORLD_CONTEXT_JSON:\n{json.dumps(realworld_context, ensure_ascii=False)}",
        ]

        # ✅ Generate structured response
        resp = gemini_model.generate_content(
            contents,
            generation_config={
                "temperature": 0.0,
                "response_mime_type": "application/json",
            },
        )

        txt = (getattr(resp, "text", "") or "").strip()
        try:
            out = json.loads(txt) if txt else {}
        except Exception:
            out = {}

    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback mock response
        out = {
            "criteria": {
                "location": 0.5,
                "hazard": 0.5,
                "severity": 0.5,
                "impact": 0.5,
                "recency": 0.5,
            },
            "verdict_score_0_10": 5,
            "real_incident": True,
            "final_severity": "Medium",
            "explanation": f"Mock response due to API error: {e}",
        }

    # -----------------------------------------------------------------------
    # ✅ Postprocessing / clamping
    # -----------------------------------------------------------------------
    crit = out.get("criteria", {})
    for k in ["location", "hazard", "severity", "impact", "recency"]:
        try:
            crit[k] = float(crit.get(k, 0))
        except Exception:
            crit[k] = 0.0
        crit[k] = max(0.0, min(1.0, crit[k]))

    out["criteria"] = crit or {
        "location": 0,
        "hazard": 0,
        "severity": 0,
        "impact": 0,
        "recency": 0,
    }

    try:
        out["verdict_score_0_10"] = int(out.get("verdict_score_0_10", 0))
    except Exception:
        out["verdict_score_0_10"] = 0

    out["verdict_score_0_10"] = max(0, min(10, out["verdict_score_0_10"]))
    out["real_incident"] = bool(out.get("real_incident", False))
    out["final_severity"] = str(out.get("final_severity", "Unknown"))
    out["explanation"] = str(out.get("explanation", ""))

    return out
