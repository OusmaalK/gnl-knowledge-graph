/**
 * Chat - Assistant IA
 * ============================================================================
 * Description: Interface de chat avec les agents IA
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { AgentSelector } from '@/components/chat/AgentSelector';
import { ChatHistory } from '@/components/chat/ChatHistory';
import { useWebSocket } from '@/hooks/useWebSocket';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export default function ChatPage() {
  const [agentType, setAgentType] = useState('diagnostic');
  const [conversationId, setConversationId] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // ✅ Récupérer les fonctions du hook
  const { isConnected, isManualMode, toggleMode, sendMessage, lastMessage } = useWebSocket();

  useEffect(() => {
    // ✅ Ne pas appeler connect() automatiquement
    // La connexion est gérée par l'interrupteur dans ChatInterface
    // Charger l'historique des conversations
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      // Charger l'historique depuis l'API
      // const data = await get('/api/chat/history');
      // setHistory(data);
    } catch (error) {
      console.error('Erreur chargement historique:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    setConversationId(Date.now().toString());
    setHistory([]);
  };

  const handleAgentChange = (type) => {
    setAgentType(type);
  };

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col p-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              🤖 Assistant IA GNL
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Dialoguez avec nos agents pour analyser le réseau GNL
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Statut de connexion */}
           
            
            <AgentSelector 
              value={agentType}
              onChange={handleAgentChange}
            />
            <button
              onClick={handleNewConversation}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Nouvelle conversation
            </button>
          </div>
        </div>

        {/* Interface de chat */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">
          {/* Historique des conversations */}
          <div className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                📋 Historique
              </h3>
            </div>
            <div className="h-[500px] overflow-y-auto">
              {loading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner size="small" />
                </div>
              ) : (
                <ChatHistory 
                  conversations={history}
                  onSelect={(id) => setConversationId(id)}
                  selectedId={conversationId}
                />
              )}
            </div>
          </div>

          {/* Chat principal */}
          <div className="lg:col-span-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <ChatInterface 
              agentType={agentType}
              conversationId={conversationId}
            />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}