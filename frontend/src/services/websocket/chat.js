/**
 * Chat WebSocket - Gestion du WebSocket pour le chat
 * ============================================================================
 * Description: Client WebSocket pour le chat en temps réel
 * ============================================================================
 */

import { toast } from 'react-hot-toast';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export class ChatWebSocket {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.isConnecting = false;
    this.messageQueue = [];
    this.reconnectTimeout = null;
  }

  /**
   * Établit la connexion WebSocket
   */
  connect() {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;

    try {
      const url = `${WS_URL}/ws/chat`;
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connecté');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.emit('connected', { status: 'connected' });

        // Envoyer les messages en file d'attente
        while (this.messageQueue.length > 0) {
          const message = this.messageQueue.shift();
          this.send(message);
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
        } catch (error) {
          console.error('Erreur parsing WebSocket message:', error);
          this.emit('error', { error: 'Erreur de parsing' });
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔒 WebSocket déconnecté');
        this.isConnected = false;
        this.isConnecting = false;
        this.emit('disconnected', { status: 'disconnected', code: event.code });
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('❌ Erreur WebSocket:', error);
        this.isConnected = false;
        this.isConnecting = false;
        this.emit('error', { error });
      };
    } catch (error) {
      console.error('Erreur WebSocket:', error);
      this.isConnecting = false;
      this.reconnect();
    }
  }

  /**
   * Tentative de reconnexion
   */
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnect attempts reached');
      this.emit('error', { error: 'Impossible de se reconnecter' });
      toast.error('Erreur de connexion au serveur de chat');
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    console.log(`🔄 Tentative de reconnexion ${this.reconnectAttempts}/${this.maxReconnectAttempts} dans ${delay}ms`);
    this.emit('reconnecting', { attempt: this.reconnectAttempts, delay });

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Envoie un message
   */
  send(message) {
    if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
      try {
        const payload = typeof message === 'string' ? message : JSON.stringify(message);
        this.ws.send(payload);
        return true;
      } catch (error) {
        console.error('Erreur envoi message:', error);
        this.messageQueue.push(message);
        return false;
      }
    }

    // Mettre en file d'attente
    this.messageQueue.push(message);
    if (!this.isConnecting && !this.isConnected) {
      this.connect();
    }
    return false;
  }

  /**
   * Envoie un message de chat
   */
  sendChatMessage(question, agentType = 'diagnostic', conversationId = null) {
    return this.send({
      type: 'chat',
      question,
      agent_type: agentType,
      conversation_id: conversationId || `conv_${Date.now()}`,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Envoie une demande de diagnostic
   */
  sendDiagnosticRequest(incidentId) {
    return this.send({
      type: 'diagnostic',
      incident_id: incidentId,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Envoie une demande de route
   */
  sendRouteRequest(params) {
    return this.send({
      type: 'route',
      ...params,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Envoie une demande de risque
   */
  sendRiskRequest(equipmentId) {
    return this.send({
      type: 'risk',
      equipment_id: equipmentId,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Enregistre un écouteur d'événement
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Supprime un écouteur d'événement
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index !== -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Émet un événement
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Erreur dans l'écouteur ${event}:`, error);
        }
      });
    }
  }

  /**
   * Déconnecte le WebSocket
   */
  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.isConnected = false;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.messageQueue = [];
    this.emit('disconnected', { status: 'disconnected' });
    console.log('🔒 WebSocket déconnecté manuellement');
  }

  /**
   * Vérifie si le WebSocket est connecté
   */
  getConnected() {
    return this.isConnected;
  }

  /**
   * Récupère le statut de la connexion
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      isConnecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      queueLength: this.messageQueue.length,
    };
  }

  /**
   * Nettoie les ressources
   */
  destroy() {
    this.disconnect();
    this.listeners.clear();
  }
}

// Instance singleton
export const chatWebSocket = new ChatWebSocket();

export default chatWebSocket;