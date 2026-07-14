/**
 * Incidents - Gestion des incidents
 * ============================================================================
 * Description: Liste, diagnostic et gestion des incidents GNL
 * Version finale avec Export PDF, IA et Filtres avancés
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { 
  FiSearch, 
  FiFilter, 
  FiPlus, 
  FiDownload,
  FiRefreshCw,
  FiChevronDown,
  FiAlertCircle,
  FiClock,
  FiCpu,
} from 'react-icons/fi';

// Composants
import { IncidentList } from '@/components/incidents/IncidentList';
import { IncidentDetail } from '@/components/incidents/IncidentDetail';
import { IncidentFilters } from '@/components/incidents/IncidentFilters';
import { IncidentDiagnostic } from '@/components/incidents/IncidentDiagnostic';

// Hooks et Utilitaires
import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

// Générateur de rapport PDF
import { generateIncidentReport } from '@/components/incidents/IncidentReport';

// Données simulées (Fallback)
const mockIncidents = [
  {
    id: 'INC-001',
    description: 'Fuite sur le pipeline Nord-Sud',
    gravite: 'critique',
    statut: 'en_cours',
    date: '2026-07-08T10:30:00Z',
    cause: 'corrosion',
    action: 'Réparation d\'urgence',
    duree_min: 240,
    equipment_id: 'PIPE-001',
    equipment_name: 'Nord-Sud',
    created_at: '2026-07-08T10:30:00Z',
    updated_at: '2026-07-08T14:30:00Z',
  },
  {
    id: 'INC-002',
    description: 'Compresseur en surchauffe',
    gravite: 'majeur',
    statut: 'resolu',
    date: '2026-07-05T14:20:00Z',
    cause: 'panne mécanique',
    action: 'Maintenance préventive',
    duree_min: 120,
    equipment_id: 'COMP-001',
    equipment_name: 'Compresseur Nord',
    created_at: '2026-07-05T14:20:00Z',
    updated_at: '2026-07-05T16:20:00Z',
  },
  {
    id: 'INC-003',
    description: 'Variation de pression sur le pipeline Est-Ouest',
    gravite: 'mineur',
    statut: 'ferme',
    date: '2026-07-01T08:00:00Z',
    cause: 'fluctuation',
    action: 'Ajustement des vannes',
    duree_min: 45,
    equipment_id: 'PIPE-002',
    equipment_name: 'Est-Ouest',
    created_at: '2026-07-01T08:00:00Z',
    updated_at: '2026-07-01T08:45:00Z',
  },
];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const [filters, setFilters] = useState({
    severity: 'all',
    status: 'all',
    dateRange: '30d',
    search: '',
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 100,
    total: 0,
  });
  
  // États IA
  const [iaSummary, setIaSummary] = useState('');
  const [loadingIa, setLoadingIa] = useState(false);

  const { api, get, post } = useApi();

  useEffect(() => {
    loadIncidents();
  }, [filters, pagination.page]);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const response = await get('/api/incidents', {
        params: {
          ...filters,
          page: pagination.page,
          limit: pagination.limit,
        },
      });
      
      console.log("🔍 Incidents reçus du Backend:", response.items);

      setIncidents(response.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
      }));
    } catch (error) {
      console.warn('Utilisation des données simulées pour les incidents');
      setIncidents(mockIncidents);
      setPagination(prev => ({
        ...prev,
        total: mockIncidents.length,
      }));
    } finally {
      setLoading(false);
    }
  };

  // --- FONCTION IA : ANALYSE GLOBALE ---
  const handleGenerateSummary = async () => {
    if (incidents.length === 0) {
      toast.error('Aucun incident à analyser');
      return;
    }

    setLoadingIa(true);
    setIaSummary('');
    try {
      const response = await post('/api/agents/diagnostic', {
        query: "Fais une analyse globale et stratégique de la situation actuelle des incidents, identifie les causes racines et propose des actions prioritaires.",
        params: { 
          context: incidents
        }
      });

      setIaSummary(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      toast.success('Analyse IA générée avec succès');
    } catch (error) {
      console.error("Erreur lors de l'appel à l'IA:", error);
      toast.error("Erreur lors de la génération de l'analyse IA");
      setIaSummary('Impossible de générer l\'analyse pour le moment.');
    } finally {
      setLoadingIa(false);
    }
  };

  // --- FONCTION IA : DIAGNOSTIC SPÉCIFIQUE (Pour le panneau de détails) ---
  const handleDiagnosticIA = async (incident) => {
    setLoadingIa(true);
    setIaSummary('');
    try {
      const response = await post('/api/agents/diagnostic', {
        query: `Analyse en profondeur l'incident ${incident.id}. Donne un diagnostic stratégique et des recommandations concrètes.`,
        params: { incident_id: incident.id }
      });
      setIaSummary(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      toast.success('Diagnostic IA généré !');
    } catch (error) {
      toast.error('Erreur lors de la génération du diagnostic');
    } finally {
      setLoadingIa(false);
    }
  };
  // ----------------------------------------------------

  // --- CALCULS POUR LES CARTES DE KPIS ---
  const totalCritiques = incidents.filter(i => i.gravite === 'critique').length;
  const totalEnCours = incidents.filter(i => i.statut === 'en_cours').length;
  const moyenneDuree = incidents.length > 0 
    ? Math.round(incidents.reduce((acc, i) => acc + i.duree_min, 0) / incidents.length) 
    : 0;

  const handleSelectIncident = (incident) => {
    setSelectedIncident(incident);
    setShowDiagnostic(false);
  };

  const handleDiagnostic = (incident) => {
    handleDiagnosticIA(incident);
    setSelectedIncident(incident);
    setShowDiagnostic(true);
  };

  // --- EXPORT PDF ---
  const handleExport = () => {
    generateIncidentReport(incidents, filters);
    toast.success('Rapport PDF téléchargé !');
  };

  const handleRefresh = () => {
    loadIncidents();
    toast.success('Liste actualisée');
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
    setPagination(prev => ({
      ...prev,
      page: 1,
    }));
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              🚨 Gestion des Incidents
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Liste et diagnostic des incidents du réseau GNL
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiRefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={handleExport}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
            >
              <FiDownload className="w-4 h-4" />
              <span>Exporter (PDF)</span>
            </button>
          </div>
        </div>

        {/* Filtres */}
        <IncidentFilters 
          filters={filters}
          onFilterChange={handleFilterChange}
        />

        {/* Bouton IA (Analyse globale) */}
        <div className="flex justify-end mb-2">
          <button
            onClick={handleGenerateSummary}
            disabled={loadingIa || incidents.length === 0}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm transition-all"
          >
            {loadingIa ? <LoadingSpinner size="small" /> : <FiCpu className="w-4 h-4" />}
            <span>{loadingIa ? 'Analyse en cours...' : '🧠 Générer analyse IA'}</span>
          </button>
        </div>

        {/* Affichage du Résumé IA (Quand il est généré) */}
        {iaSummary && (
          <div className="mb-4 p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg shadow-sm animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex items-start gap-3">
              <FiCpu className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                {iaSummary}
              </div>
            </div>
          </div>
        )}

        {/* Bandeau d'alerte critique */}
        {incidents.some(inc => inc.gravite === 'critique' && inc.statut === 'en_cours') && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-r-lg flex items-center gap-3 animate-pulse">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-ping"></div>
            <div>
              <p className="font-bold text-red-800 dark:text-red-300">⚠️ Alerte critique en cours !</p>
              <p className="text-sm text-red-700 dark:text-red-400">
                Un incident critique est actuellement ouvert. Intervention prioritaire requise.
              </p>
            </div>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">Total incidents</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{pagination.total}</p>
              </div>
              <FiAlertCircle className="w-6 h-6 text-blue-500" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">En cours</p>
                <p className="text-2xl font-bold text-yellow-600">{totalEnCours}</p>
              </div>
              <FiRefreshCw className="w-6 h-6 text-yellow-500" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">Critiques</p>
                <p className="text-2xl font-bold text-red-600">{totalCritiques}</p>
              </div>
              <FiAlertCircle className="w-6 h-6 text-red-500" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase">Durée moy. (min)</p>
                <p className="text-2xl font-bold text-green-600">{moyenneDuree}</p>
              </div>
              <FiClock className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </div>

        {/* Liste des incidents */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {pagination.total} incidents
              </span>
              <span className="text-sm text-gray-500">
                Page {pagination.page} / {Math.ceil(pagination.total / pagination.limit)}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
                className="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
              >
                Précédent
              </button>
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page * pagination.limit >= pagination.total}
                className="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
              >
                Suivant
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner size="large" />
              </div>
            ) : (
              <IncidentList 
                incidents={incidents}
                onSelect={handleSelectIncident}
                onDiagnostic={handleDiagnostic}
              />
            )}
          </div>
        </div>

        {/* Détail de l'incident */}
        {selectedIncident && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                📋 Détail de l'incident
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowDiagnostic(!showDiagnostic)}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  {showDiagnostic ? 'Cacher le diagnostic' : 'Voir le diagnostic'}
                </button>
                <button
                  onClick={() => setSelectedIncident(null)}
                  className="px-3 py-1 text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-4">
              {showDiagnostic ? (
                <IncidentDiagnostic incident={selectedIncident} iaSummary={iaSummary} loadingIa={loadingIa} />
              ) : (
                <IncidentDetail incident={selectedIncident} />
              )}
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}