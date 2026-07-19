"use client";

import { useEffect, useState, useRef } from "react";
import { api, Analysis } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getAnalysis("demo-project").then(setAnalysis).catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const response = generateAIResponse(input, analysis);
    
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: response,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, assistantMessage]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b border-border p-4">
        <h1 className="text-xl font-display font-semibold text-ink">AI Chat</h1>
        <p className="text-sm text-inkMuted mt-1">Ask questions about your project data</p>
      </header>

      <main className="flex-1 overflow-y-auto p-4 space-y-4" aria-label="Chat messages">
        {messages.length === 0 && !loading && (
          <EmptyState />
        )}
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {loading && <ThinkingIndicator />}
        <div ref={messagesEndRef} />
      </main>

      <footer className="border-t border-border p-4">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Ask about decisions, tasks, technologies..."
            className="flex-1 bg-surfaceRaised border border-border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/50"
            aria-label="Chat input"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-signal text-canvas px-4 py-2 rounded font-medium transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-signal"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <p className="text-inkMuted mb-2">No messages yet</p>
      <p className="text-sm text-inkMuted/60">Try: "What decisions were made?" or "Who discussed authentication?"</p>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-surface border border-border rounded-lg px-3 py-2">
        <span className="text-sm text-inkMuted animate-pulse">Thinking...</span>
      </div>
    </div>
  );
}

function ChatMessage({ message }: { message: Message }) {
  return (
    <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-in`}>
      <div className={`max-w-xs sm:max-w-md rounded-lg p-3 transition ${
        message.role === "user" 
          ? "bg-signal text-canvas" 
          : "bg-surface border border-border"
      }`}>
        <p className="text-sm leading-relaxed">{message.content}</p>
        <time className="text-[10px] mt-1 block opacity-60" dateTime={message.timestamp.toISOString()}>
          {message.timestamp.toLocaleTimeString()}
        </time>
      </div>
    </div>
  );
}

function generateAIResponse(question: string, analysis: Analysis | null): string {
  if (!analysis) return "No project data available. Import some data first.";

  const q = question.toLowerCase();

  if (q.includes("decision")) {
    return analysis.decisions.length 
      ? `Decisions made: ${analysis.decisions.join(", ")}`
      : "No decisions found in the project data.";
  }

  if (q.includes("task") || q.includes("todo")) {
    const openTasks = analysis.tasks.filter(t => t.status !== "done");
    return openTasks.length
      ? `Open tasks: ${openTasks.map(t => t.title).join(", ")}`
      : "No open tasks found.";
  }

  if (q.includes("who") || q.includes("person")) {
    const people = analysis.entities.filter(e => e.entity_type === "person");
    return people.length
      ? `People involved: ${people.map(p => p.name).join(", ")}`
      : "No people entities found.";
  }

  if (q.includes("technolog") || q.includes("tech")) {
    const tech = analysis.entities.filter(e => e.entity_type === "technology");
    return tech.length
      ? `Technologies used: ${tech.map(t => t.name).join(", ")}`
      : "No technologies found.";
  }

  if (q.includes("summar")) {
    return analysis.summary || "No summary available.";
  }

  return "I can help you find decisions, tasks, people, technologies, and summaries. What would you like to know?";
}