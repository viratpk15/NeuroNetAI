"use client";

import { Task } from "@/lib/api";

interface TaskBoardProps {
  tasksByStatus: { todo: Task[]; in_progress: Task[]; done: Task[] };
}

export function TaskBoard({ tasksByStatus }: TaskBoardProps) {
  const sections: Array<[keyof typeof tasksByStatus, string]> = [
    ["todo", "Todo"],
    ["in_progress", "In Progress"],
    ["done", "Done"],
  ];

  return (
    <div className="bg-surface rounded-lg p-6 border border-border">
      <h2 className="text-lg font-medium text-ink mb-4">
        Tasks ({tasksByStatus.todo.length + tasksByStatus.in_progress.length + tasksByStatus.done.length})
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {sections.map(([status, label]) => {
          const tasks = tasksByStatus[status];
          return (
            <div key={status} className="bg-surfaceRaised rounded p-3 min-h-[120px]">
              <h3 className="text-xs font-medium text-inkMuted mb-3 uppercase tracking-wider">{label}</h3>
              {tasks.length === 0 ? (
                <p className="text-inkMuted/50 text-xs">Empty</p>
              ) : (
                <div className="space-y-2">
                  {tasks.map((task) => (
                    <div key={task.id} className="bg-canvas/50 rounded p-2">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <span className="text-ink text-sm font-medium">{task.title}</span>
                        <span className={`px-1.5 py-0.5 text-[10px] rounded ${
                          task.priority === "high" ? "bg-red-900/30 text-red-300" :
                          task.priority === "low" ? "bg-green-900/30 text-green-300" :
                          "bg-yellow-900/30 text-yellow-300"
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                      {task.assignee && (
                        <p className="text-[10px] text-inkMuted font-mono">@{task.assignee}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}