import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  AlertTriangle, 
  MapPin, 
  Camera, 
  Mic, 
  Upload, 
  Phone, 
  Clock,
  Users,
  Brain,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { analyzeEmergency, AIAnalysisInput, AIAnalysisResult } from '@/lib/aiAnalysis';
import { useToast } from '@/hooks/use-toast';

export const ReportEmergencyPage = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    type: '',
    location: '',
    description: '',
    reporterName: '',
    reporterContact: '',
    severity: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AIAnalysisResult | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const emergencyTypes = [
    'Fire Emergency',
    'Medical Emergency', 
    'Natural Disaster',
    'Traffic Accident',
    'Gas Leak',
    'Flood/Water Emergency',
    'Building Collapse',
    'Chemical Spill',
    'Missing Person',
    'Crime in Progress',
    'Other Emergency'
  ];

  const severityLevels = [
    { value: 'critical', label: 'Critical - Life threatening', color: 'text-primary' },
    { value: 'high', label: 'High - Serious injury/damage', color: 'text-warning' },
    { value: 'medium', label: 'Medium - Minor injury', color: 'text-secondary' },
    { value: 'low', label: 'Low - Property damage only', color: 'text-success' }
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const runAIAnalysis = async () => {
    if (!formData.description || !formData.location) {
      toast({
        title: "Missing Information",
        description: "Please provide at least a description and location for AI analysis.",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const analysisInput: AIAnalysisInput = {
        description: formData.description,
        location: formData.location,
        reporterInfo: `${formData.reporterName} - ${formData.reporterContact}`,
        images: uploadedFiles.filter(f => f.type.startsWith('image/')),
        audio: uploadedFiles.filter(f => f.type.startsWith('audio/')),
        weatherData: {
          temperature: 72,
          humidity: 65,
          windSpeed: 12,
          precipitation: 0,
          conditions: 'Clear'
        },
        populationDensity: 1500,
        timeOfDay: new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'
      };

      const result = await analyzeEmergency(analysisInput);
      setAnalysisResult(result);
      setCurrentStep(3);
      
      toast({
        title: "AI Analysis Complete",
        description: `Emergency score: ${result.emergencyScore}/100. ${result.rescuePersonnelRequired} personnel recommended.`,
      });
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Unable to complete AI analysis. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const submitReport = () => {
    toast({
      title: "Emergency Report Submitted",
      description: "Your emergency report has been sent to dispatch. Response teams are being notified.",
    });
    
    // Reset form
    setFormData({
      type: '',
      location: '',
      description: '',
      reporterName: '',
      reporterContact: '',
      severity: ''
    });
    setUploadedFiles([]);
    setAnalysisResult(null);
    setCurrentStep(1);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-primary';
    if (score >= 60) return 'text-warning';
    if (score >= 40) return 'text-secondary';
    return 'text-success';
  };

  return (
    <div className="container mx-auto px-4 py-6 space-y-6 max-w-4xl">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-foreground">Report Emergency</h1>
        <p className="text-muted-foreground">Provide incident details for AI-powered emergency response analysis</p>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                1
              </div>
              <span className={currentStep >= 1 ? 'text-foreground' : 'text-muted-foreground'}>Report Details</span>
            </div>
            <div className="flex-1 h-px bg-border mx-4"></div>
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                {isAnalyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : '2'}
              </div>
              <span className={currentStep >= 2 ? 'text-foreground' : 'text-muted-foreground'}>AI Analysis</span>
            </div>
            <div className="flex-1 h-px bg-border mx-4"></div>
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep >= 3 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                3
              </div>
              <span className={currentStep >= 3 ? 'text-foreground' : 'text-muted-foreground'}>Submit Report</span>
            </div>
          </div>
          <Progress value={currentStep * 33.33} className="h-2" />
        </CardContent>
      </Card>

      {/* Step 1: Emergency Details */}
      {currentStep === 1 && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-primary" />
                Emergency Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="type">Emergency Type</Label>
                  <Select value={formData.type} onValueChange={(value) => handleInputChange('type', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select emergency type" />
                    </SelectTrigger>
                    <SelectContent>
                      {emergencyTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="severity">Estimated Severity</Label>
                  <Select value={formData.severity} onValueChange={(value) => handleInputChange('severity', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select severity level" />
                    </SelectTrigger>
                    <SelectContent>
                      {severityLevels.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          <span className={level.color}>{level.label}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="location">Location</Label>
                <div className="flex gap-2">
                  <Input
                    id="location"
                    placeholder="Enter specific address or landmark"
                    value={formData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                  />
                  <Button variant="outline" className="gap-2">
                    <MapPin className="h-4 w-4" />
                    GPS
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="description">Detailed Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the emergency situation in detail. Include number of people involved, visible damage, current conditions, etc."
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Reporter Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Your Name</Label>
                  <Input
                    id="name"
                    placeholder="Full name"
                    value={formData.reporterName}
                    onChange={(e) => handleInputChange('reporterName', e.target.value)}
                  />
                </div>
                
                <div>
                  <Label htmlFor="contact">Contact Number</Label>
                  <Input
                    id="contact"
                    placeholder="Phone number"
                    value={formData.reporterContact}
                    onChange={(e) => handleInputChange('reporterContact', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Evidence & Media</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="photo">Upload Photos</Label>
                  <div className="mt-2">
                    <input
                      id="photo"
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      className="w-full gap-2"
                      onClick={() => document.getElementById('photo')?.click()}
                    >
                      <Camera className="h-4 w-4" />
                      Photos
                    </Button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="audio">Audio Recording</Label>
                  <div className="mt-2">
                    <input
                      id="audio"
                      type="file"
                      accept="audio/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      className="w-full gap-2"
                      onClick={() => document.getElementById('audio')?.click()}
                    >
                      <Mic className="h-4 w-4" />
                      Audio
                    </Button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="video">Video Evidence</Label>
                  <div className="mt-2">
                    <input
                      id="video"
                      type="file"
                      accept="video/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      className="w-full gap-2"
                      onClick={() => document.getElementById('video')?.click()}
                    >
                      <Upload className="h-4 w-4" />
                      Video
                    </Button>
                  </div>
                </div>
              </div>

              {uploadedFiles.length > 0 && (
                <div>
                  <Label>Uploaded Files</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {uploadedFiles.map((file, index) => (
                      <Badge key={index} variant="outline" className="gap-1">
                        {file.name}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-4 w-4 p-0"
                          onClick={() => setUploadedFiles(prev => prev.filter((_, i) => i !== index))}
                        >
                          ×
                        </Button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex gap-4">
            <Button
              variant="emergency"
              className="flex-1 gap-2"
              onClick={() => {
                setCurrentStep(2);
                runAIAnalysis();
              }}
              disabled={!formData.description || !formData.location}
            >
              <Brain className="h-4 w-4" />
              Run AI Analysis
            </Button>
            <Button variant="outline" className="gap-2">
              <Phone className="h-4 w-4" />
              Call 911 Now
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: AI Analysis */}
      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-secondary" />
              AI Emergency Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center py-12">
            <Loader2 className="h-16 w-16 animate-spin mx-auto text-secondary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Analyzing Emergency Situation</h3>
            <p className="text-muted-foreground mb-4">
              AI is processing your report, analyzing severity, and determining resource requirements...
            </p>
            <div className="max-w-md mx-auto">
              <Progress value={75} className="h-2" />
              <div className="flex justify-between text-xs text-muted-foreground mt-2">
                <span>Processing description</span>
                <span>Weather analysis</span>
                <span>Resource calculation</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Analysis Results & Submit */}
      {currentStep === 3 && analysisResult && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-success" />
                AI Analysis Complete
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className={`text-4xl font-bold ${getScoreColor(analysisResult.emergencyScore)}`}>
                    {analysisResult.emergencyScore}
                  </div>
                  <div className="text-sm text-muted-foreground">Emergency Score</div>
                  <div className="text-xs text-muted-foreground">(out of 100)</div>
                </div>
                
                <div className="text-center">
                  <div className="text-4xl font-bold text-secondary">
                    {analysisResult.rescuePersonnelRequired}
                  </div>
                  <div className="text-sm text-muted-foreground">Personnel Required</div>
                  <div className="text-xs text-muted-foreground">rescue team members</div>
                </div>
                
                <div className="text-center">
                  <div className="text-4xl font-bold text-warning">
                    {analysisResult.priorityLevel}
                  </div>
                  <div className="text-sm text-muted-foreground">Priority Level</div>
                  <div className="text-xs text-muted-foreground">(1 = highest)</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">AI Assessment</h4>
                <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
                  {analysisResult.estimatedSeverity}
                </p>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Identified Risk Factors</h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.riskFactors.map((risk, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {risk}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Recommended Actions</h4>
                <ul className="text-sm space-y-1">
                  {analysisResult.recommendedActions.map((action, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <CheckCircle className="h-3 w-3 text-success" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Weather Impact</h4>
                  <p className="text-sm text-muted-foreground">{analysisResult.weatherImpact}</p>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Estimated Duration</h4>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {analysisResult.estimatedDuration}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4">
            <Button
              variant="emergency"
              className="flex-1 gap-2"
              onClick={submitReport}
            >
              <AlertTriangle className="h-4 w-4" />
              Submit Emergency Report
            </Button>
            <Button
              variant="outline"
              onClick={() => setCurrentStep(1)}
            >
              Back to Edit
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};