/**
 * RouteFinder - Recherche de routes
 * ============================================================================
 * Description: Interface de recherche de routes dans le réseau GNL
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiSearch, FiMapPin, FiMap } from 'react-icons/fi';
import { LoadingSpinner } from '../common/LoadingSpinner';

export function RouteFinder({ onSearch, loading }) {
  const [startId, setStartId] = useState('');
  const [endId, setEndId] = useState('');
  const [excludeId, setExcludeId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const validateInputs = () => {
    if (!startId.trim()) {
      setError('Veuillez spécifier un départ');
      return false;
    }
    if (!endId.trim()) {
      setError('Veuillez spécifier une arrivée');
      return false;
    }
    setError('');
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateInputs()) return;

    setIsSubmitting(true);
    try {
      await onSearch({
        start_id: startId.toUpperCase(),
        end_id: endId.toUpperCase(),
        exclude_id: excludeId.toUpperCase() || undefined,
      });
    } catch (err) {
      setError('Erreur lors de la recherche');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        🗺️ Trouver une route
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            <FiMapPin className="inline mr-1" />
            Départ
          </label>
          <input
            type="text"
            value={startId}
            onChange={(e) => setStartId(e.target.value.toUpperCase())}
            placeholder="ex: TERM-001"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">ID du terminal ou pipeline de départ</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            <FiMapPin className="inline mr-1" />
            Arrivée
          </label>
          <input
            type="text"
            value={endId}
            onChange={(e) => setEndId(e.target.value.toUpperCase())}
            placeholder="ex: CLIENT-001"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">ID du client ou pipeline d'arrivée</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            <FiMap className="inline mr-1" />
            Équipement à exclure (optionnel)
          </label>
          <input
            type="text"
            value={excludeId}
            onChange={(e) => setExcludeId(e.target.value.toUpperCase())}
            placeholder="ex: PIPE-001 (en panne)"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Équipement à éviter sur le chemin</p>
        </div>

        {error && (
          <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting || loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isSubmitting || loading ? (
            <LoadingSpinner size="small" color="white" />
          ) : (
            <>
              <FiSearch className="w-4 h-4" />
              <span>Rechercher la route</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          💡 Exemples de recherche :<br />
          - TERM-001 → CLIENT-001<br />
          - TERM-001 → CLIENT-001 (exclure PIPE-001)
        </p>
      </div>
    </div>
  );
}

// ✅ EXPORT PAR DÉFAUT (AJOUTER)
export default RouteFinder;