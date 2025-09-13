export interface Incident {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  location: string;
  coordinates: { lat: number; lng: number };
  description: string;
  reportedBy: string;
  timestamp: Date;
  status: 'active' | 'responding' | 'resolved';
  aiAnalysis: {
    emergencyScore: number;
    rescuePersonnelRequired: number;
    estimatedSeverity: string;
    riskFactors: string[];
    weatherImpact: string;
    priorityLevel: number;
  };
  images?: string[];
  audio?: string[];
  video?: string[];
}

export interface ResponseTeam {
  id: string;
  name: string;
  type: 'medical' | 'fire' | 'police' | 'rescue';
  status: 'available' | 'deployed' | 'busy';
  location: { lat: number; lng: number };
  contact: string;
  specialties: string[];
}

export interface Message {
  id: string;
  from: string;
  to: string;
  content: string;
  type: 'text' | 'audio' | 'video' | 'image' | 'location';
  timestamp: Date;
  isEmergency?: boolean;
}

export interface User {
  id: string;
  name: string;
  role: 'authority' | 'rescuer' | 'citizen';
  contact: string;
  location?: { lat: number; lng: number };
}