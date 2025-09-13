import { Incident, ResponseTeam, Message } from './types';

export const dummyIncidents: Incident[] = [
  {
    id: "INC001",
    type: "Building Fire",
    severity: "critical",
    location: "Downtown Business District, 5th Avenue",
    coordinates: { lat: 40.7589, lng: -73.9851 },
    description: "Multi-story office building engulfed in flames. Multiple people trapped on upper floors. Heavy smoke visible from several blocks away.",
    reportedBy: "John Martinez - Building Security",
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    status: "active",
    aiAnalysis: {
      emergencyScore: 95,
      rescuePersonnelRequired: 25,
      estimatedSeverity: "Life-threatening emergency requiring immediate response",
      riskFactors: ["High occupancy building", "Structural collapse risk", "Toxic smoke", "Limited evacuation routes"],
      weatherImpact: "Strong winds may spread fire to adjacent buildings",
      priorityLevel: 1
    },
    images: ["/api/placeholder/400/300", "/api/placeholder/400/300"]
  },
  {
    id: "INC002",
    type: "Flash Flood",
    severity: "high",
    location: "Riverside Park & Surrounding Neighborhoods",
    coordinates: { lat: 40.7829, lng: -73.9654 },
    description: "Rapid water level rise due to heavy rainfall. Several vehicles stranded, people trapped in lower levels of buildings.",
    reportedBy: "Emergency Weather Service",
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    status: "responding",
    aiAnalysis: {
      emergencyScore: 78,
      rescuePersonnelRequired: 15,
      estimatedSeverity: "Major flooding event with significant rescue needs",
      riskFactors: ["Electrical hazards", "Swift water", "Contaminated water", "Infrastructure damage"],
      weatherImpact: "Continued heavy rainfall expected for next 2 hours",
      priorityLevel: 2
    }
  },
  {
    id: "INC003",
    type: "Traffic Accident",
    severity: "medium",
    location: "Highway 101, Exit 42",
    coordinates: { lat: 40.7505, lng: -73.9934 },
    description: "Multi-vehicle collision blocking two lanes. Minor injuries reported, emergency services on scene.",
    reportedBy: "Highway Patrol Unit 7",
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    status: "responding",
    aiAnalysis: {
      emergencyScore: 45,
      rescuePersonnelRequired: 8,
      estimatedSeverity: "Standard traffic incident with manageable response needs",
      riskFactors: ["Traffic congestion", "Secondary collisions", "Fuel spill risk"],
      weatherImpact: "Clear conditions, no weather impact",
      priorityLevel: 3
    }
  },
  {
    id: "INC004",
    type: "Medical Emergency",
    severity: "high",
    location: "Central Mall, Food Court Area",
    coordinates: { lat: 40.7614, lng: -73.9776 },
    description: "Mass food poisoning incident. 12 people showing severe symptoms, requiring immediate medical attention.",
    reportedBy: "Mall Security - Lisa Chen",
    timestamp: new Date(Date.now() - 35 * 60 * 1000),
    status: "active",
    aiAnalysis: {
      emergencyScore: 72,
      rescuePersonnelRequired: 12,
      estimatedSeverity: "Public health emergency requiring multiple ambulances",
      riskFactors: ["Potential contamination source", "Public panic", "Additional victims possible"],
      weatherImpact: "No weather impact on response",
      priorityLevel: 2
    }
  },
  {
    id: "INC005",
    type: "Gas Leak",
    severity: "high",
    location: "Residential Area - Oak Street Block 400",
    coordinates: { lat: 40.7390, lng: -73.9889 },
    description: "Major natural gas leak detected in residential neighborhood. Evacuation of 3-block radius initiated.",
    reportedBy: "Utility Company Inspector",
    timestamp: new Date(Date.now() - 55 * 60 * 1000),
    status: "responding",
    aiAnalysis: {
      emergencyScore: 84,
      rescuePersonnelRequired: 18,
      estimatedSeverity: "Hazardous material incident with explosion risk",
      riskFactors: ["Explosion hazard", "Toxic exposure", "Large evacuation zone", "Utility infrastructure damage"],
      weatherImpact: "Light winds help disperse gas, reducing concentration",
      priorityLevel: 1
    }
  }
];

export const dummyResponseTeams: ResponseTeam[] = [
  {
    id: "TEAM001",
    name: "Fire Department Station 12",
    type: "fire",
    status: "deployed",
    location: { lat: 40.7580, lng: -73.9855 },
    contact: "+1-555-FIRE-012",
    specialties: ["High-rise rescue", "Hazmat response", "Technical rescue"]
  },
  {
    id: "TEAM002",
    name: "Emergency Medical Unit Alpha",
    type: "medical",
    status: "available",
    location: { lat: 40.7614, lng: -73.9776 },
    contact: "+1-555-MED-ALPHA",
    specialties: ["Mass casualty", "Trauma response", "Pediatric care"]
  },
  {
    id: "TEAM003",
    name: "Police Tactical Unit 5",
    type: "police",
    status: "available",
    location: { lat: 40.7505, lng: -73.9934 },
    contact: "+1-555-POLICE-05",
    specialties: ["Traffic control", "Crowd management", "Investigation"]
  },
  {
    id: "TEAM004",
    name: "Swift Water Rescue Team",
    type: "rescue",
    status: "deployed",
    location: { lat: 40.7829, lng: -73.9654 },
    contact: "+1-555-WATER-RES",
    specialties: ["Water rescue", "Boat operations", "Dive operations"]
  },
  {
    id: "TEAM005",
    name: "Hazmat Response Unit",
    type: "rescue",
    status: "deployed",
    location: { lat: 40.7390, lng: -73.9889 },
    contact: "+1-555-HAZMAT-01",
    specialties: ["Chemical response", "Gas leaks", "Decontamination"]
  }
];

export const dummyMessages: Message[] = [
  {
    id: "MSG001",
    from: "Command Center",
    to: "All Units",
    content: "CRITICAL: Building fire at 5th Avenue requires immediate response. All available fire units respond.",
    type: "text",
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    isEmergency: true
  },
  {
    id: "MSG002",
    from: "Fire Chief",
    to: "Command Center",
    content: "ETA 3 minutes to building fire. Requesting ladder truck and additional medical support.",
    type: "text",
    timestamp: new Date(Date.now() - 8 * 60 * 1000)
  },
  {
    id: "MSG003",
    from: "Citizen Reporter",
    to: "Emergency Services",
    content: "Water level rising rapidly in basement parking garage. Several cars trapped, people need help getting out.",
    type: "text",
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    isEmergency: true
  },
  {
    id: "MSG004",
    from: "Medical Team Alpha",
    to: "Hospital Central",
    content: "Transporting 3 patients from food poisoning incident. Severe dehydration, need prep for IV fluids.",
    type: "text",
    timestamp: new Date(Date.now() - 20 * 60 * 1000)
  },
  {
    id: "MSG005",
    from: "Police Unit 5",
    to: "Traffic Control",
    content: "Highway 101 incident cleared. Reopening lanes 2 and 3. One vehicle being towed.",
    type: "text",
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  }
];