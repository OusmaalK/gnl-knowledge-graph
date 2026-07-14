/**
 * Chat Store - Gestion d'état du chat
 * ============================================================================
 * Description: Store Zustand pour la gestion du chat
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useChatStore = create(
  devtools(
    immer((set, get) => ({
      // État
      messages: [],
      conversations: [],
      currentConversationId: null,
      agentType: 'diagnostic',
      loading: false,
      sending: false,
      error: null,
      isConnected: false,

      // Actions - Messages
      setMessages: (messages) => set({ messages }),
      addMessage: (message) => set((state) => {
        state.messages.push({
          id: Date.now(),
          timestamp: new Date().toISOString(),
          ...message,
        });
      }),
      addMessages: (messages) => set((state) => {
        state.messages.push(...messages);
      }),
      clearMessages: () => set({ messages: [] }),
      updateMessage: (messageId, updates) => set((state) => {
        const index = state.messages.findIndex(m => m.id === messageId);
        if (index !== -1) {
          state.messages[index] = { ...state.messages[index], ...updates };
        }
      }),
      removeMessage: (messageId) => set((state) => {
        state.messages = state.messages.filter(m => m.id !== messageId);
      }),

      // Actions - Conversations
      setConversations: (conversations) => set({ conversations }),
      addConversation: (conversation) => set((state) => {
        state.conversations.unshift(conversation);
      }),
      updateConversation: (conversationId, updates) => set((state) => {
        const index = state.conversations.findIndex(c => c.id === conversationId);
        if (index !== -1) {
          state.conversations[index] = { ...state.conversations[index], ...updates };
        }
      }),
      removeConversation: (conversationId) => set((state) => {
        state.conversations = state.conversations.filter(c => c.id !== conversationId);
      }),
      setCurrentConversation: (conversationId) => set({ 
        currentConversationId: conversationId 
      }),

      // Actions - Agent
      setAgentType: (agentType) => set({ agentType }),

      // Actions - UI
      setLoading: (loading) => set({ loading }),
      setSending: (sending) => set({ sending }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
      setConnected: (isConnected) => set({ isConnected }),

      // Actions - Reset
      reset: () => set({
        messages: [],
        conversations: [],
        currentConversationId: null,
        loading: false,
        sending: false,
        error: null,
      }),

      // Selectors (computed)
      getCurrentConversation: () => {
        const { conversations, currentConversationId } = get();
        return conversations.find(c => c.id === currentConversationId);
      },

      getMessagesByConversation: (conversationId) => {
        const { messages } = get();
        return messages.filter(m => m.conversationId === conversationId);
      },

      getLastMessage: () => {
        const { messages } = get();
        return messages.length > 0 ? messages[messages.length - 1] : null;
      },

      getUnreadCount: () => {
        const { messages } = get();
        return messages.filter(m => !m.read && m.role === 'agent').length;
      },
    }))
  )
);