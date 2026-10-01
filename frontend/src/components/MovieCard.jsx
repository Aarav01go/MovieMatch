import React from 'react';
import { Link } from 'react-router-dom';
import { getImageUrl } from '../api/client';
import { Play, Plus } from 'lucide-react';

export default function MovieCard({ movie }) {
  const poster = getImageUrl(movie.poster_url, movie.title);
  
  return (
    <Link to={`/movie/${movie.movieId}`} className="group relative flex-none w-32 md:w-48 aspect-[2/3] rounded overflow-hidden transition-transform duration-300 hover:scale-110 hover:z-20 shadow-lg">
      <img src={poster} alt={movie.title} className="w-full h-full object-cover" loading="lazy" />
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-3">
        <h3 className="text-white text-sm font-bold truncate">{movie.title}</h3>
        <p className="text-gray-300 text-xs truncate">{movie.genres.replace(/\|/g, ' • ')}</p>
        <div className="flex gap-2 mt-2">
          <button className="bg-white text-black rounded-full p-1"><Play size={14} className="ml-0.5" /></button>
          <button className="border border-gray-400 text-white rounded-full p-1 hover:border-white hover:bg-white/20"><Plus size={14} /></button>
        </div>
      </div>
    </Link>
  );
}
