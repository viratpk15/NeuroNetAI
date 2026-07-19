"use client";

import { Analysis, Project } from "@/lib/api";

export function ActivityTimeline({ projects, analyses }: { projects: Project[]; analyses: Record<string, Analysis> }) {
  const events = [
    ...projects.map(p => ({ type: "project" as const, label: `Project created: ${p.name}`, time: p.created_at })),
    ...Object.entries(analyses).map(([, a]) => ({ type: "analysis" as const, label: `Analysis completed`, time: a.agent_run_id })),
  ].sort((a, b) => a.time.localeCompare(b.time));

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Activity Timeline</h2>
      {events.length === 0 ? (
        <p className="text-inkMuted text-sm">No activity yet</p>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {events.slice(0, 10).map((event, idx) => (
            <div key={`${event.type}-${event.label}-${idx}`} className="flex items-center gap-2 text-sm">
              <span className="text-signal">•</span>
              <span className="text-inkMuted">{event.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}