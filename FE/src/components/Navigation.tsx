import { Button } from "@/components/ui/button";
import { AlertTriangle, Shield, MapPin, MessageSquare, Settings, BarChart3 } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export const Navigation = ({ currentPage, onPageChange }: NavigationProps) => {
  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold text-foreground">Emergency Tracker</span>
            </div>
            
            <div className="hidden md:flex items-center gap-6">
              <Button 
                variant={currentPage === 'dashboard' ? "default" : "ghost"} 
                className="gap-2"
                onClick={() => onPageChange('dashboard')}
              >
                <BarChart3 className="h-4 w-4" />
                Dashboard
              </Button>
              <Button 
                variant={currentPage === 'incidents' ? "default" : "ghost"} 
                className="gap-2"
                onClick={() => onPageChange('incidents')}
              >
                <MapPin className="h-4 w-4" />
                Incidents
              </Button>
              <Button 
                variant={currentPage === 'map' ? "default" : "ghost"} 
                className="gap-2"
                onClick={() => onPageChange('map')}
              >
                <Shield className="h-4 w-4" />
                Map View
              </Button>
              <Button 
                variant={currentPage === 'communications' ? "default" : "ghost"} 
                className="gap-2"
                onClick={() => onPageChange('communications')}
              >
                <MessageSquare className="h-4 w-4" />
                Communications
              </Button>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button 
              variant="emergency" 
              size="sm"
              onClick={() => onPageChange('report')}
            >
              Report Emergency
            </Button>
            <ThemeToggle />
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};