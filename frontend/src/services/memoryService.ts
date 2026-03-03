import axios from 'axios';

import api from './api';
import { MemoryListResponse, MemoryResult, SearchResponse, MemoryStats, ServerConfig } from '../types';

export const memoryService = {
  search: async (query: string, limit = 10, enableRlm = true, memoryType?: string): Promise<SearchResponse> => {
    const sanitizedQuery = query.trim().length >= 3 ? query : "memory";
    const body: Record<string, unknown> = {
      query: sanitizedQuery,
      limit,
      enable_rlm: enableRlm,
    };
    if (memoryType) {
      body.filters = { memory_type: memoryType };
    }
    const response = await api.post<SearchResponse>('/memory/search', body);
    return response.data;
  },

  list: async (limit = 1000, offset = 0, memoryType?: string): Promise<MemoryListResponse> => {
    const params: Record<string, unknown> = { limit, offset };
    if (memoryType) {
      params.memory_type = memoryType;
    }
    const response = await api.get<MemoryListResponse>('/memory/list', { params });
    return response.data;
  },

  save: async (content: string, type = 'knowledge', tags: string[] = []): Promise<MemoryResult> => {
    const response = await api.post('/memory/save', {
      content,
      type,
      tags
    });
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/memory/${id}`);
  },

  getTypes: async (): Promise<string[]> => {
    const response = await api.get<{ types: string[] }>('/memory/types');
    return response.data.types;
  },

  getStats: async (): Promise<MemoryStats> => {
    const response = await api.get<MemoryStats>('/memory/stats');
    return response.data;
  },

  getNamespaces: async (): Promise<string[]> => {
    const response = await api.get<{ namespaces: string[] }>('/memory/namespaces');
    return response.data.namespaces;
  },

  getConfig: async (): Promise<ServerConfig> => {
    const origin = (import.meta.env.VITE_API_URL || window.location.origin).replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');
    const response = await axios.get<ServerConfig>(`${origin}/health/config`);
    return response.data;
  },
};
