"use client";

import { useEffect, useState } from "react";
import { api, Project } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      const { items } = await api.listProjects();
      setProjects(items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
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
    try {
      await api.createProject(name, description);
      setName("");
      setDescription("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    }
  }

  async function handleArchive(id: string) {
    await api.archiveProject(id);
    await refresh();
  }

  async function handleDelete(id: string) {
    await api.deleteProject(id);
    await refresh();
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
          className="bg-surfaceRaised border border-border rounded px-3 py-2 text-sm text-ink placeholder:text-inkMuted focus:outline-none focus:ring-1 focus:ring-signal"
        />
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          className="bg-surfaceRaised border border-border rounded px-3 py-2 text-sm text-ink placeholder:text-inkMuted focus:outline-none focus:ring-1 focus:ring-signal"
        />
        <button
          type="submit"
          className="self-start bg-signal text-canvas font-medium text-sm px-4 py-2 rounded hover:brightness-110 transition"
        >
          Create project
        </button>
      </form>

      {error && <div className="text-risk text-sm mb-4">{error}</div>}
      {loading ? (
        <div className="text-inkMuted text-sm">Loading…</div>
      ) : projects.length === 0 ? (
        <div className="text-inkMuted text-sm">No projects yet — create your first one above.</div>
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
