/**
 * Maintenance - Maintenance prédictive
 * ============================================================================
 * Description: Prédiction des risques et planification de la maintenance
 * ============================================================================
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import toast from 'react-hot-toast';
import {
  FiTool,
  FiAlertCircle,
  FiCalendar,
  FiClock,
  FiRefreshCw,
  FiDownload,
  FiTrendingUp,
  FiTrendingDown,
  FiSearch,
  FiCpu, // Pour l'IA
} from 'react-icons/fi';

// IMPORTS RECHARTS POUR L'HISTORIQUE
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

import { RiskGauge } from '@/components/maintenance/RiskGauge';
import { EquipmentList } from '@/components/maintenance/EquipmentList';
import { MaintenancePlan } from '@/components/maintenance/MaintenancePlan';
import { RiskHistory } from '@/components/maintenance/RiskHistory';
import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

// Composant local pour le graphique d'historique (pour éviter de dépendre de RiskHistory si mal importé)
function HistoryChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-center py-8 text-gray-500">Aucune donnée historique disponible.</div>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">📈 Évolution des risques et incidents</h3>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="score" stroke="#F59E0B" name="Score de risque" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="incidents" stroke="#EF4444" name="Incidents" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function MaintenancePage() {
  const [equipment, setEquipment] = useState([]);
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // --- NOUVEAUX ÉTATS ---
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [iaGlobalAnalysis, setIaGlobalAnalysis] = useState('');
  const [loadingIa, setLoadingIa] = useState(false);
  // ---------------------

  const [generatedPlan, setGeneratedPlan] = useState(null);


  const { api, get, post } = useApi();

  const tabs = [
    { id: 'overview', label: '📊 Vue d\'ensemble' },
    { id: 'risks', label: '⚠️ Risques' },
    { id: 'plan', label: '📋 Plan de maintenance' },
    { id: 'history', label: '📈 Historique' },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Appels API réels vers le Backend
      const [equipmentData, riskData] = await Promise.all([
        get('/api/maintenance/equipment'),
        get('/api/maintenance/risks'),
      ]);
      setEquipment(equipmentData || []);
      setRiskData(riskData);
    } catch (error) {
      console.warn('Utilisation des données simulées pour la maintenance');
      // Données mock pour que l'interface reste belle
      setEquipment([
        { id: 'PIPE-001', nom: 'Nord-Sud', type: 'Pipeline', statut: 'actif', risk_level: 'ÉLEVÉ', incidents: 1 },
        { id: 'PIPE-002', nom: 'Est-Ouest', type: 'Pipeline', statut: 'actif', risk_level: 'MOYEN', incidents: 0 },
        { id: 'COMP-001', nom: 'Compresseur Nord', type: 'Compresseur', statut: 'actif', risk_level: 'ÉLEVÉ', incidents: 1 },
        { id: 'TERM-001', nom: 'Fos-sur-Mer', type: 'Terminal', statut: 'actif', risk_level: 'FAIBLE', incidents: 0 },
      ]);
      setRiskData({
        critical: 1,
        high: 2,
        planned: 3,
        avgResolution: '4h 30min',
        history: [
          { date: '2026-07-08', score: 65, incidents: 1 },
          { date: '2026-07-05', score: 45, incidents: 0 },
          { date: '2026-07-01', score: 30, incidents: 0 },
        ]
      });
      toast.success('Données de maintenance chargées (simulées)');
    } finally {
      setLoading(false);
    }
  };

  // --- LOGIQUE DE FILTRAGE ---
  const filteredEquipment = useMemo(() => {
    return equipment.filter(item => {
      const matchesSearch = item.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            item.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRisk = riskFilter === 'all' || item.risk_level === riskFilter;
      return matchesSearch && matchesRisk;
    });
  }, [equipment, searchTerm, riskFilter]);

  // --- FONCTION IA GLOBALE ---
  const handleGlobalIA = async () => {
    setLoadingIa(true);
    setIaGlobalAnalysis('');
    try {
      // Appel à l'agent pour une analyse globale
      const response = await post('/api/agents/maintenance', {
        query: "Analyse l'état global du réseau. Donne un résumé synthétique de la santé actuelle, des risques principaux et des recommandations stratégiques.",
        params: { equipment: equipment, riskData: riskData }
      });
      setIaGlobalAnalysis(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      toast.success('Analyse IA globale générée !');
    } catch (error) {
      toast.error('Erreur lors de la génération IA');
      setIaGlobalAnalysis('Impossible de générer l\'analyse globale pour le moment.');
    } finally {
      setLoadingIa(false);
    }
  };
  // ------------------------------------

  const handleSelectEquipment = (equipment) => {
    setSelectedEquipment(equipment);
  };

  // --- FONCTION GÉNÉRATION PLAN (Version IA connectée) ---
    // --- FONCTION GÉNÉRATION PLAN (Version qui stocke le résultat) ---
    const handlePlanMaintenance = async (equipmentId) => {
      if (!equipmentId) {
        toast.error("Veuillez sélectionner un équipement.");
        return;
      }
      
      setGeneratedPlan(null); // On efface l'ancien plan avant de charger le nouveau
      try {
        const response = await post('/api/agents/maintenance', {
          query: `Génère un plan de maintenance détaillé pour l'équipement ${equipmentId}. Inclus des tâches, leurs priorités, une durée estimée et un planning.`,
          params: { action: 'plan', equipment_id: equipmentId }
        });
        
        // On stocke la réponse (texte ou objet) dans notre variable d'état
        setGeneratedPlan(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
        toast.success('Plan généré avec succès !');
      } catch (error) {
        console.error("Erreur IA:", error);
        toast.error('Erreur lors de la génération du plan');
      }
    };
    // ------------------------------------------------
  // ------------------------------------

  const handleRefresh = () => {
    loadData();
    toast.success('Données actualisées');
  };

  const handleExport = () => {
    toast.success('Export en cours...');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              🔧 Maintenance Prédictive
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Prédiction des risques et planification de la maintenance
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
              onClick={handleGlobalIA} // Nouveau bouton IA globale
              disabled={loadingIa}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              {loadingIa ? <LoadingSpinner size="small" /> : <FiCpu className="w-4 h-4" />}
              <span>{loadingIa ? 'Analyse...' : '🧠 Analyse IA globale'}</span>
            </button>
            <button
              onClick={handleExport}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
            >
              <FiDownload className="w-4 h-4" />
              <span>Exporter</span>
            </button>
          </div>
        </div>

        {/* Affichage de l'analyse IA Globale */}
        {iaGlobalAnalysis && (
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <FiCpu className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                {iaGlobalAnalysis}
              </div>
            </div>
          </div>
        )}

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Équipements critiques</p>
                <p className="text-2xl font-bold text-red-600">
                  {riskData?.critical || 0}
                </p>
              </div>
              <FiAlertCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Risque élevé</p>
                <p className="text-2xl font-bold text-orange-600">
                  {riskData?.high || 0}
                </p>
              </div>
              <FiTrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Maintenances planifiées</p>
                <p className="text-2xl font-bold text-blue-600">
                  {riskData?.planned || 0}
                </p>
              </div>
              <FiCalendar className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Temps moyen de résolution</p>
                <p className="text-2xl font-bold text-green-600">
                  {riskData?.avgResolution || 'N/A'}
                </p>
              </div>
              <FiClock className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu */}
        <div>
          {activeTab === 'overview' && (
            <div className="space-y-4">
              {/* Filtres de recherche */}
              <div className="flex flex-col sm:flex-row gap-3 bg-white dark:bg-gray-800 p-3 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="relative flex-1">
                  <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Rechercher un équipement..."
                    className="w-full pl-9 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 outline-none"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <select
                  className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 outline-none"
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                >
                  <option value="all">Tous les risques</option>
                  <option value="ÉLEVÉ">Risque ÉLEVÉ</option>
                  <option value="MOYEN">Risque MOYEN</option>
                  <option value="FAIBLE">Risque FAIBLE</option>
                </select>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <EquipmentList 
                    equipment={filteredEquipment}
                    onSelect={handleSelectEquipment}
                    selectedId={selectedEquipment?.id}
                  />
                </div>
                <div>
                  {selectedEquipment && (
                    <RiskGauge 
                      equipment={selectedEquipment}
                      riskData={riskData}
                    />
                  )}
                  {!selectedEquipment && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500">
                      Sélectionnez un équipement pour voir ses détails
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'risks' && (
            <RiskHistory 
              equipment={equipment}
              riskData={riskData}
            />
          )}

{activeTab === 'plan' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <FiCalendar className="w-5 h-5 text-blue-500" /> 
                  Plan de maintenance
                  {selectedEquipment && (
                    <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">
                      {selectedEquipment.id} - {selectedEquipment.nom}
                    </span>
                  )}
                </h3>
                <button
                  onClick={() => handlePlanMaintenance(selectedEquipment?.id)}
                  disabled={!selectedEquipment}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <FiTool className="w-4 h-4" />
                  {selectedEquipment ? `🤖 Générer le plan` : 'Sélectionnez un équipement'}
                </button>
              </div>
              
              {/* --- ZONE D'AFFICHAGE DU PLAN (Mise à jour) --- */}
              <div className="mt-4">
                {generatedPlan ? (
                  // 1. Si le plan est généré, on l'affiche dans un bel encadré
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-5">
                    <h4 className="font-medium text-blue-800 dark:text-blue-300 mb-3 flex items-center gap-2">
                      <FiTool className="w-4 h-4" /> Plan de maintenance stratégique (IA)
                    </h4>
                    <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                      {generatedPlan}
                    </div>
                  </div>
                ) : (
                  // 2. Si aucun plan n'est généré, on affiche le message d'instruction
                  <div className="border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center text-gray-500">
                    {selectedEquipment ? (
                      <p>Cliquez sur <strong>"Générer le plan"</strong> pour obtenir un planning IA personnalisé pour <strong>{selectedEquipment.nom}</strong>.</p>
                    ) : (
                      <p>Veuillez sélectionner un équipement dans l'onglet <strong>"Vue d'ensemble"</strong> pour générer un plan.</p>
                    )}
                  </div>
                )}
              </div>
              {/* -------------------------------------------- */}
            </div>
          )}

          {activeTab === 'history' && (
            <HistoryChart data={riskData?.history || []} />
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}