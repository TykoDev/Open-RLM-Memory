import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { IconBox } from "@/components/common/IconBox";
import { MaterialIcon } from "@/components/common/MaterialIcon";

interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  unit?: string;
  icon: string;
  trend?: {
    value: string;
    isPositive: boolean;
    label?: string;
  };
  subtext?: string;
  progress?: number;
  valueColor?: string;
}

export const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ className, label, value, unit, icon, trend, subtext, progress, valueColor, ...props }, ref) => {
    return (
      <Card ref={ref} className={cn("matte-surface p-6 relative overflow-hidden group", className)} {...props}>
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">{label}</p>
            <div className="flex items-baseline gap-1">
              <h2 className={cn("text-4xl font-mono font-medium text-foreground engraved-text", valueColor)}>{value}</h2>
              {unit && <span className="text-lg text-muted-foreground font-mono">{unit}</span>}
            </div>
          </div>
          <IconBox variant="default">
            <MaterialIcon icon={icon} />
          </IconBox>
        </div>
        
        {progress !== undefined && (
          <div className="w-full bg-surface-light h-1.5 mt-2 rounded-full overflow-hidden">
            <div className="bg-primary h-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
          </div>
        )}

        {trend && (
          <div className={cn(
            "flex items-center gap-1 text-xs font-mono",
            trend.isPositive ? "text-green-500/80" : "text-red-500/80"
          )}>
            <MaterialIcon icon={trend.isPositive ? "trending_up" : "trending_down"} size="sm" />
            <span>{trend.value}</span>
            {trend.label && <span className="text-muted-foreground ml-1">{trend.label}</span>}
          </div>
        )}

        {subtext && (
          <div className="text-xs font-mono text-muted-foreground mt-2">
            {subtext}
          </div>
        )}
      </Card>
    );
  }
);

StatCard.displayName = "StatCard";
