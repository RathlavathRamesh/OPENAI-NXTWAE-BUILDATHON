import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../lib/constants";
import { Header } from "@/components/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  MapPin, 
  Clock, 
  AlertCircle, 
  User, 
  Phone,
  Users,
  Activity
} from "lucide-react";

export default function IncidentDetail() {
  const { id } = useParams();
  const username = localStorage.getItem("username") || "User";

  const [incident, setIncident] = useState<any>(null);
  useEffect(() => {
    const fetchIncident = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/allincidents`);
        const data = await res.json();
        const found = data.body?.incidents?.find((i: any) => String(i.incident_id) === String(id));
        setIncident(found || null);
      } catch {
        setIncident(null);
      }
    };
    fetchIncident();
  }, [id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-success/10 text-success border-success/20";
      case "En Route":
        return "bg-accent/10 text-accent-foreground border-accent/20";
      case "On Scene":
        return "bg-secondary/10 text-secondary border-secondary/20";
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
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  if (!incident) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <Header showBack username={username} />
        <span className="text-muted-foreground">Loading incident details...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/30">
      <Header showBack username={username} />
      <main className="container py-8 px-4 max-w-5xl mx-auto space-y-6">
        {/* Header Section */}
        <Card>
          <CardHeader>
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="space-y-2">
                  <CardTitle className="text-2xl">{incident.incident_name}</CardTitle>
                  <p className="text-muted-foreground">{incident.incident_name}</p>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Badge className={getStatusColor(incident.status)}>
                    {incident.status}
                  </Badge>
                  <Badge className={getSeverityColor(incident.severity_level)}>
                    {incident.severity_level}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span>{incident.location}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Reported {incident.time ? `${incident.time} min ago` : ""}</span>
                </div>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span>{incident.reported_by}</span>
                </div>
                {/* No reporterContact in API, so skip */}
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Description */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Description
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground leading-relaxed">{incident.description}</p>
          </CardContent>
        </Card>
        {/* Allocated Resources and Timeline not in API, so skip */}
      </main>
    </div>
  );
}
