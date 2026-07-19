"use client";

import { Analysis } from "@/lib/api";

export function SummaryCard({ analysis }: { analysis: Analysis }) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Conversation Summary</h2>
      
      <p className="text-inkMuted text-sm mb-4 leading-relaxed">
        {analysis.summary || "No summary available."}
      </p>
      
      {analysis.topics && analysis.topics.length > 0 && (
        <div className="mb-4">
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase tracking-wider">Topics</h3>
          <div className="flex flex-wrap gap-2">
            {analysis.topics.map((topic, i) => (
              <span key={i} className="px-2 py-1 text-xs bg-blue-900/30 text-blue-300 rounded">
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.decisions && analysis.decisions.length > 0 && (
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase tracking-wider">Decisions</h3>
          <ul className="space-y-1">
            {analysis.decisions.map((decision, i) => (
              <li key={i} className="text-sm text-inkMuted flex items-start gap-2">
                <span className="text-signal mt-0.5">•</span>
                <span>{decision}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}