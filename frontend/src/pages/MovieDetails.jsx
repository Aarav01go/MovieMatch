import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MovieRail from '../components/MovieRail';
import api, { getImageUrl } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Play, Plus, Check, Star } from 'lucide-react';

export default function MovieDetails() {
  const { movieId } = useParams();
  const { user } = useAuth();
  const [movie, setMovie] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [sequels, setSequels] = useState([]);
  const [synopsis, setSynopsis] = useState('Generating AI Synopsis...');

  useEffect(() => {
    window.scrollTo(0,0);
    api.get(`/movies/${movieId}`).then(res => setMovie(res.data));
    api.get(`/movies/${movieId}/similar`).then(res => setSimilar(res.data));
    api.get(`/movies/${movieId}/sequels`).then(res => setSequels(res.data)).catch(() => setSequels([]));
    api.get(`/ai/synopsis?title=${encodeURIComponent(movie?.title || '')}`).then(res => setSynopsis(res.data.synopsis)).catch(() => setSynopsis("Synopsis unavailable."));
  }, [movieId, movie?.title]);

  const addRating = async (rating) => {
    await api.post('/ratings', { user_id: user.user_id, movie_id: movie.movieId, rating });
    alert("Rating saved!");
  };

  const addWatchlist = async () => {
    await api.post('/watchlist', { user_id: user.user_id, movie_id: movie.movieId });
    alert("Added to watchlist!");
  };

  if (!movie) return <div className="h-screen bg-netflix-dark" />;

  const poster = getImageUrl(movie.poster_url, movie.title);

  return (
    <div className="pb-12 min-h-screen">
      <Navbar />
      <div className="relative h-[60vh] w-full">
        <img src={poster} alt="Backdrop" className="w-full h-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-t from-netflix-dark via-transparent to-netflix-dark/50" />
        <div className="absolute bottom-0 left-0 p-4 md:p-12 flex items-end gap-8 w-full max-w-6xl">
          <img src={poster} alt={movie.title} className="hidden md:block w-48 rounded shadow-2xl shadow-black/80" />
          <div className="flex-1">
            <h1 className="text-4xl md:text-5xl font-black mb-2">{movie.title}</h1>
            <p className="text-gray-400 font-semibold mb-4">{movie.genres.replace(/\|/g, ' • ')}</p>
            <div className="bg-gray-900/60 p-4 rounded-lg backdrop-blur-sm border border-gray-800 mb-6 max-w-2xl">
              <h3 className="text-sm text-netflix-red font-bold mb-1">✨ AI Synopsis</h3>
              <p className="text-gray-200 text-sm leading-relaxed">{synopsis}</p>
            </div>
            <div className="flex gap-4">
              <button onClick={() => addRating(5)} className="flex items-center gap-2 bg-white text-black px-6 py-2 rounded font-bold hover:bg-gray-200 transition"><Star size={20} className="fill-black" /> Rate 5⭐</button>
              <button onClick={addWatchlist} className="flex items-center gap-2 bg-gray-600/70 text-white px-6 py-2 rounded font-bold hover:bg-gray-500 transition"><Plus size={20} /> My List</button>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-12">
        {sequels.length > 0 && <MovieRail title="The Collection" movies={sequels} />}
        <MovieRail title="More Like This" movies={similar} />
      </div>
    </div>
  );
}
