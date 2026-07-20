"use client";

import { useEffect, useState, useCallback } from "react";
import { api, Analysis, Entity, ImportJobStatus } from "@/lib/api";
import { ErrorState } from "@/components/ErrorState";
import { useProjectStore } from "@/lib/store";
import { useToast } from "@/components/ToastProvider";

interface WorkspacePageProps {
  params: Promise<{ projectId: string }>;
}

// Colored badge styles for entity types
const ENTITY_BADGE_COLORS: Record<string, string> = {
  person: "bg-purple-900/30 text-purple-300",
  technology: "bg-cyan-900/30 text-cyan-300",
  api: "bg-lime-900/30 text-lime-300",
  library: "bg-cyan-900/30 text-cyan-300",
  repository: "bg-lime-900/30 text-lime-300",
  framework: "bg-violet-900/30 text-violet-300",
  database: "bg-emerald-900/30 text-emerald-300",
  tool: "bg-amber-900/30 text-amber-300",
  concept: "bg-blue-900/30 text-blue-300",
  programming_language: "bg-amber-900/30 text-amber-300",
  organization: "bg-indigo-900/30 text-indigo-300",
  deadline: "bg-red-900/30 text-red-300",
};

export default function WorkspacePage({ params }: WorkspacePageProps) {
  const { projects } = useProjectStore();
  const [projectId, setProjectId] = useState<string>("");
  const [projectName, setProjectName] = useState<string>("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ projectId: pid }) => {
      setProjectId(pid);
      // Find project name from store or use ID as fallback
      const project = projects.find((p) => p.id === pid);
      setProjectName(project?.name || pid);
    });
  }, [params, projects]);

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
    todo: analysis?.tasks.filter((t) => t.status === "todo") || [],
    in_progress: analysis?.tasks.filter((t) => t.status === "in_progress") || [],
    done: analysis?.tasks.filter((t) => t.status === "done") || [],
    blocked: analysis?.tasks.filter((t) => t.status === "blocked") || [],
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

  const entityTypeLabels: Record<string, string> = {
    person: "People",
    technology: "Technologies",
    api: "APIs",
    library: "Libraries",
    repository: "Repositories",
    framework: "Frameworks",
    database: "Databases",
    tool: "Tools",
    concept: "Concepts",
    programming_language: "Languages",
    organization: "Organizations",
    deadline: "Deadlines",
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
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-display font-semibold text-ink">Workspace</h1>
          <p className="text-sm text-inkMuted mt-1 font-mono">{projectName}</p>
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
        <>
          <ImportPanel projectId={projectId} onImportSuccess={loadAnalysis} />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
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
        </>
      )}
    </div>
  );
}

// Import Panel Component with TXT, Markdown, GitHub Issue, GitHub PR support
interface ImportPanelProps {
  projectId: string;
  onImportSuccess: () => void;
}

