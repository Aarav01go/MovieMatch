import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Heart, Users } from 'lucide-react';

export default function Matchmaker() {
  const { user } = useAuth();
  const [partner, setPartner] = useState('');
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleMatch = async (e) => {
    e.preventDefault();
    if (!partner) return;
    setLoading(true);
    setError('');
    
    try {
      // 1. Find partner user ID
      const { data: partnerUser } = await api.post('/users', { username: partner });
      
      // 2. Get mutual recommendations
      const { data } = await api.get(`/recommendations/match/${user.user_id}/${partnerUser.user_id}`);
      setMatches(data);
    } catch (err) {
      setError('Could not calculate matches. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-netflix-dark pb-12">
      <Navbar />
      <div className="pt-32 px-4 md:px-12 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <Heart size={48} className="mx-auto text-netflix-red mb-4 animate-pulse" />
          <h1 className="text-4xl font-black mb-4">Date Night Matchmaker</h1>
          <p className="text-gray-400">Enter a friend or partner's username to mathematically find a movie you'll BOTH love.</p>
        </div>
        
        <form onSubmit={handleMatch} className="max-w-md mx-auto flex gap-2 mb-12">
          <input 
            type="text" 
            placeholder="Partner's username (e.g. guest2)"
            value={partner}
            onChange={(e) => setPartner(e.target.value)}
            className="flex-1 bg-gray-800 text-white p-4 rounded outline-none focus:ring-2 focus:ring-netflix-red"
          />
          <button type="submit" disabled={loading} className="bg-netflix-red px-6 py-4 rounded font-bold hover:bg-netflix-redHover transition flex items-center gap-2 disabled:opacity-50">
            <Users size={20} /> Match
          </button>
        </form>

        {loading && <div className="text-center text-netflix-red font-bold text-xl animate-pulse">Calculating neural overlap...</div>}
        {error && <div className="text-center text-red-500">{error}</div>}

        {matches.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Top Mutual Picks for {user.username} & {partner}</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {matches.map(movie => (
                <div key={movie.movieId} className="flex flex-col items-center">
                  <MovieCard movie={movie} />
                  <div className="mt-2 text-xs text-gray-400 text-center">
                    <span className="text-green-500 font-bold">{movie.score}⭐ Match</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
