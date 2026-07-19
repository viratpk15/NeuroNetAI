import { api } from "@/lib/api";

const FUTURE_METRICS = [
  "Communication Health",
  "Collaboration Score",
  "Decision Speed",
  "Knowledge Sharing",
  "Blocked Discussions",
  "Burnout Risk",
];

export default async function DashboardPage() {
  let projectCount = 0;
  let apiReachable = true;
  try {
    const { items } = await api.listProjects();
    projectCount = items.length;
  } catch {
    apiReachable = false;
  }

  return (
    <div className="max-w-5xl">
      <h1 className="font-display text-2xl text-ink mb-1">Dashboard</h1>
      <p className="text-inkMuted text-sm mb-8">
        Organizational collaboration, at a glance.
      </p>

      {!apiReachable && (
        <div className="mb-6 rounded border border-risk/40 bg-risk/10 px-4 py-3 text-sm text-risk">
          Can&apos;t reach the backend API. Make sure it&apos;s running and
          NEXT_PUBLIC_API_URL is set correctly.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-10">
        <div className="rounded border border-border bg-surface p-5">
          <div className="text-inkMuted text-xs uppercase tracking-wide mb-2">Active Projects</div>
          <div className="font-display text-3xl text-signal">{projectCount}</div>
        </div>
      </div>

      <h2 className="font-display text-sm text-inkMuted uppercase tracking-wide mb-3">
        Coming in phase 2 — analysis agents
      </h2>
      <div className="grid grid-cols-3 gap-4">
        {FUTURE_METRICS.map((metric) => (
          <div key={metric} className="rounded border border-border bg-surface/50 p-5">
            <div className="text-inkMuted text-sm">{metric}</div>
            <div className="text-inkMuted/50 text-xs mt-1">Requires imported data + agent run</div>
          </div>
        ))}
      </div>
    </div>
  );
}
