import React from "react";
import { cn } from "@/lib/utils";

interface MaterialIconProps extends React.HTMLAttributes<HTMLSpanElement> {
  icon: string;
  size?: "sm" | "md" | "lg" | "xl" | "2xl";
}

export const MaterialIcon = React.forwardRef<HTMLSpanElement, MaterialIconProps>(
  ({ icon, className, size = "md", ...props }, ref) => {
    const sizeClasses = {
      sm: "text-sm",
      md: "text-base",
      lg: "text-lg",
      xl: "text-xl",
      "2xl": "text-2xl",
    };

    return (
      <span
        ref={ref}
        className={cn(
          "material-symbols-outlined select-none",
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {icon}
      </span>
    );
  }
);

MaterialIcon.displayName = "MaterialIcon";
