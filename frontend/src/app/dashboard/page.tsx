"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis, Project } from "@/lib/api";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const { items } = await api.listProjects();
      setProjects(items);

      const analysisData: Record<string, Analysis> = {};
      for (const project of items.filter(p => p.status === "active")) {
        try {
          const analysis = await api.getAnalysis(project.id);
          if (analysis) analysisData[project.id] = analysis;
        } catch {
          // Analysis may not exist yet
        }
      }
      setAnalyses(analysisData);
    } catch (e) {
      const err = e as Error & { status?: number; isNetworkError?: boolean };
      if (err.isNetworkError) {
        setError("Unable to connect to backend. Please ensure the backend is running.");
      } else {
        setError(err.message || "Failed to load dashboard");
      }
    } finally {
      setLoading(false);
    }
  };

  // Calculate analytics only when we have data
  const hasProjects = projects.length > 0;
  const hasAnalyses = Object.keys(analyses).length > 0;
  const totalTasks = Object.values(analyses).reduce((acc, a) => acc + a.tasks.length, 0);
  const completedTasks = Object.values(analyses).reduce((acc, a) => acc + a.tasks.filter(t => t.status === "done").length, 0);
  const pendingTasks = totalTasks - completedTasks;

  const techCounts = Object.values(analyses).flatMap(a => a.entities.filter(e => e.entity_type === "technology"));
  const techAnalytics = techCounts.reduce((acc, e) => {
    acc[e.name] = (acc[e.name] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const sortedTech = Object.entries(techAnalytics).sort((a, b) => b[1] - a[1]).slice(0, 5);

  if (loading) {
    return <LoadingState count={6} />;
  }

  if (error) {
    return (
      <div className="p-6 lg:p-8 max-w-6xl">
        <ErrorState title="Failed to load dashboard" message={error} onRetry={loadDashboard} />
      </div>
    );
  }

  // Show onboarding when no data exists
  if (!hasProjects || !hasAnalyses) {
    return (
      <div className="p-6 lg:p-8 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-display font-semibold text-ink">Intelligence Dashboard</h1>
          <p className="text-sm text-inkMuted mt-1">AI-powered insights across all projects</p>
        </div>

        <div className="space-y-4">
          {!hasProjects ? (
            <OnboardingStep
              step={1}
              title="Create a Project"
              description="Projects organize your imported data, analysis, and reports."
              actionLabel="Go to Projects"
              href="/projects"
            />
          ) : (
            <OnboardingStep
              step={2}
              title="Import Conversations"
              description="Import your team communications to analyze decisions, tasks, and insights."
              actionLabel="Import Data"
              href="/workspace/demo-project"
            />
          )}

          {hasProjects && !hasAnalyses && (
            <OnboardingStep
              step={3}
              title="Run AI Analysis"
              description="Analyze imported communications to extract decisions, tasks, and insights."
              actionLabel="Run Analysis"
              href="/workspace/demo-project"
            />
          )}

          {hasAnalyses && (
            <OnboardingStep
              step={4}
              title="View Insights"
              description="Explore your intelligence dashboard for project metrics and trends."
              actionLabel="View Dashboard"
              href="/dashboard"
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold text-ink">Intelligence Dashboard</h1>
        <p className="text-sm text-inkMuted mt-1">AI-powered insights across all projects</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <HealthScore analyses={analyses} />
        <TaskAnalytics total={totalTasks} completed={completedTasks} pending={pendingTasks} />
        <RiskDetection analyses={analyses} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <SentimentAnalytics analyses={analyses} />
        <TechnologyAnalytics tech={sortedTech} />
      </div>

      <ContributorAnalytics analyses={analyses} />
      <ActivityTimeline projects={projects} analyses={analyses} />
    </div>
  );
}

interface OnboardingStepProps {
  step: number;
  title: string;
  description: string;
  actionLabel: string;
  href: string;
}

function OnboardingStep({ step, title, description, actionLabel, href }: OnboardingStepProps) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border flex items-start gap-4">
      <div className="flex-shrink-0 w-10 h-10 bg-signal rounded-full flex items-center justify-center font-semibold text-canvas">
        {step}
      </div>
      <div className="flex-1">
        <h3 className="text-lg font-medium text-ink mb-1">{title}</h3>
        <p className="text-sm text-inkMuted mb-3">{description}</p>
        <Link href={href} className="inline-block bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition">
          {actionLabel}
        </Link>
      </div>
    </div>
  );
}

function HealthScore({ analyses }: { analyses: Record<string, Analysis> }) {
  const analysisList = Object.values(analyses);
  const avgScore = analysisList.length > 0
    ? analysisList.reduce((s, a) => s + (a.sentiment?.positivity_score || 0), 0) / analysisList.length
    : 0;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Project Health Score</h2>
      <div className="flex items-end gap-3">
        <span className="text-3xl font-display font-semibold text-ink">{Math.round(avgScore * 100)}</span>
        <span className="text-inkMuted text-sm mb-1">/ 100</span>
      </div>
      <div className="w-full bg-surfaceRaised rounded-full h-2 mt-2">
        <div className="bg-signal h-2 rounded-full" style={{ width: `${avgScore * 100}%` }} />
      </div>
    </div>
  );
}

function TaskAnalytics({ total, completed, pending }: { total: number; completed: number; pending: number }) {
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

function RiskDetection({ analyses }: { analyses: Record<string, Analysis> }) {
  const risks = Object.values(analyses).flatMap(a => 
    a.tasks.filter(t => t.priority === "high" && t.status !== "done")
  );

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Risk Detection</h2>
      {risks.length === 0 ? (
        <p className="text-inkMuted text-sm">No risks identified</p>
      ) : (
        <ul className="space-y-1">
          {risks.slice(0, 3).map((task) => (
            <li key={task.id} className="text-sm text-risk flex items-start gap-2">
              ⚠️ {task.title}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SentimentAnalytics({ analyses }: { analyses: Record<string, Analysis> }) {
  const sentiment = Object.values(analyses).find(a => a.sentiment)?.sentiment;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Sentiment Analysis</h2>
      {sentiment ? (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-inkMuted">Overall</span>
            <span className="text-signal">{sentiment.overall_sentiment}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-inkMuted">Positivity</span>
            <span className="text-ink">{Math.round(sentiment.positivity_score * 100)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-inkMuted">Confidence</span>
            <span className="text-ink">{Math.round(sentiment.confidence_score * 100)}%</span>
          </div>
        </div>
      ) : (
        <p className="text-inkMuted text-sm">No sentiment data</p>
      )}
    </div>
  );
}

function TechnologyAnalytics({ tech }: { tech: Array<[string, number]> }) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Technology Analytics</h2>
      {tech.length === 0 ? (
        <p className="text-inkMuted text-sm">No technologies detected</p>
      ) : (
        <div className="space-y-2">
          {tech.map(([name, count]) => (
            <div key={name} className="flex justify-between text-sm">
              <span className="text-cyan-300">{name}</span>
              <span className="text-inkMuted">{count} mentions</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ContributorAnalytics({ analyses }: { analyses: Record<string, Analysis> }) {
  const contributors = Object.values(analyses).flatMap(a => 
    a.entities.filter(e => e.entity_type === "person")
  ).reduce((acc, e) => {
    acc[e.name] = (acc[e.name] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const topContributors = Object.entries(contributors).sort((a, b) => b[1] - a[1]).slice(0, 5);

  return (
    <div className="bg-surface rounded-lg p-6 border border-border mb-6">
      <h2 className="text-lg font-medium text-ink mb-3">Top Contributors</h2>
      {topContributors.length === 0 ? (
        <p className="text-inkMuted text-sm">No contributors detected</p>
      ) : (
        <div className="space-y-2">
          {topContributors.map(([name, count]) => (
            <div key={name} className="flex justify-between text-sm">
              <span className="text-ink">@{name}</span>
              <span className="text-inkMuted">{count} mentions</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ActivityTimeline({ projects, analyses }: { projects: Project[]; analyses: Record<string, Analysis> }) {
  const events = [
    ...projects.map(p => ({ type: "project" as const, label: `Project created: ${p.name}`, time: p.created_at })),
    ...Object.entries(analyses).map(([, a]) => ({ type: "analysis" as const, label: "Analysis completed", time: a.agent_run_id })),
  ].sort((a, b) => a.time.localeCompare(b.time));

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Activity Timeline</h2>
      {events.length === 0 ? (
        <p className="text-inkMuted text-sm">No activity yet</p>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {events.slice(0, 10).map((event, idx) => (
            <div key={`${event.type}-${idx}`} className="flex items-center gap-2 text-sm">
              <span className="text-signal">•</span>
              <span className="text-inkMuted">{event.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}