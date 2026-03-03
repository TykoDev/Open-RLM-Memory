import React, { useState, useEffect, useMemo } from 'react';
import { useMemoryStore } from '@/store/memoryStore';
import { memoryService } from '@/services/memoryService';
import { AddMemorySidebar } from '@/components/Dashboard/AddMemorySidebar';
import { MemoryCard } from '@/components/common/MemoryCard';
import { MaterialIcon } from '@/components/common/MaterialIcon';
import { cn } from '@/lib/utils';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const PAGE_SIZE_OPTIONS = [5, 10, 50] as const;
const NAMESPACE_KEY = 'memory-namespace';

export const MemoryPage: React.FC = () => {
  const { memories, setMemories } = useMemoryStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(5);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);
  const [namespaceKey, setNamespaceKey] = useState(0);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === NAMESPACE_KEY) setNamespaceKey((k) => k + 1);
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  useEffect(() => {
    memoryService.getTypes().then(setAvailableTypes).catch(console.error);
  }, [namespaceKey]);

  useEffect(() => {
    const fetchMemories = async () => {
        try {
            setLoading(true);
            const activeType = typeFilter === 'all' ? undefined : typeFilter;
            const hasQuery = searchQuery.trim().length > 0;
            const response = hasQuery
              ? await memoryService.search(searchQuery, 1000, false, activeType)
              : await memoryService.list(1000, 0, activeType);
            setMemories(response.results);
        } catch (error) {
            console.error("Failed to fetch memories", error);
        } finally {
            setLoading(false);
        }
    }
    const timeoutId = setTimeout(() => fetchMemories(), 500);
    return () => clearTimeout(timeoutId);
  }, [setMemories, searchQuery, typeFilter, namespaceKey]);

  // Reset to page 1 when search query, type filter, or page size changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, typeFilter, pageSize]);

  const totalPages = Math.max(1, Math.ceil(memories.length / pageSize));
  const paginatedMemories = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return memories.slice(start, start + pageSize);
  }, [memories, currentPage, pageSize]);

  const handleDelete = async (id: string) => {
      if (confirm('Are you sure you want to delete this memory?')) {
          await memoryService.delete(id);
          const activeType = typeFilter === 'all' ? undefined : typeFilter;
          const hasQuery = searchQuery.trim().length > 0;
          const response = hasQuery
            ? await memoryService.search(searchQuery, 1000, false, activeType)
            : await memoryService.list(1000, 0, activeType);
          setMemories(response.results);
      }
  };

  return (
    <div>
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-heading font-bold text-foreground mb-1 engraved-text">Memory Management</h1>
          <p className="text-muted-foreground font-light text-sm">Organize, search, and manage your agent's stored knowledge base.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-main border border-border-main rounded-sm shadow-sm">
          <span className="w-2 h-2 rounded-full bg-[var(--status-success-text)] shadow-[0_0_8px_var(--status-success-glow)]"></span>
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--status-success-text)]">Indexing Active</span>
        </div>
      </header>

      <div className="mb-8 flex gap-3 items-center">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <MaterialIcon icon="search" className="text-muted-foreground" />
          </div>
          <input
            className="block w-full pl-12 pr-4 py-4 bg-surface-main border border-border-main text-foreground placeholder:text-muted-foreground/70 focus:ring-0 sm:text-sm font-mono shadow-inner rounded-sm transition-colors focus:border-primary outline-none"
            placeholder="Search across all memory fragments..."
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[180px] h-[54px] bg-surface-main border border-border-main rounded-sm text-sm font-mono text-foreground focus:border-primary focus:ring-0">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent className="bg-surface-main border-border-main text-foreground">
            <SelectItem value="all">All Types</SelectItem>
            {availableTypes.map((t) => (
              <SelectItem key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1).replace('_', ' ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-end mb-4">
            <h3 className="text-lg font-heading font-bold uppercase tracking-wide text-foreground">
              All Memories
              <span className="text-xs text-muted-foreground font-mono font-normal ml-2">({memories.length})</span>
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-widest">Per page:</span>
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <button
                    key={size}
                    onClick={() => setPageSize(size)}
                    className={cn(
                      "text-[10px] font-mono px-2 py-0.5 rounded-sm border transition-colors",
                      size === pageSize
                        ? "bg-primary/10 border-primary text-primary"
                        : "border-border-main text-muted-foreground hover:text-foreground hover:border-foreground/30"
                    )}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {loading ? (
                <div className="text-center py-8 text-muted-foreground font-mono text-xs">Loading...</div>
            ) : paginatedMemories.length > 0 ? (
                paginatedMemories.map((mem) => (
                <MemoryCard
                    key={mem.id}
                    type={mem.type}
                    content={mem.content}
                    timestamp={new Date(mem.created_at).toLocaleString()}
                    tags={mem.tags}
                    onEdit={() => console.log('Edit', mem.id)}
                    onDelete={() => handleDelete(mem.id)}
                />
                ))
            ) : (
                <div className="text-center text-muted-foreground py-8">
                    No memories match your search.
                </div>
            )}
          </div>

          {/* Pagination controls */}
          {memories.length > 0 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="px-3 py-1.5 text-xs font-mono uppercase tracking-wider border border-border-main rounded-sm text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <MaterialIcon icon="chevron_left" className="text-sm" />
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((page) => {
                  // Show first, last, current, and neighbors
                  if (page === 1 || page === totalPages) return true;
                  if (Math.abs(page - currentPage) <= 1) return true;
                  return false;
                })
                .reduce<(number | 'ellipsis')[]>((acc, page, idx, arr) => {
                  if (idx > 0 && page - (arr[idx - 1] as number) > 1) {
                    acc.push('ellipsis');
                  }
                  acc.push(page);
                  return acc;
                }, [])
                .map((item, idx) =>
                  item === 'ellipsis' ? (
                    <span key={`e-${idx}`} className="px-1 text-xs text-muted-foreground font-mono">...</span>
                  ) : (
                    <button
                      key={item}
                      onClick={() => setCurrentPage(item)}
                      className={cn(
                        "min-w-[28px] h-7 text-xs font-mono border rounded-sm transition-colors",
                        item === currentPage
                          ? "bg-primary/10 border-primary text-primary"
                          : "border-border-main text-muted-foreground hover:text-foreground hover:border-foreground/30"
                      )}
                    >
                      {item}
                    </button>
                  )
                )}

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
                className="px-3 py-1.5 text-xs font-mono uppercase tracking-wider border border-border-main rounded-sm text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <MaterialIcon icon="chevron_right" className="text-sm" />
              </button>
            </div>
          )}
        </div>

        <div className="lg:w-[380px] shrink-0">
          <AddMemorySidebar />
        </div>
      </div>
    </div>
  );
};
