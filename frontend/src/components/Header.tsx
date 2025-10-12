import { Link, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeft, Shield, Moon, Sun, Bell, BellRing } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProfileMenu } from "@/components/ProfileMenu";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  showBack?: boolean;
  username?: string;
}

export const Header = ({ showBack = false, username }: HeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isHomePage = location.pathname === "/home";

  // 🔄 Manage dark mode state
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    // Load saved theme from localStorage or system preference
    const saved = localStorage.getItem("theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  // 🔔 Mock notifications state
  const [hasNotifications, setHasNotifications] = useState(true);
  const [notificationCount, setNotificationCount] = useState(3);

  // 🌓 Apply theme to <html> tag
  useEffect(() => {
    const root = window.document.documentElement;
    if (isDarkMode) {
      root.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  const handleNotificationClick = () => {
    setHasNotifications(false);
    setNotificationCount(0);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60 shadow-sm transition-all duration-300">
      <div className="container flex h-16 items-center justify-between px-6">
        {/* Left Section - App Branding */}
        <div className="flex items-center gap-4">
          {showBack && !isHomePage && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(-1)}
              className="h-9 w-9 hover:bg-accent/50 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          )}

          {/* App Icon & Name */}
          <Link
            to="/home"
            className="flex items-center gap-3 hover:opacity-80 transition-all duration-200 group"
          >
            <div className="relative">
              <Shield className="h-8 w-8 text-primary group-hover:scale-110 transition-transform duration-200" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-foreground tracking-tight">Raksha Setu</span>
              <span className="text-xs text-muted-foreground -mt-1">Emergency Response</span>
            </div>
          </Link>
        </div>

        {/* Right Section - Actions */}
        <div className="flex items-center gap-2">
          {/* 🌗 Dark Mode Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 hover:bg-accent/50 transition-all duration-200"
            onClick={() => setIsDarkMode(!isDarkMode)}
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDarkMode ? (
              <Sun className="h-5 w-5 text-yellow-400 hover:text-yellow-300 transition-colors" />
            ) : (
              <Moon className="h-5 w-5 text-slate-600 hover:text-slate-500 transition-colors" />
            )}
          </Button>

          {/* 🔔 Notifications */}
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 hover:bg-accent/50 transition-all duration-200"
              onClick={handleNotificationClick}
              title="Notifications"
            >
              {hasNotifications ? (
                <BellRing className="h-5 w-5 text-emergency animate-pulse" />
              ) : (
                <Bell className="h-5 w-5 text-muted-foreground hover:text-foreground transition-colors" />
              )}
            </Button>
            {/* {notificationCount > 0 && (
              <Badge 
                variant="destructive" 
                className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs font-bold animate-bounce"
              >
                {notificationCount}
              </Badge>
            )} */}
          </div>

          {/* 👤 User Profile */}
          {username && <ProfileMenu username={username} />}
        </div>
      </div>
    </header>
  );
};
