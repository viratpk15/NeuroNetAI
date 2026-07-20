export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type ProjectStatus = "active" | "archived";
export type TaskStatus = "todo" | "in_progress" | "done" | "blocked";
export type EntityType = "person" | "technology" | "framework" | "database" | "programming_language" | "tool" | "organization" | "concept" | "api" | "library" | "repository" | "deadline";
export type ImportJobStatus = "pending" | "processing" | "completed" | "failed";

export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

interface ProjectListResponse {
  items: Project[];
  limit: number;
  offset: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  assignee: string | null;
  priority: string;
  status: TaskStatus;
  due_date: string | null;
}

export interface Sentiment {
  overall_sentiment: string;
  positivity_score: number;
  stress_score: number;
  confidence_score: number;
  delivery_risk?: string;
  team_morale?: string;
  burnout_probability?: number;
  blockers?: string[];
  conflicts?: string[];
}

export interface Entity {
  id: string;
  entity_type: string;
  name: string;
  context: string;
  confidence: number;
}

interface ImportJob {
  id: string;
  project_id: string;
  source_type: string;
  original_filename: string | null;
  status: ImportJobStatus;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  document_count: number;
}

export interface Analysis {
  agent_run_id: string;
  status: string;
  summary: string;
  topics: string[];
  decisions: string[];
  tasks: Task[];
  sentiment: Sentiment | null;
  entities: Entity[];
}

interface ApiError extends Error {
  status?: number;
  isNetworkError?: boolean;
}

function createApiError(message: string, status?: number, isNetworkError?: boolean): ApiError {
  const error = new Error(message) as ApiError;
  error.status = status;
  error.isNetworkError = isNetworkError;
  return error;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store",
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw createApiError(body.detail ?? `Request failed with status ${res.status}`, res.status);
    }
    if (res.status === 204) return undefined as T;
    return res.json() as Promise<T>;
  } catch (err) {
    // Handle network errors (backend offline, CORS issues, etc.)
    if (err instanceof Error && !err.message.includes("status")) {
      throw createApiError(err.message, undefined, true);
    }
    throw err;
  }
}

export const api = {
  // Projects
  listProjects: () => request<ProjectListResponse>("/projects"),
  createProject: (name: string, description: string) =>
    request<Project>("/projects", { method: "POST", body: JSON.stringify({ name, description }) }),
  archiveProject: (id: string) => request<Project>(`/projects/${id}/archive`, { method: "POST" }),
  deleteProject: (id: string) => request<void>(`/projects/${id}`, { method: "DELETE" }),
  renameProject: (id: string, name: string) =>
    request<Project>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify({ name }) }),

  // Imports
  importTxt: (projectId: string, content: string, originalFilename?: string) =>
    request<{ job: ImportJob; event_count: number }>(`/imports/txt`, {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, content, original_filename: originalFilename }),
    }),
  importMarkdown: (projectId: string, content: string, originalFilename?: string) =>
    request<{ job: ImportJob; event_count: number }>(`/imports/markdown`, {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, content, original_filename: originalFilename }),
    }),
  importGitHubIssue: (projectId: string, content: string) =>
    request<{ job: ImportJob; event_count: number }>(`/imports/github-issue`, {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, content }),
    }),
  importGitHubPr: (projectId: string, content: string) =>
    request<{ job: ImportJob; event_count: number }>(`/imports/github-pr`, {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, content }),
    }),
  listImports: (limit = 50, offset = 0) =>
    request<{ items: ImportJob[]; limit: number; offset: number }>(`/imports?limit=${limit}&offset=${offset}`),

  // Analysis
  getAnalysis: (projectId: string) => request<Analysis>(`/analysis/${projectId}`),
  runAnalysis: (projectId: string) => request<Analysis>(`/analysis/${projectId}`, { method: "POST" }),
  getTasks: (projectId: string, limit = 100, offset = 0) =>
    request<{ items: Task[]; limit: number; offset: number }>(`/analysis/${projectId}/tasks?limit=${limit}&offset=${offset}`),
  getSentiment: (projectId: string) =>
    request<Sentiment>(`/analysis/${projectId}/sentiment`),
  getEntities: (projectId: string, limit = 100, offset = 0) =>
    request<{ items: Entity[]; limit: number; offset: number }>(`/analysis/${projectId}/entities?limit=${limit}&offset=${offset}`),

};
