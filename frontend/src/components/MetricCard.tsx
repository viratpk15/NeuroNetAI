"use client";

import { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function MetricCard({ title, value, description, icon, trend = "neutral", className = "" }: MetricCardProps) {
  const trendColors = {
    up: "text-green-400",
    down: "text-risk",
    neutral: "text-inkMuted",
  };

  return (
    <div className={`bg-surface rounded-lg p-5 border border-border ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-inkMuted uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-semibold text-ink mt-1">{value}</p>
          {description && <p className={`text-xs mt-2 ${trendColors[trend]}`}>{description}</p>}
        </div>
        {icon && <div className="text-signal">{icon}</div>}
      </div>
    </div>
  );
}

interface AICardProps {
  title: string;
  description?: string;
  confidence?: number;
  sources?: number;
  className?: string;
}

export function AICard({ title, description, confidence, sources, className = "" }: AICardProps) {
  return (
    <div className={`bg-surface rounded-lg p-5 border border-border ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-ink">{title}</h3>
        <div className="flex items-center gap-2">
          {confidence !== undefined && (
            <span className="text-xs bg-signal/20 text-signal px-2 py-0.5 rounded-full">
              {Math.round(confidence * 100)}% confidence
            </span>
          )}
          {sources !== undefined && (
            <span className="text-xs text-inkMuted">{sources} sources</span>
          )}
        </div>
      </div>
      {description && <p className="text-sm text-inkMuted line-clamp-3">{description}</p>}
    </div>
  );
}

interface StatusBadgeProps {
  status: "active" | "completed" | "at-risk" | "critical" | "low" | "medium" | "high";
  className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const bgColors = {
    active: "bg-signal/20 text-signal",
    completed: "bg-green-900/30 text-green-300",
    "at-risk": "bg-amber-900/30 text-amber-300",
    critical: "bg-risk/20 text-risk",
    low: "bg-green-900/30 text-green-300",
    medium: "bg-amber-900/30 text-amber-300",
    high: "bg-risk/20 text-risk",
  };

  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${bgColors[status]} ${className}`}>
      {status.replace("-", " ")}
    </span>
  );
}