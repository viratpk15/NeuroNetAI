"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProjectStore } from "@/lib/store";

const SECTIONS = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/projects", label: "Projects", icon: "📁" },
  { href: "/chat", label: "Chat", icon: "💬" },
  { href: "/graph", label: "Knowledge Graph", icon: "🕸️" },
  { href: "/reports", label: "Reports", icon: "📊" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { projects, setCurrentProject } = useProjectStore();

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-surface flex flex-col h-screen">
      {/* Header */}
      <div className="px-4 py-5 border-b border-border">
        <span className="font-display font-semibold tracking-tight text-ink text-lg">NeuroNet</span>
        <span className="font-mono text-xs text-signal ml-1.5">AI</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 flex flex-col gap-1 overflow-y-auto">
        {SECTIONS.map((s) => {
          const isActive = pathname === s.href || pathname.startsWith(s.href);
          return (
            <Link
              key={s.href}
              href={s.href}
              className={`flex items-center gap-3 px-3 py-2 rounded text-sm font-body transition-colors ${
                isActive
                  ? "bg-surfaceRaised text-ink"
                  : "text-inkMuted hover:text-ink hover:bg-surfaceRaised"
              }`}
            >
              <span className="text-base">{s.icon}</span>
              <span>{s.label}</span>
            </Link>
          );
        })}

        {/* Project List */}
        {projects.length > 0 && (
          <div className="mt-4">
            <div className="px-3 py-1 text-xs text-inkMuted uppercase tracking-wider">Projects</div>
            <div className="mt-1 flex flex-col gap-1">
              {projects.map((project) => {
                const workspaceHref = `/workspace/${project.id}`;
                const isActive = pathname === workspaceHref || pathname.startsWith(workspaceHref) || pathname.startsWith(`/workspace/${project.id}`);
                return (
                  <Link
                    key={project.id}
                    href={workspaceHref}
                    onClick={() => setCurrentProject(project)}
                    className={`flex items-center gap-3 px-3 py-2 rounded text-sm font-body transition-colors ${
                      isActive
                        ? "bg-surfaceRaised text-ink"
                        : "text-inkMuted hover:text-ink hover:bg-surfaceRaised"
                    }`}
                    title={project.description}
                  >
                    <span className="text-base">📁</span>
                    <div className="flex-1 min-w-0">
                      <div className="truncate">{project.name}</div>
                      <div className="text-[10px] text-inkMuted/60 font-mono truncate">{project.id.substring(0, 8)}...</div>
                    </div>
                    {project.status === "archived" && (
                      <span className="text-[10px] text-inkMuted/60">archived</span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <div className="text-[10px] text-inkMuted font-mono">
          v0.3.1
        </div>
      </div>
    </aside>
  );
}
