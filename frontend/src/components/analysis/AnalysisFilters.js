/**
 * AnalysisFilters - Filtres d'analyse (Version simplifiée)
 */

'use client';

import { useState } from 'react';
import { FiCalendar, FiFilter, FiChevronDown } from 'react-icons/fi';

export function AnalysisFilters({ filters, onFilterChange }) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const periods = [
    { value: '24h', label: '24h' },
    { value: '7d', label: '7 jours' },
    { value: '30d', label: '30 jours' },
    { value: '90d', label: '90 jours' },
    { value: 'all', label: 'Tous' },
  ];

  const severities = [
    { value: 'all', label: 'Toutes' },
    { value: 'critique', label: 'Critique' },
    { value: 'majeur', label: 'Majeur' },
    { value: 'mineur', label: 'Mineur' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex flex-wrap items-center gap-4">
        {/* Période */}
        <div className="flex items-center space-x-2">
          <FiCalendar className="w-4 h-4 text-gray-400" />
          <select
            value={filters?.period || '30d'}
            onChange={(e) => onFilterChange?.('period', e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {periods.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>

        {/* Gravité */}
        <div className="flex items-center space-x-2">
          <FiFilter className="w-4 h-4 text-gray-400" />
          <select
            value={filters?.severity || 'all'}
            onChange={(e) => onFilterChange?.('severity', e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {severities.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>

        {/* Bouton Avancé */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="px-3 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-1"
        >
          <span>Avancé</span>
          <FiChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Filtres avancés */}
      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Équipement
              </label>
              <input
                type="text"
                placeholder="ID de l'équipement..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Type d'analyse
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="all">Tous</option>
                <option value="incidents">Incidents</option>
                <option value="risks">Risques</option>
                <option value="performance">Performance</option>
                <option value="trends">Tendances</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Limite
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}