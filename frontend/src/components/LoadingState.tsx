"use client";

interface LoadingStateProps {
  count?: number;
}

export function LoadingState({ count = 3 }: LoadingStateProps) {
  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="animate-pulse">
        <div className="h-8 w-48 bg-surfaceRaised rounded mb-2" />
        <div className="h-4 w-32 bg-surfaceRaised rounded mb-6" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="bg-surface rounded-lg p-6 border border-border animate-pulse">
            <div className="h-5 w-24 bg-surfaceRaised rounded mb-3" />
            <div className="h-8 w-16 bg-surfaceRaised rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}