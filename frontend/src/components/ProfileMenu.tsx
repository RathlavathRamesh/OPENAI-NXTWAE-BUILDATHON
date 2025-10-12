import { LogOut, User, Activity, Settings, Shield, MapPin, Phone, Mail, Calendar } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface ProfileMenuProps {
  username: string;
}

export const ProfileMenu = ({ username }: ProfileMenuProps) => {
  const navigate = useNavigate();
  const [userDetails, setUserDetails] = useState({
    email: "",
    phone: "",
    location: "",
    joinDate: "",
    role: "Citizen",
    status: "Active"
  });

  useEffect(() => {
    // Mock user details - in real app, this would come from API
    const mockDetails = {
      email: `${username.toLowerCase()}@rakshasetu.gov.in`,
      phone: "+91 98765 43210",
      location: "New Delhi, India",
      joinDate: "January 2024",
      role: "Citizen",
      status: "Active"
    };
    setUserDetails(mockDetails);
  }, [username]);

  const handleLogout = () => {
    localStorage.removeItem("username");
    navigate("/login");
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Avatar className="h-9 w-9 border-2 border-primary cursor-pointer hover:opacity-80 transition-all duration-200 hover:scale-105">
          <AvatarFallback className="bg-gradient-to-br from-primary to-emergency text-white font-semibold">
            {getInitials(username)}
          </AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 p-0">
        {/* User Header */}
        <div className="bg-gradient-to-r from-primary/10 to-emergency/10 p-4 border-b">
          <div className="flex items-center space-x-3">
            <Avatar className="h-12 w-12 border-2 border-primary">
              <AvatarFallback className="bg-gradient-to-br from-primary to-emergency text-white font-semibold text-lg">
                {getInitials(username)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground truncate">{username}</p>
              <p className="text-xs text-muted-foreground truncate">{userDetails.email}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-xs">
                  <Shield className="h-3 w-3 mr-1" />
                  {userDetails.role}
                </Badge>
                <Badge variant={userDetails.status === "Active" ? "default" : "secondary"} className="text-xs">
                  {userDetails.status}
                </Badge>
              </div>
            </div>
          </div>
        </div>

        {/* User Details */}
        {/* <div className="p-4 space-y-3">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Phone:</span>
              <span className="font-medium">{userDetails.phone}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Location:</span>
              <span className="font-medium">{userDetails.location}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Member since:</span>
              <span className="font-medium">{userDetails.joinDate}</span>
            </div>
          </div>
        </div>

        <DropdownMenuSeparator /> */}

        {/* Menu Items */}
        <div className="py-1">
          <DropdownMenuItem onClick={() => navigate("/home")} className="cursor-pointer">
            <User className="mr-2 h-4 w-4" />
            <span>View Profile</span>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate("/home")} className="cursor-pointer">
            <Activity className="mr-2 h-4 w-4" />
            <span>My Activity</span>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate("/home")} className="cursor-pointer">
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </DropdownMenuItem>
        </div>

        <DropdownMenuSeparator />

        <div className="py-1">
          <DropdownMenuItem onClick={handleLogout} className="text-destructive cursor-pointer">
            <LogOut className="mr-2 h-4 w-4" />
            <span>Logout</span>
          </DropdownMenuItem>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
