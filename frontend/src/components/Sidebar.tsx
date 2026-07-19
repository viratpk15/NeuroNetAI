"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const SECTIONS = [
  { href: "/", label: "Dashboard", icon: "🏠" },
  { href: "/projects", label: "Projects", icon: "📁" },
  { href: "/workspace/demo-project", label: "Workspace", icon: "🤖" },
  { href: "/chat", label: "Chat", icon: "💬", disabled: true },
  { href: "/graph", label: "Knowledge Graph", icon: "🌐", disabled: true },
  { href: "/analytics", label: "Analytics", icon: "📊", disabled: true },
  { href: "/reports", label: "Reports", icon: "📄", disabled: true },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-surface flex flex-col">
      {/* Header */}
      <div className="px-4 py-5 border-b border-border">
        <span className="font-display font-semibold tracking-tight text-ink text-lg">NeuroNet</span>
        <span className="font-mono text-xs text-signal ml-1.5">AI</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 flex flex-col gap-1">
        {SECTIONS.map((s) => {
          const isActive = !s.disabled && (pathname === s.href || pathname.startsWith(s.href));
          return (
            <Link
              key={s.href}
              href={s.disabled ? "#" : s.href}
              className={`flex items-center gap-3 px-3 py-2 rounded text-sm font-body transition-colors ${
                s.disabled
                  ? "text-inkMuted/50 cursor-not-allowed"
                  : isActive
                  ? "bg-surfaceRaised text-ink"
                  : "text-inkMuted hover:text-ink hover:bg-surfaceRaised"
              }`}
            >
              <span className="text-base">{s.icon}</span>
              <span>{s.label}</span>
              {s.disabled && <span className="ml-auto text-[10px] uppercase tracking-wide text-inkMuted/30">Phase 2</span>}
            </Link>
          );
        })}
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