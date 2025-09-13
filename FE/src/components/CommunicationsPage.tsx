import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  MessageSquare, 
  Phone, 
  Video, 
  Send, 
  Mic, 
  Image, 
  MapPin, 
  AlertTriangle,
  Users,
  Volume2,
  Paperclip,
  Search
} from 'lucide-react';
import { dummyMessages } from '@/lib/dummyData';
import { Message } from '@/lib/types';

export const CommunicationsPage = () => {
  const [messages, setMessages] = useState<Message[]>(dummyMessages);
  const [newMessage, setNewMessage] = useState<string>('');
  const [selectedChannel, setSelectedChannel] = useState<string>('all-units');
  const [isRecording, setIsRecording] = useState<boolean>(false);

  const channels = [
    { id: 'all-units', name: 'All Units', description: 'General emergency communications' },
    { id: 'fire-dept', name: 'Fire Department', description: 'Fire and rescue operations' },
    { id: 'medical', name: 'Medical Teams', description: 'Medical emergency response' },
    { id: 'police', name: 'Police Units', description: 'Police and security operations' },
    { id: 'command', name: 'Command Center', description: 'Command and coordination' },
    { id: 'citizens', name: 'Citizen Reports', description: 'Public emergency reports' },
  ];

  const emergencyContacts = [
    { name: 'Fire Chief Johnson', role: 'Fire Department', status: 'online', phone: '+1-555-FIRE-001' },
    { name: 'Dr. Sarah Chen', role: 'Medical Director', status: 'busy', phone: '+1-555-MED-001' },
    { name: 'Captain Rodriguez', role: 'Police Chief', status: 'online', phone: '+1-555-POLICE-001' },
    { name: 'Command Center', role: 'Operations', status: 'online', phone: '+1-555-COMMAND' },
    { name: 'Emergency Dispatch', role: 'Dispatch', status: 'online', phone: '+1-555-911-DISP' },
  ];

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const message: Message = {
        id: `MSG${Date.now()}`,
        from: 'Current User',
        to: selectedChannel,
        content: newMessage,
        type: 'text',
        timestamp: new Date(),
        isEmergency: newMessage.toLowerCase().includes('emergency') || newMessage.toLowerCase().includes('urgent')
      };
      setMessages([...messages, message]);
      setNewMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-success';
      case 'busy': return 'bg-warning';
      case 'offline': return 'bg-muted';
      default: return 'bg-muted';
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Emergency Communications</h1>
          <p className="text-muted-foreground">Real-time communication hub for emergency response</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Phone className="h-4 w-4" />
            Emergency Call
          </Button>
          <Button variant="emergency" className="gap-2">
            <AlertTriangle className="h-4 w-4" />
            Alert All Units
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[80vh]">
        {/* Channels & Contacts Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Channels
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {channels.map((channel) => (
                <Button
                  key={channel.id}
                  variant={selectedChannel === channel.id ? "default" : "ghost"}
                  className="w-full justify-start h-auto p-3"
                  onClick={() => setSelectedChannel(channel.id)}
                >
                  <div className="text-left">
                    <div className="font-medium">{channel.name}</div>
                    <div className="text-xs text-muted-foreground">{channel.description}</div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Emergency Contacts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {emergencyContacts.map((contact, index) => (
                <div key={index} className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50">
                  <div className="relative">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="text-xs">
                        {contact.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-card ${getStatusColor(contact.status)}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">{contact.name}</div>
                    <div className="text-xs text-muted-foreground">{contact.role}</div>
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                      <Phone className="h-3 w-3" />
                    </Button>
                    <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                      <Video className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <Card className="h-full flex flex-col">
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  {channels.find(c => c.id === selectedChannel)?.name || 'Channel'}
                  <Badge variant="outline" className="ml-2">
                    {messages.filter(m => m.to === selectedChannel || m.from === selectedChannel).length} messages
                  </Badge>
                </CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="gap-2">
                    <Search className="h-3 w-3" />
                    Search
                  </Button>
                  <Button variant="outline" size="sm" className="gap-2">
                    <Volume2 className="h-3 w-3" />
                    Audio
                  </Button>
                </div>
              </div>
            </CardHeader>

            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto space-y-4 p-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.from === 'Current User' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback className="text-xs">
                      {message.from.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className={`flex-1 max-w-[70%] ${message.from === 'Current User' ? 'text-right' : ''}`}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{message.from}</span>
                      <span className="text-xs text-muted-foreground">{formatTime(message.timestamp)}</span>
                      {message.isEmergency && (
                        <Badge variant="outline" className="text-xs text-primary border-primary">
                          URGENT
                        </Badge>
                      )}
                    </div>
                    <div className={`rounded-lg p-3 ${
                      message.from === 'Current User' 
                        ? 'bg-primary text-primary-foreground ml-auto' 
                        : message.isEmergency
                          ? 'bg-primary/10 border border-primary/20'
                          : 'bg-muted'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>

            {/* Message Input */}
            <div className="flex-shrink-0 p-4 border-t">
              <div className="flex gap-2">
                <div className="flex-1 space-y-2">
                  <Textarea
                    placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="min-h-[60px] resize-none"
                  />
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className={`gap-2 ${isRecording ? 'bg-primary text-primary-foreground' : ''}`}
                      onClick={() => setIsRecording(!isRecording)}
                    >
                      <Mic className="h-3 w-3" />
                      {isRecording ? 'Recording...' : 'Voice'}
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <Image className="h-3 w-3" />
                      Image
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <MapPin className="h-3 w-3" />
                      Location
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <Paperclip className="h-3 w-3" />
                      File
                    </Button>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  <Button
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim()}
                    className="h-[60px] px-6"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                  <Button variant="emergency" size="sm" className="gap-2">
                    <AlertTriangle className="h-3 w-3" />
                    URGENT
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Button variant="emergency" className="gap-2">
          <AlertTriangle className="h-4 w-4" />
          Mass Alert
        </Button>
        <Button variant="secondary" className="gap-2">
          <Phone className="h-4 w-4" />
          Conference Call
        </Button>
        <Button variant="outline" className="gap-2">
          <Video className="h-4 w-4" />
          Video Meeting
        </Button>
        <Button variant="outline" className="gap-2">
          <MessageSquare className="h-4 w-4" />
          Broadcast SMS
        </Button>
        <Button variant="outline" className="gap-2">
          <Volume2 className="h-4 w-4" />
          Public Address
        </Button>
      </div>
    </div>
  );
};