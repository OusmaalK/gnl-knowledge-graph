/**
 * ChatInterface - Interface de chat avec interrupteur ON/OFF
 * Version avec support REST en priorité pour des réponses réelles
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { useApi } from '@/hooks/useApi';
import { useWebSocket } from '@/hooks/useWebSocket';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { MessageList } from './MessageList';
import { FiSend, FiRefreshCw } from 'react-icons/fi';

export function ChatInterface({ agentType, conversationId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const { isConnected, isManualMode, toggleMode, lastMessage } = useWebSocket();
  const { api, post, get } = useApi();
  const messagesEndRef = useRef(null);

  // Messages de bienvenue
  const welcomeMessages = [
    {
      id: 'welcome-1',
      role: 'system',
      content: '👋 Bonjour ! Je suis votre assistant GNL. ' + 
               (isManualMode ? '🔌 Mode connecté' : '📡 Mode hors-ligne'),
      timestamp: new Date().toISOString(),
    }
  ];

  useEffect(() => {
    setMessages(welcomeMessages);
  }, []);

  // Mise à jour du statut quand le mode change
  useEffect(() => {
    const statusMsg = isManualMode ? '🔌 Mode connecté activé' : '📡 Mode hors-ligne activé';
    addMessage('system', statusMsg);
  }, [isManualMode]);

  // Réception des messages WebSocket
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'response') {
      addMessage('agent', lastMessage.content);
      setLoading(false);
    }
  }, [lastMessage]);

  const generateUniqueId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const addMessage = (role, content) => {
    setMessages(prev => [...prev, {
      id: generateUniqueId(),
      role,
      content,
      timestamp: new Date().toISOString(),
    }]);
  };

  // ✅ RÉPONSES RÉELLES VIA REST (PRIORITAIRE)
  const getRealResponse = async (userMessage) => {
    try {
      const response = await post('/api/agents/chat', {
        question: userMessage,
        agent_type: agentType,
        conversation_id: conversationId,
      });
      
      if (response && response.response) {
        return response.response;
      }
      return null;
    } catch (error) {
      console.error('❌ Erreur REST:', error);
      return null;
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    addMessage('user', userMessage);
    setLoading(true);

    try {
      if (isManualMode) {
        // ✅ MODE ON : TENTER D'ABORD LE REST (RÉPONSES RÉELLES)
        const realResponse = await getRealResponse(userMessage);
        
        if (realResponse) {
          addMessage('agent', realResponse);
        } else {
          // Fallback simulation si REST échoue
          addMessage('system', '⚠️ Backend indisponible - Mode simulation');
          addMessage('agent', getMockResponse(userMessage, agentType));
        }
      } else {
        // ✅ MODE OFF : Simulation
        addMessage('agent', getMockResponse(userMessage, agentType));
      }
    } catch (error) {
      addMessage('error', `❌ Erreur: ${error.message}`);
      addMessage('agent', getMockResponse(userMessage, agentType));
    } finally {
      setLoading(false);
    }
  };

  const getMockResponse = (question, type) => {
    const responses = {
      diagnostic: `🔍 **Diagnostic en cours... (Mode simulation)**

📋 **Information reçue :** "${question}"

🔧 **Recommandations :**
- Inspecter l'équipement concerné
- Vérifier l'historique des incidents
- Planifier une maintenance préventive

💡 *Activez le mode connecté pour des réponses réelles.*`,

      incident: `📋 **Gestion des incidents (Mode simulation)**

Analyse de votre demande : "${question}"

📊 **Statistiques simulées :**
- Incidents critiques : 1
- Incidents en cours : 2
- Incidents résolus : 3`,

      logistics: `🗺️ **Analyse logistique (Mode simulation)**

Votre demande : "${question}"

🚚 **Informations simulées :**
- Route : TERM-001 → PIPE-001 → CLIENT-001
- Distance : 2 sauts
- Statut : Actif`,

      maintenance: `🔧 **Maintenance prédictive (Mode simulation)**

Analyse : "${question}"

📈 **Score de risque :** 65/100 (ÉLEVÉ)

⚠️ **Recommandations :**
- Inspection dans les 30 jours
- Surveillance renforcée`
    };
    return responses[type] || responses.diagnostic;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { label: '🔍 Diagnostiquer INC-001', action: "Diagnostiquer l'incident INC-001" },
    { label: '🗺️ Route TERM-001 → CLIENT-001', action: "Trouver la route entre TERM-001 et CLIENT-001" },
    { label: '📊 Risque PIPE-001', action: "Analyser le risque de PIPE-001" },
    { label: '📋 Historique PIPE-001', action: "Afficher l'historique de PIPE-001" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* En-tête avec interrupteur */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className={`w-2 h-2 rounded-full ${isManualMode && isConnected ? 'bg-green-500 animate-pulse' : isManualMode ? 'bg-yellow-500' : 'bg-red-500'}`} />
          <span className={`text-sm font-medium ${isManualMode && isConnected ? 'text-green-600' : isManualMode ? 'text-yellow-600' : 'text-red-600'}`}>
            {isManualMode && isConnected ? '🟢 Connecté' : isManualMode ? '🟡 En attente' : '🔴 Déconnecté'}
          </span>
          <span className="text-sm text-gray-400">|</span>
          <span className="text-sm text-gray-500 dark:text-gray-400">Agent: {agentType}</span>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Interrupteur ON/OFF */}
          <div className="flex items-center space-x-2">
            <span className={`text-xs font-medium ${!isManualMode ? 'text-gray-400' : 'text-green-600'}`}>
              OFF
            </span>
            <button
              onClick={toggleMode}
              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isManualMode ? 'bg-green-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
              title={isManualMode ? 'Mode connecté (ON)' : 'Mode simulation (OFF)'}
            >
              <span
                className={`inline-block w-4 h-4 transform transition-transform bg-white rounded-full ${
                  isManualMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-xs font-medium ${isManualMode ? 'text-green-600' : 'text-gray-400'}`}>
              ON
            </span>
          </div>
          
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {isManualMode ? (isConnected ? '🔌 Connecté' : '📡 Connexion...') : '💻 Simulation'}
          </span>
          
          <button
            onClick={() => window.location.reload()}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Rafraîchir"
          >
            <FiRefreshCw className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} loading={loading} />
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-800">
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => setInput(action.action)}
              className="text-xs px-3 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-colors text-gray-700 dark:text-gray-300"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez votre question sur le réseau GNL..."
            className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading ? (
              <LoadingSpinner size="small" color="white" />
            ) : (
              <>
                <FiSend className="w-4 h-4" />
                <span>Envoyer</span>
              </>
            )}
          </button>
        </div>
        
        {/* Statut du mode */}
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs">
            {isManualMode && isConnected ? (
              <span className="text-green-600 dark:text-green-400">✅ Mode connecté - Réponses réelles</span>
            ) : isManualMode ? (
              <span className="text-yellow-600 dark:text-yellow-400">⏳ Connexion en cours...</span>
            ) : (
              <span className="text-gray-500 dark:text-gray-400">💻 Mode simulation - Réponses locales</span>
            )}
          </p>
          <span className="text-xs text-gray-400">
            {isManualMode ? (isConnected ? '🔌 WebSocket' : '📡 Reconnexion...') : '📁 Local'}
          </span>
        </div>
      </div>
    </div>
  );
}