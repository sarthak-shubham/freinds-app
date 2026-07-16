import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [allUsers, setAllUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch all users on mount
  useEffect(() => {
    api.getUsers()
      .then(res => {
        if (res.success && res.users.length > 0) {
          setAllUsers(res.users);

          // Restore saved user or default to first
          const savedEmail = localStorage.getItem('freinds-current-user');
          const restored = res.users.find(u => u.email === savedEmail);
          setCurrentUser(restored || res.users[0]);
        }
      })
      .catch(err => {
        console.error('Failed to load users:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  const switchUser = useCallback((user) => {
    setCurrentUser(user);
    localStorage.setItem('freinds-current-user', user.email);
  }, []);

  const value = {
    allUsers,
    currentUser,
    switchUser,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
