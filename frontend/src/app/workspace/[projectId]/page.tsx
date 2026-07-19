"use client";

import { useEffect, useState, useCallback } from "react";
import { api, Analysis, Entity } from "@/lib/api";
import { ErrorState } from "@/components/ErrorState";

interface WorkspacePageProps {
  params: Promise<{ projectId: string }>;
}

export default function WorkspacePage({ params }: WorkspacePageProps) {
  const [projectId, setProjectId] = useState<string>("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ projectId: pid }) => setProjectId(pid));
  }, [params]);

  const loadAnalysis = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAnalysis(projectId);
      setAnalysis(data);
    } catch (e) {
      const err = e as Error & { status?: number; isNetworkError?: boolean };
      if (err.status === 404) {
        setError("Project not found. Please check the project ID.");
      } else if (err.isNetworkError) {
        setError("Unable to connect to backend. Please ensure the backend is running.");
      } else {
        setError(err.message || "Failed to load analysis");
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadAnalysis();
  }, [loadAnalysis]);

  const runAnalysis = useCallback(async () => {
    setRunning(true);
    setError(null);
    try {
      const data = await api.runAnalysis(projectId);
      setAnalysis(data);
    } catch (e) {
      const err = e as Error & { status?: number; isNetworkError?: boolean };
      if (err.status === 404) {
        setError("No project data found. Import communications first.");
      } else if (err.isNetworkError) {
        setError("Unable to connect to backend. Please ensure the backend is running.");
      } else {
        setError(err.message || "Failed to run analysis");
      }
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

  if (error && !analysis) {
    return (
      <div className="p-6 lg:p-8 max-w-6xl">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">Workspace</h1>
        <ErrorState title="Failed to load workspace" message={error} onRetry={loadAnalysis} />
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

      {error && <div className="bg-risk/10 border border-risk rounded p-3 mb-4 text-sm text-risk">{error}</div>}

      {!analysis ? (
        <WorkspaceEmptyState onRun={runAnalysis} running={running} />
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

function WorkspaceEmptyState({ onRun, running }: { onRun: () => void; running: boolean }) {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <svg className="w-16 h-16 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m3-2v2m3-2v2M9 21h6m-6 0a3 3 0 006 0H9z" />
      </svg>
      <h2 className="text-xl font-medium text-ink mb-2">No analysis available</h2>
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

function SummaryCard({ analysis }: { analysis: Analysis }) {
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

interface SentimentCardProps {
  sentiment: { overall_sentiment: string; positivity_score: number; stress_score: number; confidence_score: number };
}

function SentimentCard({ sentiment }: SentimentCardProps) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Sentiment</h2>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-inkMuted">Overall</span>
          <span className="text-signal">{sentiment.overall_sentiment}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-inkMuted">Positivity</span>
          <span className="text-ink">{Math.round(sentiment.positivity_score * 100)}%</span>
        </div>
      </div>
    </div>
  );
}

interface EntityExplorerProps {
  entitiesByType: Record<string, Entity[]>;
  typeLabels: Record<string, string>;
}

function EntityExplorer({ entitiesByType, typeLabels }: EntityExplorerProps) {
  const types = Object.keys(typeLabels).filter(key => entitiesByType[key]?.length > 0);

  if (types.length === 0) {
    return (
      <div className="bg-surface rounded-lg p-6 border border-border">
        <h2 className="text-lg font-medium text-ink mb-3">Entities</h2>
        <p className="text-inkMuted text-sm">No entities extracted</p>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Entity Explorer</h2>
      <div className="space-y-3">
        {types.map(type => (
          <div key={type}>
            <h3 className="text-xs text-inkMuted uppercase">{typeLabels[type]}</h3>
            <div className="flex flex-wrap gap-1 mt-1">
              {entitiesByType[type].map(e => (
                <span key={e.id} className="text-xs bg-cyan-900/30 text-cyan-300 px-2 py-1 rounded">
                  {e.name}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface TaskBoardProps {
  tasksByStatus: { todo: Analysis["tasks"]; in_progress: Analysis["tasks"]; done: Analysis["tasks"] };
}

function TaskBoard({ tasksByStatus }: TaskBoardProps) {
  const { todo, in_progress, done } = tasksByStatus;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Tasks</h2>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">To Do</h3>
          {todo.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : todo.map(t => <div key={t.id} className="text-sm text-ink mb-1">{t.title}</div>)}
        </div>
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">In Progress</h3>
          {in_progress.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : in_progress.map(t => <div key={t.id} className="text-sm text-ink mb-1">{t.title}</div>)}
        </div>
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">Done</h3>
          {done.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : done.map(t => <div key={t.id} className="text-sm text-green-400 mb-1 line-through">{t.title}</div>)}
        </div>
      </div>
    </div>
  );
}

function Timeline({ analysis }: { analysis: Analysis }) {
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Timeline</h2>
      <div className="space-y-2">
        {analysis.decisions.map((d, i) => (
          <div key={i} className="text-sm text-ink">{d}</div>
        ))}
      </div>
    </div>
  );
}