"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import Link from "next/link";
import { api, Analysis } from "@/lib/api";
import { LoadingState } from "@/components/LoadingState";

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
  const [initLoading, setInitLoading] = useState(true);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setInitLoading(true);
    api.getAnalysis("demo-project")
      .then(setAnalysis)
      .catch(() => {})
      .finally(() => setInitLoading(false));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
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
  }, [input, analysis]);

  if (initLoading) {
    return (
      <div className="p-8">
        <div className="h-8 w-32 bg-surfaceRaised rounded mb-2 animate-pulse" />
        <div className="h-4 w-48 bg-surfaceRaised rounded mb-6 animate-pulse" />
        <LoadingState count={2} />
      </div>
    );
  }

  // Show onboarding if no analyzed project exists
  if (!analysis) {
    return (
      <div className="flex flex-col h-screen">
        <header className="border-b border-border p-4">
          <h1 className="text-xl font-display font-semibold text-ink">AI Chat</h1>
          <p className="text-sm text-inkMuted mt-1">Ask questions about your project data</p>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md">
            <svg className="w-16 h-16 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4-.84c-1.21.436-2.429.82-3.654.943A1 1 0 013 19V7a1 1 0 011.447-.892c.96.378 2.025.72 3.116.996C8.03 6.29 9.19 6 10.5 6h9c4.418 0 8 3.582 8 8z" />
            </svg>
            <h3 className="text-lg font-medium text-ink mb-2">Import project data before chatting</h3>
            <p className="text-sm text-inkMuted mb-4">
              Import your team communications in the workspace to enable AI-powered chat insights.
            </p>
            <Link href="/workspace/demo-project" className="inline-block bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition">
              Go to Workspace
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b border-border p-4">
        <h1 className="text-xl font-display font-semibold text-ink">AI Chat</h1>
        <p className="text-sm text-inkMuted mt-1">Ask questions about your project data</p>
      </header>

      <main className="flex-1 overflow-y-auto p-4 space-y-4" aria-label="Chat messages">
        {messages.length === 0 && !loading && (
          <ChatEmptyState />
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

function ChatEmptyState() {
  return (
    <div className="text-center py-12">
      <h3 className="text-lg font-medium text-ink mb-2">Ask me anything about your project</h3>
      <p className="text-sm text-inkMuted/60">
        Try: &ldquo;What decisions were made?&rdquo; or &ldquo;Who discussed authentication?&rdquo;
      </p>
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