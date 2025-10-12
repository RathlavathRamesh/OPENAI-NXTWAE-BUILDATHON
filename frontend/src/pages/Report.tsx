import { useEffect, useState } from "react";
import { API_BASE_URL } from "../lib/constants";
import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  AlertCircle,
  AlertTriangle,
  Upload,
  X,
  FileImage,
  FileVideo,
  FileAudio,
  MapPin,
  Navigation,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Report() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [reportType, setReportType] = useState<"emergency" | "public">("emergency");
  const [formData, setFormData] = useState({
    category: "",
    location: "",
    description: "",
    severity: "",
  });
  const [incidentTypes, setIncidentTypes] = useState<{ id: number; value: string }[]>([]);
  const [severityLevels, setSeverityLevels] = useState<{ id: number; value: string }[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  // Remove loading state to prevent blank page
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [incidentTypesLoaded, setIncidentTypesLoaded] = useState(false);
  const [severityLevelsLoaded, setSeverityLevelsLoaded] = useState(false);

  const username = localStorage.getItem("username") || "User";

  // 🔹 Fetch Incident Types and Severity Levels
  // Fetch incident types only when dropdown is opened
  const fetchIncidentTypes = async () => {
    if (incidentTypesLoaded) return;
    try {
      const incidentRes = await fetch(`${API_BASE_URL}/api/incidenttypes`);
      if (!incidentRes.ok) throw new Error("API fetch failed");
      const incidentDataJson = await incidentRes.json();
      setIncidentTypes(incidentDataJson.body?.emergency_types || []);
      setIncidentTypesLoaded(true);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to load categories",
        description: "Unable to fetch categories.",
      });
    }
  };

  // Fetch severity levels only when dropdown is opened
  const fetchSeverityLevels = async () => {
    if (severityLevelsLoaded) return;
    try {
      const severityRes = await fetch(`${API_BASE_URL}/api/severitylevels`);
      if (!severityRes.ok) throw new Error("API fetch failed");
      const severityDataJson = await severityRes.json();
      setSeverityLevels(severityDataJson.body?.severity_levels || []);
      setSeverityLevelsLoaded(true);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to load severity levels",
        description: "Unable to fetch severity levels.",
      });
    }
  };

  // 🔹 Get Current Location
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast({
        variant: "destructive",
        title: "Geolocation not supported",
        description: "Your browser doesn't support geolocation.",
      });
      return;
    }

    setIsGettingLocation(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const coordinates = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
        setFormData({ ...formData, location: coordinates });

        toast({
          title: "Location captured",
          description: "GPS coordinates have been added to the location field.",
        });
        setIsGettingLocation(false);
      },
      (error) => {
        let errorMessage = "Unable to retrieve your location.";
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "Location access denied by user.";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information is unavailable.";
            break;
          case error.TIMEOUT:
            errorMessage = "Location request timed out.";
            break;
        }

        toast({
          variant: "destructive",
          title: "Location Error",
          description: errorMessage,
        });
        setIsGettingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  // 🔹 Handle File Upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFiles([...files, ...Array.from(e.target.files)]);
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith("image/")) return <FileImage className="h-4 w-4" />;
    if (file.type.startsWith("video/")) return <FileVideo className="h-4 w-4" />;
    if (file.type.startsWith("audio/")) return <FileAudio className="h-4 w-4" />;
    return <Upload className="h-4 w-4" />;
  };

  // 🔹 Submit Incident API Integration
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // Find selected incident type and severity level objects
      const selectedIncident = incidentTypes.find((i) => i.value === formData.category);
      const selectedSeverity = severityLevels.find((s) => s.value === formData.severity);
      const userId = localStorage.getItem("userId") || null;

      // Prepare FormData
      const form = new FormData();
      form.append("description", formData.description);
      form.append("location", formData.location);
      form.append("reporterId", userId ? String(userId) : "");
      form.append("reporterName", username);
      form.append("reporterContactNumber", "9876543211");
      form.append("emergencyType", formData.category);
      form.append("emergencyTypeId", selectedIncident?.id ? String(selectedIncident.id) : "");
      form.append("estimatedSeverity", formData.severity || "medium");
      form.append("severityId", selectedSeverity?.id ? String(selectedSeverity.id) : "");

      // Append files
      files.forEach((file) => {
        if (file.type.startsWith("image/")) {
          form.append("images", file);
        } else if (file.type.startsWith("video/")) {
          form.append("video", file);
        } else if (file.type.startsWith("audio/")) {
          form.append("audio", file);
        }
      });

      const response = await fetch(
        `http://127.0.0.1:8002/api/submitrequest`,
        {
          method: "POST",
          body: form,
        }
      );
      if (!response.ok) throw new Error("Failed to submit incident");
      toast({
        title: "Incident Submitted",
        description: "Your report has been sent successfully.",
      });
      navigate("/incidents");
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "Could not submit the report. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <Header showBack username={username} />

      <main className="container py-8 px-4 max-w-3xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <AlertCircle className="h-6 w-6 text-primary" />
              Report an Incident
            </CardTitle>
            <CardDescription>
              Choose the type of report and provide details
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Report Type */}
              <div className="space-y-3">
                <Label>Report Type</Label>
                <RadioGroup
                  value={reportType}
                  onValueChange={(value) =>
                    setReportType(value as "emergency" | "public")
                  }
                  className="grid grid-cols-2 gap-4"
                >
                  <div>
                    <RadioGroupItem
                      value="emergency"
                      id="emergency"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="emergency"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary cursor-pointer"
                    >
                      <AlertCircle className="mb-3 h-8 w-8" />
                      <span className="text-sm font-medium">Emergency</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem
                      value="public"
                      id="public"
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor="public"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary cursor-pointer"
                    >
                      <AlertTriangle className="mb-3 h-8 w-8" />
                      <span className="text-sm font-medium">Public Issue</span>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) =>
                    setFormData({ ...formData, category: value })
                  }
                  required
                  onOpenChange={(open) => { if (open) fetchIncidentTypes(); }}
                >
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {incidentTypes && incidentTypes.length > 0 ? (
                      incidentTypes
                        .filter((item) => item?.value) // ✅ ensure defined
                        .map((item) => (
                          <SelectItem key={item.id} value={String(item.value)}>
                            {item.value}
                          </SelectItem>
                        ))
                    ) : (
                      <SelectItem value="none" disabled>No categories found</SelectItem>
                    )}
                  </SelectContent>

                </Select>
              </div>

              {/* Severity */}
              {reportType === "emergency" && (
                <div className="space-y-2">
                  <Label htmlFor="severity">Severity Level</Label>
                  <Select
                    value={formData.severity}
                    onValueChange={(value) =>
                      setFormData({ ...formData, severity: value })
                    }
                    required
                    onOpenChange={(open) => { if (open) fetchSeverityLevels(); }}
                  >
                    <SelectTrigger id="severity">
                      <SelectValue placeholder="Select severity" />
                    </SelectTrigger>
                    <SelectContent>
                      {severityLevels && severityLevels.length > 0 ? (
                        severityLevels
                          .filter((level) => level?.value)
                          .map((level) => (
                            <SelectItem key={level.id} value={String(level.value)}>
                              {level.value}
                            </SelectItem>
                          ))
                      ) : (
                        <SelectItem value="none" disabled>No severity levels found</SelectItem>
                      )}
                    </SelectContent>

                  </Select>
                </div>
              )}

              {/* Location */}
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <div className="flex gap-2">
                  <Input
                    id="location"
                    placeholder="Enter incident location"
                    value={formData.location}
                    onChange={(e) =>
                      setFormData({ ...formData, location: e.target.value })
                    }
                    className="flex-1"
                    required
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={getCurrentLocation}
                    disabled={isGettingLocation}
                    title="Get current location"
                  >
                    {isGettingLocation ? (
                      <Navigation className="h-4 w-4 animate-spin" />
                    ) : (
                      <MapPin className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Provide detailed description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  required
                />
              </div>

              {/* File Upload */}
              <div className="space-y-2">
                <Label>Attachments</Label>
                <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary transition-colors">
                  <input
                    type="file"
                    id="file-upload"
                    multiple
                    accept="image/*,video/*,audio/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      Click to upload or drag and drop
                    </p>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="space-y-2 mt-4">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-muted rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          {getFileIcon(file)}
                          <span className="text-sm truncate max-w-[200px]">
                            {file.name}
                          </span>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeFile(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate("/home")}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-emergency hover:bg-emergency/90"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Submitting..." : "Submit"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
