import { Button } from "@/components/ui/button";
import { AlertTriangle, Shield, MapPin, BarChart3 } from "lucide-react";
import heroImage from "@/assets/emergency-hero.jpg";

interface HeroSectionProps {
  onPageChange: (page: string) => void;
}

export const HeroSection = ({ onPageChange }: HeroSectionProps) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <img 
          src={heroImage} 
          alt="Emergency Operations Center" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" />
      </div>
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-6">
            <AlertTriangle className="h-12 w-12 text-primary emergency-pulse" />
            <h1 className="text-5xl md:text-7xl font-bold text-foreground">
              Emergency Tracker
            </h1>
          </div>
          
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            AI-powered emergency response system that analyzes real-time data, prioritizes incidents by severity, 
            and coordinates rescue operations to save lives during disasters and natural calamities.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button variant="emergency" size="lg" className="text-lg px-8 py-6" onClick={() => onPageChange('dashboard')}>
              Launch Dashboard
            </Button>
            <Button variant="rescue" size="lg" className="text-lg px-8 py-6" onClick={() => onPageChange('report')}>
              Report Incident
            </Button>
          </div>
          
          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="bg-card/80 backdrop-blur-sm p-6 rounded-xl border border-border">
              <div className="h-12 w-12 gradient-emergency rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">AI Severity Analysis</h3>
              <p className="text-muted-foreground">
                Automatically analyze weather data and citizen reports to prioritize emergency response
              </p>
            </div>
            
            <div className="bg-card/80 backdrop-blur-sm p-6 rounded-xl border border-border">
              <div className="h-12 w-12 gradient-rescue rounded-lg flex items-center justify-center mx-auto mb-4">
                <MapPin className="h-6 w-6 text-secondary-foreground" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Real-Time Mapping</h3>
              <p className="text-muted-foreground">
                Interactive maps showing incident locations, severity zones, and rescue team positions
              </p>
            </div>
            
            <div className="bg-card/80 backdrop-blur-sm p-6 rounded-xl border border-border">
              <div className="h-12 w-12 gradient-success rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="h-6 w-6 text-success-foreground" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Coordinated Response</h3>
              <p className="text-muted-foreground">
                Streamlined communication between authorities, rescue teams, and affected citizens
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Floating Emergency Indicator */}
      <div className="absolute top-4 right-4 z-20">
        <div className="bg-card/90 backdrop-blur-sm p-3 rounded-lg border border-border">
          <div className="flex items-center gap-2 text-sm">
            <div className="h-2 w-2 bg-primary rounded-full emergency-pulse"></div>
            <span className="text-muted-foreground">System Active</span>
          </div>
        </div>
      </div>
    </section>
  );
};