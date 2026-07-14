/**
 * IncidentFilters - Filtres des incidents
 * ============================================================================
 * Description: Composant de filtrage pour la liste des incidents
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiSearch, FiFilter, FiX } from 'react-icons/fi';

export function IncidentFilters({ filters, onFilterChange }) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSearch = (e) => {
    onFilterChange('search', e.target.value);
  };

  const handleSeverityChange = (e) => {
    onFilterChange('severity', e.target.value);
  };

  const handleStatusChange = (e) => {
    onFilterChange('status', e.target.value);
  };

  const handleDateRangeChange = (e) => {
    onFilterChange('dateRange', e.target.value);
  };

  const clearFilters = () => {
    onFilterChange('search', '');
    onFilterChange('severity', 'all');
    onFilterChange('status', 'all');
    onFilterChange('dateRange', '30d');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex flex-wrap items-center gap-4">
        {/* Recherche */}
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher un incident..."
              value={filters.search || ''}
              onChange={handleSearch}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Filtres de base */}
        <div className="flex items-center space-x-2">
          <select
            value={filters.severity || 'all'}
            onChange={handleSeverityChange}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Toutes les gravités</option>
            <option value="critique">Critique</option>
            <option value="majeur">Majeur</option>
            <option value="mineur">Mineur</option>
          </select>

          <select
            value={filters.status || 'all'}
            onChange={handleStatusChange}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tous les statuts</option>
            <option value="ouvert">Ouvert</option>
            <option value="en_cours">En cours</option>
            <option value="resolu">Résolu</option>
            <option value="ferme">Fermé</option>
          </select>

          <select
            value={filters.dateRange || '30d'}
            onChange={handleDateRangeChange}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="24h">24h</option>
            <option value="7d">7 jours</option>
            <option value="30d">30 jours</option>
            <option value="90d">90 jours</option>
            <option value="all">Tous</option>
          </select>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="px-3 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-1"
          >
            <FiFilter className="w-4 h-4" />
            <span>Avancé</span>
          </button>
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-1"
          >
            <FiX className="w-4 h-4" />
            <span>Effacer</span>
          </button>
        </div>
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
                Cause
              </label>
              <input
                type="text"
                placeholder="Cause de l'incident..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Temps de résolution
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="all">Tous</option>
                <option value="<30">Moins de 30 min</option>
                <option value="30-60">30-60 min</option>
                <option value="60-120">1-2 heures</option>
                <option value=">120">Plus de 2 heures</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}