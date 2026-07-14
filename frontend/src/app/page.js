/**
 * Dashboard - Page d'accueil
 * ============================================================================
 * Description: Vue d'ensemble du réseau GNL avec statistiques et visualisations
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  FiActivity, 
  FiMoreVertical,
} from 'react-icons/fi';

import { StatsCards } from '@/components/dashboard/StatsCards';
import { GraphVisualization } from '@/components/graph/GraphVisualization';
import { RiskGauge } from '@/components/dashboard/RiskGauge';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState({
    nodes: 27,
    relationships: 14,
    incidents: 3,
    clients: 1,
  });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    loadDashboard();
  }, [timeRange]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      // Simuler le chargement des données (à remplacer par l'appel API réel)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées
      setStats({
        nodes: 27,
        relationships: 14,
        incidents: 3,
        clients: 1,
        nodes_change: 5,
        relationships_change: 2,
        incidents_change: -1,
        clients_change: 0,
      });
    } catch (error) {
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    router.push(`/analysis?node=${node.id}`);
  };

  const handleRefresh = () => {
    loadDashboard();
  };

  // Composant IncidentList simplifié pour éviter les erreurs
  const IncidentList = ({ limit }) => {
    const incidents = [
      { id: 'INC-001', description: 'Fuite sur le pipeline Nord-Sud', gravite: 'critique', statut: 'en_cours', date: '2026-07-08T10:30:00Z' },
      { id: 'INC-002', description: 'Compresseur en surchauffe', gravite: 'majeur', statut: 'resolu', date: '2026-07-05T14:20:00Z' },
    ];
    
    return (
      <div className="space-y-2">
        {incidents.slice(0, limit || 5).map((incident) => (
          <div key={incident.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer">
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-sm font-medium text-gray-900 dark:text-white">{incident.id}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  incident.gravite === 'critique' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                  incident.gravite === 'majeur' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300' :
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                }`}>
                  {incident.gravite}
                </span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  incident.statut === 'en_cours' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                  incident.statut === 'resolu' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {incident.statut}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{incident.description}</p>
            </div>
            <span className="text-xs text-gray-400">
              {new Date(incident.date).toLocaleDateString('fr-FR')}
            </span>
          </div>
        ))}
        {incidents.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>Aucun incident récent</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              🌐 Tableau de Bord GNL
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Réseau de connaissances du transport de gaz méthanier
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="24h">24h</option>
              <option value="7d">7 jours</option>
              <option value="30d">30 jours</option>
              <option value="90d">90 jours</option>
            </select>
            
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <FiActivity className="w-4 h-4" />
              <span>Actualiser</span>
            </button>
          </div>
        </div>

        {/* Cartes de statistiques */}
        <StatsCards stats={stats} loading={loading} />

        {/* Graphique et analyses */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Visualisation du graphe */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                🗺️ Visualisation du Réseau
              </h2>
              <div className="flex space-x-2">
                <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <FiMoreVertical className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>
            
            <div className="p-4 h-[500px]">
              <GraphVisualization 
                onNodeClick={handleNodeClick}
                selectedNode={selectedNode}
              />
            </div>
            
            {/* Contrôles du graphe */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-wrap gap-2">
                <button className="px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors text-sm">
                  🔍 Zoom In
                </button>
                <button className="px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors text-sm">
                  🔍 Zoom Out
                </button>
                <button className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm">
                  🔄 Réinitialiser
                </button>
                <button className="px-3 py-1 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 transition-colors text-sm">
                  📥 Exporter
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar droite */}
          <div className="space-y-6">
            {/* Risques */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  📊 Évaluation des Risques
                </h2>
              </div>
              <div className="p-4">
                <RiskGauge equipmentId="PIPE-001" />
              </div>
            </div>

            {/* Activité récente */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  🔄 Activité Récente
                </h2>
              </div>
              <div className="p-4">
                <RecentActivity />
              </div>
            </div>
          </div>
        </div>

        {/* Incidents récents */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              🚨 Incidents Récents
            </h2>
            <button 
              onClick={() => router.push('/incidents')}
              className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
            >
              Voir tous →
            </button>
          </div>
          <div className="p-4">
            <IncidentList limit={5} />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}