import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Shield, Users, MapPin, Activity, Clock } from "lucide-react";

interface DashboardProps {
  onPageChange: (page: string) => void;
}

export const Dashboard = ({ onPageChange }: DashboardProps) => {
  const incidents = [
    { id: 1, type: "Wildfire", location: "Northern District", severity: "Critical", time: "2 min ago", status: "Active" },
    { id: 2, type: "Flood", location: "Central Valley", severity: "High", time: "15 min ago", status: "Responding" },
    { id: 3, type: "Earthquake", location: "Eastern Region", severity: "Medium", time: "1 hour ago", status: "Monitoring" },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "Critical": return "text-primary";
      case "High": return "text-warning";
      case "Medium": return "text-secondary";
      default: return "text-success";
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case "Critical": return "bg-primary/10 border-primary/20";
      case "High": return "bg-warning/10 border-warning/20";
      case "Medium": return "bg-secondary/10 border-secondary/20";
      default: return "bg-success/10 border-success/20";
    }
  };

  return (
    <section className="py-16 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Emergency Operations Dashboard
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Real-time monitoring and coordination of emergency incidents across all regions
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Incidents</p>
                  <p className="text-3xl font-bold text-primary">23</p>
                </div>
                <div className="h-12 w-12 gradient-emergency rounded-lg flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Response Teams</p>
                  <p className="text-3xl font-bold text-secondary">47</p>
                </div>
                <div className="h-12 w-12 gradient-rescue rounded-lg flex items-center justify-center">
                  <Shield className="h-6 w-6 text-secondary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">People Assisted</p>
                  <p className="text-3xl font-bold text-success">1,247</p>
                </div>
                <div className="h-12 w-12 gradient-success rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-success-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Response</p>
                  <p className="text-3xl font-bold text-foreground">8 min</p>
                </div>
                <div className="h-12 w-12 bg-accent rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-accent-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Incidents */}
          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Recent Incidents
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {incidents.map((incident) => (
                <div
                  key={incident.id}
                  className={`p-4 rounded-lg border ${getSeverityBg(incident.severity)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-foreground">{incident.type}</h4>
                    <span className={`text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {incident.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {incident.time}
                    </div>
                  </div>
                  <div className="mt-3">
                    <Button variant="outline" size="sm" onClick={() => onPageChange('incidents')}>
                      View Details
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-secondary" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button variant="emergency" className="w-full justify-start gap-3" size="lg" onClick={() => onPageChange('report')}>
                <AlertTriangle className="h-5 w-5" />
                Report New Emergency
              </Button>
              <Button variant="rescue" className="w-full justify-start gap-3" size="lg" onClick={() => onPageChange('incidents')}>
                <Shield className="h-5 w-5" />
                Deploy Response Team
              </Button>
              <Button variant="hero" className="w-full justify-start gap-3" size="lg" onClick={() => onPageChange('map')}>
                <MapPin className="h-5 w-5" />
                View Interactive Map
              </Button>
              <Button variant="hero" className="w-full justify-start gap-3" size="lg" onClick={() => onPageChange('communications')}>
                <Users className="h-5 w-5" />
                Manage Resources
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};