import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MovieCard from '../components/MovieCard';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function TopPicks() {
  const { user } = useAuth();
  const [algo, setAlgo] = useState('svd');
  const [recs, setRecs] = useState([]);
  const [mood, setMood] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiMessage, setAiMessage] = useState('');

  useEffect(() => {
    if (user) {
      setLoading(true);
      api.get(`/recommendations/${user.user_id}?algo=${algo}`)
         .then(res => setRecs(res.data))
         .catch(console.error)
         .finally(() => setLoading(false));
    }
  }, [algo, user]);

  const handleMoodRerank = async (e) => {
    e.preventDefault();
    if (!mood || recs.length === 0) return;
    setLoading(true);
    try {
      const { data } = await api.post('/ai/rerank', { movies: recs.map(m => m.title), mood });
      setAiMessage(data.result);
    } catch(err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Navbar />
      <div className="pt-24 px-4 md:px-12 min-h-screen">
        <div className="flex justify-between items-end mb-8">
          <h1 className="text-3xl font-bold">Made For You</h1>
          <select value={algo} onChange={e => setAlgo(e.target.value)} className="bg-gray-800 text-white p-2 rounded outline-none cursor-pointer">
            <option value="svd">SVD Engine</option>
            <option value="knn">KNN Engine</option>
            <option value="baseline">Baseline Engine</option>
          </select>
        </div>
        
        <form onSubmit={handleMoodRerank} className="mb-12 bg-gray-900 p-6 rounded-lg border border-gray-800">
          <h2 className="text-xl font-bold mb-4">AI Mood Mode ✨</h2>
          <div className="flex gap-2">
            <input type="text" placeholder="I want something mind-bending..." value={mood} onChange={e => setMood(e.target.value)} className="flex-1 bg-gray-800 p-3 rounded outline-none focus:ring-1 focus:ring-netflix-red" />
            <button type="submit" className="bg-netflix-red px-6 rounded font-bold hover:bg-netflix-redHover transition">Re-rank</button>
          </div>
          {aiMessage && <div className="mt-4 p-4 bg-gray-800 text-green-400 rounded">{aiMessage}</div>}
        </form>

        {loading && <p className="text-center text-gray-400">Consulting Recommendation Engine...</p>}
        {!loading && recs.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 pb-12">
            {recs.map((m, i) => (
              <div key={m.movieId} className="relative">
                <div className="absolute -left-2 -top-2 bg-netflix-red text-white w-8 h-8 rounded-full flex items-center justify-center font-bold z-20 shadow-lg">{i+1}</div>
                <MovieCard movie={m} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
