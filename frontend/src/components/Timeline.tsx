"use client";

import { Analysis } from "@/lib/api";

export function Timeline({ analysis }: { analysis: Analysis }) {
  const events = [
    { label: "Import Completed", active: true },
    { label: "Analysis Started", active: analysis.status === "completed" },
    { label: "Analysis Completed", active: analysis.status === "completed" },
    { label: "Ready", active: analysis.status === "completed" },
  ];

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Timeline</h2>
      <div className="space-y-3">
        {events.map((event, i) => (
          <div key={event.label} className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${event.active ? "bg-signal" : "bg-border"}`} />
            <span className={`text-xs ${event.active ? "text-ink" : "text-inkMuted"}`}>
              {event.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}