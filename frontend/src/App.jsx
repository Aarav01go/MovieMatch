import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Home from './pages/Home';
import Discover from './pages/Discover';
import MovieDetails from './pages/MovieDetails';
import TopPicks from './pages/TopPicks';
import MyList from './pages/MyList';
import Matchmaker from './pages/Matchmaker';
import FloatingAI from './components/FloatingAI';

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/discover" element={<ProtectedRoute><Discover /></ProtectedRoute>} />
        <Route path="/movie/:movieId" element={<ProtectedRoute><MovieDetails /></ProtectedRoute>} />
        <Route path="/top-picks" element={<ProtectedRoute><TopPicks /></ProtectedRoute>} />
        <Route path="/my-list" element={<ProtectedRoute><MyList /></ProtectedRoute>} />
        <Route path="/matchmaker" element={<ProtectedRoute><Matchmaker /></ProtectedRoute>} />
      </Routes>
      <FloatingAI />
    </BrowserRouter>
  );
}
export default App;