function ImportPanel({ projectId, onImportSuccess }: ImportPanelProps) {
  // eslint-disable-next-line @typescript-eslint/no-use-before-define
  const { toast } = useToast();
  const [content, setContent] = useState("");
  const [importing, setImporting] = useState(false);
  const [importType, setImportType] = useState<"txt" | "markdown" | "github-issue" | "github-pr">("txt");
  const [importStatus, setImportStatus] = useState<ImportJobStatus | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const handleImport = async () => {
    if (!content.trim()) return;
    setImporting(true);
    setImportError(null);
    
    try {
      toast({
        title: "Import started",
        description: `Processing ${importType} content...`,
        variant: "default",
      });
      
      let result;
      switch (importType) {
        case "txt":
          result = await api.importTxt(projectId, content);
          break;
        case "markdown":
          result = await api.importMarkdown(projectId, content);
          break;
        case "github-issue":
          result = await api.importGitHubIssue(projectId, content);
          break;
        case "github-pr":
          result = await api.importGitHubPr(projectId, content);
          break;
      }
      setImportStatus(result.job.status);
      setContent("");
      toast({
        title: "Import completed",
        description: `${importType === "github-pr" ? "PR" : importType === "github-issue" ? "Issue" : importType.charAt(0).toUpperCase() + importType.slice(1)} data imported successfully.`,
        variant: "success",
      });
      onImportSuccess();
    } catch (e) {
      const err = e as Error & { status?: number; isNetworkError?: boolean };
      const msg = err.isNetworkError 
        ? "Unable to connect to backend. Please ensure the backend is running."
        : err.message || "Import failed";
      setImportError(msg);
      toast({
        title: "Import failed",
        description: msg,
        variant: "error",
      });
    } finally {
      setImporting(false);
    }
  };

  const placeholderText = {
    txt: "Paste conversation content (e.g., Slack messages, meeting notes)...",
    markdown: "Paste markdown content...",
    "github-issue": 'Paste GitHub issue JSON (e.g., {"title": "...", "body": "..."})...',
    "github-pr": 'Paste GitHub PR JSON (e.g., {"title": "...", "body": "...", "state": "open"})...',
  } as const;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border mb-6">
      <h2 className="text-lg font-medium text-ink mb-4">Import Data</h2>
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setImportType("txt")}
            className={`px-3 py-1 text-sm rounded ${importType === "txt" ? "bg-signal text-canvas" : "bg-surfaceRaised border border-border"}`}
          >
            TXT
          </button>
          <button
            onClick={() => setImportType("markdown")}
            className={`px-3 py-1 text-sm rounded ${importType === "markdown" ? "bg-signal text-canvas" : "bg-surfaceRaised border border-border"}`}
          >
            Markdown
          </button>
          <button
            onClick={() => setImportType("github-issue")}
            className={`px-3 py-1 text-sm rounded ${importType === "github-issue" ? "bg-signal text-canvas" : "bg-surfaceRaised border border-border"}`}
          >
            GitHub Issue
          </button>
          <button
            onClick={() => setImportType("github-pr")}
            className={`px-3 py-1 text-sm rounded ${importType === "github-pr" ? "bg-signal text-canvas" : "bg-surfaceRaised border border-border"}`}
          >
            GitHub PR
          </button>
        </div>
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          placeholder={placeholderText[importType]}
          className="w-full h-32 bg-surfaceRaised border border-border rounded px-3 py-2 text-sm text-ink placeholder:text-inkMuted focus:outline-none focus:ring-1 focus:ring-signal"
          aria-label="Import content"
        />
        {importError && <div className="text-risk text-xs">{importError}</div>}
        {importStatus && (
          <div className="text-xs text-inkMuted">
            Import status: <span className="text-signal">{importStatus}</span>
          </div>
        )}
        <button
          onClick={handleImport}
          disabled={importing || !content.trim()}
          className="self-start bg-signal text-canvas font-medium text-sm px-4 py-2 rounded hover:brightness-110 transition disabled:opacity-50"
        >
          {importing ? "Importing..." : "Import"}
        </button>
      </div>
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
  sentiment: Analysis["sentiment"];
}

