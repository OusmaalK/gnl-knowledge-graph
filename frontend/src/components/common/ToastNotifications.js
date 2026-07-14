/**
 * ToastNotifications - Notifications toast
 * ============================================================================
 * Description: Composant de notifications toast
 * ============================================================================
 */

'use client';

import { useEffect } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export function ToastNotifications() {
  useEffect(() => {
    // Configuration globale
    toast.configure({
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  }, []);

  return (
    <ToastContainer
      position="top-right"
      autoClose={5000}
      hideProgressBar={false}
      newestOnTop
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="colored"
    />
  );
}

// Helpers pour les notifications
export const showSuccess = (message) => {
  toast.success(message, {
    icon: '✅',
    style: {
      background: '#10B981',
      color: 'white',
    },
  });
};

export const showError = (message) => {
  toast.error(message, {
    icon: '❌',
    style: {
      background: '#EF4444',
      color: 'white',
    },
  });
};

export const showWarning = (message) => {
  toast.warning(message, {
    icon: '⚠️',
    style: {
      background: '#F59E0B',
      color: 'white',
    },
  });
};

export const showInfo = (message) => {
  toast.info(message, {
    icon: 'ℹ️',
    style: {
      background: '#3B82F6',
      color: 'white',
    },
  });
};