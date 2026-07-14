// frontend/src/hooks/useAuth.js
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();

  // Ne pas utiliser useApi à l'intérieur de useAuth
  // pour éviter la circularité

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, { email, password });
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setUser(user);
      
      return user;
    } catch (err) {
      setError(err.message || 'Erreur de connexion');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    router.push('/login');
  }, [router]);

  return {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
  };
}