function SentimentCard({ sentiment }: SentimentCardProps) {
  if (!sentiment) return null;
  
  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Sentiment</h2>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-inkMuted">Overall</span>
          <span className="text-signal">{sentiment.overall_sentiment}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-inkMuted">Positivity</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-2 bg-surfaceRaised rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-400 transition-all"
                style={{ width: `${Math.round(sentiment.positivity_score * 100)}%` }}
              />
            </div>
            <span className="text-ink w-10 text-right">{Math.round(sentiment.positivity_score * 100)}%</span>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-inkMuted">Stress</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-2 bg-surfaceRaised rounded-full overflow-hidden">
              <div 
                className="h-full bg-risk transition-all"
                style={{ width: `${Math.round(sentiment.stress_score * 100)}%` }}
              />
            </div>
            <span className="text-ink w-10 text-right">{Math.round(sentiment.stress_score * 100)}%</span>
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-inkMuted">Confidence</span>
          <span className="text-ink">{Math.round(sentiment.confidence_score * 100)}%</span>
        </div>
        {sentiment.delivery_risk && (
          <div className="flex justify-between">
            <span className="text-inkMuted">Delivery Risk</span>
            <span className="text-ink">{sentiment.delivery_risk}</span>
          </div>
        )}
        {sentiment.team_morale && (
          <div className="flex justify-between">
            <span className="text-inkMuted">Team Morale</span>
            <span className="text-ink">{sentiment.team_morale}</span>
          </div>
        )}
        {sentiment.burnout_probability !== undefined && (
          <div className="flex justify-between">
            <span className="text-inkMuted">Burnout Risk</span>
            <span className="text-ink">{Math.round(sentiment.burnout_probability * 100)}%</span>
          </div>
        )}
        {sentiment.blockers && sentiment.blockers.length > 0 && (
          <div className="mt-2">
            <h4 className="text-xs text-risk mb-1">Blockers</h4>
            <ul className="space-y-0.5">
              {sentiment.blockers.map((b, i) => (
                <li key={i} className="text-xs text-inkMuted">• {b}</li>
              ))}
            </ul>
          </div>
        )}
        {sentiment.conflicts && sentiment.conflicts.length > 0 && (
          <div className="mt-2">
            <h4 className="text-xs text-risk mb-1">Conflicts</h4>
            <ul className="space-y-0.5">
              {sentiment.conflicts.map((c, i) => (
                <li key={i} className="text-xs text-inkMuted">• {c}</li>
              ))}
            </ul>
          </div>
        )}
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
              {entitiesByType[type].map(e => {
                const badgeClass = ENTITY_BADGE_COLORS[type] || "bg-cyan-900/30 text-cyan-300";
                return (
                  <span key={e.id} className={`text-xs px-2 py-1 rounded ${badgeClass}`}>
                    {e.name}
                  </span>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface TaskBoardProps {
  tasksByStatus: { todo: Analysis["tasks"]; in_progress: Analysis["tasks"]; done: Analysis["tasks"]; blocked: Analysis["tasks"] };
}

function TaskBoard({ tasksByStatus }: TaskBoardProps) {
  const { todo, in_progress, done, blocked } = tasksByStatus;

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">Tasks</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">To Do</h3>
          {todo.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : todo.map(t => (
            <div key={t.id} className="text-sm mb-2">
              <div className="text-ink">{t.title}</div>
              {t.assignee && <div className="text-inkMuted/60 text-xs">@{t.assignee}</div>}
              {t.due_date && <div className="text-signal/80 text-xs">Due: {t.due_date}</div>}
            </div>
          ))}
        </div>
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">In Progress</h3>
          {in_progress.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : in_progress.map(t => (
            <div key={t.id} className="text-sm mb-2">
              <div className="text-ink">{t.title}</div>
              {t.assignee && <div className="text-inkMuted/60 text-xs">@{t.assignee}</div>}
              {t.due_date && <div className="text-signal/80 text-xs">Due: {t.due_date}</div>}
            </div>
          ))}
        </div>
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">Done</h3>
          {done.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : done.map(t => (
            <div key={t.id} className="text-sm mb-2">
              <div className="text-green-400 line-through">{t.title}</div>
              {t.assignee && <div className="text-inkMuted/60 text-xs">@{t.assignee}</div>}
            </div>
          ))}
        </div>
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-2 uppercase">Blocked</h3>
          {blocked.length === 0 ? <p className="text-inkMuted/60 text-xs">None</p> : blocked.map(t => (
            <div key={t.id} className="text-sm mb-2">
              <div className="text-risk">{t.title}</div>
              {t.assignee && <div className="text-inkMuted/60 text-xs">@{t.assignee}</div>}
            </div>
          ))}
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