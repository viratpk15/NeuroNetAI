"use client";

import { Analysis } from "@/lib/api";

interface RiskDetectionProps {
  analyses: Record<string, Analysis>;
}

export function RiskDetection({ analyses }: RiskDetectionProps) {
  const risks: string[] = [];

  Object.entries(analyses).forEach(([id, analysis]) => {
    if (analysis.sentiment?.overall_sentiment === "negative") {
      risks.push(`Project ${id.slice(0, 8)} has negative sentiment`);
    }
  });

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Risk Detection</h2>
      {risks.length === 0 ? (
        <p className="text-inkMuted text-sm">No risks detected</p>
      ) : (
        <ul className="space-y-1">
          {risks.map((risk, i) => (
            <li key={i} className="text-sm text-risk flex items-start gap-2">
              <span>⚠️</span>
              <span>{risk}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}