"use client";

import { Analysis } from "@/lib/api";

export function TeamReport({ analysis }: { analysis: Analysis }) {
  const contributors = analysis.entities
    .filter(e => e.entity_type === "person")
    .reduce((acc, e) => { acc[e.name] = (acc[e.name] || 0) + 1; return acc; }, {} as Record<string, number>);
  const topContributors = Object.entries(contributors).sort((a, b) => b[1] - a[1]).slice(0, 3);

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Team Report</h2>
      <div className="space-y-2">
        {topContributors.map(([name, count]) => (
          <div key={name} className="flex justify-between text-sm">
            <span className="text-ink">@{name}</span>
            <span className="text-inkMuted">{count} mentions</span>
          </div>
        ))}
      </div>
    </div>
  );
}