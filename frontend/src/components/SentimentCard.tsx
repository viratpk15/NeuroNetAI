"use client";

import { Sentiment } from "@/lib/api";

export function SentimentCard({ sentiment }: { sentiment: Sentiment }) {
  const sentimentColors = {
    positive: "text-green-400",
    negative: "text-risk",
    neutral: "text-inkMuted",
  };

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Sentiment Analysis</h2>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-inkMuted text-xs uppercase">Overall</span>
          <span className={`text-xs font-medium ${sentimentColors[sentiment.overall_sentiment as keyof typeof sentimentColors]}`}>
            {sentiment.overall_sentiment}
          </span>
        </div>

        {[
          { label: "Positivity", value: sentiment.positivity_score, color: "bg-green-500" },
          { label: "Stress", value: sentiment.stress_score, color: "bg-risk" },
          { label: "Confidence", value: sentiment.confidence_score, color: "bg-signal" },
        ].map(({ label, value, color }) => (
          <div key={label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-inkMuted uppercase">{label}</span>
              <span className="text-ink font-mono">{Math.round(value * 100)}%</span>
            </div>
            <div className="w-full bg-surfaceRaised rounded-full h-1.5">
              <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${value * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}