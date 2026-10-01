import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function MyList() {
  const { user } = useAuth();
  const [ratings, setRatings] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [tab, setTab] = useState('favorites'); // favorites, watchlist, completed

  useEffect(() => {
    if(user) {
      api.get(`/ratings/${user.user_id}`).then(res => setRatings(res.data));
      api.get(`/watchlist/${user.user_id}`).then(res => setWatchlist(res.data));
    }
  }, [user]);

  const favorites = ratings.filter(r => r.rating >= 4.0);
  const completed = ratings;

  const displayMovies = tab === 'favorites' ? favorites : tab === 'watchlist' ? watchlist : completed;

  return (
    <div>
      <Navbar />
      <div className="pt-24 px-4 md:px-12 min-h-screen">
        <h1 className="text-3xl font-bold mb-6">My List</h1>
        <div className="flex gap-8 border-b border-gray-800 mb-8 pb-2 text-gray-400 font-semibold">
          <button onClick={()=>setTab('favorites')} className={`hover:text-white transition ${tab==='favorites'?'text-white border-b-2 border-netflix-red':''}`}>Favorites</button>
          <button onClick={()=>setTab('watchlist')} className={`hover:text-white transition ${tab==='watchlist'?'text-white border-b-2 border-netflix-red':''}`}>Plan to Watch</button>
          <button onClick={()=>setTab('completed')} className={`hover:text-white transition ${tab==='completed'?'text-white border-b-2 border-netflix-red':''}`}>Completed</button>
        </div>
        
        {displayMovies.length === 0 ? (
          <p className="text-gray-500 text-center mt-20">Nothing to see here yet.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 pb-12">
            {displayMovies.map(m => <MovieCard key={m.movieId} movie={m} />)}
          </div>
        )}
      </div>
    </div>
  );
}
