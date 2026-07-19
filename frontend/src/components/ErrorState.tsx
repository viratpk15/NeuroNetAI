"use client";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export function ErrorState({
  title = "Something went wrong",
  message = "Unable to load data. Please check your connection and try again.",
  onRetry,
  retryLabel = "Retry",
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="bg-surface rounded-full p-6 mb-4">
        <svg className="w-8 h-8 text-risk" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-ink mb-2">{title}</h3>
      <p className="text-sm text-inkMuted text-center max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-signal text-canvas px-4 py-2 rounded font-medium text-sm hover:brightness-110 transition"
        >
          {retryLabel}
        </button>
      )}
    </div>
  );
}