import { Header } from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Navigation } from "lucide-react";

export default function MapView() {
  const username = localStorage.getItem("username") || "User";

  const incidents = [
    { id: 1, location: "Main Street", type: "Fire", severity: "High", lat: 28.6139, lng: 77.2090 },
    { id: 2, location: "Park Avenue", type: "Medical", severity: "Medium", lat: 28.6129, lng: 77.2295 },
    { id: 3, location: "City Center", type: "Accident", severity: "Low", lat: 28.6149, lng: 77.2190 }
  ];

  return (
    <div className="min-h-screen bg-muted/30">
      <Header showBack username={username} />
      
      <main className="container mx-auto py-6 px-4">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Map View</h1>
            <p className="text-muted-foreground">Real-time incident tracking</p>
          </div>
          <Navigation className="h-6 w-6 text-primary" />
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <Card className="p-0 overflow-hidden">
              <div className="relative h-[600px] bg-gradient-to-br from-primary/5 to-secondary/5 flex items-center justify-center">
                <div className="text-center space-y-4">
                  <MapPin className="h-16 w-16 text-primary mx-auto" />
                  <div>
                    <p className="text-lg font-semibold">Interactive Map</p>
                    <p className="text-sm text-muted-foreground">Map integration placeholder</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Active Incidents</h3>
            {incidents.map((incident) => (
              <Card key={incident.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{incident.type}</span>
                    <Badge variant={
                      incident.severity === "High" ? "destructive" : 
                      incident.severity === "Medium" ? "default" : 
                      "secondary"
                    }>
                      {incident.severity}
                    </Badge>
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 mr-1" />
                    {incident.location}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Lat: {incident.lat}, Lng: {incident.lng}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
