"use client";

interface TaskAnalyticsProps {
  total: number;
  completed: number;
  pending: number;
}

export function TaskAnalytics({ total, completed, pending }: TaskAnalyticsProps) {
  const completionRate = total > 0 ? completed / total : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Task Analytics</h2>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-inkMuted">Completed</span>
          <span className="text-green-400">{completed}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-inkMuted">Pending</span>
          <span className="text-ink">{pending}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-inkMuted">Completion Rate</span>
          <span className="text-ink">{Math.round(completionRate * 100)}%</span>
        </div>
      </div>
    </div>
  );
}