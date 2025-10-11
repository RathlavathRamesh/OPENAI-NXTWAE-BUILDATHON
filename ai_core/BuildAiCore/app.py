# app.py
from __future__ import annotations
import os, sys, base64
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Resolve project root and load .env early
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
load_dotenv(os.path.join(os.path.dirname(ROOT), ".env"))
load_dotenv()  # fallback search

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
if not GEMINI_API_KEY:
    print("⚠️ No Gemini key found (GEMINI_API_KEY/GOOGLE_API_KEY).")

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from schemas import IncidentRequest, CompleteResponse
from preprocess_agent import run_preprocess_agent
from analysis_agent import run_analysis_agent
from judge_agent import run_judge_agent

app = FastAPI(
    title="Disaster Response AI System (Gemini Only)",
    description="3-layer AI pipeline: Preprocess → Analysis → Judge",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/upload_request", response_model=CompleteResponse)
async def upload_request(
    channel: str = Form(...),
    text: str = Form(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    incident_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[])
):
    start_time = datetime.utcnow()
    request_id = incident_id or f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
    errors: List[str] = []

    latlon = f"{lat},{lon}" if lat is not None and lon is not None else None

    uploads: List[Dict[str, Any]] = []
    for f in files:
        try:
            content = await f.read()
            uploads.append({
                "filename": f.filename,
                "content": base64.b64encode(content).decode("utf-8"),
                "mime_type": f.content_type or "application/octet-stream",
                "size": len(content),
            })
        except Exception as e:
            errors.append(f"file {f.filename}: {e}")

    layer1 = await run_preprocess_agent(channel=channel, text=text, latlon=latlon, uploads=uploads)
    breakpoint()
    lat_coord, lon_coord = 17.3850, 78.4867
    if lat is not None and lon is not None:
        lat_coord, lon_coord = lat, lon
    layer2 = run_analysis_agent(layer1, lat_coord, lon_coord)
    layer3 = run_judge_agent(layer2)

    processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    final_priority = layer3.get("priority_score_0_10", 0)
    final_authentic = layer3.get("incident_authentic", True)
    final_severity = layer3.get("final_severity", "Unknown")

    return CompleteResponse(
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        status="completed",
        processing_time_ms=processing_time,
        layer1_preprocess=layer1,
        layer2_analysis=layer2,
        layer3_judge=layer3,
        final_results={
            "priority_score": final_priority,
            "authentic": final_authentic,
            "severity": final_severity,
            "summary": layer1.get("situation_analysis", {}).get("summary", ""),
            "recommendations": layer3.get("recommendations", []),
        },
        errors=errors,
    )
