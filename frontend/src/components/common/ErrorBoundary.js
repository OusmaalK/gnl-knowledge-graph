/**
 * ErrorBoundary - Gestionnaire d'erreurs
 * ============================================================================
 * Description: Boundary d'erreur pour capturer les erreurs React
 * ============================================================================
 */

'use client';

import { Component } from 'react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Erreur capturée par ErrorBoundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
          <div className="text-6xl mb-4">💥</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Oups ! Une erreur est survenue
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {this.state.error?.message || 'Une erreur inattendue s\'est produite'}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}