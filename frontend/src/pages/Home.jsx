import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Info } from 'lucide-react';
import api, { getImageUrl } from '../api/client';
import MovieRail from '../components/MovieRail';
import Navbar from '../components/Navbar';

export default function Home() {
  const [trending, setTrending] = useState([]);
  const [recent, setRecent] = useState([]);
  const [marvel, setMarvel] = useState([]);
  const [indian, setIndian] = useState([]);
  const [action, setAction] = useState([]);
  const [comedy, setComedy] = useState([]);
  const [scifi, setScifi] = useState([]);
  const [thriller, setThriller] = useState([]);
  const [romance, setRomance] = useState([]);
  const [horror, setHorror] = useState([]);
  const [animation, setAnimation] = useState([]);
  
  useEffect(() => {
    api.get('/movies/trending').then(res => setTrending(res.data)).catch(console.error);
    api.get('/movies/recent').then(res => setRecent(res.data)).catch(console.error);
    api.get('/movies/marvel').then(res => setMarvel(res.data)).catch(console.error);
    api.get('/movies/indian-cinema').then(res => setIndian(res.data)).catch(console.error);
    api.get('/movies/search?q=Action').then(res => setAction(res.data)).catch(console.error);
    api.get('/movies/search?q=Comedy').then(res => setComedy(res.data)).catch(console.error);
    api.get('/movies/search?q=Sci-Fi').then(res => setScifi(res.data)).catch(console.error);
    api.get('/movies/search?q=Thriller').then(res => setThriller(res.data)).catch(console.error);
    api.get('/movies/search?q=Romance').then(res => setRomance(res.data)).catch(console.error);
    api.get('/movies/search?q=Horror').then(res => setHorror(res.data)).catch(console.error);
    api.get('/movies/search?q=Animation').then(res => setAnimation(res.data)).catch(console.error);
  }, []);

  const hero = trending[0];

  return (
    <div className="pb-12">
      <Navbar />
      {hero && (
        <div className="relative h-[85vh] w-full mb-8">
          <img src={getImageUrl(hero.poster_url, hero.title)} alt={hero.title} className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-netflix-dark via-netflix-dark/40 to-transparent" />
          <div className="absolute bottom-20 md:bottom-32 left-0 p-4 md:p-12 w-full md:w-1/2 z-10">
            <h1 className="text-5xl md:text-7xl font-black mb-4 shadow-sm leading-tight">{hero.title}</h1>
            <p className="text-lg text-gray-300 mb-6 font-semibold">{hero.genres.replace(/\|/g, ' • ')}</p>
            <div className="flex gap-4">
              <Link to={`/movie/${hero.movieId}`} className="flex items-center gap-2 bg-white text-black px-6 py-2.5 rounded font-bold hover:bg-gray-200 transition"><Play size={20} className="fill-black" /> Play</Link>
              <Link to={`/movie/${hero.movieId}`} className="flex items-center gap-2 bg-gray-500/70 text-white px-6 py-2.5 rounded font-bold hover:bg-gray-500 transition"><Info size={20} /> More Info</Link>
            </div>
          </div>
        </div>
      )}
      <div className="-mt-20 md:-mt-32 relative z-20">
        <MovieRail title="Marvel Cinematic Universe" movies={marvel} />
        <MovieRail title="Blockbusters: Bollywood & Tollywood" movies={indian} />
        <MovieRail title="New Releases (Last 15 Years)" movies={recent} />
        <MovieRail title="Trending Now" movies={trending.slice(1)} />
        <MovieRail title="Action & Adventure" movies={action} />
        <MovieRail title="Sci-Fi Marvels" movies={scifi} />
        <MovieRail title="Comedies" movies={comedy} />
        <MovieRail title="Animation Station" movies={animation} />
        <MovieRail title="Nail-biting Thrillers" movies={thriller} />
        <MovieRail title="Chilling Horror" movies={horror} />
        <MovieRail title="Romantic Favorites" movies={romance} />
      </div>
    </div>
  );
}
