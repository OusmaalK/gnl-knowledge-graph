/**
 * EquipmentList - Liste des équipements
 * ============================================================================
 * Description: Liste des équipements avec leur niveau de risque
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiSearch, FiFilter } from 'react-icons/fi';

const riskColors = {
  CRITIQUE: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  ELEVE: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  MOYEN: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  FAIBLE: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
};

export function EquipmentList({ equipment = [], onSelect, selectedId }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = equipment.filter((item) => {
    const matchSearch = item.nom?.toLowerCase().includes(search.toLowerCase()) ||
                       item.id?.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || item.risk_level === filter;
    return matchSearch && matchFilter;
  });

  const getRiskColor = (level) => {
    const key = level?.toUpperCase() || 'FAIBLE';
    return riskColors[key] || riskColors.FAIBLE;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher un équipement..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tous les risques</option>
            <option value="CRITIQUE">Critique</option>
            <option value="ELEVE">Élevé</option>
            <option value="MOYEN">Moyen</option>
            <option value="FAIBLE">Faible</option>
          </select>
        </div>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <p>Aucun équipement trouvé</p>
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              className={`
                p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors
                ${selectedId === item.id ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500' : ''}
              `}
              onClick={() => onSelect(item)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-sm font-medium text-gray-900 dark:text-white">
                      {item.id}
                    </span>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {item.nom || 'Sans nom'}
                    </span>
                    <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                      {item.type || 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <span>Statut: {item.statut || 'N/A'}</span>
                    <span>Incidents: {item.incidents || 0}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(item.risk_level)}`}>
                    {item.risk_level || 'FAIBLE'}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}