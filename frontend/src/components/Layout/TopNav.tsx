import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { MaterialIcon } from "@/components/common/MaterialIcon";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { getStoredTheme, setStoredTheme, type Theme } from "@/lib/theme";
import { cn } from "@/lib/utils";
import { memoryService } from "@/services/memoryService";

interface TopNavProps {
  isAdmin?: boolean;
}

const NAMESPACE_KEY = "memory-namespace";

const getNamespace = (): string => {
  const value = localStorage.getItem(NAMESPACE_KEY) ?? "local";
  const normalized = value.trim().toLowerCase();
  return normalized.length > 0 ? normalized : "local";
};

export const TopNav = ({ isAdmin = false }: TopNavProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [namespace, setNamespace] = useState<string>(getNamespace());
  const [theme, setTheme] = useState<Theme>(() => getStoredTheme());
  const [namespaces, setNamespaces] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setNamespace(getNamespace());
  }, [location.pathname]);

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(`${path}/`);

  const handleDropdownOpen = async (open: boolean) => {
    if (!open) return;
    setLoading(true);
    try {
      const result = await memoryService.getNamespaces();
      setNamespaces(result);
    } catch {
      setNamespaces([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNamespace = (ns: string) => {
    localStorage.setItem(NAMESPACE_KEY, ns);
    setNamespace(ns);
    window.dispatchEvent(new StorageEvent("storage", { key: NAMESPACE_KEY, newValue: ns }));
    navigate("/dashboard");
  };

  const handleThemeToggle = (checked: boolean) => {
    const nextTheme: Theme = checked ? "dark" : "light";
    setStoredTheme(nextTheme);
    setTheme(nextTheme);
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border-main bg-header-bg backdrop-blur-sm shadow-md">
      <div className={cn("mx-auto px-4 sm:px-6 lg:px-8", isAdmin ? "max-w-[1440px]" : "max-w-[1400px]")}>
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="flex flex-col">
              <span className="font-heading text-lg font-bold uppercase tracking-widest text-foreground leading-tight">
                Open<span className="text-primary"> RLM Memory</span>
              </span>
              <span className="text-[11px] tracking-widest uppercase text-right text-black dark:text-[#f5f5dc]">Created by <a href="https://tykotech.eu" target="_blank" rel="noopener noreferrer" className="hover:underline" onClick={(e) => e.stopPropagation()}>TykoTech</a></span>
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-2 h-full">
            <Link
              to="/dashboard"
              className={cn(
                "h-full flex items-center px-4 text-xs font-bold uppercase tracking-wider transition-colors gap-2 border-b-2",
                isActive("/dashboard") ? "text-primary bg-primary/10 border-primary" : "text-muted-foreground border-transparent hover:text-foreground",
              )}
            >
              <MaterialIcon icon="dashboard" className="text-lg" />
              Dashboard
            </Link>
            <Link
              to="/memory"
              className={cn(
                "h-full flex items-center px-4 text-xs font-bold uppercase tracking-wider transition-colors gap-2 border-b-2",
                isActive("/memory") ? "text-primary bg-primary/10 border-primary" : "text-muted-foreground border-transparent hover:text-foreground",
              )}
            >
              <MaterialIcon icon="database" className="text-lg" />
              Memory
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <DropdownMenu onOpenChange={handleDropdownOpen}>
              <DropdownMenuTrigger asChild>
                <button className="hidden md:flex items-center gap-3 group focus-visible:outline-none" title="Switch namespace">
                  <div className="text-right">
                    <div className="text-xs font-bold text-foreground uppercase tracking-wide group-hover:text-primary transition-colors">Namespace</div>
                    <div className="text-[10px] text-muted-foreground font-mono">{namespace}</div>
                  </div>
                  <Avatar className="h-8 w-8 bg-surface-light border border-border-light rounded-full">
                    <AvatarFallback className="text-primary font-bold text-xs bg-transparent">
                      {namespace.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Switch Namespace</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {loading ? (
                  <div className="px-2 py-3 text-xs text-muted-foreground text-center">Loading...</div>
                ) : namespaces.length === 0 ? (
                  <div className="px-2 py-3 text-xs text-muted-foreground text-center">No namespaces found</div>
                ) : (
                  namespaces.map((ns) => (
                    <DropdownMenuItem
                      key={ns}
                      onClick={() => handleSelectNamespace(ns)}
                      className={cn("cursor-pointer font-mono text-sm", ns === namespace && "bg-primary/10 text-primary")}
                    >
                      <MaterialIcon icon={ns === namespace ? "radio_button_checked" : "radio_button_unchecked"} className="text-base mr-1" />
                      {ns}
                    </DropdownMenuItem>
                  ))
                )}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Mobile-only avatar trigger */}
            <DropdownMenu onOpenChange={handleDropdownOpen}>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="md:hidden rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                  title="Switch namespace"
                >
                  <Avatar className="h-8 w-8 bg-surface-light border border-border-light rounded-full">
                    <AvatarFallback className="text-primary font-bold text-xs bg-transparent">
                      {namespace.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Switch Namespace</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {loading ? (
                  <div className="px-2 py-3 text-xs text-muted-foreground text-center">Loading...</div>
                ) : namespaces.length === 0 ? (
                  <div className="px-2 py-3 text-xs text-muted-foreground text-center">No namespaces found</div>
                ) : (
                  namespaces.map((ns) => (
                    <DropdownMenuItem
                      key={ns}
                      onClick={() => handleSelectNamespace(ns)}
                      className={cn("cursor-pointer font-mono text-sm", ns === namespace && "bg-primary/10 text-primary")}
                    >
                      <MaterialIcon icon={ns === namespace ? "radio_button_checked" : "radio_button_unchecked"} className="text-base mr-1" />
                      {ns}
                    </DropdownMenuItem>
                  ))
                )}
              </DropdownMenuContent>
            </DropdownMenu>

            <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-surface-main border border-border-main">
              <MaterialIcon icon="light_mode" className={cn("text-sm", theme === "light" ? "text-primary" : "text-muted-foreground")} />
              <Switch
                checked={theme === "dark"}
                onCheckedChange={handleThemeToggle}
                aria-label="Toggle dark mode"
              />
              <MaterialIcon icon="dark_mode" className={cn("text-sm", theme === "dark" ? "text-primary" : "text-muted-foreground")} />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
