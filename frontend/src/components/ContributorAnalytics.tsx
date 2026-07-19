"use client";

import { Analysis } from "@/lib/api";

export function ContributorAnalytics({ analyses }: { analyses: Record<string, Analysis> }) {
  const contributorCounts = Object.values(analyses).flatMap(a => 
    a.entities.filter(e => e.entity_type === "person")
  ).reduce((acc, e) => {
    acc[e.name] = (acc[e.name] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const topContributors = Object.entries(contributorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="bg-surface rounded-lg p-6 border border-border mb-4">
      <h2 className="text-lg font-medium text-ink mb-3">Contributor Analytics</h2>
      {topContributors.length === 0 ? (
        <p className="text-inkMuted text-sm">No contributor data</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {topContributors.map(([name, count]) => (
            <div key={name} className="bg-surfaceRaised rounded px-3 py-2">
              <span className="text-ink font-medium text-sm">@{name}</span>
              <span className="text-inkMuted text-xs ml-2">{count} mentions</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}