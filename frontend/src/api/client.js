import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const getImageUrl = (url, title) => {
  if (url) return url.startsWith('/static') ? `http://localhost:8000${url}` : url;
  const colors = ["18181b", "27272a", "09090b"];
  const bg = colors[title.length % colors.length];
  return `https://placehold.co/400x600/${bg}/e50914?text=${encodeURIComponent(title.charAt(0).toUpperCase())}&font=inter`;
};

export default api;
