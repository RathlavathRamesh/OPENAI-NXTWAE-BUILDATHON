import os
from typing import List, Optional, Tuple

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your existing modules (absolute package imports)
from input_preprocessing.router import preprocess_request
from ai_core.multimodel_inference_gateway import multimodal_infer_gemini
from ai_core.weather_reports import get_weather_by_coords
from ai_core.incident_judge import judge_incident_with_gemini
app = FastAPI(title="Disaster Smart API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models (Pydantic)
class AnalyzeResponse(BaseModel):
    incident_request: dict
    realworld_context: dict
    judge: dict
    priority_score_0_10: int
    real_incident: bool

# Helpers
def _to_uploads(files: List[UploadFile]) -> List[Tuple[str, bytes, str]]:
    uploads = []
    for f in files or []:
        try:
            content = f.file.read()
        finally:
            f.file.close()
        uploads.append((f.filename or "upload.bin", content, f.content_type or ""))
    return uploads

def _compute_priority(severity: str, verdict: int) -> int:
    s = (severity or "").lower()
    base = 10 if s == "critical" else 8 if s == "high" else 5 if s in ("moderate","medium") else 3 if s == "low" else 4
    bonus = 2 if verdict >= 8 else 1 if verdict >= 5 else 0
    return min(10, base + bonus)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    channel: str = Form("app"),
    text: str = Form(""),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    files: List[UploadFile] = File(default=[]),
):
    try:
        # 1) Preprocess into incident
        uploads = _to_uploads(files)
        latlon_str = f"{lat},{lon}" if lat is not None and lon is not None else ""
        incident = preprocess_request(channel, text, latlon_str, uploads)

        # 2) Multimodal inference (Gemini) -> situation JSON
        situation = multimodal_infer_gemini(incident)

        # 3) Real-world context (weather/locality); require coords for fetch
        if lat is None or lon is None:
            realworld_context = {"ok": False, "reason": "missing_lat_lon"}
        else:
            realworld_context = get_weather_by_coords(lat, lon)

        # 4) Build incident_request object for judge
        incident_request = {
            "lat": incident.lat,
            "lon": incident.lon,
            "text_report": (incident.text or "").strip(),
            "transcript_excerpt": " ".join([t.text for t in incident.transcripts if t.text])[:6000],
            "situation_json": situation,
        }

        # 5) LLM-as-a-Judge gating (Gemini)
        judge = judge_incident_with_gemini(incident_request, realworld_context)

        # 6) Priority after gating
        if not judge.get("real_incident", False):
            priority = 0
        else:
            sev = (judge.get("final_severity") or situation.get("severity", "Unknown"))
            priority = _compute_priority(sev, int(judge.get("verdict_score_0_10", 0)))

        return AnalyzeResponse(
            incident_request=incident_request,
            realworld_context=realworld_context,
            judge=judge,
            priority_score_0_10=priority,
            real_incident=bool(judge.get("real_incident", False)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
