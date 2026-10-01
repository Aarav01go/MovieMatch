import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import api from '../api/client';
import { Search } from 'lucide-react';

export default function Discover() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await api.get(`/movies/search?q=${encodeURIComponent(query)}`);
        setResults(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }, 500); // Debounce
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div>
      <Navbar />
      <div className="pt-24 px-4 md:px-12 min-h-screen">
        <div className="relative mb-8 max-w-2xl mx-auto">
          <Search className="absolute left-4 top-3.5 text-gray-400" size={24} />
          <input 
            type="text" 
            placeholder="Search movies, genres (e.g. Inception)..." 
            value={query} 
            onChange={e => setQuery(e.target.value)}
            className="w-full bg-gray-800 text-white p-4 pl-12 rounded-full outline-none focus:ring-2 focus:ring-netflix-red transition"
          />
        </div>
        
        {loading && <p className="text-center text-gray-400 mt-12">Searching database and consulting AI...</p>}
        
        {!loading && results.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {results.map(m => <MovieCard key={m.movieId} movie={m} />)}
          </div>
        )}
      </div>
    </div>
  );
}
