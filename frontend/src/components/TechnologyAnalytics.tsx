"use client";

interface TechnologyAnalyticsProps {
  tech: [string, number][];
}

export function TechnologyAnalytics({ tech }: TechnologyAnalyticsProps) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Technology Analytics</h2>
      {tech.length === 0 ? (
        <p className="text-inkMuted text-sm">No technology data</p>
      ) : (
        <div className="space-y-2">
          {tech.map(([name, count]) => (
            <div key={name} className="flex items-center gap-2">
              <span className="text-inkMuted text-xs w-20 truncate">{name}</span>
              <div className="flex-1 bg-surfaceRaised rounded h-4">
                <div className="bg-cyan-500 h-4 rounded" style={{ width: `${Math.min(count * 20, 100)}%` }} />
              </div>
              <span className="text-ink text-xs font-mono">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}