import Link from "next/link";

const SECTIONS = [
  { href: "/", label: "Dashboard" },
  { href: "/projects", label: "Projects" },
  { href: "/chat", label: "Chat", disabled: true },
  { href: "/graph", label: "Knowledge Graph", disabled: true },
  { href: "/analytics", label: "Analytics", disabled: true },
  { href: "/reports", label: "Reports", disabled: true },
];

export function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-border bg-surface p-4 flex flex-col gap-1">
      <div className="px-2 py-3 mb-2">
        <span className="font-display font-semibold tracking-tight text-ink">NeuroNet</span>
        <span className="font-mono text-xs text-signal ml-1">AI</span>
      </div>
      {SECTIONS.map((s) => (
        <Link
          key={s.href}
          href={s.disabled ? "#" : s.href}
          className={`px-3 py-2 rounded text-sm font-body ${
            s.disabled
              ? "text-inkMuted/50 cursor-not-allowed"
              : "text-inkMuted hover:text-ink hover:bg-surfaceRaised transition-colors"
          }`}
        >
          {s.label}
          {s.disabled && <span className="ml-2 text-[10px] uppercase tracking-wide">phase 2</span>}
        </Link>
      ))}
    </aside>
  );
}
