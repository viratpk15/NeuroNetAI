"use client";

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: "project" | "analysis" | "report" | "chat" | "graph" | "data";
}

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon = "data",
}: EmptyStateProps) {
  const icons = {
    project: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0l-4-4m4 4l-4 4M5 11l4-4-4-4-4 4z" />
      </svg>
    ),
    analysis: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m3-2v2m3-2v2M9 21h6m-6 0a3 3 0 006 0H9z" />
      </svg>
    ),
    report: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    chat: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4-.84c-1.21.436-2.429.82-3.654.943A1 1 0 013 19V7a1 1 0 011.447-.892c.96.378 2.025.72 3.116.996C8.03 6.29 9.19 6 10.5 6h9c4.418 0 8 3.582 8 8z" />
      </svg>
    ),
    graph: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0h6m-6 0V7m6 4v5m-6 0h6" />
      </svg>
    ),
    data: (
      <svg className="w-12 h-12 mx-auto mb-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    ),
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      {icons[icon]}
      <h3 className="text-lg font-medium text-ink mb-2">{title}</h3>
      <p className="text-sm text-inkMuted text-center max-w-sm mb-4">{description}</p>
      {onAction && actionLabel && (
        <button
          onClick={onAction}
          className="bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}