import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Map, 
  MapPin, 
  Users, 
  Truck, 
  Shield, 
  Stethoscope, 
  Flame,
  Navigation,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCcw
} from 'lucide-react';
import { dummyIncidents, dummyResponseTeams } from '@/lib/dummyData';

export const MapPage = () => {
  const [selectedLayer, setSelectedLayer] = useState<string>('all');
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null);
  const [mapView, setMapView] = useState<'satellite' | 'terrain' | 'roadmap'>('roadmap');

  const getIncidentIcon = (type: string) => {
    if (type.toLowerCase().includes('fire')) return <Flame className="h-4 w-4 text-primary" />;
    if (type.toLowerCase().includes('medical')) return <Stethoscope className="h-4 w-4 text-secondary" />;
    if (type.toLowerCase().includes('police')) return <Shield className="h-4 w-4 text-blue-500" />;
    return <MapPin className="h-4 w-4 text-warning" />;
  };

  const getTeamIcon = (type: string) => {
    switch (type) {
      case 'fire': return <Flame className="h-4 w-4 text-red-500" />;
      case 'medical': return <Stethoscope className="h-4 w-4 text-blue-500" />;
      case 'police': return <Shield className="h-4 w-4 text-blue-600" />;
      case 'rescue': return <Users className="h-4 w-4 text-green-500" />;
      default: return <Truck className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-primary border-primary';
      case 'high': return 'bg-warning border-warning';
      case 'medium': return 'bg-secondary border-secondary';
      case 'low': return 'bg-success border-success';
      default: return 'bg-muted border-muted';
    }
  };

  const getTeamStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-success border-success';
      case 'deployed': return 'bg-warning border-warning';
      case 'busy': return 'bg-primary border-primary';
      default: return 'bg-muted border-muted';
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Interactive Emergency Map</h1>
          <p className="text-muted-foreground">Real-time visualization of incidents and response teams</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Navigation className="h-4 w-4" />
            Live Tracking
          </Button>
          <Button variant="emergency" className="gap-2">
            <MapPin className="h-4 w-4" />
            Add Incident
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[80vh]">
        {/* Map Controls */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Map Layers
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Select value={selectedLayer} onValueChange={setSelectedLayer}>
                <SelectTrigger>
                  <SelectValue placeholder="Select layer" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Elements</SelectItem>
                  <SelectItem value="incidents">Incidents Only</SelectItem>
                  <SelectItem value="teams">Response Teams</SelectItem>
                  <SelectItem value="hazards">Hazard Zones</SelectItem>
                  <SelectItem value="evacuation">Evacuation Routes</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={mapView} onValueChange={(value: 'satellite' | 'terrain' | 'roadmap') => setMapView(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Map view" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="roadmap">Roadmap</SelectItem>
                  <SelectItem value="satellite">Satellite</SelectItem>
                  <SelectItem value="terrain">Terrain</SelectItem>
                </SelectContent>
              </Select>

              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full gap-2">
                  <ZoomIn className="h-3 w-3" />
                  Zoom In
                </Button>
                <Button variant="outline" size="sm" className="w-full gap-2">
                  <ZoomOut className="h-3 w-3" />
                  Zoom Out
                </Button>
                <Button variant="outline" size="sm" className="w-full gap-2">
                  <RotateCcw className="h-3 w-3" />
                  Reset View
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader>
              <CardTitle>Legend</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h4 className="font-medium mb-2">Incidents</h4>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-primary"></div>
                    <span>Critical</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-warning"></div>
                    <span>High</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-secondary"></div>
                    <span>Medium</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full bg-success"></div>
                    <span>Low</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Response Teams</h4>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <Flame className="h-3 w-3 text-red-500" />
                    <span>Fire Dept</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Stethoscope className="h-3 w-3 text-blue-500" />
                    <span>Medical</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Shield className="h-3 w-3 text-blue-600" />
                    <span>Police</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="h-3 w-3 text-green-500" />
                    <span>Rescue</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Map Area */}
        <div className="lg:col-span-3">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Map className="h-5 w-5" />
                Emergency Response Map
                <Badge variant="outline" className="ml-auto">
                  {mapView.charAt(0).toUpperCase() + mapView.slice(1)} View
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="h-full p-0">
              {/* Simulated Map Interface */}
              <div className="relative h-full bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 rounded-b-lg overflow-hidden">
                {/* Map Grid Lines */}
                <div className="absolute inset-0 opacity-20">
                  {Array.from({ length: 20 }, (_, i) => (
                    <div
                      key={`h-${i}`}
                      className="absolute w-full border-t border-muted"
                      style={{ top: `${i * 5}%` }}
                    />
                  ))}
                  {Array.from({ length: 20 }, (_, i) => (
                    <div
                      key={`v-${i}`}
                      className="absolute h-full border-l border-muted"
                      style={{ left: `${i * 5}%` }}
                    />
                  ))}
                </div>

                {/* Incident Markers */}
                {dummyIncidents.map((incident, index) => (
                  <div
                    key={incident.id}
                    className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all hover:scale-110 ${
                      selectedIncident === incident.id ? 'scale-125 z-20' : 'z-10'
                    }`}
                    style={{
                      left: `${20 + index * 15}%`,
                      top: `${25 + index * 12}%`,
                    }}
                    onClick={() => setSelectedIncident(selectedIncident === incident.id ? null : incident.id)}
                  >
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${getSeverityColor(incident.severity)}`}>
                      {getIncidentIcon(incident.type)}
                    </div>
                    {selectedIncident === incident.id && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-card border border-border rounded-lg p-3 shadow-lg min-w-[200px]">
                        <div className="font-medium">{incident.type}</div>
                        <div className="text-sm text-muted-foreground">{incident.location.split(',')[0]}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Score: {incident.aiAnalysis.emergencyScore}/100
                        </div>
                        <div className="flex gap-1 mt-2">
                          <Button size="sm" variant="emergency" className="text-xs">
                            Respond
                          </Button>
                          <Button size="sm" variant="outline" className="text-xs">
                            Details
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Response Team Markers */}
                {dummyResponseTeams.map((team, index) => (
                  <div
                    key={team.id}
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all hover:scale-110"
                    style={{
                      left: `${30 + index * 18}%`,
                      top: `${60 + (index % 2) * 10}%`,
                    }}
                  >
                    <div className={`w-5 h-5 rounded-sm border flex items-center justify-center ${getTeamStatusColor(team.status)}`}>
                      {getTeamIcon(team.type)}
                    </div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 bg-card border border-border rounded px-2 py-1 text-xs opacity-0 hover:opacity-100 transition-opacity">
                      {team.name}
                    </div>
                  </div>
                ))}

                {/* Hazard Zones */}
                <div className="absolute opacity-30">
                  <div 
                    className="absolute border-2 border-dashed border-primary rounded-full"
                    style={{
                      left: '18%',
                      top: '23%',
                      width: '120px',
                      height: '120px',
                    }}
                  />
                  <div 
                    className="absolute border-2 border-dashed border-warning rounded-full"
                    style={{
                      left: '45%',
                      top: '35%',
                      width: '80px',
                      height: '80px',
                    }}
                  />
                </div>

                {/* Coordinate Display */}
                <div className="absolute bottom-4 right-4 bg-card border border-border rounded px-3 py-2 text-sm">
                  <div>Lat: 40.7589</div>
                  <div>Lng: -73.9851</div>
                </div>

                {/* Scale */}
                <div className="absolute bottom-4 left-4 bg-card border border-border rounded px-3 py-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-px bg-foreground"></div>
                    <span>1 km</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Map Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">{dummyIncidents.length}</div>
            <div className="text-sm text-muted-foreground">Active Incidents</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-secondary">{dummyResponseTeams.length}</div>
            <div className="text-sm text-muted-foreground">Response Teams</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">
              {dummyResponseTeams.filter(t => t.status === 'deployed').length}
            </div>
            <div className="text-sm text-muted-foreground">Teams Deployed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">87%</div>
            <div className="text-sm text-muted-foreground">Coverage Area</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};