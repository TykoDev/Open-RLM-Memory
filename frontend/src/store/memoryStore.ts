import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { MemoryResult } from '../types';

interface MemoryStore {
  memories: MemoryResult[];
  loading: boolean;
  error: string | null;

  setMemories: (memories: MemoryResult[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addMemory: (memory: MemoryResult) => void;
  deleteMemory: (id: string) => void;
}

export const useMemoryStore = create<MemoryStore>()(
  persist(
    (set) => ({
      memories: [],
      loading: false,
      error: null,

      setMemories: (memories) => set({ memories }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      addMemory: (memory) => set((state) => ({
        memories: [memory, ...state.memories]
      })),

      deleteMemory: (id) => set((state) => ({
        memories: state.memories.filter((m) => m.id !== id)
      })),
    }),
    {
      name: 'memory-store',
      partialize: (state) => ({ memories: state.memories }),
    }
  )
);
