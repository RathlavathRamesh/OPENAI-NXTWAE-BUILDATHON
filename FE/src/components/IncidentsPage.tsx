import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AlertTriangle, Clock, MapPin, Users, Eye, MessageSquare, Phone } from 'lucide-react';
import { dummyIncidents } from '@/lib/dummyData';
import { Incident } from '@/lib/types';

export const IncidentsPage = () => {
  const [incidents] = useState<Incident[]>(dummyIncidents);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-primary';
      case 'high': return 'text-warning';
      case 'medium': return 'text-secondary';
      case 'low': return 'text-success';
      default: return 'text-muted-foreground';
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-primary/10 border-primary/20';
      case 'high': return 'bg-warning/10 border-warning/20';
      case 'medium': return 'bg-secondary/10 border-secondary/20';
      case 'low': return 'bg-success/10 border-success/20';
      default: return 'bg-muted/10 border-muted/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-primary text-primary-foreground';
      case 'responding': return 'bg-warning text-warning-foreground';
      case 'resolved': return 'bg-success text-success-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const filteredIncidents = incidents.filter(incident => {
    const matchesSeverity = filterSeverity === 'all' || incident.severity === filterSeverity;
    const matchesStatus = filterStatus === 'all' || incident.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      incident.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      incident.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      incident.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSeverity && matchesStatus && matchesSearch;
  });

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Emergency Incidents</h1>
          <p className="text-muted-foreground">Monitor and manage all emergency incidents</p>
        </div>
        <Button variant="emergency" className="gap-2">
          <AlertTriangle className="h-4 w-4" />
          Report New Incident
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Search incidents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select value={filterSeverity} onValueChange={setFilterSeverity}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="responding">Responding</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
            <div className="text-sm text-muted-foreground flex items-center">
              {filteredIncidents.length} of {incidents.length} incidents
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Incidents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Incident</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>AI Score</TableHead>
                <TableHead>Personnel</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredIncidents.map((incident) => (
                <TableRow 
                  key={incident.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => setSelectedIncident(incident)}
                >
                  <TableCell>
                    <div>
                      <div className="font-medium">{incident.type}</div>
                      <div className="text-sm text-muted-foreground">{incident.id}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getSeverityColor(incident.severity)}>
                      {incident.severity.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(incident.status)}>
                      {incident.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      <span className="text-sm">{incident.location.split(',')[0]}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className={`text-lg font-bold ${
                        incident.aiAnalysis.emergencyScore >= 80 ? 'text-primary' :
                        incident.aiAnalysis.emergencyScore >= 60 ? 'text-warning' :
                        'text-success'
                      }`}>
                        {incident.aiAnalysis.emergencyScore}
                      </div>
                      <div className="text-xs text-muted-foreground">/100</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      <span>{incident.aiAnalysis.rescuePersonnelRequired}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span className="text-sm">{formatTimeAgo(incident.timestamp)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button size="sm" variant="ghost">
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="ghost">
                        <MessageSquare className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="ghost">
                        <Phone className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Incident Detail Modal */}
      {selectedIncident && (
        <Card className="fixed inset-4 z-50 overflow-auto">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                {selectedIncident.type} - {selectedIncident.id}
              </CardTitle>
              <p className="text-muted-foreground">{selectedIncident.location}</p>
            </div>
            <Button variant="ghost" onClick={() => setSelectedIncident(null)}>×</Button>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Incident Details</h3>
                  <p className="text-sm text-muted-foreground">{selectedIncident.description}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Reported By</h3>
                  <p className="text-sm">{selectedIncident.reportedBy}</p>
                  <p className="text-xs text-muted-foreground">{formatTimeAgo(selectedIncident.timestamp)}</p>
                </div>
                <div className="flex gap-2">
                  <Badge className={getStatusColor(selectedIncident.status)}>
                    {selectedIncident.status}
                  </Badge>
                  <Badge variant="outline" className={getSeverityColor(selectedIncident.severity)}>
                    {selectedIncident.severity}
                  </Badge>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">AI Analysis</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Emergency Score:</span>
                      <span className="font-bold text-primary">{selectedIncident.aiAnalysis.emergencyScore}/100</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Personnel Required:</span>
                      <span className="font-bold">{selectedIncident.aiAnalysis.rescuePersonnelRequired}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Priority Level:</span>
                      <span className="font-bold">Level {selectedIncident.aiAnalysis.priorityLevel}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Risk Factors</h3>
                  <div className="flex flex-wrap gap-1">
                    {selectedIncident.aiAnalysis.riskFactors.map((risk, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {risk}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2 pt-4 border-t">
              <Button variant="emergency" className="flex-1">Deploy Response Team</Button>
              <Button variant="secondary" className="flex-1">Open Communications</Button>
              <Button variant="outline" className="flex-1">View on Map</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};