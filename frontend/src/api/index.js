import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 5000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const raw = window.localStorage.getItem('user');
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.token) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${parsed.token}`;
        }
      } catch (e) {}
    }
  }
  return config;
});

export default apiClient;
