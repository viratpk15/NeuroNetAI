"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis, ImportJobStatus } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { MetricCard, AICard } from "@/components/MetricCard";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import { useProjectStore } from "@/lib/store";

interface ImportJob {
  id: string;
  project_id: string;
  source_type: string;
  original_filename: string | null;
  status: ImportJobStatus;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  document_count: number;
}

export default function DashboardPage() {
  const { currentProject } = useProjectStore();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [recentImports, setRecentImports] = useState<ImportJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const projectId = currentProject?.id;

  useEffect(() => {
    if (!projectId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    Promise.all([
      api.getAnalysis(projectId).catch(() => null),
      api.listImports(5, 0).catch(() => ({ items: [] })),
    ])
      .then(([analysisData, importsData]) => {
        setAnalysis(analysisData);
        setRecentImports(importsData.items);
      })
      .catch((e) => {
        const err = e as Error & { status?: number; isNetworkError?: boolean };
        if (err.isNetworkError) {
          setError("Unable to connect to backend. Please ensure the backend is running.");
        } else {
          setError(err.message || "Failed to load dashboard");
        }
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-2 animate-pulse" />
        <div className="h-4 w-64 bg-surfaceRaised rounded mb-6 animate-pulse" />
        <LoadingState count={4} />
      </div>
    );
  }

  if (!projectId) {
    return (
      <div className="p-8">
        <PageHeader title="Dashboard" description="Project intelligence overview" />
        <div className="text-center py-16">
          <p className="text-inkMuted mb-4">Select a project to view its dashboard.</p>
          <Link href="/projects" className="text-signal hover:underline">
            Go to Projects
          </Link>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <PageHeader title="Dashboard" description="Project intelligence overview" />
        <ErrorState title="Failed to load dashboard" message={error} />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-8">
        <PageHeader title="Dashboard" description="Project intelligence overview" />
        <div className="text-center py-16">
          <p className="text-inkMuted mb-4">No project analysis available.</p>
          <Link href={`/workspace/${projectId}`} className="text-signal hover:underline">
            Import project data to get started
          </Link>
        </div>
      </div>
    );
  }

  const totalTasks = analysis.tasks.length;
  const completedTasks = analysis.tasks.filter((t) => t.status === "done").length;
  const taskRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="p-8">
      <PageHeader
        title="Dashboard"
        description={`Project intelligence overview — ${currentProject?.name || projectId}`}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Health Score"
          value={`${taskRate}%`}
          description="Based on task completion"
          trend={taskRate > 70 ? "up" : taskRate > 30 ? "neutral" : "down"}
        />
        <MetricCard
          title="Active Tasks"
          value={totalTasks - completedTasks}
          description={`${completedTasks} completed`}
          trend="neutral"
        />
        <MetricCard
          title="Entities"
          value={analysis.entities.length}
          description="People, tech, resources"
        />
        <MetricCard
          title="Decisions"
          value={analysis.decisions?.length || 0}
          description="Key project decisions"
        />
      </div>

      {/* AI Insights */}
      <div className="mb-6">
        <h2 className="text-lg font-medium text-ink mb-4">AI Insights</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <AICard
            title="Executive Summary"
            description={analysis.summary}
            confidence={0.95}
          />
          <AICard
            title="Delivery Risk"
            description={`Risk level: ${analysis.sentiment?.delivery_risk || "unknown"}`}
            confidence={analysis.sentiment ? 0.85 : 0}
            sources={analysis.entities.length}
          />
        </div>
      </div>

      {/* Recent Imports */}
      <div className="mb-6">
        <h2 className="text-lg font-medium text-ink mb-4">Recent Imports</h2>
        <div className="bg-surface rounded-lg border border-border">
          {recentImports.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-inkMuted text-sm">No imports yet.</p>
              <Link
                href={`/workspace/${projectId}`}
                className="text-signal text-sm hover:underline mt-2 inline-block"
              >
                Import data
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {recentImports.map((job) => (
                <div key={job.id} className="p-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-ink">{job.source_type}</div>
                    {job.original_filename && (
                      <div className="text-xs text-inkMuted">{job.original_filename}</div>
                    )}
                    <div className="text-xs text-inkMuted/60 mt-0.5">
                      {job.document_count} documents
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        job.status === "completed"
                          ? "bg-green-900/30 text-green-300"
                          : job.status === "failed"
                          ? "bg-red-900/30 text-red-300"
                          : job.status === "processing"
                          ? "bg-yellow-900/30 text-yellow-300"
                          : "bg-gray-900/30 text-gray-300"
                      }`}
                    >
                      {job.status}
                    </span>
                    <span className="text-xs text-inkMuted/60">
                      {new Date(job.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickActionCard
          title="Chat with AI"
          description="Ask questions about your project"
          href="/chat"
          icon="💬"
        />
        <QuickActionCard
          title="View Knowledge Graph"
          description="Explore entity relationships"
          href="/graph"
          icon="🕸️"
        />
        <QuickActionCard
          title="Generate Reports"
          description="Export project insights"
          href="/reports"
          icon="📊"
        />
      </div>
    </div>
  );
}

function QuickActionCard({
  title,
  description,
  href,
  icon,
}: {
  title: string;
  description: string;
  href: string;
  icon: string;
}) {
  return (
    <Link
      href={href}
      className="bg-surface rounded-lg p-5 border border-border hover:border-signal transition block"
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-medium text-ink">{title}</h3>
          <p className="text-sm text-inkMuted mt-1">{description}</p>
        </div>
      </div>
    </Link>
  );
}
