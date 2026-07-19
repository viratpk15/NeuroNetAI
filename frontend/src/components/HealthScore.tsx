"use client";

import { Analysis } from "@/lib/api";

export function HealthScore({ analyses }: { analyses: Record<string, Analysis> }) {
  const analysisList = Object.values(analyses);
  const avgScore = analysisList.length > 0
    ? analysisList.reduce((s, a) => s + (a.sentiment?.positivity_score || 0), 0) / analysisList.length
    : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Project Health Score</h2>
      <div className="flex items-end gap-3">
        <span className="text-3xl font-display font-semibold text-ink">{Math.round(avgScore * 100)}</span>
        <span className="text-inkMuted text-sm mb-1">/ 100</span>
      </div>
      <div className="w-full bg-surfaceRaised rounded-full h-2 mt-2">
        <div className="bg-signal h-2 rounded-full" style={{ width: `${avgScore * 100}%` }} />
      </div>
    </div>
  );
}