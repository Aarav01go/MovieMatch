import axios from 'axios';

// In production this is set to your Render backend URL via VITE_API_URL
// In development it falls back to localhost:8000
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 90000, // 90s — Render free tier can take up to 60s to cold-start
});

export const getImageUrl = (url, title) => {
  if (url) {
    // Local static path → prefix with backend URL
    if (url.startsWith('/static')) return `${BASE_URL}${url}`;
    return url;
  }
  // Placeholder fallback
  const colors = ['18181b', '27272a', '09090b'];
  const bg = colors[title.length % colors.length];
  return `https://placehold.co/400x600/${bg}/e50914?text=${encodeURIComponent(title.charAt(0).toUpperCase())}&font=inter`;
};

export default api;
