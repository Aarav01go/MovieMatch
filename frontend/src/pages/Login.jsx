import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [slowNotice, setSlowNotice] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setError('');
    setSlowNotice(false);

    // If server takes > 5s, show a "waking up" notice (Render free tier cold start)
    const slowTimer = setTimeout(() => setSlowNotice(true), 5000);

    try {
      const { data } = await api.post('/users', { username: username.trim() });
      clearTimeout(slowTimer);
      setUser(data);
      navigate('/');
    } catch (err) {
      clearTimeout(slowTimer);
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError('Cannot reach the server. Please wait a moment and try again — it may be waking up.');
      } else if (err.response?.status >= 500) {
        setError('Server error. Please try again in a few seconds.');
      } else {
        setError('Login failed. Please check your username and try again.');
      }
    } finally {
      setLoading(false);
      setSlowNotice(false);
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
            disabled={loading}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full bg-gray-700 text-white p-3 rounded mb-4 outline-none focus:ring-2 focus:ring-gray-400"
            disabled={loading}
          />

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-900/60 border border-red-500 rounded text-red-300 text-sm">
              {error}
            </div>
          )}

          {/* Slow server notice (Render free tier cold start) */}
          {slowNotice && (
            <div className="mb-4 p-3 bg-yellow-900/60 border border-yellow-500 rounded text-yellow-300 text-sm">
              ⏳ Server is waking up… this can take up to 60 seconds on the free tier. Hang tight!
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-netflix-red hover:bg-netflix-redHover disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold py-3 rounded transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Connecting…
              </>
            ) : (
              'Start Watching'
            )}
          </button>

          <p className="text-gray-400 text-sm mt-6">
            New to MovieMatch? <span className="text-white hover:underline cursor-pointer">Sign up now.</span>
          </p>
        </form>
      </div>
    </div>
  );
}
