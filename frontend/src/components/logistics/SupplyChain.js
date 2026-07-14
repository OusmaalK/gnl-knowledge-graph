/**
 * SupplyChain - Chaîne d'approvisionnement
 * ============================================================================
 * Description: Visualisation de la chaîne d'approvisionnement GNL
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiChevronDown, FiChevronRight } from 'react-icons/fi';

// Données simulées par défaut
const defaultData = [
  {
    fournisseur: 'TotalEnergies',
    terminal: 'Fos-sur-Mer',
    pipeline: 'Nord-Sud',
    client: 'EDF',
    clients: ['EDF', 'Engie'],
    incidents: ['Fuite sur le pipeline Nord-Sud']
  },
  {
    fournisseur: 'Shell',
    terminal: 'Montoir',
    pipeline: 'Est-Ouest',
    client: 'Total',
    clients: ['Total', 'BP'],
    incidents: []
  }
];

export function SupplyChain({ data }) {
  const [expanded, setExpanded] = useState(true);

  const supplyData = data && data.length > 0 ? data : defaultData;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          📦 Chaîne d'approvisionnement
        </h3>
        <button
          onClick={() => setExpanded(!expanded)}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          {expanded ? <FiChevronDown className="w-5 h-5" /> : <FiChevronRight className="w-5 h-5" />}
        </button>
      </div>

      {expanded && (
        <div className="space-y-4">
          {supplyData.map((chain, index) => (
            <div
              key={index}
              className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-lg">🔹</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  Chaîne {index + 1}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <div className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg text-sm">
                  {chain.fournisseur || 'N/A'}
                </div>
                <span className="text-gray-400">→</span>
                <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg text-sm">
                  {chain.terminal || 'N/A'}
                </div>
                <span className="text-gray-400">→</span>
                <div className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-lg text-sm">
                  {chain.pipeline || 'N/A'}
                </div>
                <span className="text-gray-400">→</span>
                <div className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm">
                  {chain.client || 'N/A'}
                </div>
              </div>

              {(chain.clients?.length > 0 || chain.incidents?.length > 0) && (
                <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {chain.clients?.length > 0 && chain.clients[0] !== 'N/A' && (
                    <p>👥 Clients: {chain.clients.join(', ')}</p>
                  )}
                  {chain.incidents?.length > 0 && chain.incidents[0] !== 'N/A' && (
                    <p className="text-yellow-600 dark:text-yellow-400">⚠️ Incidents: {chain.incidents.join(', ')}</p>
                  )}
                </div>
              )}
            </div>
          ))}
          
          {supplyData.length === 0 && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>Aucune chaîne d'approvisionnement disponible</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ✅ EXPORT PAR DÉFAUT (AJOUTER)
export default SupplyChain;