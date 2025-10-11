# Preprocess Agent (Layer 1): Input Processing + Situation Analysis
"""
Preprocess Agent: Handles multimodal input processing and situation analysis
- Processes text, images, audio, video inputs
- Uses real AI models for analysis
- Returns incident summary (what happened, no judgment)
"""

import os
import sys
import asyncio
from typing import List, Tuple, Dict, Any

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent1_multimodal_processor_gemini import process_multimodal_input

class PreprocessAgent:
    """
    Layer 1: Preprocess Agent
    Handles input preprocessing and situation analysis
    """
    
    def __init__(self):
        self.agent_name = "PreprocessAgent"
        self.layer = 1
    
    async def process_incident(self, 
                             channel: str, 
                             text: str, 
                             latlon: str, 
                             uploads: List[Tuple[str, bytes, str]]) -> Dict[str, Any]:
        """
        Process multimodal input and analyze situation
        
        Args:
            channel: Input channel (app, whatsapp, sms)
            text: Text message content
            latlon: Location as "lat,lon" string
            uploads: List of (filename, bytes, mime_type) tuples
            
        Returns:
            Incident summary with situation analysis
        """
        try:
            print(f"🔍 {self.agent_name}: Processing multimodal input...")
            # Use the existing multimodal processor
            result = await process_multimodal_input(channel, text, latlon, uploads)
            # Extract and structure the incident summary
            incident_summary = {
                "agent": self.agent_name,
                "layer": self.layer,
                "timestamp": result.get("timestamp"),
                "incident_id": result.get("incident_id"),
                "status": result.get("status"),
                
                # Situation analysis (what happened)
                "situation_analysis": {
                    "situation_summary": result.get("analysis", {}).get("situation_summary", ""),
                    "hazards": result.get("analysis", {}).get("hazards", []),
                    "people_affected": result.get("analysis", {}).get("people_affected", {}),
                    "infrastructure": result.get("analysis", {}).get("infrastructure", {}),
                    "access_constraints": result.get("analysis", {}).get("access_constraints", []),
                    "severity": result.get("analysis", {}).get("severity", "Unknown"),
                    "location_hint": result.get("analysis", {}).get("location_hint", ""),
                    "evidence_notes": result.get("analysis", {}).get("evidence_notes", "")
                },
                
                # Media processing details
                "media_processed": result.get("media_processed", {}),
                "confidence": result.get("confidence", {}),
                
                # Preprocessed input
                "preprocessed_input": result.get("preprocessed_input", {}),
                
                # Processing metadata
                "processing_metadata": {
                    "total_media_items": len(uploads),
                    "text_length": len(text),
                    "has_location": bool(latlon),
                    "channel": channel
                }
            }
            
            print(f"✅ {self.agent_name}: Situation analysis complete")
            return incident_summary
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Error processing incident - {e}")
            return {
                "agent": self.agent_name,
                "layer": self.layer,
                "status": "failed",
                "error": str(e),
                "situation_analysis": {
                    "situation_summary": f"Processing failed: {str(e)}",
                    "hazards": [],
                    "people_affected": {"visible_count_estimate": 0, "injuries_visible": False, "notes": "Processing failed"},
                    "infrastructure": {"blocked_roads": [], "power_lines_down": False, "critical_facilities_affected": []},
                    "access_constraints": [],
                    "severity": "Unknown",
                    "location_hint": latlon or "unknown",
                    "evidence_notes": f"Error: {str(e)}"
                },
                "preprocessed_input": {},
                "processing_metadata": {
                    "total_media_items": len(uploads),
                    "text_length": len(text),
                    "has_location": bool(latlon),
                    "channel": channel
                }
            }

# Convenience function
async def run_preprocess_agent(channel: str, 
                             text: str, 
                             latlon: str, 
                             uploads: List[Tuple[str, bytes, str]]) -> Dict[str, Any]:
    """
    Convenience function to run the preprocess agent
    """
    agent = PreprocessAgent()
    return await agent.process_incident(channel, text, latlon, uploads)
