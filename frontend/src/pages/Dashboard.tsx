import React, { useState, useEffect } from 'react';
import { memoryService } from '@/services/memoryService';
import { StatCard } from '@/components/common/StatCard';
import { MaterialIcon } from '@/components/common/MaterialIcon';
import { Card } from '@/components/ui/card';
import { IconBox } from '@/components/common/IconBox';

import { MemoryResult, MemoryStats, ServerConfig } from '@/types';

const NAMESPACE_KEY = 'memory-namespace';
const getNamespace = (): string => {
  const value = localStorage.getItem(NAMESPACE_KEY) ?? 'local';
  return value.trim().toLowerCase() || 'local';
};

export const Dashboard: React.FC = () => {
  const [namespace, setNamespace] = useState(getNamespace);

  const [stats, setStats] = useState<MemoryStats>({
    total_memories: 0,
    storage_size: 0,
    entries_today: 0,
    cache_hits_24h: 0,
  });
  const [recentMemories, setRecentMemories] = useState<MemoryResult[]>([]);
  const [config, setConfig] = useState<ServerConfig | null>(null);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === NAMESPACE_KEY) setNamespace(getNamespace());
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  useEffect(() => {
    memoryService.getStats().then(setStats).catch(console.error);
    memoryService.list(5, 0).then((response) => setRecentMemories(response.results)).catch(console.error);
    memoryService.getConfig().then(setConfig).catch(console.error);
  }, [namespace]);

  const allocatedStorageMb = 1024;
  const usedStorageMb = Number(stats.storage_size ?? 0);

  return (
    <div>
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-heading font-bold text-foreground mb-1 engraved-text">Welcome, {namespace}</h1>
          <p className="text-muted-foreground font-light text-sm">Access your local memory namespace and semantic search.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-main border border-border-main rounded-sm shadow-sm">
          <span className="w-2 h-2 rounded-full bg-[var(--status-success-text)] shadow-[0_0_8px_var(--status-success-glow)]"></span>
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--status-success-text)]">Connected</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          label="Total Memories"
          value={stats.total_memories.toLocaleString()}
          icon="memory_alt"
        />
        <StatCard
          label="Storage Used"
          value={usedStorageMb.toLocaleString()}
          unit="MB"
          icon="cloud_queue"
          subtext={`of ${allocatedStorageMb.toLocaleString()} MB allocated`}
        />
        <StatCard
          label="Memories Added Today"
          value={stats.entries_today}
          icon="history"
          subtext="Last 24 hours"
        />
        <StatCard
          label="Cache Hits (24h)"
          value={stats.cache_hits_24h ?? 0}
          unit="hits"
          icon="bolt"
          subtext="Search cache utilization"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="matte-surface p-6 relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">LLM Model</p>
            <IconBox variant="default">
              <MaterialIcon icon="psychology" />
            </IconBox>
          </div>
          {config ? (
            <div className="space-y-2 font-mono text-xs">
              <div>
                <span className="text-muted-foreground">Model: </span>
                <span className="text-foreground break-all">{config.llm.model}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Endpoint: </span>
                <span className="text-foreground break-all">{config.llm.base_url}</span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-muted-foreground font-mono">Loading...</div>
          )}
        </Card>

        <Card className="matte-surface p-6 relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Embedding Model</p>
            <IconBox variant="default">
              <MaterialIcon icon="hub" />
            </IconBox>
          </div>
          {config ? (
            <div className="space-y-2 font-mono text-xs">
              <div>
                <span className="text-muted-foreground">Model: </span>
                <span className="text-foreground break-all">{config.embedding.model}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Endpoint: </span>
                <span className="text-foreground break-all">{config.embedding.base_url}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Dimensions: </span>
                <span className="text-foreground">{config.embedding.dimensions}</span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-muted-foreground font-mono">Loading...</div>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-8">
         <div>
            <div className="bg-surface-main border border-border-main rounded-sm flex flex-col h-full min-h-[200px] overflow-hidden">
                <div className="p-4 border-b border-border-main flex justify-between items-center bg-surface-accent">
                    <h3 className="text-sm font-heading font-bold uppercase tracking-wide text-foreground">Namespace Status</h3>
                    <MaterialIcon icon="history" className="text-muted-foreground" />
                </div>
                <div className="flex-1 overflow-auto p-0">
                    <div className="p-6 text-xs text-muted-foreground font-mono leading-relaxed">
                      <p className="mb-3">Current namespace: <span className="text-primary">{namespace}</span></p>
                      <p>All memory operations are scoped to this namespace via <code>X-Memory-Namespace</code>.</p>
                      <div className="mt-6 border-t border-border-main pt-4">
                        <p className="mb-3 text-[10px] uppercase tracking-wider text-muted-foreground">Recent memories</p>
                        {recentMemories.length > 0 ? (
                          <ul className="space-y-2">
                            {recentMemories.map((memory) => (
                              <li key={memory.id} className="text-xs text-foreground/85 truncate">
                                - {memory.content}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-xs text-muted-foreground">No memories found in this namespace yet.</p>
                        )}
                      </div>
                    </div>
                </div>
            </div>
         </div>
      </div>
    </div>
  );
};
