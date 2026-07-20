"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Project } from "@/lib/api";

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projects: [],
      currentProject: null,
      setProjects: (projects) => set({ projects }),
      setCurrentProject: (project) => set({ currentProject: project }),
      addProject: (project) => {
        const existing = get().projects.find((p) => p.id === project.id);
        if (!existing) {
          set({ projects: [...get().projects, project] });
        }
      },
    }),
    {
      name: "neuronet-projects",
      partialize: (state) => ({
        projects: state.projects,
        currentProject: state.currentProject,
      }),
    }
  )
);