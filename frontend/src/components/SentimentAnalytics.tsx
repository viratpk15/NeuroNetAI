"use client";

import { Analysis } from "@/lib/api";

export function SentimentAnalytics({ analyses }: { analyses: Record<string, Analysis> }) {
  const analysisList = Object.values(analyses);
  const avgSentiment = analysisList.length > 0
    ? analysisList.reduce((sum, a) => sum + (a.sentiment?.positivity_score || 0), 0) / analysisList.length
    : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Sentiment Analytics</h2>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-inkMuted uppercase">Average Positivity</span>
            <span className="text-ink font-mono">{Math.round(avgSentiment * 100)}%</span>
          </div>
          <div className="w-full bg-surfaceRaised rounded-full h-1.5">
            <div className="bg-green-500 h-1.5 rounded-full" style={{ width: `${avgSentiment * 100}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-inkMuted uppercase">Projects Analyzed</span>
            <span className="text-ink font-mono">{Object.keys(analyses).length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}