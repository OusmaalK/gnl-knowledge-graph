/**
 * Header - En-tête de l'application
 * ============================================================================
 * Description: Barre d'en-tête avec recherche, notifications et profil
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiSearch, FiBell, FiUser, FiChevronDown } from 'react-icons/fi';

export function Header() {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const notifications = [
    { id: 1, title: 'Nouvel incident critique', time: 'il y a 5 min', read: false },
    { id: 2, title: 'Maintenance planifiée', time: 'il y a 2h', read: false },
    { id: 3, title: 'Rapport hebdomadaire disponible', time: 'il y a 1j', read: true },
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    // Implémenter la recherche
    console.log('Recherche:', searchQuery);
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Titre de la page */}
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
            GNL Knowledge Graph
          </h2>
          <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
            v1.0.0
          </span>
        </div>

        {/* Recherche */}
        <form onSubmit={handleSearch} className="hidden md:block flex-1 max-w-md mx-8">
          <div className="relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </form>

        {/* Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors relative"
            >
              <FiBell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
                <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold">Notifications</h3>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={`
                        p-3 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer
                        ${!notif.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
                      `}
                    >
                      <p className="text-sm font-medium">{notif.title}</p>
                      <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                    </div>
                  ))}
                </div>
                <div className="p-2 border-t border-gray-200 dark:border-gray-700 text-center">
                  <button className="text-sm text-blue-600 hover:text-blue-700">
                    Voir toutes les notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Profil */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                <FiUser />
              </div>
              <FiChevronDown size={16} className="text-gray-500" />
            </button>

            {showProfile && (
              <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <p className="font-semibold">Administrateur</p>
                  <p className="text-sm text-gray-500">admin@gnl-company.com</p>
                </div>
                <div className="py-2">
                  <button className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    Mon profil
                  </button>
                  <button className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    Paramètres
                  </button>
                  <hr className="my-1 border-gray-200 dark:border-gray-700" />
                  <button className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                    Se déconnecter
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}