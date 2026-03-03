import axios from 'axios';

const rawBaseURL = import.meta.env.VITE_API_URL || window.location.origin;
const baseURL = rawBaseURL.endsWith('/api/v1')
  ? rawBaseURL
  : `${rawBaseURL.replace(/\/$/, '')}/api/v1`;

const NAMESPACE_KEY = 'memory-namespace';

const getNamespace = (): string => {
  const value = localStorage.getItem(NAMESPACE_KEY) ?? 'local';
  const normalized = value.trim().toLowerCase();
  return normalized.length > 0 ? normalized : 'local';
};

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add namespace header for user-scoped memory separation.
api.interceptors.request.use((config) => {
  config.headers['X-Memory-Namespace'] = getNamespace();
  return config;
});

export default api;
