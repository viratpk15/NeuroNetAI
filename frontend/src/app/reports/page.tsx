"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis } from "@/lib/api";
import { ErrorState } from "@/components/ErrorState";

export default function ReportsPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getAnalysis("demo-project")
      .then(setAnalysis)
      .catch(e => {
        const err = e as Error & { status?: number; isNetworkError?: boolean };
        if (err.isNetworkError) {
          setError("Unable to connect to backend. Please ensure the backend is running.");
        } else {
          setError(err.message || "Failed to load analysis");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <ReportsSkeleton />;
  }

  if (error) {
    return (
      <div className="p-6 lg:p-8 max-w-6xl">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">AI Reports</h1>
        <ErrorState title="Failed to load reports" message={error} />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold text-ink">AI Reports</h1>
        <p className="text-sm text-inkMuted mt-1">Generate and export project insights</p>
      </div>

      {!analysis ? (
        <ReportsEmptyState />
      ) : (
        <div className="space-y-6">
          <ExecutiveSummary analysis={analysis} />
          <TaskReport analysis={analysis} />
          <TeamReport analysis={analysis} />
          <TechnologyReport analysis={analysis} />
          <TimelineReport />
          <RiskReport analysis={analysis} />
          <ExportPanel analysis={analysis} />
        </div>
      )}
    </div>
  );
}

function ReportsEmptyState() {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <svg className="w-16 h-16 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 className="text-lg font-medium text-ink mb-2">No reports generated yet</h3>
      <p className="text-sm text-inkMuted mb-4">
        Run AI analysis to generate your first report with insights about decisions, tasks, and technologies.
      </p>
      <Link href="/workspace/demo-project" className="inline-block bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition">
        Generate Report
      </Link>
    </div>
  );
}

function ReportsSkeleton() {
  return (
    <div className="p-8">
      <div className="h-8 w-32 bg-surfaceRaised rounded mb-6 animate-pulse" />
      <div className="space-y-4">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="bg-surface rounded-lg p-6 border border-border animate-pulse">
            <div className="h-5 w-24 bg-surfaceRaised rounded mb-3" />
            <div className="h-20 bg-surfaceRaised rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

function ExecutiveSummary({ analysis }: { analysis: Analysis }) {
  const totalTasks = analysis.tasks.length;
  const completed = analysis.tasks.filter(t => t.status === "done").length;
  const rate = totalTasks > 0 ? completed / totalTasks : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Executive Summary</h2>
      <p className="text-inkMuted text-sm mb-4 leading-relaxed">{analysis.summary}</p>
      <div className="flex gap-4 text-xs">
        <span className="text-inkMuted">Health: <span className="text-signal">{Math.round(rate * 100)}%</span></span>
        <span className="text-inkMuted">Decisions: <span className="text-ink">{analysis.decisions?.length || 0}</span></span>
        <span className="text-inkMuted">Topics: <span className="text-ink">{analysis.topics?.length || 0}</span></span>
      </div>
    </div>
  );
}

function TaskReport({ analysis }: { analysis: Analysis }) {
  const completed = analysis.tasks.filter(t => t.status === "done").length;
  const pending = analysis.tasks.filter(t => t.status === "open").length;
  const highPriority = analysis.tasks.filter(t => t.priority === "high").length;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Task Report</h2>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div><span className="text-inkMuted">Completed</span><div className="text-green-400 text-lg font-medium">{completed}</div></div>
        <div><span className="text-inkMuted">Pending</span><div className="text-ink text-lg font-medium">{pending}</div></div>
        <div><span className="text-inkMuted">High Priority</span><div className="text-risk text-lg font-medium">{highPriority}</div></div>
      </div>
    </div>
  );
}

function TeamReport({ analysis }: { analysis: Analysis }) {
  const contributors = analysis.entities
    .filter(e => e.entity_type === "person")
    .reduce((acc, e) => { acc[e.name] = (acc[e.name] || 0) + 1; return acc; }, {} as Record<string, number>);
  const topContributors = Object.entries(contributors).sort((a, b) => b[1] - a[1]).slice(0, 3);

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Team Report</h2>
      <div className="space-y-2">
        {topContributors.length === 0 ? (
          <p className="text-inkMuted text-sm">No contributors detected</p>
        ) : (
          topContributors.map(([name, count]) => (
            <div key={name} className="flex justify-between text-sm">
              <span className="text-ink">@{name}</span>
              <span className="text-inkMuted">{count} mentions</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function TechnologyReport({ analysis }: { analysis: Analysis }) {
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

function TimelineReport() {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Timeline Report</h2>
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2"><span className="text-signal">●</span><span>Analysis completed</span></div>
        <div className="flex items-center gap-2"><span className="text-inkMuted">○</span><span>Project active</span></div>
      </div>
    </div>
  );
}

function RiskReport({ analysis }: { analysis: Analysis }) {
  const risks: string[] = [];
  if (analysis.sentiment?.overall_sentiment === "negative") risks.push("Negative sentiment detected");
  const highPriority = analysis.tasks.filter(t => t.priority === "high").length;
  if (highPriority > 0) risks.push(`${highPriority} high priority tasks pending`);

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Risk Report</h2>
      {risks.length === 0 ? (
        <p className="text-inkMuted text-sm">No risks identified</p>
      ) : (
        <ul className="space-y-1">
          {risks.map((risk, i) => (
            <li key={i} className="text-sm text-risk flex items-start gap-2">⚠️ {risk}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ExportPanel({ analysis }: { analysis: Analysis }) {
  const exportReport = async (format: "pdf" | "markdown" | "json") => {
    const data = generateReportData(analysis, format);
    const blob = new Blob([data], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report.${format === "markdown" ? "md" : format}`;
    a.click();
  };

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Export Center</h2>
      <div className="flex gap-2">
        <button onClick={() => exportReport("pdf")} className="bg-signal text-canvas px-3 py-1.5 rounded text-sm">PDF</button>
        <button onClick={() => exportReport("markdown")} className="bg-surfaceRaised border border-border px-3 py-1.5 rounded text-sm">Markdown</button>
        <button onClick={() => exportReport("json")} className="bg-surfaceRaised border border-border px-3 py-1.5 rounded text-sm">JSON</button>
      </div>
    </div>
  );
}

function generateReportData(analysis: Analysis, format: string): string {
  if (format === "json") {
    return JSON.stringify(analysis, null, 2);
  }
  if (format === "markdown") {
    return `# Project Report\n\n## Summary\n${analysis.summary}\n\n## Tasks\n${analysis.tasks.map(t => `- ${t.title}`).join("\n")}`;
  }
  return `# Report\n${analysis.summary}\n\nTasks: ${analysis.tasks.length}`;
}