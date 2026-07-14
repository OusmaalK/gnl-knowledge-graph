/**
 * RouteMap - Carte de la route
 * ============================================================================
 * Description: Visualisation de la route trouvée
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiCheckCircle } from 'react-icons/fi';

export function RouteMap({ data }) {
  if (!data || !data.path || data.path.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="text-lg font-medium">Aucune route sélectionnée</p>
        <p className="text-sm">Utilisez le formulaire pour rechercher une route</p>
      </div>
    );
  }

  const { path, distance, types, relations } = data;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          🗺️ Itinéraire
        </h3>
        <div className="flex items-center space-x-2">
          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg text-sm font-medium">
            {distance || path.length - 1 || 0} sauts
          </span>
          <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg text-sm font-medium">
            {path?.length || 0} étapes
          </span>
        </div>
      </div>

      {/* Visualisation du chemin */}
      <div className="relative p-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg overflow-x-auto">
        <div className="flex flex-wrap items-center justify-center gap-2 min-w-max">
          {path.map((node, index) => {
            const isStart = index === 0;
            const isEnd = index === path.length - 1;
            const type = types?.[index] || 'Node';
            const relation = relations?.[index] || '→';

            return (
              <div key={index} className="flex items-center">
                <div className={`
                  flex flex-col items-center p-3 rounded-lg min-w-[80px] transition-all
                  ${isStart ? 'bg-green-100 dark:bg-green-900/30 border-2 border-green-500 shadow-lg' :
                    isEnd ? 'bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-500 shadow-lg' :
                    'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 shadow-sm'}
                `}>
                  <span className="text-2xl">
                    {isStart ? '🚀' : isEnd ? '🏁' : '📍'}
                  </span>
                  <span className="text-xs font-mono font-medium mt-1 text-gray-900 dark:text-white">{node}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{type}</span>
                  {isStart && <span className="text-xs text-green-600 font-medium mt-1">DÉPART</span>}
                  {isEnd && <span className="text-xs text-blue-600 font-medium mt-1">ARRIVÉE</span>}
                </div>
                {!isEnd && (
                  <div className="flex flex-col items-center mx-2">
                    <div className="text-gray-400 text-2xl">→</div>
                    <span className="text-xs text-gray-400">{relation}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Détails */}
      {data.details && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="flex items-center space-x-2">
              <FiCheckCircle className="w-4 h-4 text-green-600" />
              <span className="font-medium text-green-800 dark:text-green-300">Route disponible</span>
            </div>
            <p className="text-sm text-green-700 dark:text-green-400 mt-1">
              {data.details.status || 'Route optimale trouvée'}
            </p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Détails</p>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1 space-y-1">
              <p>• {distance || path.length - 1 || 0} relations traversées</p>
              <p>• {path?.length || 0} nœuds dans le chemin</p>
              {data.details.incidents && (
                <p className="text-yellow-600">⚠️ {data.details.incidents} incidents sur le chemin</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ✅ EXPORT PAR DÉFAUT (AJOUTER)
export default RouteMap;