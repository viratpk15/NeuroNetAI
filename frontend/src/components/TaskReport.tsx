"use client";

import { Analysis } from "@/lib/api";

export function TaskReport({ analysis }: { analysis: Analysis }) {
  const completed = analysis.tasks.filter(t => t.status === "done").length;
  const pending = analysis.tasks.filter(t => t.status === "open").length;
  const highPriority = analysis.tasks.filter(t => t.priority === "high").length;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Task Report</h2>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div><span className="text-inkMuted">Completed</span><div className="text-green-400 text-lg font-medium">{completed}</div></div>
        <div><span className="text-inkMuted">Pending</span><div className="text-ink text-lg font-medium">{pending}</div></div>
        <div><span className="text-inkMuted">High Priority</span><div className="text-risk text-lg font-medium">{highPriority}</div></div>
      </div>
    </div>
  );
}