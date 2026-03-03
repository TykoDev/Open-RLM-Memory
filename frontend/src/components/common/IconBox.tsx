import React from "react";
import { cn } from "@/lib/utils";

interface IconBoxProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "primary" | "secondary" | "success" | "warning" | "destructive";
  size?: "sm" | "md" | "lg";
}

export const IconBox = React.forwardRef<HTMLDivElement, IconBoxProps>(
  ({ className, variant = "default", size = "md", children, ...props }, ref) => {
    const variants = {
      default: "bg-surface-main border-border-main text-muted-foreground",
      primary: "bg-primary-dim border-primary/20 text-primary",
      secondary: "bg-surface-light border-border-light text-foreground/85",
      success: "bg-[var(--status-success-bg)] border-[var(--status-success-text)] text-[var(--status-success-text)]",
      warning: "bg-yellow-900/10 border-yellow-500/20 text-yellow-500",
      destructive: "bg-red-900/10 border-red-500/20 text-red-500",
    };

    const sizes = {
      sm: "w-8 h-8 rounded-sm",
      md: "w-10 h-10 rounded-sm",
      lg: "w-12 h-12 rounded-md",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center justify-center border shadow-inner transition-colors",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

IconBox.displayName = "IconBox";
