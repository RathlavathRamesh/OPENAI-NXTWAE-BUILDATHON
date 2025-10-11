# app.py
from __future__ import annotations
import os, sys, base64
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

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
from BE.utils import (processed_input_summary_json, analyze_summarize_json ,
 judgement_summary_json , final_summary_json)

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

# ---------- MIME correction helpers ----------
def sniff_mime_from_name(name: str) -> str:
    n = (name or "").lower()
    if n.endswith(".mp4"):   return "video/mp4"
    if n.endswith(".mov"):   return "video/quicktime"
    if n.endswith(".mkv"):   return "video/x-matroska"
    if n.endswith(".webm"):  return "video/webm"
    if n.endswith(".wav"):   return "audio/wav"
    if n.endswith(".mp3"):   return "audio/mpeg"
    if n.endswith(".m4a"):   return "audio/mp4"
    if n.endswith(".aac"):   return "audio/aac"
    if n.endswith(".jpg") or n.endswith(".jpeg"): return "image/jpeg"
    if n.endswith(".png"):   return "image/png"
    if n.endswith(".webp"):  return "image/webp"
    return "application/octet-stream"

def force_mime_by_name(filename: str, incoming: Optional[str]) -> str:
    # Always trust filename extension over incoming header
    guessed = sniff_mime_from_name(filename)
    return guessed or (incoming or "application/octet-stream")

# ---------- Endpoint ----------
@app.post("/upload_request", response_model=CompleteResponse)
async def upload_request(
    channel: str = Form(...),
    text: str = Form(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    incident_id: Optional[int] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    start_time = datetime.utcnow()
    request_id = incident_id or f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
    errors: List[str] = []

    latlon = f"{lat},{lon}" if lat is not None and lon is not None else None

    print(f"[upload_request] received files count = {len(files or [])}")

    uploads: List[Dict[str, Any]] = []
    for f in files or []:
        try:
            # Show what client sent
            print(f"[upload_request] incoming part: {f.filename} -> {f.content_type}")
            content = await f.read()

            # Hard override MIME by filename, ignoring incorrect client headers
            mime = force_mime_by_name(f.filename or "", f.content_type)
            if (f.content_type or "").startswith("image/") and mime.startswith("video/"):
                print(f"[upload_request] correcting client MIME: {f.filename} {f.content_type} -> {mime}")

            uploads.append({
                "filename": f.filename or "",
                "content": base64.b64encode(content).decode("utf-8"),
                "mime_type": mime,
                "size": len(content),
            })
            print(f"[upload_request] normalized: {f.filename} -> {mime}, size={len(content)}")

        except Exception as e:
            errors.append(f"file {getattr(f, 'filename', 'unknown')}: {e}")

    # Proceed through agents; uploads may be empty (text-only)
    layer1 = await run_preprocess_agent(channel=channel, text=text, latlon=latlon, uploads=uploads)
    result1=processed_input_summary_json(incident_id, layer1)
    print(f"result1: {result1}")
    lat_coord, lon_coord = (lat or 17.3850), (lon or 78.4867)
    layer2 = run_analysis_agent(layer1, lat_coord, lon_coord)
    result2=analyze_summarize_json(incident_id, layer2)
    print(f"result2: {result2}")
    layer3 = run_judge_agent(layer2)
    result3=judgement_summary_json(incident_id, layer3)
    print(f"result3: {result3}")
    processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    final_priority = layer3.get("priority_score_0_10", 0)
    final_authentic = layer3.get("incident_authentic", True)
    final_severity = layer3.get("final_severity", "Unknown")
    final_json={
            "priority_score": final_priority,
            "authentic": final_authentic,
            "severity": final_severity,
            "summary": layer1.get("situation_analysis", {}).get("summary", ""),
            "recommendations": layer3.get("recommendations", []),
        }
    final_result=final_summary_json(incident_id, final_json)
    print(f"final_result: {final_result}")
    return CompleteResponse(
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        status="completed",
        processing_time_ms=processing_time,
        layer1_preprocess=layer1,
        layer2_analysis=layer2,
        layer3_judge=layer3,
        final_results=final_json,
        errors=errors,
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

