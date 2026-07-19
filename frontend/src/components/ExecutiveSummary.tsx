"use client";

import { Analysis } from "@/lib/api";

export function ExecutiveSummary({ analysis }: { analysis: Analysis }) {
  const totalTasks = analysis.tasks.length;
  const completed = analysis.tasks.filter(t => t.status === "done").length;
  const rate = totalTasks > 0 ? completed / totalTasks : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Executive Summary</h2>
      <p className="text-inkMuted text-sm mb-4 leading-relaxed">{analysis.summary}</p>
      <div className="flex gap-4 text-xs">
        <span className="text-inkMuted">Health: <span className="text-signal">{Math.round(rate * 100)}%</span></span>
        <span className="text-inkMuted">Decisions: <span className="text-ink">{analysis.decisions?.length || 0}</span></span>
        <span className="text-inkMuted">Topics: <span className="text-ink">{analysis.topics?.length || 0}</span></span>
      </div>
    </div>
  );
}