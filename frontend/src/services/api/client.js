/**
 * API Client - Configuration et intercepteurs
 * ============================================================================
 * Description: Client HTTP avec intercepteurs pour authentification et erreurs
 * ============================================================================
 */

import axios from 'axios';
import { toast } from 'react-hot-toast';

// Configuration de base
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

// Création du client
export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Intercepteur de requête - Ajout du token
apiClient.interceptors.request.use(
  (config) => {
    // Récupérer le token depuis le store ou localStorage
    let token = null;
    try {
      const store = require('@/store/authStore').useAuthStore.getState();
      token = store.token || localStorage.getItem('access_token');
    } catch {
      token = localStorage.getItem('access_token');
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Ajouter le request ID pour le tracing
    config.headers['X-Request-ID'] = `${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;

    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur de réponse - Gestion des erreurs
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Gestion des erreurs 401 (token expiré)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Mettre à jour le header et réessayer
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Nettoyer les tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // Rediriger vers login
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    // Gestion des erreurs courantes
    const status = error.response?.status;
    const message = error.response?.data?.message || error.response?.data?.error || error.message;

    // Afficher les toasts d'erreur
    if (typeof window !== 'undefined') {
      if (status === 400) {
        toast.error(`Erreur de requête: ${message}`);
      } else if (status === 403) {
        toast.error('Accès non autorisé');
      } else if (status === 404) {
        toast.error('Ressource non trouvée');
      } else if (status === 422) {
        const errors = error.response?.data?.errors || {};
        const firstError = Object.values(errors)[0]?.[0] || message;
        toast.error(`Erreur de validation: ${firstError}`);
      } else if (status === 500) {
        toast.error('Erreur interne du serveur');
      } else if (status !== 401) {
        toast.error(message || 'Une erreur est survenue');
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;