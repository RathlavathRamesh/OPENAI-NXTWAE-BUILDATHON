# Pydantic Schemas for Disaster Response System
"""
All Pydantic models for request/response validation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

# =============================================================================
# Input Schemas
# =============================================================================

class MediaItem(BaseModel):
    """Schema for media items in the input"""
    filename: str
    content: str  # Base64 encoded content
    mime_type: str
    size: Optional[int] = None
    
    @validator('content')
    def validate_base64(cls, v):
        try:
            import base64
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError('Content must be valid base64 encoded')

class IncidentRequest(BaseModel):
    """Schema for incident processing request"""
    channel: str = Field(..., description="Input channel: app, whatsapp, sms")
    text: str = Field(..., description="Text message content")
    location: Optional[Dict[str, float]] = Field(None, description="Location as {lat: float, lon: float}")
    media_items: List[MediaItem] = Field(default=[], description="List of media files")
    incident_id: Optional[str] = Field(None, description="Optional incident ID")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    
    @validator('channel')
    def validate_channel(cls, v):
        if v not in ['app', 'whatsapp', 'sms']:
            raise ValueError('Channel must be one of: app, whatsapp, sms')
        return v

# =============================================================================
# Layer Response Schemas
# =============================================================================

class Layer1Response(BaseModel):
    """Response from Layer 1: Preprocess Agent"""
    agent: str
    layer: int
    timestamp: str
    incident_id: str
    status: str
    situation_analysis: Dict[str, Any]
    media_processed: Dict[str, Any]
    confidence: Dict[str, Any]
    preprocessed_input: Dict[str, Any]
    processing_metadata: Dict[str, Any]

class Layer2Response(BaseModel):
    """Response from Layer 2: Analysis Agent"""
    agent: str
    layer: int
    timestamp: str
    incident_id: str
    status: str
    incident_summary: Dict[str, Any]
    realworld_context: Dict[str, Any]
    location: Dict[str, Any]
    geospatial_analysis: Dict[str, Any]
    combined_analysis: Dict[str, Any]
    processing_metadata: Dict[str, Any]

class Layer3Response(BaseModel):
    """Response from Layer 3: Judge Agent"""
    agent: str
    layer: int
    timestamp: str
    incident_id: str
    status: str
    judge_verdict: Dict[str, Any]
    additional_analysis: Dict[str, Any]
    priority_score_0_10: int
    final_severity: str
    incident_authentic: bool
    reasoning: Dict[str, Any]
    recommendations: List[str]
    processing_metadata: Dict[str, Any]

# =============================================================================
# Final Response Schema
# =============================================================================

class CompleteResponse(BaseModel):
    """Complete response from all 3 layers"""
    request_id: str
    timestamp: str
    status: str
    processing_time_ms: int
    
    # Layer responses
    layer1_preprocess: Layer1Response
    layer2_analysis: Layer2Response
    layer3_judge: Layer3Response
    
    # Final results
    final_results: Dict[str, Any]
    
    # Error handling
    errors: List[str] = []

# =============================================================================
# Utility Schemas
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str

class StatusResponse(BaseModel):
    """System status response"""
    status: str
    timestamp: str
    layers: Dict[str, str]
    supported_channels: List[str]
    supported_media: List[str]

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str
