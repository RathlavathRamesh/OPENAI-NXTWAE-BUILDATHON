# Analysis Agent (Layer 2): Real-world Data + Analysis
"""
Analysis Agent: Fetches real-world geospatial data and combines with incident analysis
- Fetches weather, alerts, and other real-world data
- Combines incident summary with external context
- Returns comprehensive analysis for judge
"""

import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_core.weather_reports import get_weather_by_coords

class AnalysisAgent:
    """
    Layer 2: Analysis Agent
    Fetches real-world data and combines with incident analysis
    """
    
    def __init__(self):
        self.agent_name = "AnalysisAgent"
        self.layer = 2
    
    def analyze_incident_with_context(self, 
                                    incident_summary: Dict[str, Any],
                                    lat: float = None,
                                    lon: float = None) -> Dict[str, Any]:
        """
        Analyze incident with real-world context
        
        Args:
            incident_summary: Incident data from Preprocess Agent
            lat: Latitude for real-world data
            lon: Longitude for real-world data
            
        Returns:
            Combined incident analysis with real-world context
        """
        try:
            print(f"🌍 {self.agent_name}: Fetching real-world data and analyzing...")
            
            # Extract location from incident if not provided
            if lat is None or lon is None:
                location_hint = incident_summary.get("situation_analysis", {}).get("location_hint", "")
                if location_hint and "," in location_hint:
                    try:
                        lat_str, lon_str = location_hint.split(",", 1)
                        lat, lon = float(lat_str.strip()), float(lon_str.strip())
                    except ValueError:
                        lat, lon = 17.3850, 78.4867  # Default to Hyderabad
                else:
                    lat, lon = 17.3850, 78.4867  # Default to Hyderabad
            
            # Fetch real-world data
            realworld_context = self._fetch_realworld_data(lat, lon)
            
            # Perform geospatial analysis
            geospatial_analysis = self._analyze_geospatial_context(incident_summary, realworld_context, lat, lon)
            
            # Create comprehensive analysis
            analysis_result = {
                "agent": self.agent_name,
                "layer": self.layer,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": incident_summary.get("incident_id"),
                "status": "completed",
                
                # Original incident data
                "incident_summary": incident_summary,
                
                # Real-world context
                "realworld_context": realworld_context,
                
                # Location data
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{lat},{lon}",
                    "source": "user_input" if lat != 17.3850 or lon != 78.4867 else "default"
                },
                
                # Geospatial analysis
                "geospatial_analysis": geospatial_analysis,
                
                # Combined analysis
                "combined_analysis": {
                    "incident_severity": incident_summary.get("situation_analysis", {}).get("severity", "Unknown"),
                    "weather_conditions": realworld_context.get("weather", {}).get("description", "Unknown"),
                    "location_verified": geospatial_analysis.get("location_verified", False),
                    "context_consistency": geospatial_analysis.get("context_consistency", "Unknown"),
                    "data_quality": self._assess_data_quality(incident_summary, realworld_context)
                },
                
                # Processing metadata
                "processing_metadata": {
                    "realworld_data_available": bool(realworld_context.get("weather")),
                    "location_accuracy": geospatial_analysis.get("location_accuracy", "Unknown"),
                    "analysis_confidence": self._calculate_analysis_confidence(incident_summary, realworld_context)
                }
            }
            
            print(f"✅ {self.agent_name}: Analysis complete")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Error analyzing incident - {e}")
            return {
                "agent": self.agent_name,
                "layer": self.layer,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": incident_summary.get("incident_id"),
                "status": "failed",
                "error": str(e),
                "incident_summary": incident_summary,
                "realworld_context": {"error": str(e)},
                "location": {"latitude": lat, "longitude": lon, "formatted": f"{lat},{lon}"},
                "geospatial_analysis": {"error": str(e)},
                "combined_analysis": {"error": str(e)},
                "processing_metadata": {"error": str(e)}
            }
    
    def _fetch_realworld_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch real-world data for the location"""
        try:
            # Get weather data
            weather_data = get_weather_by_coords(lat, lon)
            
            return {
                "weather": weather_data,
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "data_sources": ["weather_api"],
                "data_quality": "good" if weather_data.get("weather") else "limited"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "weather": {"error": "Weather data unavailable"},
                "location": {"latitude": lat, "longitude": lon},
                "data_sources": [],
                "data_quality": "poor"
            }
    
    def _analyze_geospatial_context(self, 
                                  incident_summary: Dict[str, Any], 
                                  realworld_context: Dict[str, Any],
                                  lat: float, 
                                  lon: float) -> Dict[str, Any]:
        """Analyze geospatial context and consistency"""
        try:
            situation = incident_summary.get("situation_analysis", {})
            weather = realworld_context.get("weather", {})
            
            # Check location consistency
            location_hint = situation.get("location_hint", "")
            location_verified = False
            if location_hint and "," in location_hint:
                try:
                    hint_lat, hint_lon = map(float, location_hint.split(","))
                    # Check if locations are within reasonable distance (e.g., 10km)
                    distance = self._calculate_distance(lat, lon, hint_lat, hint_lon)
                    location_verified = distance < 10.0  # 10km threshold
                except:
                    location_verified = False
            
            # Check weather consistency with incident type
            incident_hazards = [h.get("type", "").lower() for h in situation.get("hazards", [])]
            weather_consistency = self._check_weather_consistency(incident_hazards, weather)
            
            # Assess context consistency
            context_consistency = "Good"
            if not location_verified:
                context_consistency = "Location mismatch"
            elif weather_consistency == "Inconsistent":
                context_consistency = "Weather inconsistent"
            elif realworld_context.get("data_quality") == "poor":
                context_consistency = "Limited data"
            
            return {
                "location_verified": location_verified,
                "location_accuracy": "High" if location_verified else "Low",
                "weather_consistency": weather_consistency,
                "context_consistency": context_consistency,
                "geospatial_confidence": 0.8 if location_verified and weather_consistency == "Consistent" else 0.4
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "location_verified": False,
                "location_accuracy": "Unknown",
                "weather_consistency": "Unknown",
                "context_consistency": "Error",
                "geospatial_confidence": 0.0
            }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        import math
        
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def _check_weather_consistency(self, incident_hazards: list, weather: Dict[str, Any]) -> str:
        """Check if weather conditions are consistent with incident hazards"""
        try:
            weather_desc = weather.get("description", "").lower()
            
            # Define consistency rules
            consistency_rules = {
                "flood": ["rain", "heavy rain", "storm", "precipitation"],
                "fire": ["dry", "hot", "windy", "low humidity"],
                "storm": ["wind", "storm", "severe weather", "tornado", "hurricane"],
                "earthquake": []  # Weather doesn't predict earthquakes
            }
            
            for hazard in incident_hazards:
                if hazard in consistency_rules:
                    expected_weather = consistency_rules[hazard]
                    if expected_weather:
                        if any(term in weather_desc for term in expected_weather):
                            return "Consistent"
                        else:
                            return "Inconsistent"
            
            return "Neutral"  # No specific weather expectations
            
        except Exception:
            return "Unknown"
    
    def _assess_data_quality(self, incident_summary: Dict[str, Any], realworld_context: Dict[str, Any]) -> str:
        """Assess overall data quality"""
        try:
            quality_score = 0
            
            # Incident data quality
            situation = incident_summary.get("situation_analysis", {})
            if situation.get("situation_summary"):
                quality_score += 1
            if situation.get("hazards"):
                quality_score += 1
            if situation.get("people_affected", {}).get("visible_count_estimate", 0) > 0:
                quality_score += 1
            
            # Real-world data quality
            if realworld_context.get("weather"):
                quality_score += 1
            if realworld_context.get("data_quality") == "good":
                quality_score += 1
            
            if quality_score >= 4:
                return "High"
            elif quality_score >= 2:
                return "Medium"
            else:
                return "Low"
                
        except Exception:
            return "Unknown"
    
    def _calculate_analysis_confidence(self, incident_summary: Dict[str, Any], realworld_context: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis"""
        try:
            confidence = 0.5  # Base confidence
            
            # Add confidence based on data quality
            data_quality = self._assess_data_quality(incident_summary, realworld_context)
            if data_quality == "High":
                confidence += 0.3
            elif data_quality == "Medium":
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception:
            return 0.5

# Convenience function
def run_analysis_agent(incident_summary: Dict[str, Any], 
                      lat: float = None, 
                      lon: float = None) -> Dict[str, Any]:
    """
    Convenience function to run the analysis agent
    """
    agent = AnalysisAgent()
    return agent.analyze_incident_with_context(incident_summary, lat, lon)
