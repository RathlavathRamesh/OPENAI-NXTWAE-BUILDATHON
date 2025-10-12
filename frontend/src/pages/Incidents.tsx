import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../lib/constants";
import { Header } from "@/components/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Clock, AlertCircle } from "lucide-react";

export default function Incidents() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username") || "User";

  const [incidents, setIncidents] = useState([]);
  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/allincidents`);
        const data = await res.json();
        setIncidents(data.body?.incidents || []);
      } catch {
        setIncidents([]);
      }
    };
    fetchIncidents();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-success/10 text-success border-success/20";
      case "In Progress":
        return "bg-accent/10 text-accent-foreground border-accent/20";
      case "Completed":
        return "bg-muted text-muted-foreground border-muted-foreground/20";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "Critical":
        return "bg-destructive/10 text-destructive border-destructive/20";
      case "High":
        return "bg-primary/10 text-primary border-primary/20";
      case "Medium":
        return "bg-accent/10 text-accent-foreground border-accent/20";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <Header showBack username={username} />
      
      <main className="container py-8 px-4 max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">All Incidents</h1>
          <p className="text-muted-foreground">Track and manage emergency incidents</p>
        </div>

        <div className="grid gap-4">
          {incidents.map((incident) => (
            <Card 
              key={incident.incident_id} 
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/incident/${incident.incident_id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <CardTitle className="text-xl">{incident.incident_name}</CardTitle>
                      <Badge className={getStatusColor(incident.status)}>
                        {incident.status}
                      </Badge>
                      <Badge className={getSeverityColor(incident.severity_level)}>
                        {incident.severity_level}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{incident.incident_name}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              </CardHeader>

              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>{incident.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>{incident.time ? `${incident.time} min ago` : ""}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    <span>Reported by: {incident.reported_by}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
