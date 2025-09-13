from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

Modality = Literal["text", "image", "audio", "video"]

class MediaItem(BaseModel):
    modality: Modality
    filename: str
    mime_type: str
    bytes_b64: str  # keep small for demo; use object storage in prod

class ImageMeta(BaseModel):
    width: int
    height: int
    format: str
    exif: dict
    bytes_b64: str      # ADD THIS LINE
    mime_type: str  
class Transcript(BaseModel):
    text: str
    language: Optional[str] = None
    segments: List[Dict[str, Any]] = Field(default_factory=list)

class NormalizedIncident(BaseModel):
    channel: Literal["sms", "whatsapp", "app", "unknown"] = "app"
    text: str = ""
    media: List[MediaItem] = Field(default_factory=list)
    images_meta: List[ImageMeta] = Field(default_factory=list)
    transcripts: List[Transcript] = Field(default_factory=list)
    lat: Optional[float] = None
    lon: Optional[float] = None
    detected_language: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
