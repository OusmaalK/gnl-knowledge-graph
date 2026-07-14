/**
 * Auth Store - Gestion d'état de l'authentification
 * ============================================================================
 * Description: Store Zustand pour la gestion de l'authentification
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useAuthStore = create(
  devtools(
    persist(
      immer((set, get) => ({
        // État
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        permissions: [],
        roles: [],

        // Actions - Auth
        setUser: (user) => set({ user }),
        setToken: (token) => set({ token }),
        setRefreshToken: (refreshToken) => set({ refreshToken }),
        setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
        
        login: (user, token, refreshToken) => set({
          user,
          token,
          refreshToken,
          isAuthenticated: true,
          error: null,
        }),

        logout: () => set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        }),

        updateUser: (updates) => set((state) => {
          state.user = { ...state.user, ...updates };
        }),

        // Actions - Permissions
        setPermissions: (permissions) => set({ permissions }),
        setRoles: (roles) => set({ roles }),

        hasPermission: (permission) => {
          const { permissions } = get();
          return permissions.includes(permission);
        },

        hasRole: (role) => {
          const { roles } = get();
          return roles.includes(role);
        },

        // Actions - UI
        setLoading: (isLoading) => set({ isLoading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),

        // Actions - Reset
        reset: () => set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
          permissions: [],
          roles: [],
        }),

        // Selectors (computed)
        getCurrentUser: () => {
          const { user } = get();
          return user;
        },

        getToken: () => {
          const { token } = get();
          return token;
        },

        isTokenValid: () => {
          const { token } = get();
          if (!token) return false;
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp > Date.now() / 1000;
          } catch {
            return false;
          }
        },

        getUserFullName: () => {
          const { user } = get();
          if (!user) return '';
          return `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username || user.email || '';
        },

        getUserAvatar: () => {
          const { user } = get();
          return user?.avatar || null;
        },
      })),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          refreshToken: state.refreshToken,
          isAuthenticated: state.isAuthenticated,
          permissions: state.permissions,
          roles: state.roles,
        }),
      }
    )
  )
);