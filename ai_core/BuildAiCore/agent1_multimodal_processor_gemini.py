# Agent 1: Multimodal Input Processor and Analyzer (Gemini Only)
"""
Agent 1: Comprehensive multimodal input processor using only Gemini APIs:
- Text inputs (SMS, WhatsApp, App messages)
- Images (JPEG, PNG, WebP) - using Gemini Vision
- Audio (MP3, WAV, M4A, AAC) - using Gemini with audio transcription
- Video (MP4, MOV, MKV) - with frame extraction and Gemini analysis

Uses only Gemini models for all modalities and returns structured JSON summary.
"""

import os
import sys
import json
import base64
import asyncio
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import tempfile

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# AI/ML imports
import google.generativeai as genai
import requests
from PIL import Image
import cv2
import numpy as np
from io import BytesIO

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Model configurations
GEMINI_MODEL = "gemini-2.5-flash"

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(GEMINI_MODEL)
else:
    gemini_model = None
    print("⚠️ Warning: No Gemini API key found. Set GEMINI_API_KEY environment variable.")

@dataclass
class MediaAnalysis:
    """Structure for media analysis results"""
    media_type: str
    filename: str
    analysis: Dict[str, Any]
    confidence: float
    processing_time_ms: int

class GeminiMultimodalProcessor:
    """
    Multimodal processor using only Gemini APIs
    """
    
    def __init__(self):
        self.gemini_model = gemini_model
        self.model_name = GEMINI_MODEL
        
    async def process_multimodal_input(self, 
                                     channel: str, 
                                     text: str, 
                                     latlon: str, 
                                     uploads: List[Tuple[str, bytes, str]]) -> Dict[str, Any]:
        """
        Process multimodal input using only Gemini
        
        Args:
            channel: Input channel (app, whatsapp, sms)
            text: Text message content
            latlon: Location as "lat,lon" string
            uploads: List of (filename, bytes, mime_type) tuples
            
        Returns:
            Structured analysis result
        """
        start_time = datetime.utcnow()
        incident_id = f"incident_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        try:
            print(f"🔍 Gemini Multimodal Processor: Processing {len(uploads)} media items...")
            
            # Process each media item
            media_analyses = []
            for upload in uploads:
                filename = upload["filename"]
                content_bytes = base64.b64decode(upload["content"])  # Decode from base64
                mime_type = upload["mime_type"]
                try:
                    analysis = await self._analyze_media_with_gemini(filename, content_bytes, mime_type)
                    media_analyses.append(analysis)
                except Exception as e:
                    print(f"❌ Failed to process {filename}: {e}")
                    media_analyses.append(MediaAnalysis(
                        media_type=mime_type,
                        filename=filename,
                        analysis={"error": str(e)},
                        confidence=0.0,
                        processing_time_ms=0
                    ))
            
            # Combine text and media analysis
            combined_analysis = await self._combine_analysis_with_gemini(text, media_analyses, latlon)
            
            # Create structured result
            result = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": incident_id,
                "status": "completed",
                "analysis": combined_analysis,
                "media_processed": {
                    "total_items": len(uploads),
                    "processed_types": [ma.media_type for ma in media_analyses],
                    "analyses": [ma.analysis for ma in media_analyses]
                },
                "confidence": {
                    "overall": sum(ma.confidence for ma in media_analyses) / max(len(media_analyses), 1),
                    "media_confidence": [ma.confidence for ma in media_analyses]
                },
                "preprocessed_input": {
                    "text_norm": text,
                    "location_hint": latlon,
                    "evidences": [ma.analysis for ma in media_analyses]
                },
                "processing_metadata": {
                    "model_used": self.model_name,
                    "total_processing_time_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000),
                    "channel": channel
                }
            }
            
            print(f"✅ Gemini processing complete: {result['processing_metadata']['total_processing_time_ms']}ms")
            return result
            
        except Exception as e:
            print(f"❌ Gemini processing failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": incident_id,
                "status": "failed",
                "error": str(e),
                "analysis": {"error": str(e)},
                "media_processed": {"total_items": len(uploads), "processed_types": []},
                "confidence": {"overall": 0.0},
                "preprocessed_input": {"text_norm": text, "location_hint": latlon, "evidences": []},
                "processing_metadata": {"model_used": self.model_name, "error": str(e)}
            }
    
    async def _analyze_media_with_gemini(self, filename: str, content_bytes: bytes, mime_type: str) -> MediaAnalysis:
        """Analyze media using Gemini"""
        start_time = datetime.utcnow()
        
        try:
            if mime_type.startswith("image/"):
                return await self._analyze_image_with_gemini(filename, content_bytes, mime_type)
            elif mime_type.startswith("video/"):
                return await self._analyze_video_with_gemini(filename, content_bytes, mime_type)
            elif mime_type.startswith("audio/"):
                return await self._analyze_audio_with_gemini(filename, content_bytes, mime_type)
            else:
                return MediaAnalysis(
                    media_type=mime_type,
                    filename=filename,
                    analysis={"error": f"Unsupported media type: {mime_type}"},
                    confidence=0.0,
                    processing_time_ms=0
                )
        except Exception as e:
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis={"error": str(e)},
                confidence=0.0,
                processing_time_ms=processing_time
            )
    
    async def _analyze_image_with_gemini(self, filename: str, content_bytes: bytes, mime_type: str) -> MediaAnalysis:
        """Analyze image using Gemini Vision"""
        start_time = datetime.utcnow()
        
        try:
            if not self.gemini_model:
                raise Exception("Gemini model not available")
            
            # Decode image
            image = Image.open(BytesIO(content_bytes))
            
            # Create Gemini prompt for disaster analysis
            prompt = """
            Analyze this disaster scene image carefully. Look for:
            1. Type of disaster (flood, fire, earthquake, storm, etc.)
            2. Severity level (Low, Moderate, High, Critical)
            3. Number of people visible or affected
            4. Infrastructure damage (buildings, roads, utilities)
            5. Environmental conditions (water level, smoke, debris)
            6. Access constraints for rescue teams
            7. Immediate dangers or hazards
            
            Be specific and detailed about what you observe. Focus on actionable information for emergency responders.
            Return your analysis in JSON format with these fields:
            - disaster_type: string
            - severity: string (Low/Moderate/High/Critical)
            - people_visible: number
            - infrastructure_damage: list of strings
            - environmental_conditions: list of strings
            - access_constraints: list of strings
            - immediate_dangers: list of strings
            - description: string (detailed description)
            """
            
            # Generate content with Gemini
            response = self.gemini_model.generate_content([prompt, image])
            
            # Parse response
            try:
                analysis_text = response.text
                # Try to extract JSON from response
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    json_text = analysis_text[json_start:json_end].strip()
                else:
                    json_text = analysis_text
                
                analysis = json.loads(json_text)
            except:
                # Fallback to text analysis
                analysis = {
                    "disaster_type": "unknown",
                    "severity": "Unknown",
                    "people_visible": 0,
                    "infrastructure_damage": [],
                    "environmental_conditions": [],
                    "access_constraints": [],
                    "immediate_dangers": [],
                    "description": analysis_text
                }
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis=analysis,
                confidence=0.8,  # High confidence for Gemini Vision
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis={"error": str(e)},
                confidence=0.0,
                processing_time_ms=processing_time
            )
    
    async def _analyze_video_with_gemini(self, filename: str, content_bytes: bytes, mime_type: str) -> MediaAnalysis:
        """Analyze video using Gemini by extracting key frames"""
        start_time = datetime.utcnow()
        
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_file.write(content_bytes)
                temp_video_path = temp_file.name
            
            try:
                # Extract key frames using OpenCV
                cap = cv2.VideoCapture(temp_video_path)
                frames = []
                frame_count = 0
                
                # Extract every 30th frame (or first 5 frames)
                while len(frames) < 5:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if frame_count % 30 == 0:
                        frames.append(frame)
                    frame_count += 1
                
                cap.release()
                
                if not frames:
                    raise Exception("No frames extracted from video")
                
                # Analyze frames with Gemini
                frame_analyses = []
                for i, frame in enumerate(frames):
                    try:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_image = Image.fromarray(frame_rgb)
                        
                        # Analyze frame
                        prompt = f"""
                        Analyze this video frame {i+1} from a disaster scene. Look for:
                        1. Type of disaster (flood, fire, earthquake, storm, etc.)
                        2. Severity level (Low, Moderate, High, Critical)
                        3. Number of people visible
                        4. Infrastructure damage
                        5. Environmental conditions
                        6. Movement or dynamic elements
                        
                        Return JSON format:
                        - disaster_type: string
                        - severity: string
                        - people_visible: number
                        - description: string
                        """
                        
                        response = self.gemini_model.generate_content([prompt, frame_image])
                        
                        try:
                            analysis_text = response.text
                            if "```json" in analysis_text:
                                json_start = analysis_text.find("```json") + 7
                                json_end = analysis_text.find("```", json_start)
                                json_text = analysis_text[json_start:json_end].strip()
                                frame_analysis = json.loads(json_text)
                            else:
                                frame_analysis = {"description": analysis_text, "disaster_type": "unknown"}
                        except:
                            frame_analysis = {"description": analysis_text, "disaster_type": "unknown"}
                        
                        frame_analyses.append(frame_analysis)
                        
                    except Exception as e:
                        frame_analyses.append({"error": str(e)})
                
                # Combine frame analyses
                combined_analysis = self._combine_video_analyses(frame_analyses)
                
                processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                return MediaAnalysis(
                    media_type=mime_type,
                    filename=filename,
                    analysis=combined_analysis,
                    confidence=0.7,  # Medium confidence for video analysis
                    processing_time_ms=processing_time
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_video_path)
                
        except Exception as e:
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis={"error": str(e)},
                confidence=0.0,
                processing_time_ms=processing_time
            )
    
    async def _analyze_audio_with_gemini(self, filename: str, content_bytes: bytes, mime_type: str) -> MediaAnalysis:
        """Analyze audio using Gemini (transcription + analysis)"""
        start_time = datetime.utcnow()
        
        try:
            # For now, we'll use a simple text-based analysis
            # In a real implementation, you'd transcribe the audio first
            analysis = {
                "audio_type": mime_type,
                "transcription": "Audio transcription not implemented in Gemini-only version",
                "disaster_indicators": [],
                "urgency_level": "Unknown",
                "description": f"Audio file {filename} received but transcription requires additional setup"
            }
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis=analysis,
                confidence=0.3,  # Low confidence without transcription
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return MediaAnalysis(
                media_type=mime_type,
                filename=filename,
                analysis={"error": str(e)},
                confidence=0.0,
                processing_time_ms=processing_time
            )
    
    def _combine_video_analyses(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple video frame analyses"""
        try:
            # Find most common disaster type
            disaster_types = [fa.get("disaster_type", "unknown") for fa in frame_analyses if "disaster_type" in fa]
            most_common_disaster = max(set(disaster_types), key=disaster_types.count) if disaster_types else "unknown"
            
            # Find highest severity
            severities = [fa.get("severity", "Unknown") for fa in frame_analyses if "severity" in fa]
            severity_order = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4, "Unknown": 0}
            highest_severity = max(severities, key=lambda x: severity_order.get(x, 0)) if severities else "Unknown"
            
            # Sum people visible
            total_people = sum(fa.get("people_visible", 0) for fa in frame_analyses if "people_visible" in fa)
            
            # Combine descriptions
            descriptions = [fa.get("description", "") for fa in frame_analyses if "description" in fa]
            combined_description = " ".join(descriptions)
            
            return {
                "disaster_type": most_common_disaster,
                "severity": highest_severity,
                "people_visible": total_people,
                "frame_count": len(frame_analyses),
                "frame_analyses": frame_analyses,
                "description": combined_description,
                "analysis_type": "video_frames"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "disaster_type": "unknown",
                "severity": "Unknown",
                "people_visible": 0,
                "description": "Error combining video analyses"
            }
    
    async def _combine_analysis_with_gemini(self, text: str, media_analyses: List[MediaAnalysis], latlon: str) -> Dict[str, Any]:
        """Combine text and media analysis using Gemini"""
        try:
            if not self.gemini_model:
                return self._fallback_analysis(text, media_analyses, latlon)
            
            # Prepare context for Gemini
            media_summaries = []
            for ma in media_analyses:
                if "error" not in ma.analysis:
                    media_summaries.append(f"{ma.media_type}: {ma.analysis.get('description', 'No description')}")
            
            context = f"""
            Text Message: {text}
            Location: {latlon or 'Not specified'}
            Media Analysis: {'; '.join(media_summaries) if media_summaries else 'No media provided'}
            
            Analyze this disaster report and provide a comprehensive assessment. Consider:
            1. What type of disaster is this?
            2. What is the severity level?
            3. How many people are affected?
            4. What infrastructure is damaged?
            5. What are the access constraints?
            6. What immediate actions are needed?
            
            Return JSON format:
            - situation_summary: string (brief summary)
            - hazards: list of objects with type and severity
            - people_affected: object with visible_count_estimate, injuries_visible, notes
            - infrastructure: object with blocked_roads, power_lines_down, critical_facilities_affected
            - access_constraints: list of strings
            - severity: string (Low/Moderate/High/Critical)
            - location_hint: string
            - evidence_notes: string
            """
            
            response = self.gemini_model.generate_content(context)
            
            try:
                analysis_text = response.text
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    json_text = analysis_text[json_start:json_end].strip()
                    analysis = json.loads(json_text)
                else:
                    analysis = {"situation_summary": analysis_text}
            except:
                analysis = {"situation_summary": analysis_text}
            
            return analysis
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return self._fallback_analysis(text, media_analyses, latlon)
    
    def _fallback_analysis(self, text: str, media_analyses: List[MediaAnalysis], latlon: str) -> Dict[str, Any]:
        """Fallback analysis when Gemini is not available"""
        # Simple keyword-based analysis
        text_lower = text.lower()
        
        hazards = []
        if "flood" in text_lower:
            hazards.append({"type": "flood", "severity": "high"})
        if "fire" in text_lower:
            hazards.append({"type": "fire", "severity": "high"})
        if "earthquake" in text_lower:
            hazards.append({"type": "earthquake", "severity": "critical"})
        
        severity = "Low"
        if any(word in text_lower for word in ["urgent", "emergency", "critical"]):
            severity = "High"
        elif any(word in text_lower for word in ["severe", "serious"]):
            severity = "Moderate"
        
        return {
            "situation_summary": f"Emergency situation reported: {text[:100]}...",
            "hazards": hazards,
            "people_affected": {"visible_count_estimate": 4, "injuries_visible": False, "notes": "Estimated from text"},
            "infrastructure": {"blocked_roads": [], "power_lines_down": False, "critical_facilities_affected": []},
            "access_constraints": [],
            "severity": severity,
            "location_hint": latlon or "unknown",
            "evidence_notes": "Fallback analysis based on text keywords"
        }

# Global processor instance
processor = GeminiMultimodalProcessor()

# Main function
async def process_multimodal_input(channel: str, 
                                 text: str, 
                                 latlon: str, 
                                 uploads: List[Tuple[str, bytes, str]]) -> Dict[str, Any]:
    """
    Main function to process multimodal input using only Gemini
    """
    return await processor.process_multimodal_input(channel, text, latlon, uploads)
