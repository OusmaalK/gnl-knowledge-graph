/**
 * Sidebar - Barre latérale de navigation
 * ============================================================================
 * Description: Navigation principale de l'application
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import {
  FiHome,
  FiMessageSquare,
  FiAlertTriangle,
  FiMap,
  FiTool,
  FiBarChart2,
  FiSettings,
  FiLogOut,
  FiChevronLeft,
  FiChevronRight,
  FiMenu,
} from 'react-icons/fi';

// Configuration de la navigation avec gestion des rôles
const navigation = [
  { name: 'Dashboard', href: '/', icon: FiHome },
  { name: 'Assistant IA', href: '/chat', icon: FiMessageSquare },
  { name: 'Incidents', href: '/incidents', icon: FiAlertTriangle },
  { name: 'Logistique', href: '/logistics', icon: FiMap },
  { name: 'Maintenance', href: '/maintenance', icon: FiTool },
  { name: 'Analyses', href: '/analysis', icon: FiBarChart2 },
  // Seuls les admins peuvent voir ces pages
  { name: 'Administration', href: '/admin', icon: FiSettings, role: 'admin' },
  { name: 'Paramétrage IoT', href: '/settings/iot', icon: FiSettings, role: 'admin' },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  
  // --- CORRECTION : Attendre le montage côté client ---
  const [isClient, setIsClient] = useState(false);
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    setIsClient(true);
    // Récupérer le rôle uniquement côté client
    setUserRole(localStorage.getItem('role'));
  }, []);
  // ------------------------------------------------

  // --- FONCTION DE DÉCONNEXION ---
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    Cookies.remove('token');
    Cookies.remove('role');
    router.push('/auth/login');
  };

  // Filtrer les items de navigation selon le rôle
  // Ne filtre que si on est côté client et qu'on a un rôle
  const filteredNavigation = isClient && userRole 
    ? navigation.filter((item) => {
        if (item.role) {
          return userRole === item.role;
        }
        return true;
      })
    : navigation; // Pendant le SSR, on affiche tout (pas de filtre)

  return (
    <aside
      className={`
        bg-gradient-to-b from-gray-900 to-gray-800 text-white
        transition-all duration-300 ease-in-out
        ${collapsed ? 'w-20' : 'w-64'}
        flex flex-col
        h-screen
        sticky top-0
        shadow-xl
      `}
    >
      {/* Logo */}
      <div className={`
        flex items-center h-16 px-4 border-b border-gray-700
        ${collapsed ? 'justify-center' : 'justify-between'}
      `}>
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <span className="text-2xl">⛽</span>
            <span className="font-bold text-lg bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
              GNL KG
            </span>
          </div>
        )}
        {collapsed && (
          <span className="text-2xl">⛽</span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-lg hover:bg-gray-700 transition-colors"
        >
          {collapsed ? <FiChevronRight size={20} /> : <FiChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <ul className="space-y-1">
          {filteredNavigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`
                    flex items-center px-3 py-2.5 rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' 
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                    ${collapsed ? 'justify-center' : 'space-x-3'}
                  `}
                  title={collapsed ? item.name : ''}
                >
                  <Icon size={20} className="flex-shrink-0" />
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-700 p-4">
        {!collapsed ? (
          <button 
            onClick={handleLogout}
            className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors w-full px-3 py-2 rounded-lg hover:bg-gray-700"
          >
            <FiLogOut size={20} />
            <span>Déconnexion</span>
          </button>
        ) : (
          <button 
            onClick={handleLogout}
            className="flex justify-center text-gray-300 hover:text-white transition-colors w-full py-2 rounded-lg hover:bg-gray-700"
          >
            <FiLogOut size={20} />
          </button>
        )}
      </div>
    </aside>
  );
}