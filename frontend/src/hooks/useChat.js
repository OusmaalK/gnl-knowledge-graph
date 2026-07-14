/**
 * useChat - Hook pour la gestion du chat
 * ============================================================================
 * Description: Hook personnalisé pour la gestion des conversations de chat
 * ============================================================================
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useApi } from './useApi';
import { useWebSocket } from './useWebSocket';

export function useChat(conversationId = null) {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [agentType, setAgentType] = useState('diagnostic');
  const { get, post } = useApi();
  const { isConnected, sendChatMessage, lastMessage } = useWebSocket();
  const messagesEndRef = useRef(null);

  const loadMessages = useCallback(async (convId) => {
    if (!convId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await get(`/api/chat/messages/${convId}`);
      setMessages(data.messages || []);
    } catch (err) {
      setError(err.message);
      console.error('Erreur chargement messages:', err);
    } finally {
      setLoading(false);
    }
  }, [get]);

  const loadConversations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await get('/api/chat/conversations');
      setConversations(data.conversations || []);
    } catch (err) {
      console.error('Erreur chargement conversations:', err);
    } finally {
      setLoading(false);
    }
  }, [get]);

  const sendMessage = useCallback(async (question, agentType = 'diagnostic') => {
    if (!question.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setSending(true);
    setError(null);

    try {
      // Utiliser WebSocket si connecté
      if (isConnected) {
        const sent = sendChatMessage(question, agentType, conversationId);
        if (!sent) {
          // Fallback REST
          const response = await post('/api/chat', {
            question,
            agent_type: agentType,
            conversation_id: conversationId,
          });
          const agentMessage = {
            id: Date.now() + 1,
            role: 'agent',
            content: response.response,
            timestamp: new Date().toISOString(),
          };
          setMessages(prev => [...prev, agentMessage]);
        }
      } else {
        // REST API
        const response = await post('/api/chat', {
          question,
          agent_type: agentType,
          conversation_id: conversationId,
        });
        const agentMessage = {
          id: Date.now() + 1,
          role: 'agent',
          content: response.response,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, agentMessage]);
      }
    } catch (err) {
      setError(err.message);
      // Ajouter un message d'erreur
      const errorMessage = {
        id: Date.now() + 1,
        role: 'error',
        content: `❌ Erreur: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setSending(false);
    }
  }, [conversationId, isConnected, sendChatMessage, post]);

  const createConversation = useCallback(async (title = 'Nouvelle conversation') => {
    try {
      const data = await post('/api/chat/conversations', { title });
      await loadConversations();
      return data;
    } catch (err) {
      console.error('Erreur création conversation:', err);
      throw err;
    }
  }, [post, loadConversations]);

  const deleteConversation = useCallback(async (convId) => {
    try {
      await get(`/api/chat/conversations/${convId}/delete`);
      await loadConversations();
      if (conversationId === convId) {
        setMessages([]);
      }
      return true;
    } catch (err) {
      console.error('Erreur suppression conversation:', err);
      throw err;
    }
  }, [get, loadConversations, conversationId]);

  // Réception des messages WebSocket
  useEffect(() => {
    if (lastMessage?.type === 'response') {
      const agentMessage = {
        id: Date.now(),
        role: 'agent',
        content: lastMessage.content,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, agentMessage]);
      setSending(false);
    }
  }, [lastMessage]);

  // Chargement des conversations
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Chargement des messages
  useEffect(() => {
    if (conversationId) {
      loadMessages(conversationId);
    }
  }, [conversationId, loadMessages]);

  return {
    messages,
    conversations,
    loading,
    sending,
    error,
    agentType,
    setAgentType,
    sendMessage,
    loadMessages,
    loadConversations,
    createConversation,
    deleteConversation,
    messagesEndRef,
    isConnected,
  };
}