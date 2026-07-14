/**
 * useApi - Hook pour les appels API
 * ============================================================================
 * Description: Hook personnalisé pour les appels API avec gestion d'état
 * ============================================================================
 */

'use client';

import { useState, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './useAuth';

// Configuration de base d'axios
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`,
          { refresh_token: refreshToken }
        );
        localStorage.setItem('access_token', response.data.access_token);
        apiClient.defaults.headers.common.Authorization = `Bearer ${response.data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user, logout } = useAuth();

  const request = useCallback(async (config) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient(config);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Une erreur est survenue';
      setError(errorMessage);
      
      // Gestion des erreurs d'authentification
      if (err.response?.status === 401) {
        logout();
      }
      
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [logout]);

  const get = useCallback((url, params = {}) => {
    return request({ method: 'GET', url, params });
  }, [request]);

  const post = useCallback((url, data = {}) => {
    return request({ method: 'POST', url, data });
  }, [request]);

  const put = useCallback((url, data = {}) => {
    return request({ method: 'PUT', url, data });
  }, [request]);

  const patch = useCallback((url, data = {}) => {
    return request({ method: 'PATCH', url, data });
  }, [request]);

  const del = useCallback((url) => {
    return request({ method: 'DELETE', url });
  }, [request]);

  // Méthodes spécifiques pour l'API GNL
  const getStatistics = useCallback(() => {
    return get('/api/statistics');
  }, [get]);

  const getIncidents = useCallback((params = {}) => {
    return get('/api/incidents', params);
  }, [get]);

  const getIncident = useCallback((id) => {
    return get(`/api/incidents/${id}`);
  }, [get]);

  const getRisk = useCallback((equipmentId) => {
    return get(`/api/risk/${equipmentId}`);
  }, [get]);

  const findRoute = useCallback((params) => {
    return post('/api/routes', params);
  }, [post]);

  const chat = useCallback((message) => {
    return post('/api/chat', message);
  }, [post]);

  const getEquipment = useCallback((id) => {
    return get(`/api/equipment/${id}`);
  }, [get]);

  const getSupplyChain = useCallback(() => {
    return get('/api/supply-chain');
  }, [get]);

  const analyzeImpact = useCallback((equipmentId) => {
    return get(`/api/impact/${equipmentId}`);
  }, [get]);

  return {
    apiClient,
    loading,
    error,
    get,
    post,
    put,
    patch,
    delete: del,
    getStatistics,
    getIncidents,
    getIncident,
    getRisk,
    findRoute,
    chat,
    getEquipment,
    getSupplyChain,
    analyzeImpact,
  };
}