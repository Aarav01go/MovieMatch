import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, X, Send } from 'lucide-react';
import api, { getImageUrl } from '../api/client';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function FloatingAI() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [hasWelcomed, setHasWelcomed] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (user && !hasWelcomed && isOpen) {
      setHasWelcomed(true);
      setMessages([{ type: 'ai', text: "Analyzing your watch history...", movie: null }]);
      setLoading(true);
      api.post('/ai/assistant', { query: `I am ${user.username}. I just logged in. Greet me warmly in 1 short sentence, and suggest one specific movie based on what you think I might like. Keep it very short.` })
        .then(({ data }) => setMessages([{ type: 'ai', text: data.message, movie: data.movie }]))
        .catch(() => setMessages([{ type: 'ai', text: `Welcome back, ${user.username}! What are you in the mood to watch today?`, movie: null }]))
        .finally(() => setLoading(false));
    }
  }, [user, isOpen, hasWelcomed]);


  const handleSend = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = query;
    setMessages(prev => [...prev, { type: 'user', text: userMsg, movie: null }]);
    setQuery('');
    setLoading(true);

    try {
      const { data } = await api.post('/ai/assistant', { query: userMsg });
      setMessages(prev => [...prev, { 
        type: 'ai', 
        text: data.message, 
        movie: data.movie 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'ai', text: "Sorry, my brain is taking a break. Try again later!", movie: null }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-80 md:w-96 bg-netflix-black border border-gray-700 rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 fade-in duration-300">
          
          {/* Header */}
          <div className="bg-gradient-to-r from-netflix-red to-red-900 p-4 flex justify-between items-center text-white">
            <div className="flex items-center gap-2 font-bold">
              <Sparkles size={20} /> MovieMatch AI
            </div>
            <button onClick={() => setIsOpen(false)} className="hover:bg-white/20 p-1 rounded-full transition">
              <X size={20} />
            </button>
          </div>

          {/* Chat Window */}
          <div className="h-96 p-4 overflow-y-auto flex flex-col gap-4 bg-netflix-dark">
            {messages.map((m, i) => (
              <div key={i} className={`flex flex-col ${m.type === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`p-3 rounded-lg max-w-[85%] text-sm shadow-sm ${m.type === 'user' ? 'bg-gray-700 text-white rounded-tr-none' : 'bg-gray-800 text-gray-200 rounded-tl-none border border-gray-700'}`}>
                  {m.text}
                </div>
                {m.movie && (
                  <Link to={`/movie/${m.movie.movieId}`} className="mt-2 group relative w-32 aspect-[2/3] rounded overflow-hidden shadow-lg border border-gray-700 hover:border-netflix-red transition-colors block">
                    <img src={getImageUrl(m.movie.poster_url, m.movie.title)} alt={m.movie.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300" />
                    <div className="absolute bottom-0 w-full bg-black/80 text-white text-xs font-bold p-1 text-center truncate">
                      {m.movie.title}
                    </div>
                  </Link>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-start">
                <div className="p-3 bg-gray-800 border border-gray-700 rounded-lg rounded-tl-none flex gap-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSend} className="p-3 bg-gray-900 border-t border-gray-800 flex gap-2">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. A space movie..." 
              className="flex-1 bg-gray-800 text-white px-4 py-2 rounded-full text-sm outline-none focus:ring-1 focus:ring-netflix-red"
            />
            <button type="submit" disabled={!query.trim() || loading} className="bg-netflix-red text-white p-2 rounded-full hover:bg-netflix-redHover transition disabled:opacity-50 disabled:cursor-not-allowed">
              <Send size={18} />
            </button>
          </form>
        </div>
      )}

      {/* FAB Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="bg-netflix-red text-white p-4 rounded-full shadow-2xl hover:bg-netflix-redHover transition-transform hover:scale-110 focus:outline-none flex items-center justify-center group"
      >
        {isOpen ? <X size={28} /> : <Sparkles size={28} className="group-hover:animate-pulse" />}
      </button>
    </div>
  );
}
