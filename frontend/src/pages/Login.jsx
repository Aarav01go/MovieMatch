import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { setUser } = useAuth();
  const navigate = useNavigate();
  
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username) return;
    try {
      // The backend uses a "Get or Create" pattern based on username for ML profiles.
      // Password is included for UI realism but not strictly validated in the backend yet.
      const { data } = await api.post('/users', { username });
      setUser(data);
      navigate('/'); // Route the user into the app!
    } catch (err) {
      alert("Failed to login");
    }
  };

  return (
    <div className="min-h-screen bg-[url('https://assets.nflxext.com/ffe/siteui/vlv3/19448866-9ab5-4927-aa7c-87dcf2027e46/1c6d3d44-59e3-4dff-a64d-51d0da61d36c/US-en-20231113-popsignuptwoweeks-perspective_alpha_website_medium.jpg')] bg-cover bg-center">
      <div className="min-h-screen bg-black/60 flex flex-col items-center justify-center p-4">
        <h1 className="text-netflix-red font-black text-5xl mb-8 tracking-tighter">MOVIEMATCH</h1>
        <form onSubmit={handleLogin} className="bg-black/80 p-12 rounded-lg w-full max-w-md shadow-2xl">
          <h2 className="text-3xl font-bold text-white mb-6">Sign In</h2>
          
          <input 
            type="text" 
            placeholder="Username (e.g. guest)" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            className="w-full bg-gray-700 text-white p-3 rounded mb-4 outline-none focus:ring-2 focus:ring-gray-400" 
            required 
          />
          
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            className="w-full bg-gray-700 text-white p-3 rounded mb-8 outline-none focus:ring-2 focus:ring-gray-400" 
          />
          
          <button type="submit" className="w-full bg-netflix-red hover:bg-netflix-redHover text-white font-bold py-3 rounded transition">
            Start Watching
          </button>
          
          <p className="text-gray-400 text-sm mt-6">
            New to MovieMatch? <span className="text-white hover:underline cursor-pointer">Sign up now.</span>
          </p>
        </form>
      </div>
    </div>
  );
}
