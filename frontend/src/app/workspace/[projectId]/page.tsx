"use client";

import { useEffect, useState, useCallback } from "react";
import { api, Analysis, Entity } from "@/lib/api";
import { SummaryCard } from "@/components/SummaryCard";
import { TaskBoard } from "@/components/TaskBoard";
import { SentimentCard } from "@/components/SentimentCard";
import { EntityExplorer } from "@/components/EntityExplorer";
import { Timeline } from "@/components/Timeline";

interface WorkspacePageProps {
  params: Promise<{ projectId: string }>;
}

export default function WorkspacePage({ params }: WorkspacePageProps) {
  const [projectId, setProjectId] = useState<string>("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    params.then(({ projectId: pid }) => setProjectId(pid));
  }, [params]);

  const loadAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getAnalysis(projectId);
      setAnalysis(data);
    } catch (e) {
      console.error("Failed to load analysis", e);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) {
      loadAnalysis();
    }
  }, [projectId, loadAnalysis]);

  const runAnalysis = useCallback(async () => {
    setRunning(true);
    try {
      const data = await api.runAnalysis(projectId);
      setAnalysis(data);
    } catch (e) {
      console.error("Failed to run analysis", e);
    } finally {
      setRunning(false);
    }
  }, [projectId]);

  const tasksByStatus = {
    todo: analysis?.tasks.filter((t) => t.status === "open") || [],
    in_progress: analysis?.tasks.filter((t) => t.status === "in_progress") || [],
    done: analysis?.tasks.filter((t) => t.status === "done") || [],
  };

  const entitiesByType = analysis?.entities.reduce(
    (acc, entity) => {
      const key = entity.entity_type;
      if (!acc[key]) acc[key] = [];
      acc[key].push(entity);
      return acc;
    },
    {} as Record<string, Entity[]>
  ) || {};

  const entityTypeLabels = {
    person: "People",
    technology: "Technologies",
    api: "APIs",
    library: "Libraries",
    repository: "Repositories",
    framework: "Frameworks",
    deadline: "Deadlines",
    organization: "Organizations",
  };

  if (loading) {
    return (
      <div className="p-8">
        <HeaderSkeleton />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <div className="lg:col-span-2 space-y-6">
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-display font-semibold text-ink">Workspace</h1>
          <p className="text-sm text-inkMuted mt-1 font-mono">Project ID: {projectId}</p>
        </div>
        
        <div className="flex items-center gap-3">
          {analysis && (
            <span className="text-xs text-inkMuted">
              Status: <span className="text-signal">{analysis.status}</span>
            </span>
          )}
          <button
            onClick={runAnalysis}
            disabled={running}
            className="flex items-center gap-2 bg-signal text-canvas font-medium text-sm px-4 py-2 rounded hover:brightness-110 transition disabled:opacity-50"
          >
            {running ? (
              <>
                <Spinner />
                Running...
              </>
            ) : (
              "Refresh Analysis"
            )}
          </button>
        </div>
      </div>

      {!analysis ? (
        <EmptyState onRun={runAnalysis} running={running} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <SummaryCard analysis={analysis} />
            <TaskBoard tasksByStatus={tasksByStatus} />
          </div>

          <div className="space-y-6">
            {analysis.sentiment && <SentimentCard sentiment={analysis.sentiment} />}
            <EntityExplorer entitiesByType={entitiesByType} typeLabels={entityTypeLabels} />
            <Timeline analysis={analysis} />
          </div>
        </div>
      )}
    </div>
  );
}

function HeaderSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 w-48 bg-surfaceRaised rounded mb-2" />
      <div className="h-4 w-32 bg-surfaceRaised rounded" />
    </div>
  );
}

function CardSkeleton() {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border animate-pulse">
      <div className="h-6 w-32 bg-surfaceRaised rounded mb-4" />
      <div className="space-y-3">
        <div className="h-4 w-full bg-surfaceRaised rounded" />
        <div className="h-4 w-5/6 bg-surfaceRaised rounded" />
        <div className="h-4 w-4/6 bg-surfaceRaised rounded" />
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 0 0 12h4zm2 5.291A7.966 7.966 0 014 12H0c1.065.0 2.114.334 2.99.914z" />
    </svg>
  );
}

function EmptyState({ onRun, running }: { onRun: () => void; running: boolean }) {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <h2 className="text-xl font-medium text-ink mb-2">No Analysis Yet</h2>
      <p className="text-inkMuted mb-6">Run AI analysis to extract insights from imported communications.</p>
      <button
        onClick={onRun}
        disabled={running}
        className="bg-signal text-canvas font-medium px-6 py-2 rounded hover:brightness-110 transition disabled:opacity-50"
      >
        {running ? "Running..." : "Run AI Analysis"}
      </button>
    </div>
  );
}