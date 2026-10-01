import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, setUser } = useAuth();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 w-full z-50 transition-colors duration-300 ${scrolled ? 'bg-netflix-black' : 'bg-gradient-to-b from-black/80 to-transparent'}`}>
      <div className="flex items-center justify-between px-4 md:px-12 py-4">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-netflix-red font-black text-2xl tracking-tighter">MOVIEMATCH</Link>
          <div className="hidden md:flex gap-4 text-sm font-semibold text-gray-300">
            <Link to="/" className="hover:text-white transition">Home</Link>
            <Link to="/discover" className="hover:text-white transition">Discover</Link>
            <Link to="/top-picks" className="hover:text-white transition">Top Picks</Link>
            <Link to="/my-list" className="hover:text-white transition">My List</Link>
          </div>
        </div>
        <div className="flex items-center gap-6 text-white">
          <Link to="/discover"><Search size={20} className="cursor-pointer hover:text-gray-400" /></Link>
          <div className="flex items-center gap-2 cursor-pointer group">
            <User size={20} />
            <span className="text-sm font-semibold">{user?.username}</span>
            <div className="hidden group-hover:block absolute top-12 right-12 bg-netflix-black border border-gray-800 p-4 rounded shadow-xl">
              <button onClick={() => setUser(null)} className="text-sm hover:text-netflix-red transition">Sign Out</button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
