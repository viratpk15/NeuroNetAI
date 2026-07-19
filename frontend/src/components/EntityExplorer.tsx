"use client";

import { Entity } from "@/lib/api";

interface EntityExplorerProps {
  entitiesByType: Record<string, Entity[]>;
  typeLabels: Record<string, string>;
}

const typeColors: Record<string, string> = {
  person: "bg-purple-900/30 text-purple-300",
  technology: "bg-cyan-900/30 text-cyan-300",
  repository: "bg-orange-900/30 text-orange-300",
  api: "bg-indigo-900/30 text-indigo-300",
  library: "bg-pink-900/30 text-pink-300",
  framework: "bg-violet-900/30 text-violet-300",
  deadline: "bg-amber-900/30 text-amber-300",
  organization: "bg-teal-900/30 text-teal-300",
};

export function EntityExplorer({ entitiesByType, typeLabels }: EntityExplorerProps) {
  const total = Object.values(entitiesByType).flat().length;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Entities ({total})</h2>
      
      {total === 0 ? (
        <p className="text-inkMuted text-sm">No entities extracted.</p>
      ) : (
        <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
          {Object.entries(entitiesByType).map(([type, entities]) => (
            <div key={type}>
              <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase tracking-wider">
                {typeLabels[type] || type}
              </h3>
              <div className="flex flex-wrap gap-2">
                {entities.map((entity) => (
                  <span key={entity.id} className={`px-2 py-1 text-xs rounded ${typeColors[type] || "bg-surfaceRaised"}`}>
                    {entity.name}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}