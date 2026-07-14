/**
 * IncidentList - Liste des incidents
 * ============================================================================
 * Description: Tableau des incidents avec filtres et actions
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { FiChevronDown } from 'react-icons/fi';

const severityColors = {
  critique: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-300' },
  majeur: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-300' },
  mineur: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-300' },
};

const statusColors = {
  ouvert: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-300' },
  en_cours: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-800 dark:text-blue-300' },
  resolu: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-300' },
  ferme: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-800 dark:text-gray-300' },
};

export function IncidentList({ incidents, onSelect, onDiagnostic, loading }) {
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="animate-pulse">Chargement des incidents...</div>
      </div>
    );
  }

  if (!incidents || incidents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <div className="text-4xl mb-4">✅</div>
        <p className="text-lg font-medium">Aucun incident</p>
        <p className="text-sm">Aucun incident n'a été enregistré</p>
      </div>
    );
  }

  const sortedIncidents = [...incidents].sort((a, b) => {
    const valA = a[sortField] || '';
    const valB = b[sortField] || '';
    const comparison = valA < valB ? -1 : valA > valB ? 1 : 0;
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Description
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('gravite')}>
              <div className="flex items-center space-x-1">
                <span>Gravité</span>
                <FiChevronDown className={`w-3 h-3 transition-transform ${sortField === 'gravite' && sortDirection === 'asc' ? 'rotate-180' : ''}`} />
              </div>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('statut')}>
              <div className="flex items-center space-x-1">
                <span>Statut</span>
                <FiChevronDown className={`w-3 h-3 transition-transform ${sortField === 'statut' && sortDirection === 'asc' ? 'rotate-180' : ''}`} />
              </div>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('date')}>
              <div className="flex items-center space-x-1">
                <span>Date</span>
                <FiChevronDown className={`w-3 h-3 transition-transform ${sortField === 'date' && sortDirection === 'asc' ? 'rotate-180' : ''}`} />
              </div>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {sortedIncidents.map((incident, index) => {
            const severity = severityColors[incident.gravite] || severityColors.mineur;
            const status = statusColors[incident.statut] || statusColors.ouvert;
            const date = (() => {
              try {
                if (!incident.date) return 'N/A';
                const d = new Date(incident.date);
                // Vérification supplémentaire : si la date est invalide (NaN), on retourne 'N/A'
                if (isNaN(d.getTime())) return 'N/A';
                return format(d, 'dd/MM/yyyy HH:mm', { locale: fr });
              } catch (e) {
                return 'N/A';
              }
            })();

            return (
              <tr
                // --- CORRECTION ICI : Clé unique combinant ID et INDEX ---
                key={`${incident.id}-${index}`}
                className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                onClick={() => onSelect(incident)}
              >
                <td className="px-4 py-3 text-sm font-mono text-gray-900 dark:text-white">
                  {incident.id}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-xs truncate">
                  {incident.description}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${severity.bg} ${severity.text}`}>
                    {incident.gravite || 'N/A'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                    {incident.statut || 'N/A'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {date}
                </td>
                <td className="px-4 py-3">
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDiagnostic(incident);
                      }}
                      className="px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      Diagnostic
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                      className="px-3 py-1 text-xs font-medium text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-300"
                    >
                      Détails
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}