/**
 * IncidentCard - Carte d'incident
 * ============================================================================
 * Description: Carte d'affichage d'un incident dans une liste
 * ============================================================================
 */

'use client';

import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { FiAlertCircle, FiClock, FiMapPin } from 'react-icons/fi';

const severityColors = {
  critique: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-300', icon: '🔴' },
  majeur: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-300', icon: '🟠' },
  mineur: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-300', icon: '🟡' },
};

export function IncidentCard({ incident, onClick }) {
  if (!incident) return null;

  const severity = severityColors[incident.gravite] || severityColors.mineur;
  const date = incident.date ? format(new Date(incident.date), 'dd/MM/yyyy HH:mm', { locale: fr }) : 'N/A';

  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{severity.icon}</span>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="font-semibold text-gray-900 dark:text-white">
                {incident.id}
              </h4>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severity.bg} ${severity.text}`}>
                {incident.gravite || 'N/A'}
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {incident.description}
            </p>
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-1">
                <FiClock className="w-3 h-3" />
                <span>{date}</span>
              </div>
              {incident.equipment_name && (
                <div className="flex items-center space-x-1">
                  <FiMapPin className="w-3 h-3" />
                  <span>{incident.equipment_name}</span>
                </div>
              )}
              {incident.duree_min && (
                <div className="flex items-center space-x-1">
                  <FiAlertCircle className="w-3 h-3" />
                  <span>{incident.duree_min} min</span>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end space-y-1">
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
            incident.statut === 'resolu' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
            incident.statut === 'en_cours' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
            'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
          }`}>
            {incident.statut || 'N/A'}
          </span>
          {incident.cause && (
            <span className="text-xs text-gray-400">
              Cause: {incident.cause}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}