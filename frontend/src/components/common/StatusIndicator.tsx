import React from "react";
import { cn } from "@/lib/utils";

interface StatusIndicatorProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: "active" | "inactive" | "pending" | "warning" | "error";
  label?: string;
  showPulse?: boolean;
}

export const StatusIndicator = React.forwardRef<HTMLSpanElement, StatusIndicatorProps>(
  ({ className, status, label, showPulse = false, ...props }, _ref) => {
    const colors = {
      active: "bg-[var(--status-success-text)] shadow-[0_0_8px_var(--status-success-glow)]",
      inactive: "bg-muted-foreground",
      pending: "bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]",
      warning: "bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]",
      error: "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]",
    };

    const textColors = {
      active: "text-[var(--status-success-text)]",
      inactive: "text-muted-foreground",
      pending: "text-yellow-500/90",
      warning: "text-orange-500/90",
      error: "text-red-500/90",
    };

    return (
      <div className={cn("flex items-center gap-2", className)} {...props}>
        <div className="relative flex h-2 w-2">
          {showPulse && (status === "active" || status === "pending" || status === "warning" || status === "error") && (
            <span className={cn(
              "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
              colors[status].split(' ')[0].replace('bg-', 'bg-') // Simple hack to get color
            )}></span>
          )}
          <span className={cn(
            "relative inline-flex rounded-full h-2 w-2",
            colors[status]
          )}></span>
        </div>
        {label && (
          <span className={cn(
            "text-xs font-bold uppercase tracking-wider",
            textColors[status]
          )}>
            {label}
          </span>
        )}
      </div>
    );
  }
);

StatusIndicator.displayName = "StatusIndicator";
