"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { MetricCard } from "@/components/MetricCard";
import { AICard } from "@/components/MetricCard";
import { LoadingState } from "@/components/LoadingState";

export default function DashboardPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getAnalysis("demo-project")
      .then(setAnalysis)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-2 animate-pulse" />
        <div className="h-4 w-64 bg-surfaceRaised rounded mb-6 animate-pulse" />
        <LoadingState count={4} />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-8">
        <PageHeader title="Dashboard" description="Project intelligence overview" />
        <div className="text-center py-16">
          <p className="text-inkMuted mb-4">No project analysis available.</p>
          <Link href="/workspace/demo-project" className="text-signal hover:underline">
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
      <PageHeader title="Dashboard" description="Project intelligence overview" />

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