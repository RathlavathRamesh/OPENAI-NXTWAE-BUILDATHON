#!/usr/bin/env python3
"""
Simple test API for RakshaSetu Disaster Response System
This version doesn't require database connections for testing
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime

# Import your existing modules
from shared.models import NormalizedIncident
from input_preprocessing.router import preprocess_request

app = FastAPI(title="RakshaSetu Test API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AnalyzeResponse(BaseModel):
    incident_id: str
    incident_request: dict
    realworld_context: dict
    priority_score_0_10: int
    real_incident: bool

class TestResponse(BaseModel):
    message: str
    status: str
    timestamp: str

@app.get("/")
async def root():
    return TestResponse(
        message="🚨 RakshaSetu Disaster Response API is running!",
        status="operational",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rakshasetu-api"}

@app.post("/test-analyze", response_model=AnalyzeResponse)
async def test_analyze(
    channel: str = Form("app"),
    text: str = Form(""),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    files: List[UploadFile] = File(default=[]),
):
    """
    Test endpoint for incident analysis without external dependencies
    """
    try:
        # Generate a test incident ID
        incident_id = str(uuid.uuid4())
        
        # Create a mock incident request
        incident_request = {
            "situation_summary": f"Test emergency: {text}",
            "hazards": [{"type": "test", "severity": "medium", "details": "Test hazard"}],
            "people_affected": {"visible_count_estimate": 1, "injuries_visible": False},
            "infrastructure": {"blocked_roads": []},
            "location_hint": f"{lat},{lon}" if lat and lon else "Unknown location",
            "lat": lat,
            "lon": lon
        }
        
        # Mock real-world context
        realworld_context = {
            "location": "Test Location",
            "description": "Clear weather",
            "temperature_C": 22,
            "humidity_percent": 60
        }
        
        # Mock priority calculation
        priority = 5  # Medium priority for test
        
        return AnalyzeResponse(
            incident_id=incident_id,
            incident_request=incident_request,
            realworld_context=realworld_context,
            priority_score_0_10=priority,
            real_incident=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test analysis failed: {str(e)}")

@app.post("/test-preprocess")
async def test_preprocess(
    channel: str = Form("app"),
    text: str = Form(""),
    latlon_str: str = Form(""),
    files: List[UploadFile] = File(default=[]),
):
    """
    Test the preprocessing pipeline
    """
    try:
        # Convert files to the expected format
        uploads = []
        for f in files or []:
            try:
                content = f.file.read()
            finally:
                f.file.close()
            uploads.append((f.filename or "upload.bin", content, f.content_type or ""))
        
        # Test preprocessing
        incident = preprocess_request(channel, text, latlon_str, uploads)
        
        return {
            "status": "success",
            "incident": {
                "channel": incident.channel,
                "text": incident.text,
                "lat": incident.lat,
                "lon": incident.lon,
                "media_count": len(incident.media),
                "transcripts_count": len(incident.transcripts),
                "images_meta_count": len(incident.images_meta),
                "notes": incident.notes
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
