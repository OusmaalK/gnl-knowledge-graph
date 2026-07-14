/**
 * UI Store - Gestion d'état de l'interface utilisateur
 * ============================================================================
 * Description: Store Zustand pour la gestion de l'UI
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useUIStore = create(
  devtools(
    persist(
      immer((set, get) => ({
        // État
        theme: 'system',
        sidebarCollapsed: false,
        sidebarOpen: true,
        notifications: [],
        modals: [],
        loading: false,
        error: null,
        breadcrumbs: [],
        searchQuery: '',
        searchResults: [],
        isSearching: false,

        // Actions - Theme
        setTheme: (theme) => set({ theme }),
        toggleTheme: () => set((state) => {
          const themes = ['light', 'dark', 'system'];
          const currentIndex = themes.indexOf(state.theme);
          state.theme = themes[(currentIndex + 1) % themes.length];
        }),

        // Actions - Sidebar
        toggleSidebar: () => set((state) => {
          state.sidebarCollapsed = !state.sidebarCollapsed;
        }),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        toggleSidebarOpen: () => set((state) => {
          state.sidebarOpen = !state.sidebarOpen;
        }),

        // Actions - Notifications
        addNotification: (notification) => set((state) => {
          state.notifications.unshift({
            id: Date.now(),
            timestamp: new Date().toISOString(),
            read: false,
            ...notification,
          });
          if (state.notifications.length > 50) {
            state.notifications = state.notifications.slice(0, 50);
          }
        }),
        markNotificationRead: (notificationId) => set((state) => {
          const index = state.notifications.findIndex(n => n.id === notificationId);
          if (index !== -1) {
            state.notifications[index].read = true;
          }
        }),
        markAllNotificationsRead: () => set((state) => {
          state.notifications.forEach(n => n.read = true);
        }),
        removeNotification: (notificationId) => set((state) => {
          state.notifications = state.notifications.filter(n => n.id !== notificationId);
        }),
        clearNotifications: () => set({ notifications: [] }),

        // Actions - Modals
        openModal: (modal) => set((state) => {
          state.modals.push({
            id: Date.now(),
            ...modal,
          });
        }),
        closeModal: (modalId) => set((state) => {
          state.modals = state.modals.filter(m => m.id !== modalId);
        }),
        closeAllModals: () => set({ modals: [] }),

        // Actions - Breadcrumbs
        setBreadcrumbs: (breadcrumbs) => set({ breadcrumbs }),
        addBreadcrumb: (breadcrumb) => set((state) => {
          state.breadcrumbs.push(breadcrumb);
        }),
        removeLastBreadcrumb: () => set((state) => {
          state.breadcrumbs.pop();
        }),
        clearBreadcrumbs: () => set({ breadcrumbs: [] }),

        // Actions - Search
        setSearchQuery: (query) => set({ searchQuery: query }),
        setSearchResults: (results) => set({ searchResults: results }),
        clearSearch: () => set({ searchQuery: '', searchResults: [] }),
        setIsSearching: (isSearching) => set({ isSearching }),

        // Actions - Loading/Error
        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),

        // Actions - Reset
        reset: () => set({
          sidebarCollapsed: false,
          sidebarOpen: true,
          notifications: [],
          modals: [],
          loading: false,
          error: null,
          breadcrumbs: [],
          searchQuery: '',
          searchResults: [],
          isSearching: false,
        }),

        // Selectors (computed)
        getUnreadNotifications: () => {
          const { notifications } = get();
          return notifications.filter(n => !n.read);
        },

        getUnreadCount: () => {
          const { notifications } = get();
          return notifications.filter(n => !n.read).length;
        },

        isModalOpen: (modalId) => {
          const { modals } = get();
          return modals.some(m => m.id === modalId);
        },

        getCurrentModal: () => {
          const { modals } = get();
          return modals.length > 0 ? modals[modals.length - 1] : null;
        },
      })),
      {
        name: 'ui-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    )
  )
);