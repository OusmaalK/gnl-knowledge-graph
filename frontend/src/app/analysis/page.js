/**
 * Analysis - Analyses avancées
 * ============================================================================
 * Description: Analyses approfondies du réseau GNL avec IA prédictive
 * ============================================================================
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import toast from 'react-hot-toast';
import {
  FiBarChart2,
  FiPieChart,
  FiTrendingUp,
  FiTrendingDown,
  FiDownload,
  FiRefreshCw,
  FiCalendar,
  FiFilter,
  FiCpu,
  FiFileText,
} from 'react-icons/fi';

// IMPORTS RECHARTS POUR LES GRAPHIQUES
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart, Scatter, Area
} from 'recharts';

import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

// --- COMPOSANTS DE GRAPHIQUES INTERNES (Pour éviter les dépendances externes) ---
const ChartCard = ({ title, children, className = "" }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">{title}</h3>
    <div className="h-[250px] w-full">
      {children}
    </div>
  </div>
);

// --- COMPOSANT FILTRES AVANCÉS ---
function AnalysisFilters({ filters, onFilterChange }) {
  return (
    <div className="flex flex-wrap gap-3 bg-white dark:bg-gray-800 p-3 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-600">
        <FiCalendar className="w-4 h-4 text-gray-500" />
        <select
          value={filters.period}
          onChange={(e) => onFilterChange('period', e.target.value)}
          className="bg-transparent text-sm outline-none"
        >
          <option value="7d">7 jours</option>
          <option value="30d">30 jours</option>
          <option value="90d">90 jours</option>
          <option value="1y">1 an</option>
        </select>
      </div>
      
      <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-600">
        <FiFilter className="w-4 h-4 text-gray-500" />
        <select
          value={filters.equipment}
          onChange={(e) => onFilterChange('equipment', e.target.value)}
          className="bg-transparent text-sm outline-none"
        >
          <option value="all">Tous les équipements</option>
          <option value="PIPE-001">Nord-Sud</option>
          <option value="PIPE-002">Est-Ouest</option>
          <option value="COMP-001">Compresseur Nord</option>
        </select>
      </div>

      <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-600">
        <FiFilter className="w-4 h-4 text-gray-500" />
        <select
          value={filters.severity}
          onChange={(e) => onFilterChange('severity', e.target.value)}
          className="bg-transparent text-sm outline-none"
        >
          <option value="all">Toutes gravités</option>
          <option value="critique">Critique</option>
          <option value="majeur">Majeur</option>
          <option value="mineur">Mineur</option>
        </select>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  const [activeTab, setActiveTab] = useState('incidents');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState({
    period: '30d',
    equipment: 'all',
    severity: 'all',
  });

  // --- ÉTATS POUR L'IA ---
  const [iaReport, setIaReport] = useState('');
  const [loadingIa, setLoadingIa] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [loadingPred, setLoadingPred] = useState(false);
  // ------------------------

  const { api, get, post } = useApi();

  const tabs = [
    { id: 'incidents', label: '📊 Incidents' },
    { id: 'risks', label: '⚠️ Risques' },
    { id: 'performance', label: '📈 Performance' },
    { id: 'trends', label: '📉 Tendances' },
  ];

  // Générer des données simulées (Mock) en attendant l'API
  const generateMockData = (tab, filters) => {
    const baseData = {
      incidents: {
        incidents_by_severity: { labels: ['Critique', 'Majeur', 'Mineur'], datasets: [{ data: [1, 2, 3], backgroundColor: ['#EF4444', '#F59E0B', '#EAB308'] }] },
        incidents_over_time: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [2, 3, 1, 4, 2, 5, 3], color: '#3B82F6' }] },
        incidents_by_cause: { labels: ['Corrosion', 'Panne mécanique', 'Fluctuation'], datasets: [{ data: [2, 3, 1], backgroundColor: ['#8B5CF6', '#EC4899', '#F59E0B'] }] },
        resolution_time: { labels: ['Corrosion', 'Mécanique', 'Fluctuation'], datasets: [{ data: [120, 240, 45], backgroundColor: '#3B82F6' }] }
      },
      risks: {
        risk_levels: { labels: ['Critique', 'Élevé', 'Moyen', 'Faible'], datasets: [{ data: [1, 2, 3, 1], backgroundColor: ['#EF4444', '#F59E0B', '#3B82F6', '#10B981'] }] },
        risk_trend: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [45, 50, 55, 60, 55, 65, 60], color: '#EF4444' }] },
        critical_equipment: { labels: ['PIPE-001', 'COMP-001'], datasets: [{ data: [1, 1], backgroundColor: ['#EF4444', '#F59E0B'] }] },
        risk_correlation: { labels: ['PIPE-001', 'TERM-001'], datasets: [{ data: [60, 30], backgroundColor: '#8B5CF6' }] }
      },
      performance: {
        pipeline_performance: { labels: ['Nord-Sud', 'Est-Ouest', 'Sud-Est'], datasets: [{ data: [95, 88, 92], backgroundColor: ['#10B981', '#F59E0B', '#3B82F6'] }] },
        availability: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [99, 98, 97, 96, 98, 99, 98], color: '#10B981' }] },
        volume_transported: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [500, 550, 480, 600, 520, 580, 550], backgroundColor: '#3B82F6' }] },
        energy_efficiency: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [85, 87, 86, 88, 87, 89, 88], color: '#8B5CF6' }] }
      },
      trends: {
        incident_trend: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [2, 3, 1, 4, 2, 5, 3], color: '#EF4444' }] },
        incident_prediction: { labels: ['Août', 'Sep', 'Oct', 'Nov', 'Déc'], datasets: [{ data: [4, 3, 5, 4, 6], color: '#8B5CF6' }] },
        risk_trend: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [45, 50, 55, 60, 55, 65, 60], color: '#F59E0B' }] },
        performance_trend: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'], datasets: [{ data: [85, 87, 86, 88, 87, 89, 88], color: '#10B981' }] }
      }
    };
    return baseData[tab] || baseData.incidents;
  };

  useEffect(() => {
    loadAnalysis();
  }, [activeTab, filters]);

  const loadAnalysis = async () => {
    setLoading(true);
    setIaReport(''); // Reset IA report on load
    try {
      const data = await get(`/api/analysis/${activeTab}`, { params: filters });
      setData(data);
    } catch (error) {
      console.warn('Utilisation des données simulées pour:', activeTab);
      setData(generateMockData(activeTab, filters));
      toast.success(`Analyse "${activeTab}" chargée`);
    } finally {
      setLoading(false);
    }
  };

  // --- FONCTION IA : ANALYSE DES TENDANCES ---
  const handleGenerateReport = async () => {
    setLoadingIa(true);
    setIaReport('');
    try {
      const response = await post('/api/agents/diagnostic', {
        query: `Analyse les tendances du réseau GNL sur la période ${filters.period}. Fais un résumé stratégique des points clés et des recommandations.`,
        params: { 
          tab: activeTab,
          filters: filters,
          data: data // On envoie les données du graphique actuel
        }
      });
      setIaReport(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      toast.success('Rapport stratégique généré !');
    } catch (error) {
      toast.error('Erreur lors de la génération du rapport');
      setIaReport('Impossible de générer le rapport pour le moment.');
    } finally {
      setLoadingIa(false);
    }
  };
  // ------------------------------------

  // --- FONCTION IA : PRÉDICTION DES INCIDENTS ---
  const handlePredict = async () => {
    setLoadingPred(true);
    setPredictions(null);
    try {
      // Utiliser l'historique pour demander une prédiction
      const historyData = data?.incident_trend?.datasets?.[0]?.data || [2, 3, 1, 4, 2, 5, 3];
      const response = await post('/api/agents/diagnostic', {
        query: "Prédit le nombre d'incidents pour les 6 prochains mois basé sur l'historique. Retourne uniquement une liste de nombres séparés par des virgules (ex: 4,5,3,6,2,4).",
        params: { history: historyData }
      });
      
      // Parser la réponse pour l'afficher
      const predNumbers = response.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
      if(predNumbers.length > 0) {
        setPredictions(predNumbers);
        toast.success('Prédictions IA calculées !');
      } else {
        throw new Error("Format de prédiction invalide");
      }
    } catch (error) {
      toast.error('Erreur lors de la prédiction');
      setPredictions([4, 3, 5, 4, 6, 5]); // Fallback
    } finally {
      setLoadingPred(false);
    }
  };
  // ------------------------------------

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleExport = () => {
    toast.success('Export en cours...');
  };

  // Composant Helper pour le rendu des graphiques
  const renderChart = (type, dataObj, title) => {
    if (!dataObj) return <div className="h-[250px] flex items-center justify-center text-gray-500">Aucune donnée</div>;
    
    const labels = dataObj.labels || [];
    const dataset = dataObj.datasets?.[0] || {};
    const values = dataset.data || [];
    const color = dataset.backgroundColor || dataset.color || '#3B82F6';

    if(type === 'pie') {
      return (
        <ChartCard title={title}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={values.map((v, i) => ({ name: labels[i], value: v }))} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                {values.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={Array.isArray(color) ? color[index % color.length] : color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      );
    }

    if(type === 'bar') {
      return (
        <ChartCard title={title}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={values.map((v, i) => ({ name: labels[i], value: v }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill={Array.isArray(color) ? color[0] : color} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      );
    }

    // Line / Prediction
    if(type === 'line' || type === 'prediction') {
      // Si c'est une prédiction, on utilise les données passées ou calculées
      const displayValues = type === 'prediction' && predictions ? predictions : values;
      return (
        <ChartCard title={title}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayValues.map((v, i) => ({ name: labels[i % labels.length], value: v }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      );
    }
    
    return <div>Type de graphique non supporté</div>;
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              📊 Analyses Avancées
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Analyses approfondies du réseau GNL
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button onClick={loadAnalysis} className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
              <FiRefreshCw className="w-5 h-5" />
            </button>
            <button onClick={handleExport} className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center space-x-2">
              <FiDownload className="w-4 h-4" /><span>Exporter</span>
            </button>
          </div>
        </div>

        {/* Filtres */}
        <AnalysisFilters filters={filters} onFilterChange={handleFilterChange} />

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu */}
        {loading ? (
          <div className="flex justify-center py-12"><LoadingSpinner size="large" /></div>
        ) : (
          <div className="space-y-6">
            
            {/* BOUTONS IA */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleGenerateReport}
                disabled={loadingIa}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2 shadow-sm"
              >
                {loadingIa ? <LoadingSpinner size="small" /> : <FiFileText className="w-4 h-4" />}
                <span>{loadingIa ? 'Génération...' : '📄 Générer un rapport de synthèse'}</span>
              </button>
              
              {activeTab === 'trends' && (
                <button
                  onClick={handlePredict}
                  disabled={loadingPred}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 shadow-sm"
                >
                  {loadingPred ? <LoadingSpinner size="small" /> : <FiCpu className="w-4 h-4" />}
                  <span>{loadingPred ? 'Calcul...' : '🔮 Prédiction IA'}</span>
                </button>
              )}
            </div>

            {/* AFFICHAGE IA */}
            {iaReport && (
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg shadow-sm">
                <div className="flex items-start gap-3">
                  <FiCpu className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                    {iaReport}
                  </div>
                </div>
              </div>
            )}

            {/* GRAPHIQUES PAR ONGLET */}
            <div>
              {activeTab === 'incidents' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {renderChart('pie', data?.incidents_by_severity, 'Incidents par gravité')}
                  {renderChart('line', data?.incidents_over_time, 'Incidents dans le temps')}
                  {renderChart('bar', data?.incidents_by_cause, 'Incidents par cause')}
                  {renderChart('bar', data?.resolution_time, 'Temps de résolution (min)')}
                </div>
              )}

              {activeTab === 'risks' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {renderChart('pie', data?.risk_levels, 'Niveau de risque des équipements')}
                  {renderChart('line', data?.risk_trend, 'Évolution du risque')}
                  {renderChart('bar', data?.critical_equipment, 'Équipements critiques')}
                  {renderChart('bar', data?.risk_correlation, 'Corrélation risque/incidents')}
                </div>
              )}

              {activeTab === 'performance' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {renderChart('bar', data?.pipeline_performance, 'Performance des pipelines')}
                  {renderChart('line', data?.availability, 'Taux de disponibilité (Seuil 95%)', '95%')}
                  {renderChart('bar', data?.volume_transported, 'Volume transporté (m³)')}
                  {renderChart('line', data?.energy_efficiency, 'Efficacité énergétique (%)')}
                </div>
              )}

              {activeTab === 'trends' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {renderChart('line', data?.incident_trend, 'Tendance des incidents')}
                  {renderChart('prediction', data?.incident_prediction, 'Prédiction des incidents')}
                  {renderChart('line', data?.risk_trend, 'Tendance des risques')}
                  {renderChart('line', data?.performance_trend, 'Tendance de performance')}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}