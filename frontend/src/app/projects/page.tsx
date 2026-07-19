"use client";

import { useEffect, useState } from "react";
import { api, Project } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const { items } = await api.listProjects();
      setProjects(items);
    } catch (err) {
      const e = err as Error & { status?: number; isNetworkError?: boolean };
      if (e.isNetworkError) {
        setError("Unable to connect to backend. Please ensure the backend is running.");
      } else {
        setError(e.message || "Failed to load projects");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await api.createProject(name, description);
      setName("");
      setDescription("");
      await refresh();
    } catch (err) {
      const e = err as Error & { status?: number; isNetworkError?: boolean };
      setError(e.isNetworkError 
        ? "Unable to connect to backend. Please ensure the backend is running."
        : e.message || "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleArchive(id: string) {
    try {
      await api.archiveProject(id);
      await refresh();
    } catch (err) {
      const e = err as Error & { status?: number; isNetworkError?: boolean };
      setError(e.isNetworkError 
        ? "Unable to connect to backend. Please ensure the backend is running."
        : e.message || "Failed to archive project");
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.deleteProject(id);
      await refresh();
    } catch (err) {
      const e = err as Error & { status?: number; isNetworkError?: boolean };
      setError(e.isNetworkError 
        ? "Unable to connect to backend. Please ensure the backend is running."
        : e.message || "Failed to delete project");
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl">
        <div className="animate-pulse">
          <div className="h-8 w-32 bg-surfaceRaised rounded mb-1" />
          <div className="h-4 w-48 bg-surfaceRaised rounded mb-8" />
        </div>
        <div className="bg-surface rounded-lg p-6 border border-border animate-pulse mb-8">
          <div className="h-10 bg-surfaceRaised rounded mb-3" />
          <div className="h-10 bg-surfaceRaised rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-2xl text-ink mb-1">Projects</h1>
      <p className="text-inkMuted text-sm mb-8">
        Each project holds its own imported data, chats, and analysis.
      </p>

      <form onSubmit={handleCreate} className="rounded border border-border bg-surface p-5 mb-8 flex flex-col gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          disabled={submitting}
          className="bg-surfaceRaised border border-border rounded px-3 py-2 text-sm text-ink placeholder:text-inkMuted focus:outline-none focus:ring-1 focus:ring-signal disabled:opacity-50"
        />
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          disabled={submitting}
          className="bg-surfaceRaised border border-border rounded px-3 py-2 text-sm text-ink placeholder:text-inkMuted focus:outline-none focus:ring-1 focus:ring-signal disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={submitting || !name.trim()}
          className="self-start bg-signal text-canvas font-medium text-sm px-4 py-2 rounded hover:brightness-110 transition disabled:opacity-50"
        >
          {submitting ? "Creating..." : "Create project"}
        </button>
      </form>

      {error && <div className="text-risk text-sm mb-4">{error}</div>}
      
      {projects.length === 0 ? (
        <ProjectsEmptyState />
      ) : (
        <ul className="flex flex-col gap-2">
          {projects.map((p) => (
            <li
              key={p.id}
              className="rounded border border-border bg-surface p-4 flex items-center justify-between"
            >
              <div>
                <div className="text-ink text-sm font-medium">{p.name}</div>
                {p.description && <div className="text-inkMuted text-xs mt-0.5">{p.description}</div>}
                <div className="text-inkMuted/60 text-[11px] mt-1 font-mono uppercase">{p.status}</div>
              </div>
              <div className="flex gap-2">
                {p.status === "active" && (
                  <button
                    onClick={() => handleArchive(p.id)}
                    className="text-xs text-inkMuted hover:text-ink px-2 py-1 rounded border border-border"
                  >
                    Archive
                  </button>
                )}
                <button
                  onClick={() => handleDelete(p.id)}
                  className="text-xs text-risk hover:brightness-110 px-2 py-1 rounded border border-risk/40"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ProjectsEmptyState() {
  return (
    <div className="bg-surface rounded-lg p-12 border border-border text-center">
      <svg className="w-16 h-16 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0l-4-4m4 4l-4 4M5 11l4-4-4-4-4 4z" />
      </svg>
      <h3 className="text-lg font-medium text-ink mb-2">No projects yet</h3>
      <p className="text-sm text-inkMuted">Create your first project above to get started.</p>
    </div>
  );
}