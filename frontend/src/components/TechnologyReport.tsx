"use client";

import { Analysis } from "@/lib/api";

export function TechnologyReport({ analysis }: { analysis: Analysis }) {
  const groups = ["technology", "library", "framework", "api", "repository"].map(type => ({
    type,
    items: analysis.entities.filter(e => e.entity_type === type),
  }));

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Technology Report</h2>
      <div className="space-y-3">
        {groups.map(({ type, items }) => items.length > 0 && (
          <div key={type}>
            <h3 className="text-xs text-inkMuted uppercase">{type}</h3>
            <div className="flex flex-wrap gap-1 mt-1">
              {items.map(e => <span key={e.id} className="text-xs bg-cyan-900/30 text-cyan-300 px-2 py-1 rounded">{e.name}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}