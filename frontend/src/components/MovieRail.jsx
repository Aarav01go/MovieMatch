import React from 'react';
import MovieCard from './MovieCard';

export default function MovieRail({ title, movies }) {
  if (!movies || movies.length === 0) return null;
  
  return (
    <div className="mb-8 px-4 md:px-12">
      <h2 className="text-xl font-bold mb-3 text-white">{title}</h2>
      <div className="flex overflow-x-auto gap-4 py-4 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
        {movies.map(movie => <MovieCard key={movie.movieId} movie={movie} />)}
      </div>
    </div>
  );
}
