"use client";

import { useEffect, useState } from "react";
import { api, Analysis, Entity } from "@/lib/api";

export default function GraphPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    api.getAnalysis("demo-project")
      .then(setAnalysis)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-6 animate-pulse" />
        <GraphSkeleton />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-display font-semibold text-ink mb-4">Knowledge Graph</h1>
        <p className="text-inkMuted">No analysis data available. Run AI analysis first.</p>
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

function GraphSkeleton() {
  return (
    <div className="bg-surface rounded-lg p-8 border border-border animate-pulse">
      <div className="h-64 bg-surfaceRaised rounded" />
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
            {nodeTypes.person.map(e => (
              <button
                key={e.id}
                onClick={() => onSelect(e.id)}
                className="block text-sm text-purple-300 hover:underline"
              >
                {e.name}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase">Technologies</h3>
          <div className="space-y-1">
            {nodeTypes.technology.map(e => (
              <button
                key={e.id}
                onClick={() => onSelect(e.id)}
                className="block text-sm text-cyan-300 hover:underline"
              >
                {e.name}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase">Tasks</h3>
          <div className="space-y-1">
            {nodeTypes.task.slice(0, 5).map(t => (
              <button
                key={t.id}
                onClick={() => onSelect(t.id)}
                className="block text-sm text-blue-300 hover:underline truncate"
              >
                {t.name}
              </button>
            ))}
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
