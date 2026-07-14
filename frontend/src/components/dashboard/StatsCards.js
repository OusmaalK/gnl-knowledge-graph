/**
 * StatsCards - Cartes de statistiques
 * ============================================================================
 * Description: Cartes affichant les statistiques principales du dashboard
 * ============================================================================
 */

import { FiDatabase, FiLink, FiAlertTriangle, FiUsers } from 'react-icons/fi';

const statsConfig = [
  {
    id: 'nodes',
    label: 'Nœuds',
    icon: FiDatabase,
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    iconColor: 'text-blue-600 dark:text-blue-400',
  },
  {
    id: 'relationships',
    label: 'Relations',
    icon: FiLink,
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    iconColor: 'text-green-600 dark:text-green-400',
  },
  {
    id: 'incidents',
    label: 'Incidents',
    icon: FiAlertTriangle,
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    iconColor: 'text-red-600 dark:text-red-400',
  },
  {
    id: 'clients',
    label: 'Clients',
    icon: FiUsers,
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    iconColor: 'text-purple-600 dark:text-purple-400',
  },
];

export function StatsCards({ stats = {}, loading = false }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-pulse">
            <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statsConfig.map((config) => {
        const Icon = config.icon;
        const value = stats?.[config.id] ?? 0;

        return (
          <div
            key={config.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {config.label}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {value.toLocaleString()}
                </p>
              </div>
              <div className={`p-3 rounded-xl ${config.bgColor}`}>
                <Icon className={`w-6 h-6 ${config.iconColor}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}