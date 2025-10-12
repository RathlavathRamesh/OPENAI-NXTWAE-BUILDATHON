import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Bot, User, History, Trash2, Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { API_BASE_URL } from "../lib/constants";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatHistory {
  id: string;
  title: string;
  timestamp: Date;
  messages: Message[];
}

export default function AIAssistant() {
  const username = localStorage.getItem("username") || "User";
  const [currentChatId, setCurrentChatId] = useState<string>("default");
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hello! I'm your AI assistant for emergency response guidance. How can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedHistories = localStorage.getItem("chatHistories");
    if (savedHistories) {
      setChatHistories(JSON.parse(savedHistories));
    }
  }, []);

  const saveCurrentChat = () => {
    if (messages.length > 1) {
      const existingIndex = chatHistories.findIndex(h => h.id === currentChatId);
      const chatTitle = messages.find(m => m.role === "user")?.content.slice(0, 30) || "New Chat";
      
      const updatedHistory: ChatHistory = {
        id: currentChatId,
        title: chatTitle,
        timestamp: new Date(),
        messages: messages
      };

      let newHistories;
      if (existingIndex >= 0) {
        newHistories = [...chatHistories];
        newHistories[existingIndex] = updatedHistory;
      } else {
        newHistories = [...chatHistories, updatedHistory];
      }
      
      setChatHistories(newHistories);
      localStorage.setItem("chatHistories", JSON.stringify(newHistories));
    }
  };

  const loadChat = (chatId: string) => {
    saveCurrentChat();
    const chat = chatHistories.find(h => h.id === chatId);
    if (chat) {
      setCurrentChatId(chatId);
      setMessages(chat.messages);
    }
  };

  const startNewChat = () => {
    saveCurrentChat();
    const newChatId = `chat_${Date.now()}`;
    setCurrentChatId(newChatId);
    setMessages([
      {
        id: 1,
        role: "assistant",
        content: "Hello! I'm your AI assistant for emergency response guidance. How can I help you today?",
        timestamp: new Date()
      }
    ]);
  };

  const deleteChat = (chatId: string) => {
    const newHistories = chatHistories.filter(h => h.id !== chatId);
    setChatHistories(newHistories);
    localStorage.setItem("chatHistories", JSON.stringify(newHistories));
    if (currentChatId === chatId) {
      startNewChat();
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      role: "user",
      content: input,
      timestamp: new Date()
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    // Call backend API for response
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-response`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          prompt: input,
          section_id: 1,
          section_name: "section1",
          prompt_given_at: new Date().toISOString(),
          user_id: localStorage.getItem("userId") || 1
        })
      });
      const data = await response.json();
      const responseText = data?.body?.response || "No response received.";
      const aiMessage: Message = {
        id: newMessages.length + 1,
        role: "assistant",
        content: responseText,
        timestamp: new Date()
      };
      setMessages((prev) => {
        const updated = [...prev, aiMessage];
        saveCurrentChat();
        return updated;
      });
    } catch (error) {
      const aiMessage: Message = {
        id: newMessages.length + 1,
        role: "assistant",
        content: "Failed to get response from AI.",
        timestamp: new Date()
      };
      setMessages((prev) => {
        const updated = [...prev, aiMessage];
        saveCurrentChat();
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-muted/30 flex flex-col">
      <Header showBack username={username} />
      
      <main className="flex-1 container max-w-4xl mx-auto py-6 px-4 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">AI Assistant</h1>
          <div className="flex gap-2">
            <Button onClick={startNewChat} variant="outline" size="sm">
              New Chat
            </Button>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm">
                  <History className="h-4 w-4 mr-2" />
                  History
                </Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle>Chat History</SheetTitle>
                  <SheetDescription>
                    View your previous conversations
                  </SheetDescription>
                </SheetHeader>
                <ScrollArea className="h-[calc(100vh-120px)] mt-4">
                  <div className="space-y-2">
                    {chatHistories.map((chat) => (
                      <Card
                        key={chat.id}
                        className={`p-3 cursor-pointer hover:bg-accent transition-colors ${
                          currentChatId === chat.id ? "bg-accent" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1" onClick={() => loadChat(chat.id)}>
                            <p className="font-medium text-sm truncate">{chat.title}</p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(chat.timestamp).toLocaleDateString()}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteChat(chat.id);
                            }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </Card>
                    ))}
                    {chatHistories.length === 0 && (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No chat history yet
                      </p>
                    )}
                  </div>
                </ScrollArea>
              </SheetContent>
            </Sheet>
          </div>
        </div>
        
        
        {/* Chat Messages */}
        <div className="flex-1 space-y-4 mb-4 overflow-y-auto">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {message.role === "assistant" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                  <Bot className="h-5 w-5 text-secondary-foreground" />
                </div>
              )}
              
              <Card className={`max-w-[80%] p-4 ${
                message.role === "user" 
                  ? "bg-primary text-primary-foreground" 
                  : "bg-card"
              }`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <span className={`text-xs mt-2 block ${
                  message.role === "user" 
                    ? "text-primary-foreground/70" 
                    : "text-muted-foreground"
                }`}>
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </Card>

              {message.role === "user" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <User className="h-5 w-5 text-primary-foreground" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Area */}
        <Card className="p-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="min-h-[60px] resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={loading}
            />
            <Button 
              onClick={handleSend}
              size="icon"
              className="h-[60px] w-[60px] flex-shrink-0"
              disabled={loading}
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </Button>
          </div>
        </Card>
      </main>
    </div>
  );
}
