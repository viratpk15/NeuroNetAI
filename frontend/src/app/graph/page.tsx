"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis, Entity } from "@/lib/api";
import { ErrorState } from "@/components/ErrorState";

export default function GraphPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

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
    return (
      <div className="p-6 lg:p-8">
        <div className="animate-pulse">
          <div className="h-8 w-48 bg-surfaceRaised rounded mb-4" />
        </div>
        <div className="bg-surface rounded-lg p-8 border border-border animate-pulse">
          <div className="h-64 bg-surfaceRaised rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 lg:p-8 max-w-6xl">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">Knowledge Graph</h1>
        <ErrorState title="Failed to load graph" message={error} />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-6 lg:p-8 max-w-6xl">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">Knowledge Graph</h1>
        <GraphPlaceholder />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 flex gap-6">
      <div className="flex-1">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">Knowledge Graph</h1>
        <GraphView entities={analysis.entities} tasks={analysis.tasks} onSelect={setSelectedNode} />
      </div>
      
      {selectedNode && <ContextPanel nodeId={selectedNode} analysis={analysis} />}
    </div>
  );
}

function GraphPlaceholder() {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <svg className="w-16 h-16 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0h6m-6 0V7m6 4v5m-6 0h6" />
      </svg>
      <h3 className="text-lg font-medium text-ink mb-2">Knowledge graph will appear after analysis</h3>
      <p className="text-sm text-inkMuted mb-4">
        Run AI analysis to extract entities and relationships from your project communications.
      </p>
      <Link href="/workspace/demo-project" className="inline-block bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition">
        Run Analysis
      </Link>
    </div>
  );
}

interface GraphViewProps {
  entities: Entity[];
  tasks: Array<{ id: string; title: string; assignee: string | null }>;
  onSelect: (id: string | null) => void;
}

function GraphView({ entities, tasks, onSelect }: GraphViewProps) {
  const nodeTypes = {
    person: entities.filter(e => e.entity_type === "person"),
    technology: entities.filter(e => e.entity_type === "technology"),
    task: tasks.map(t => ({ name: t.title, id: t.id })),
  };

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase">People</h3>
          <div className="space-y-1">
            {nodeTypes.person.length === 0 ? (
              <p className="text-inkMuted/60 text-xs">No people detected</p>
            ) : (
              nodeTypes.person.map(e => (
                <button
                  key={e.id}
                  onClick={() => onSelect(e.id)}
                  className="block text-sm text-purple-300 hover:underline text-left"
                >
                  {e.name}
                </button>
              ))
            )}
          </div>
        </div>

        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase">Technologies</h3>
          <div className="space-y-1">
            {nodeTypes.technology.length === 0 ? (
              <p className="text-inkMuted/60 text-xs">No technologies detected</p>
            ) : (
              nodeTypes.technology.map(e => (
                <button
                  key={e.id}
                  onClick={() => onSelect(e.id)}
                  className="block text-sm text-cyan-300 hover:underline text-left"
                >
                  {e.name}
                </button>
              ))
            )}
          </div>
        </div>

        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase">Tasks</h3>
          <div className="space-y-1">
            {nodeTypes.task.length === 0 ? (
              <p className="text-inkMuted/60 text-xs">No tasks detected</p>
            ) : (
              nodeTypes.task.slice(0, 5).map(t => (
                <button
                  key={t.id}
                  onClick={() => onSelect(t.id)}
                  className="block text-sm text-blue-300 hover:underline truncate text-left"
                >
                  {t.name}
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ContextPanel({ nodeId, analysis }: { nodeId: string; analysis: Analysis }) {
  const entity = analysis.entities.find(e => e.id === nodeId);
  const task = analysis.tasks.find(t => t.id === nodeId);

  if (!entity && !task) return null;

  const name = entity?.name || task?.title || "Unknown";
  const context = entity?.context || task?.description || "Related to project discussions";

  return (
    <div className="w-80 bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-3">Context</h2>
      <div className="space-y-3 text-sm">
        <p className="text-inkMuted">{name}</p>
        <p className="text-inkMuted/70">{context}</p>
      </div>
    </div>
  );
}