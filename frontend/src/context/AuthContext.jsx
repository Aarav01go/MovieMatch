import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Initialize state from localStorage if it exists
  const [user, setUser] = useState(() => {
    try {
      const storedUser = localStorage.getItem('movieMatchUser');
      return storedUser ? JSON.parse(storedUser) : null;
    } catch (e) {
      return null;
    }
  });

  // Whenever user state changes, sync it to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('movieMatchUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('movieMatchUser');
    }
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
