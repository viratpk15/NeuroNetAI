"use client";

import { useEffect, useState } from "react";
import { api, Analysis, Project } from "@/lib/api";
import { HealthScore } from "@/components/HealthScore";
import { TaskAnalytics } from "@/components/TaskAnalytics";
import { RiskDetection } from "@/components/RiskDetection";
import { SentimentAnalytics } from "@/components/SentimentAnalytics";
import { TechnologyAnalytics } from "@/components/TechnologyAnalytics";
import { ContributorAnalytics } from "@/components/ContributorAnalytics";
import { ActivityTimeline } from "@/components/ActivityTimeline";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const { items } = await api.listProjects();
      setProjects(items);

      const analysisData: Record<string, Analysis> = {};
      for (const project of items.filter(p => p.status === "active")) {
        try {
          const analysis = await api.getAnalysis(project.id);
          if (analysis) analysisData[project.id] = analysis;
        } catch {
          // Analysis may not exist yet
        }
      }
      setAnalyses(analysisData);
    } catch (e) {
      console.error("Failed to load dashboard", e);
    } finally {
      setLoading(false);
    }
  };

  const totalTasks = Object.values(analyses).reduce((acc, a) => acc + a.tasks.length, 0);
  const completedTasks = Object.values(analyses).reduce((acc, a) => acc + a.tasks.filter(t => t.status === "done").length, 0);
  const pendingTasks = totalTasks - completedTasks;

  const techCounts = Object.values(analyses).flatMap(a => a.entities.filter(e => e.entity_type === "technology"));
  const techAnalytics = techCounts.reduce((acc, e) => {
    acc[e.name] = (acc[e.name] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const sortedTech = Object.entries(techAnalytics).sort((a, b) => b[1] - a[1]).slice(0, 5);

  if (loading) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-2 animate-pulse" />
        <div className="h-4 w-32 bg-surfaceRaised rounded animate-pulse mb-6" />
        <DashboardSkeleton />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold text-ink">Intelligence Dashboard</h1>
        <p className="text-sm text-inkMuted mt-1">AI-powered insights across all projects</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <HealthScore analyses={analyses} />
        <TaskAnalytics total={totalTasks} completed={completedTasks} pending={pendingTasks} />
        <RiskDetection analyses={analyses} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <SentimentAnalytics analyses={analyses} />
        <TechnologyAnalytics tech={sortedTech} />
      </div>

      <ContributorAnalytics analyses={analyses} />
      <ActivityTimeline projects={projects} analyses={analyses} />
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3, 4, 5, 6].map(i => (
        <div key={i} className="bg-surface rounded-lg p-6 border border-border animate-pulse">
          <div className="h-5 w-24 bg-surfaceRaised rounded mb-3" />
          <div className="h-8 w-16 bg-surfaceRaised rounded" />
        </div>
      ))}
    </div>
  );
}