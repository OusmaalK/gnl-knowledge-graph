/**
 * Notification Store - Gestion d'état des notifications
 * ============================================================================
 * Description: Store Zustand pour la gestion des notifications
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useNotificationStore = create(
  devtools(
    immer((set, get) => ({
      // État
      notifications: [],
      unreadCount: 0,
      isOpen: false,

      // Actions - Notifications
      add: (notification) => set((state) => {
        state.notifications.unshift({
          id: Date.now(),
          timestamp: new Date().toISOString(),
          read: false,
          ...notification,
        });
        state.unreadCount += 1;
        if (state.notifications.length > 100) {
          state.notifications = state.notifications.slice(0, 100);
        }
      }),

      addSuccess: (message, title = 'Succès') => {
        get().add({
          type: 'success',
          title,
          message,
          icon: '✅',
        });
      },

      addError: (message, title = 'Erreur') => {
        get().add({
          type: 'error',
          title,
          message,
          icon: '❌',
        });
      },

      addWarning: (message, title = 'Attention') => {
        get().add({
          type: 'warning',
          title,
          message,
          icon: '⚠️',
        });
      },

      addInfo: (message, title = 'Information') => {
        get().add({
          type: 'info',
          title,
          message,
          icon: 'ℹ️',
        });
      },

      markAsRead: (notificationId) => set((state) => {
        const index = state.notifications.findIndex(n => n.id === notificationId);
        if (index !== -1 && !state.notifications[index].read) {
          state.notifications[index].read = true;
          state.unreadCount -= 1;
        }
      }),

      markAllAsRead: () => set((state) => {
        state.notifications.forEach(n => n.read = true);
        state.unreadCount = 0;
      }),

      remove: (notificationId) => set((state) => {
        const index = state.notifications.findIndex(n => n.id === notificationId);
        if (index !== -1) {
          if (!state.notifications[index].read) {
            state.unreadCount -= 1;
          }
          state.notifications.splice(index, 1);
        }
      }),

      clearAll: () => set({
        notifications: [],
        unreadCount: 0,
      }),

      // Actions - UI
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      toggle: () => set((state) => {
        state.isOpen = !state.isOpen;
      }),

      // Actions - Reset
      reset: () => set({
        notifications: [],
        unreadCount: 0,
        isOpen: false,
      }),

      // Selectors (computed)
      getUnread: () => {
        const { notifications } = get();
        return notifications.filter(n => !n.read);
      },

      getRecent: (limit = 10) => {
        const { notifications } = get();
        return notifications.slice(0, limit);
      },

      getByType: (type) => {
        const { notifications } = get();
        return notifications.filter(n => n.type === type);
      },

      hasNotifications: () => {
        const { notifications } = get();
        return notifications.length > 0;
      },

      hasUnread: () => {
        const { unreadCount } = get();
        return unreadCount > 0;
      },
    }))
  )
);