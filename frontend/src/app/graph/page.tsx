"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Analysis, Entity } from "@/lib/api";
import { ErrorState } from "@/components/ErrorState";

const NODE_TYPE_COLORS: Record<string, string> = {
  person: "#a855f7",
  technology: "#06b6d4",
  framework: "#8b5cf6",
  language: "#f59e0b",
  library: "#06b6d4",
  database: "#10b981",
  api: "#84cc16",
  task: "#3b82f6",
  decision: "#ec4899",
};

interface TaskItem {
  id: string;
  title: string;
  entity_type: "task";
}

export default function GraphPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api
      .getAnalysis("demo-project")
      .then((a) => {
        setAnalysis(a);
        const types = [...new Set(a.entities.map((e) => e.entity_type))];
        setFilters(
          types.reduce(
            (acc, t) => ({ ...acc, [t]: true }),
            { person: true, technology: true, task: true },
          ),
        );
      })
      .catch((e) => {
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
    return <GraphSkeleton />;
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
        <GraphEmptyState />
      </div>
    );
  }

  const filteredEntities = analysis.entities.filter((e) => filters[e.entity_type]);

  return (
    <div className="h-screen flex flex-col">
      <header className="border-b border-border p-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-semibold text-ink">Knowledge Graph</h1>
            <p className="text-sm text-inkMuted mt-1">
              Interactive visualization of project entities and relationships
            </p>
          </div>
          <div className="flex items-center gap-2">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search nodes..."
              className="bg-surfaceRaised border border-border rounded px-3 py-1.5 text-sm"
              aria-label="Search graph nodes"
            />
            <span className="text-xs text-inkMuted">
              {filteredEntities.length} entities
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-6">
        {filteredEntities.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <p className="text-inkMuted">No entities to display. Try adjusting filters.</p>
          </div>
        ) : (
          <GraphVisualization entities={filteredEntities} tasks={analysis.tasks} search={search} />
        )}
      </div>

      <footer className="border-t border-border p-4 flex-shrink-0">
        <FilterPanel filters={filters} onChange={setFilters} />
      </footer>
    </div>
  );
}

function GraphVisualization({
  entities,
  tasks,
  search,
}: {
  entities: Entity[];
  tasks: Array<{ id: string; title: string }>;
  search: string;
}) {
  const filteredEntities = search
    ? entities.filter((e) => e.name.toLowerCase().includes(search.toLowerCase()))
    : entities;

  const people = filteredEntities.filter((e) => e.entity_type === "person");
  const tech = filteredEntities.filter((e) =>
    ["technology", "framework", "language", "library", "database", "api"].includes(e.entity_type),
  );
  const taskItems: TaskItem[] = tasks.map((t) => ({ ...t, entity_type: "task" }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
      <NodeColumn type="person" label="People" items={people} />
      <NodeColumn type="technology" label="Technologies" items={tech} />
      <NodeColumn type="task" label="Tasks" items={taskItems} />
    </div>
  );
}

function NodeColumn({
  type,
  label,
  items,
}: {
  type: string;
  label: string;
  items: Entity[] | TaskItem[];
}) {
  if (items.length === 0) {
    return (
      <div className="bg-surface rounded-lg p-4 border border-border">
        <h3 className="text-sm font-medium text-inkMuted uppercase mb-3">{label}</h3>
        <p className="text-xs text-inkMuted/60">No items</p>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-lg p-4 border border-border">
      <h3 className="text-sm font-medium text-inkMuted uppercase mb-3">{label}</h3>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {items.map((item) => {
          const displayName = type === "task" 
            ? (item as TaskItem).title 
            : (item as Entity).name;
          const entityType = type === "task" ? "task" : (item as Entity).entity_type;
          return (
            <div
              key={item.id}
              className="flex items-center gap-2 p-2 rounded hover:bg-surfaceRaised transition cursor-pointer"
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: NODE_TYPE_COLORS[entityType] || "#9ca3af" }}
              />
              <span className="text-sm text-ink truncate" title={displayName}>
                {displayName}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function FilterPanel({
  filters,
  onChange,
}: {
  filters: Record<string, boolean>;
  onChange: (f: Record<string, boolean>) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Node filters">
      {Object.entries(filters).map(([type, checked]) => (
        <label key={type} className="flex items-center gap-1 text-xs">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => onChange({ ...filters, [type]: e.target.checked })}
            className="rounded"
            aria-label={`Filter ${type} nodes`}
          />
          <span className="text-inkMuted capitalize">{type}</span>
        </label>
      ))}
    </div>
  );
}

function GraphSkeleton() {
  return (
    <div className="h-screen flex flex-col animate-pulse">
      <div className="p-4 border-b border-border">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-2" />
        <div className="h-4 w-64 bg-surfaceRaised rounded" />
      </div>
      <div className="flex-1 p-4">
        <div className="grid grid-cols-3 gap-4 h-full">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-surface rounded-lg border border-border" />
          ))}
        </div>
      </div>
    </div>
  );
}

function GraphEmptyState() {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <svg
        className="w-16 h-16 mx-auto mb-4 text-signal"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0h6m-6 0V7m7 4v5m-6 0h6"
        />
      </svg>
      <h3 className="text-lg font-medium text-ink mb-2">Knowledge graph will appear after analysis</h3>
      <p className="text-sm text-inkMuted mb-4">
        Run AI analysis to extract entities and relationships from your project communications.
      </p>
      <Link
        href="/workspace/demo-project"
        className="inline-block bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition"
      >
        Run Analysis
      </Link>
    </div>
  );
}