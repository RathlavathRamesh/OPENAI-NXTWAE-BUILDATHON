import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { API_BASE_URL } from "../lib/constants";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, CheckCircle, Clock, TrendingUp } from "lucide-react";

export default function Dashboard() {
  const username = localStorage.getItem("username") || "User";

  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [recentIncidents, setRecentIncidents] = useState<any[]>([]);
  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/dashboardreport`);
        const data = await res.json();
        setDashboardStats(data.body || null);
      } catch {
        setDashboardStats(null);
      }
    };
    const fetchRecentIncidents = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/recentincidents`);
        const data = await res.json();
        setRecentIncidents(data.body?.recent_incidents || []);
      } catch {
        setRecentIncidents([]);
      }
    };
    fetchDashboard();
    fetchRecentIncidents();
  }, []);

  return (
    <div className="min-h-screen bg-muted/30">
      <Header showBack username={username} />
      
      <main className="container mx-auto py-6 px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Overview of emergency response system</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Incidents</CardTitle>
              <AlertCircle className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats?.active_incidents ?? "-"}</div>
              <p className="text-xs text-muted-foreground">Current active emergencies</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Response Teams</CardTitle>
              <CheckCircle className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats?.response_teams ?? "-"}</div>
              <p className="text-xs text-muted-foreground">Teams available</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">People Assisted</CardTitle>
              <TrendingUp className="h-4 w-4 text-secondary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats?.people_assisted ?? "-"}</div>
              <p className="text-xs text-muted-foreground">Total assisted</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-emergency" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats?.avg_response ?? "-"} min</div>
              <p className="text-xs text-muted-foreground">Average response time</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Incidents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentIncidents.length > 0 ? recentIncidents.map((incident) => (
                  <div key={incident.incident_id} className="flex items-center gap-4 p-3 rounded-lg bg-muted/50">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{incident.incident_name} at {incident.location}</p>
                      <p className="text-xs text-muted-foreground">Severity: {incident.severity_level} | {incident.elapsed_time} min ago</p>
                    </div>
                  </div>
                )) : <p className="text-muted-foreground">No recent incidents found.</p>}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Resource Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {["Ambulance", "Fire Truck", "Police Unit", "Rescue Team"].map((resource, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <span className="text-sm font-medium">{resource}</span>
                    <span className="text-sm text-muted-foreground">{5 - index} available</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
