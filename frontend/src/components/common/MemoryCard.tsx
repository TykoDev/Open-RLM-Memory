import React from "react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IconBox } from "@/components/common/IconBox";
import { MaterialIcon } from "@/components/common/MaterialIcon";

interface MemoryCardProps extends React.HTMLAttributes<HTMLDivElement> {
  type: "knowledge" | "event" | "code_snippet" | "preference" | "context" | "summary" | string;
  content: string;
  timestamp: string;
  tags?: string[];
  onEdit?: () => void;
  onDelete?: () => void;
}

export const MemoryCard = React.forwardRef<HTMLDivElement, MemoryCardProps>(
  ({ className, type, content, timestamp, tags, onEdit, onDelete, ...props }, ref) => {
    
    const getTypeIcon = (type: string) => {
      switch (type.toLowerCase()) {
        case "knowledge": return "lightbulb";
        case "event": return "event";
        case "code_snippet": return "terminal";
        case "preference": return "tune";
        case "context": return "account_tree";
        case "summary": return "summarize";
        default: return "memory";
      }
    };

    const isKnowledge = type.toLowerCase() === "knowledge";

    return (
      <Card ref={ref} className={cn(
        "matte-surface p-6 transition-colors group hover:border-primary/50",
        className
      )} {...props}>
        <div className="flex items-start gap-4">
          <IconBox 
            variant={isKnowledge ? "primary" : "secondary"}
            className={cn("shrink-0", !isKnowledge && "group-hover:text-primary transition-colors")}
          >
            <MaterialIcon icon={getTypeIcon(type)} />
          </IconBox>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="text-[10px] font-bold uppercase tracking-wider bg-surface-light border-border-light text-muted-foreground">
                  {type}
                </Badge>
                <span className="text-[10px] text-muted-foreground font-mono">{timestamp}</span>
              </div>
              
              {(onEdit || onDelete) && (
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {onEdit && (
                    <button onClick={onEdit} className="p-1 hover:text-primary transition-colors text-muted-foreground" title="Edit">
                      <MaterialIcon icon="edit" size="sm" />
                    </button>
                  )}
                  {onDelete && (
                    <button onClick={onDelete} className="p-1 hover:text-destructive transition-colors text-muted-foreground" title="Delete">
                      <MaterialIcon icon="delete" size="sm" />
                    </button>
                  )}
                </div>
              )}
            </div>
            
            <p className="text-foreground font-medium mb-3 leading-snug line-clamp-3">
              {content}
            </p>
            
            {tags && tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span key={tag} className="text-[10px] text-primary font-mono opacity-70">
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </Card>
    );
  }
);

MemoryCard.displayName = "MemoryCard";
