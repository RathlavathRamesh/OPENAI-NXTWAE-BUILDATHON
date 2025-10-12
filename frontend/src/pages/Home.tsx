import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  AlertCircle, 
  MessageSquare, 
  ClipboardList, 
  Users,
  Activity,
  MapPin,
  Clock,
  LayoutDashboard,
  Map
} from "lucide-react";
import { useState, useEffect } from "react";

export default function Home() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "User";
    setUsername(storedUsername);
  }, []);

  // Mock data
  const myActivities = [
    {
      id: 1,
      type: "Report",
      title: "Fire Emergency at MG Road",
      status: "Active",
      timestamp: "2 hours ago",
      role: "Reporter"
    },
    {
      id: 2,
      type: "Rescue",
      title: "Medical Emergency - Sector 5",
      status: "Completed",
      timestamp: "1 day ago",
      role: "Responder"
    }
  ];

  const allocatedResources = [
    {
      id: 1,
      name: "Fire Brigade Unit A",
      designation: "Fire & Rescue Team",
      incident: "Fire Emergency at MG Road",
      status: "En Route"
    },
    {
      id: 2,
      name: "Ambulance 108",
      designation: "Medical Response Unit",
      incident: "Medical Emergency - Sector 5",
      status: "Completed"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-muted/30 via-background to-muted/20">
      <Header username={username} />
      
      <main className="container py-8 px-4 max-w-6xl mx-auto space-y-8">
        {/* Welcome Section */}
        <Card className="bg-gradient-to-r from-primary/10 via-secondary/10 to-emergency/10 border-none shadow-lg animate-fade-in">
          <CardHeader className="text-center py-8">
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-emergency rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">RS</span>
                </div>
                <CardTitle className="text-3xl font-bold gradient-text">Welcome, {username}!</CardTitle>
              </div>
              <CardDescription className="text-lg text-muted-foreground">
                Emergency Response & Rescue Management System
              </CardDescription>
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-emergency rounded-full animate-pulse"></div>
                <span>Bridge between Government and People</span>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card 
            className="cursor-pointer hover-lift glass-effect border-primary/20 group animate-slide-up"
            onClick={() => navigate("/dashboard")}
          >
            <CardHeader className="text-center space-y-4 py-6">
              <div className="mx-auto bg-gradient-to-br from-primary/20 to-primary/10 w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <LayoutDashboard className="h-8 w-8 text-primary" />
              </div>
              <CardTitle className="text-lg font-semibold">Dashboard</CardTitle>
              <CardDescription className="text-sm">System overview</CardDescription>
            </CardHeader>
          </Card>

          <Card 
            className="cursor-pointer hover-lift glass-effect border-secondary/20 group animate-slide-up delay-100"
            onClick={() => navigate("/map")}
          >
            <CardHeader className="text-center space-y-4 py-6">
              <div className="mx-auto bg-gradient-to-br from-secondary/20 to-secondary/10 w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <Map className="h-8 w-8 text-secondary" />
              </div>
              <CardTitle className="text-lg font-semibold">Map View</CardTitle>
              <CardDescription className="text-sm">Track on map</CardDescription>
            </CardHeader>
          </Card>

          <Card 
            className="cursor-pointer hover-lift glass-effect border-emergency/20 group animate-slide-up delay-200"
            onClick={() => navigate("/report")}
          >
            <CardHeader className="text-center space-y-4 py-6">
              <div className="mx-auto bg-gradient-to-br from-emergency/20 to-emergency/10 w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <AlertCircle className="h-8 w-8 text-emergency" />
              </div>
              <CardTitle className="text-lg font-semibold">Report Emergency</CardTitle>
              <CardDescription className="text-sm">Report incidents</CardDescription>
            </CardHeader>
          </Card>

          <Card 
            className="cursor-pointer hover-lift glass-effect border-secondary/20 group animate-slide-up delay-300"
            onClick={() => navigate("/ai-assistant")}
          >
            <CardHeader className="text-center space-y-4 py-6">
              <div className="mx-auto bg-gradient-to-br from-secondary/20 to-secondary/10 w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <MessageSquare className="h-8 w-8 text-secondary" />
              </div>
              <CardTitle className="text-lg font-semibold">AI Assistant</CardTitle>
              <CardDescription className="text-sm">Get guidance</CardDescription>
            </CardHeader>
          </Card>

          <Card 
            className="cursor-pointer hover-lift glass-effect border-accent/20 group animate-slide-up delay-400"
            onClick={() => navigate("/incidents")}
          >
            <CardHeader className="text-center space-y-4 py-6">
              <div className="mx-auto bg-gradient-to-br from-accent/20 to-accent/10 w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <ClipboardList className="h-8 w-8 text-accent-foreground" />
              </div>
              <CardTitle className="text-lg font-semibold">View Incidents</CardTitle>
              <CardDescription className="text-sm">Track incidents</CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="activity" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-muted/50">
            <TabsTrigger value="activity" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              <Activity className="h-4 w-4" />
              My Activity
            </TabsTrigger>
            <TabsTrigger value="resources" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              <Users className="h-4 w-4" />
              Allocated Resources
            </TabsTrigger>
          </TabsList>

          <TabsContent value="activity" className="space-y-4 mt-6">
            {myActivities.map((activity, index) => (
              <Card key={activity.id} className="hover-lift glass-effect animate-scale-in" style={{ animationDelay: `${index * 100}ms` }}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg font-semibold">{activity.title}</CardTitle>
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                          activity.status === 'Active' 
                            ? 'bg-success/10 text-success border border-success/20' 
                            : 'bg-muted text-muted-foreground border border-muted'
                        }`}>
                          {activity.status}
                        </span>
                      </div>
                      <CardDescription className="flex items-center gap-4 text-sm">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {activity.role}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {activity.timestamp}
                        </span>
                      </CardDescription>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="hover:bg-primary hover:text-primary-foreground transition-colors"
                      onClick={() => navigate(`/incident/${activity.id}`)}
                    >
                      View Details
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="resources" className="space-y-4 mt-6">
            {allocatedResources.map((resource, index) => (
              <Card key={resource.id} className="hover-lift glass-effect animate-scale-in" style={{ animationDelay: `${index * 100}ms` }}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-lg">{resource.name}</h3>
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                          resource.status === 'En Route' 
                            ? 'bg-accent/10 text-accent-foreground border border-accent/20' 
                            : 'bg-muted text-muted-foreground border border-muted'
                        }`}>
                          {resource.status}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{resource.designation}</p>
                      <p className="text-sm flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        Assigned to: {resource.incident}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
