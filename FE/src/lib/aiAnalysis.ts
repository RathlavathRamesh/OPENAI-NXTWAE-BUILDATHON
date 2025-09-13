import { Incident } from './types';

export interface AIAnalysisInput {
  description: string;
  location: string;
  reporterInfo?: string;
  images?: File[];
  audio?: File[];
  weatherData?: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    precipitation: number;
    conditions: string;
  };
  populationDensity?: number;
  timeOfDay?: string;
}

export interface AIAnalysisResult {
  emergencyScore: number; // 0-100 scale
  rescuePersonnelRequired: number;
  estimatedSeverity: string;
  riskFactors: string[];
  weatherImpact: string;
  priorityLevel: number; // 1-5, 1 being highest priority
  recommendedActions: string[];
  estimatedDuration: string;
  resourcesNeeded: string[];
}

// Simulated AI analysis function
export const analyzeEmergency = async (input: AIAnalysisInput): Promise<AIAnalysisResult> => {
  // Simulate AI processing delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  const description = input.description.toLowerCase();
  
  // Emergency type detection
  let emergencyType = 'general';
  let baseScore = 30;
  let basePersonnel = 5;
  let riskFactors: string[] = [];
  
  if (description.includes('fire') || description.includes('explosion') || description.includes('smoke')) {
    emergencyType = 'fire';
    baseScore = 80;
    basePersonnel = 15;
    riskFactors.push('Fire spread risk', 'Smoke inhalation', 'Structural damage');
  } else if (description.includes('flood') || description.includes('water') || description.includes('drowning')) {
    emergencyType = 'flood';
    baseScore = 70;
    basePersonnel = 12;
    riskFactors.push('Swift water', 'Electrical hazards', 'Contamination');
  } else if (description.includes('medical') || description.includes('poisoning') || description.includes('illness')) {
    emergencyType = 'medical';
    baseScore = 60;
    basePersonnel = 8;
    riskFactors.push('Disease spread', 'Multiple casualties', 'Public health risk');
  } else if (description.includes('gas') || description.includes('chemical') || description.includes('hazmat')) {
    emergencyType = 'hazmat';
    baseScore = 85;
    basePersonnel = 20;
    riskFactors.push('Toxic exposure', 'Explosion risk', 'Environmental contamination');
  } else if (description.includes('accident') || description.includes('collision') || description.includes('crash')) {
    emergencyType = 'accident';
    baseScore = 45;
    basePersonnel = 6;
    riskFactors.push('Traffic disruption', 'Secondary accidents', 'Injury severity unknown');
  }

  // Severity modifiers
  const severityWords = ['critical', 'severe', 'major', 'multiple', 'trapped', 'urgent'];
  const severityBonus = severityWords.filter(word => description.includes(word)).length * 10;
  
  // Weather impact analysis
  let weatherImpact = "No significant weather impact on response operations";
  if (input.weatherData) {
    if (input.weatherData.windSpeed > 25) {
      baseScore += 10;
      weatherImpact = "High winds may complicate response operations and spread hazards";
      riskFactors.push('High wind conditions');
    }
    if (input.weatherData.precipitation > 5) {
      baseScore += 5;
      weatherImpact = "Heavy precipitation may slow response and create additional hazards";
      riskFactors.push('Weather-related delays');
    }
  }

  // Time of day modifier
  const hour = new Date().getHours();
  if (hour >= 22 || hour <= 6) {
    baseScore += 5;
    basePersonnel += 2;
    riskFactors.push('Nighttime operations');
  }

  // Population density modifier
  if (input.populationDensity && input.populationDensity > 1000) {
    baseScore += 15;
    basePersonnel += 5;
    riskFactors.push('High population density area');
  }

  const finalScore = Math.min(100, baseScore + severityBonus);
  const finalPersonnel = basePersonnel + Math.floor(finalScore / 20);

  // Priority level (1-5, lower number = higher priority)
  let priorityLevel = 3;
  if (finalScore >= 90) priorityLevel = 1;
  else if (finalScore >= 70) priorityLevel = 2;
  else if (finalScore >= 50) priorityLevel = 3;
  else if (finalScore >= 30) priorityLevel = 4;
  else priorityLevel = 5;

  // Generate severity description
  let estimatedSeverity = "";
  if (finalScore >= 90) estimatedSeverity = "Life-threatening emergency requiring immediate massive response";
  else if (finalScore >= 70) estimatedSeverity = "Major incident requiring significant emergency response";
  else if (finalScore >= 50) estimatedSeverity = "Moderate emergency requiring standard response protocol";
  else if (finalScore >= 30) estimatedSeverity = "Minor incident requiring basic emergency response";
  else estimatedSeverity = "Low-priority incident requiring monitoring";

  // Recommended actions based on emergency type
  const recommendedActions: string[] = [];
  const resourcesNeeded: string[] = [];
  
  switch (emergencyType) {
    case 'fire':
      recommendedActions.push('Deploy fire suppression teams', 'Establish evacuation perimeter', 'Medical standby for smoke inhalation');
      resourcesNeeded.push('Fire trucks', 'Ladder units', 'Ambulances', 'Police for traffic control');
      break;
    case 'flood':
      recommendedActions.push('Deploy swift water rescue teams', 'Evacuate affected areas', 'Establish shelter locations');
      resourcesNeeded.push('Boats', 'Water rescue equipment', 'Pumping equipment', 'Shelters');
      break;
    case 'medical':
      recommendedActions.push('Deploy multiple ambulances', 'Set up triage area', 'Contact hospitals for capacity');
      resourcesNeeded.push('Ambulances', 'Medical personnel', 'Medical supplies', 'Transport vehicles');
      break;
    case 'hazmat':
      recommendedActions.push('Establish containment zone', 'Deploy hazmat teams', 'Begin evacuation procedures');
      resourcesNeeded.push('Hazmat units', 'Decontamination equipment', 'Protective gear', 'Evacuation vehicles');
      break;
    default:
      recommendedActions.push('Assess situation', 'Deploy appropriate response teams', 'Secure area');
      resourcesNeeded.push('First responders', 'Assessment team', 'Basic emergency equipment');
  }

  // Estimated duration
  let estimatedDuration = "2-4 hours";
  if (finalScore >= 80) estimatedDuration = "4-8 hours";
  if (finalScore >= 90) estimatedDuration = "6-12 hours or more";

  return {
    emergencyScore: finalScore,
    rescuePersonnelRequired: finalPersonnel,
    estimatedSeverity,
    riskFactors,
    weatherImpact,
    priorityLevel,
    recommendedActions,
    estimatedDuration,
    resourcesNeeded
  };
};