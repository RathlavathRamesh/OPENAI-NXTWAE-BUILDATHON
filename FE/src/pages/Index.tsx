import { useState } from "react";
import { Navigation } from "@/components/Navigation";
import { HeroSection } from "@/components/HeroSection";
import { Dashboard } from "@/components/Dashboard";
import { IncidentsPage } from "@/components/IncidentsPage";
import { MapPage } from "@/components/MapPage";
import { CommunicationsPage } from "@/components/CommunicationsPage";
import { ReportEmergencyPage } from "@/components/ReportEmergencyPage";

const Index = () => {
  const [currentPage, setCurrentPage] = useState("home");

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onPageChange={setCurrentPage} />;
      case 'incidents':
        return <IncidentsPage />;
      case 'map':
        return <MapPage />;
      case 'communications':
        return <CommunicationsPage />;
      case 'report':
        return <ReportEmergencyPage />;
      default:
        return (
          <>
            <HeroSection onPageChange={setCurrentPage} />
            <Dashboard onPageChange={setCurrentPage} />
          </>
        );
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      {renderCurrentPage()}
    </main>
  );
};

export default Index;
