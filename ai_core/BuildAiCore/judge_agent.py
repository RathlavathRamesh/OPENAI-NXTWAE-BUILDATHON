# Judge Agent (Layer 3): Incident Verification and Judgment
"""
Judge Agent: Compares incident analysis with real-world data and makes final judgment
- Verifies incident authenticity
- Detects hallucinations and inconsistencies
- Assigns final severity and priority
- Provides detailed verdict with reasoning
"""

import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from incident_judge import judge_incident_with_gemini

class JudgeAgent:
    """
    Layer 3: Judge Agent
    Verifies incident authenticity and makes final judgment
    """
    
    def __init__(self):
        self.agent_name = "JudgeAgent"
        self.layer = 3
    
    def judge_incident(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Judge the incident based on analysis and real-world data
        
        Args:
            analysis_result: Combined analysis from Analysis Agent
            
        Returns:
            Final verdict with authenticity, severity, and priority
        """
        try:
            print(f"⚖️ {self.agent_name}: Judging incident authenticity and severity...")
            
            # Extract data for judgment
            incident_summary = analysis_result.get("incident_summary", {})
            realworld_context = analysis_result.get("realworld_context", {})
            geospatial_analysis = analysis_result.get("geospatial_analysis", {})
            
            # Prepare incident data for judge
            incident_for_judge = self._prepare_incident_for_judge(incident_summary)
            
            # Get judge verdict using existing judge function
            judge_verdict = judge_incident_with_gemini(incident_for_judge, realworld_context)
            
            # Perform additional analysis
            additional_analysis = self._perform_additional_analysis(incident_summary, realworld_context, geospatial_analysis)
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(judge_verdict, additional_analysis)
            
            # Create comprehensive judgment
            judgment_result = {
                "agent": self.agent_name,
                "layer": self.layer,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": analysis_result.get("incident_id"),
                "status": "completed",
                
                # Judge verdict
                "judge_verdict": judge_verdict,
                
                # Additional analysis
                "additional_analysis": additional_analysis,
                
                # Priority and severity
                "priority_score_0_10": priority_score,
                "final_severity": judge_verdict.get("final_severity", "Unknown"),
                "incident_authentic": judge_verdict.get("real_incident", False),
                
                # Detailed reasoning
                "reasoning": {
                    "verdict_explanation": judge_verdict.get("explanation", ""),
                    "criteria_scores": judge_verdict.get("criteria", {}),
                    "hallucination_detection": additional_analysis.get("hallucination_detection", {}),
                    "consistency_analysis": additional_analysis.get("consistency_analysis", {}),
                    "confidence_assessment": additional_analysis.get("confidence_assessment", {})
                },
                
                # Recommendations
                "recommendations": self._generate_recommendations(judge_verdict, additional_analysis),
                
                # Processing metadata
                "processing_metadata": {
                    "judge_confidence": judge_verdict.get("verdict_score_0_10", 0) / 10.0,
                    "data_quality": analysis_result.get("combined_analysis", {}).get("data_quality", "Unknown"),
                    "verification_complete": True
                }
            }
            
            print(f"✅ {self.agent_name}: Judgment complete - Priority: {priority_score}/10")
            return judgment_result
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Error judging incident - {e}")
            return {
                "agent": self.agent_name,
                "layer": self.layer,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "incident_id": analysis_result.get("incident_id"),
                "status": "failed",
                "error": str(e),
                "judge_verdict": {
                    "real_incident": False,
                    "final_severity": "Unknown",
                    "verdict_score_0_10": 0,
                    "explanation": f"Judgment failed: {str(e)}"
                },
                "priority_score_0_10": 0,
                "incident_authentic": False,
                "reasoning": {"error": str(e)},
                "recommendations": [],
                "processing_metadata": {"error": str(e)}
            }
    
    def _prepare_incident_for_judge(self, incident_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare incident data for the judge function"""
        try:
            situation = incident_summary.get("situation_analysis", {})
            
            return {
                "hazard": situation.get("hazards", [{}])[0].get("type", "unknown") if situation.get("hazards") else "unknown",
                "severity": situation.get("severity", "unknown").lower(),
                "people_estimate": situation.get("people_affected", {}).get("visible_count_estimate", 0),
                "confidence": 0.8,  # Default confidence
                "rationale": situation.get("evidence_notes", "Preprocess Agent analysis"),
                "situation_summary": situation.get("situation_summary", ""),
                "infrastructure": situation.get("infrastructure", {}),
                "access_constraints": situation.get("access_constraints", [])
            }
            
        except Exception as e:
            return {
                "hazard": "unknown",
                "severity": "unknown",
                "people_estimate": 0,
                "confidence": 0.0,
                "rationale": f"Error preparing data: {str(e)}",
                "situation_summary": "",
                "infrastructure": {},
                "access_constraints": []
            }
    
    def _perform_additional_analysis(self, 
                                   incident_summary: Dict[str, Any], 
                                   realworld_context: Dict[str, Any],
                                   geospatial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform additional analysis beyond basic judge verdict"""
        try:
            # Hallucination detection
            hallucination_detection = self._detect_hallucinations(incident_summary, realworld_context)
            
            # Consistency analysis
            consistency_analysis = self._analyze_consistency(incident_summary, realworld_context, geospatial_analysis)
            
            # Confidence assessment
            confidence_assessment = self._assess_confidence(incident_summary, realworld_context, geospatial_analysis)
            
            return {
                "hallucination_detection": hallucination_detection,
                "consistency_analysis": consistency_analysis,
                "confidence_assessment": confidence_assessment
            }
            
        except Exception as e:
            return {
                "hallucination_detection": {"error": str(e)},
                "consistency_analysis": {"error": str(e)},
                "confidence_assessment": {"error": str(e)}
            }
    
    def _detect_hallucinations(self, incident_summary: Dict[str, Any], realworld_context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential hallucinations in the incident report"""
        try:
            situation = incident_summary.get("situation_analysis", {})
            weather = realworld_context.get("weather", {})
            
            hallucination_indicators = []
            hallucination_score = 0.0
            
            # Check for impossible claims
            people_count = situation.get("people_affected", {}).get("visible_count_estimate", 0)
            if people_count > 1000:  # Unrealistic people count
                hallucination_indicators.append("Unrealistic people count")
                hallucination_score += 0.3
            
            # Check for contradictory information
            hazards = [h.get("type", "").lower() for h in situation.get("hazards", [])]
            if "flood" in hazards and "fire" in hazards:
                hallucination_indicators.append("Contradictory hazards (flood + fire)")
                hallucination_score += 0.2
            
            # Check for location inconsistencies
            location_hint = situation.get("location_hint", "")
            if location_hint and "unknown" in location_hint.lower():
                hallucination_indicators.append("Vague location information")
                hallucination_score += 0.1
            
            # Check for weather inconsistencies
            weather_desc = weather.get("description", "").lower()
            if "flood" in hazards and "sunny" in weather_desc and "rain" not in weather_desc:
                hallucination_indicators.append("Weather inconsistent with flood claim")
                hallucination_score += 0.2
            
            return {
                "hallucination_score": min(1.0, hallucination_score),
                "indicators": hallucination_indicators,
                "likely_hallucination": hallucination_score > 0.5,
                "confidence": 0.8 if hallucination_indicators else 0.2
            }
            
        except Exception as e:
            return {
                "hallucination_score": 0.0,
                "indicators": [f"Analysis error: {str(e)}"],
                "likely_hallucination": False,
                "confidence": 0.0
            }
    
    def _analyze_consistency(self, 
                           incident_summary: Dict[str, Any], 
                           realworld_context: Dict[str, Any],
                           geospatial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency between incident and real-world data"""
        try:
            consistency_score = 0.0
            consistency_issues = []
            
            # Location consistency
            if geospatial_analysis.get("location_verified", False):
                consistency_score += 0.3
            else:
                consistency_issues.append("Location not verified")
            
            # Weather consistency
            weather_consistency = geospatial_analysis.get("weather_consistency", "Unknown")
            if weather_consistency == "Consistent":
                consistency_score += 0.3
            elif weather_consistency == "Inconsistent":
                consistency_issues.append("Weather conditions inconsistent")
            
            # Data quality consistency
            data_quality = realworld_context.get("data_quality", "Unknown")
            if data_quality == "good":
                consistency_score += 0.2
            elif data_quality == "poor":
                consistency_issues.append("Poor real-world data quality")
            
            # Overall context consistency
            context_consistency = geospatial_analysis.get("context_consistency", "Unknown")
            if context_consistency == "Good":
                consistency_score += 0.2
            else:
                consistency_issues.append(f"Context issue: {context_consistency}")
            
            return {
                "consistency_score": min(1.0, consistency_score),
                "issues": consistency_issues,
                "overall_consistency": "High" if consistency_score > 0.7 else "Medium" if consistency_score > 0.4 else "Low",
                "confidence": 0.8 if consistency_issues else 0.6
            }
            
        except Exception as e:
            return {
                "consistency_score": 0.0,
                "issues": [f"Analysis error: {str(e)}"],
                "overall_consistency": "Unknown",
                "confidence": 0.0
            }
    
    def _assess_confidence(self, 
                         incident_summary: Dict[str, Any], 
                         realworld_context: Dict[str, Any],
                         geospatial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall confidence in the judgment"""
        try:
            confidence_factors = []
            total_confidence = 0.0
            
            # Incident data quality
            situation = incident_summary.get("situation_analysis", {})
            if situation.get("situation_summary"):
                confidence_factors.append("Clear situation description")
                total_confidence += 0.2
            
            if situation.get("hazards"):
                confidence_factors.append("Specific hazards identified")
                total_confidence += 0.2
            
            if situation.get("people_affected", {}).get("visible_count_estimate", 0) > 0:
                confidence_factors.append("People count estimated")
                total_confidence += 0.1
            
            # Real-world data quality
            if realworld_context.get("weather"):
                confidence_factors.append("Weather data available")
                total_confidence += 0.2
            
            # Geospatial analysis quality
            if geospatial_analysis.get("location_verified", False):
                confidence_factors.append("Location verified")
                total_confidence += 0.2
            
            if geospatial_analysis.get("geospatial_confidence", 0) > 0.7:
                confidence_factors.append("High geospatial confidence")
                total_confidence += 0.1
            
            return {
                "confidence_score": min(1.0, total_confidence),
                "confidence_factors": confidence_factors,
                "confidence_level": "High" if total_confidence > 0.7 else "Medium" if total_confidence > 0.4 else "Low",
                "recommendations": self._get_confidence_recommendations(total_confidence)
            }
            
        except Exception as e:
            return {
                "confidence_score": 0.0,
                "confidence_factors": [f"Analysis error: {str(e)}"],
                "confidence_level": "Unknown",
                "recommendations": ["Unable to assess confidence"]
            }
    
    def _get_confidence_recommendations(self, confidence_score: float) -> list:
        """Get recommendations based on confidence score"""
        if confidence_score > 0.8:
            return ["High confidence - proceed with standard response"]
        elif confidence_score > 0.6:
            return ["Medium confidence - consider additional verification"]
        elif confidence_score > 0.4:
            return ["Low confidence - recommend manual review"]
        else:
            return ["Very low confidence - manual verification required"]
    
    def _calculate_priority_score(self, judge_verdict: Dict[str, Any], additional_analysis: Dict[str, Any]) -> int:
        """Calculate final priority score (0-10)"""
        try:
            if not judge_verdict.get("real_incident", False):
                return 0
            
            # Base priority from severity
            severity = judge_verdict.get("final_severity", "Unknown").lower()
            base_priority = {
                "critical": 10,
                "high": 8,
                "moderate": 5,
                "low": 3,
                "unknown": 1
            }.get(severity, 1)
            
            # Adjust based on judge score
            judge_score = judge_verdict.get("verdict_score_0_10", 5)
            if judge_score >= 8:
                base_priority += 2
            elif judge_score >= 5:
                base_priority += 1
            
            # Adjust based on hallucination detection
            hallucination = additional_analysis.get("hallucination_detection", {})
            if hallucination.get("likely_hallucination", False):
                base_priority = max(0, base_priority - 3)
            
            # Adjust based on consistency
            consistency = additional_analysis.get("consistency_analysis", {})
            if consistency.get("overall_consistency") == "Low":
                base_priority = max(0, base_priority - 2)
            
            return min(10, max(0, base_priority))
            
        except Exception:
            return 5  # Default medium priority
    
    def _generate_recommendations(self, judge_verdict: Dict[str, Any], additional_analysis: Dict[str, Any]) -> list:
        """Generate actionable recommendations based on judgment"""
        try:
            recommendations = []
            
            # Basic recommendations based on verdict
            if judge_verdict.get("real_incident", False):
                severity = judge_verdict.get("final_severity", "Unknown").lower()
                if severity == "critical":
                    recommendations.append("Immediate emergency response required")
                    recommendations.append("Alert all emergency services")
                elif severity == "high":
                    recommendations.append("High priority response needed")
                    recommendations.append("Notify emergency services")
                elif severity == "moderate":
                    recommendations.append("Standard emergency response")
                else:
                    recommendations.append("Monitor situation closely")
            else:
                recommendations.append("Incident not verified - investigate further")
                recommendations.append("Consider false alarm protocols")
            
            # Additional recommendations based on analysis
            hallucination = additional_analysis.get("hallucination_detection", {})
            if hallucination.get("likely_hallucination", False):
                recommendations.append("Potential false report - verify with additional sources")
            
            consistency = additional_analysis.get("consistency_analysis", {})
            if consistency.get("overall_consistency") == "Low":
                recommendations.append("Data inconsistencies detected - manual review recommended")
            
            confidence = additional_analysis.get("confidence_assessment", {})
            if confidence.get("confidence_level") == "Low":
                recommendations.append("Low confidence in assessment - gather more information")
            
            return recommendations
            
        except Exception:
            return ["Unable to generate recommendations"]

# Convenience function
def run_judge_agent(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the judge agent
    """
    agent = JudgeAgent()
    return agent.judge_incident(analysis_result)
