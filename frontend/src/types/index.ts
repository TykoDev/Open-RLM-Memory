export interface User {
  id: string;
  email: string;
  name: string;
  role?: string;
}

export interface MemoryResult {
  id: string;
  content: string;
  score: number;
  type: string;
  tags: string[];
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface RLMMetrics {
  steps: number;
  sub_queries: number;
  used_cache: boolean;
}

export interface MemoryStats {
  total_memories: number;
  storage_size: number;
  entries_today: number;
  cache_hits_24h?: number;
}

export interface SearchResponse {
  results: MemoryResult[];
  total_results: number;
  processing_time_ms: number;
  rlm_decomposition: RLMMetrics;
}

export interface MemoryListResponse {
  results: MemoryResult[];
  total_results: number;
}

export interface ServerConfig {
  llm: {
    model: string;
    base_url: string;
  };
  embedding: {
    model: string;
    base_url: string;
    dimensions: number;
  };
}
