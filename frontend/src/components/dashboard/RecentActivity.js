/**
 * RecentActivity - Activité récente
 * ============================================================================
 * Description: Liste des activités récentes sur le réseau GNL
 * ============================================================================
 */

import { FiClock } from 'react-icons/fi';

export function RecentActivity() {
  const activities = [
    {
      id: 1,
      type: 'incident',
      title: 'Nouvel incident critique sur PIPE-001',
      time: 'il y a 5 min',
      description: 'Fuite détectée sur le pipeline Nord-Sud',
    },
    {
      id: 2,
      type: 'maintenance',
      title: 'Maintenance planifiée sur COMP-001',
      time: 'il y a 2h',
      description: 'Remplacement programmé des pièces',
    },
    {
      id: 3,
      type: 'update',
      title: 'Mise à jour du graphe',
      time: 'il y a 5h',
      description: 'Ajout de nouveaux nœuds',
    },
  ];

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>Aucune activité récente</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
            <span className="text-lg">
              {activity.type === 'incident' ? '🚨' :
               activity.type === 'maintenance' ? '🔧' :
               activity.type === 'update' ? '🔄' : '📌'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {activity.title}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {activity.description}
            </p>
            <div className="flex items-center space-x-2 mt-1">
              <FiClock className="w-3 h-3 text-gray-400" />
              <span className="text-xs text-gray-400">{activity.time}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}