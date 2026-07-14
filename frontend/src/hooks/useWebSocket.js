'use client';

import { useState, useCallback } from 'react';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [isManualMode, setIsManualMode] = useState(false);

  const toggleMode = useCallback(() => {
    const newMode = !isManualMode;
    setIsManualMode(newMode);
    setIsConnected(newMode); // ON = connecté, OFF = déconnecté
    console.log(newMode ? '🔌 Mode connecté (REST)' : '🔌 Mode simulation');
  }, [isManualMode]);

  const sendMessage = useCallback((message) => {
    console.log('📤 Message:', message);
    return true;
  }, []);

  return {
    isConnected,
    isManualMode,
    sendMessage,
    toggleMode,
  };
}