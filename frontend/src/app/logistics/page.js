/**
 * Logistics - Logistique et routes
 * ============================================================================
 * Description: Optimisation des routes et analyse logistique
 * ============================================================================
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { 
  FiMap, 
  FiNavigation,
  FiTruck, 
  FiAnchor,
  FiSearch,
  FiRefreshCw,
  FiDownload,
  FiCpu,
  FiRefreshCcw,
} from 'react-icons/fi';

// IMPORTS CHART.JS POUR LA CARTE THERMIQUE
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useApi } from '@/hooks/useApi';

// --- RouteFinder ---
function RouteFinder({ onSearch, loading }) {
  const [startId, setStartId] = useState('');
  const [endId, setEndId] = useState('');
  const [excludeId, setExcludeId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!startId || !endId) return;
    setIsSubmitting(true);
    try {
      await onSearch({ start_id: startId, end_id: endId, exclude_id: excludeId || undefined });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">🗺️ Trouver une route</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Départ</label>
          <input type="text" value={startId} onChange={(e) => setStartId(e.target.value.toUpperCase())} placeholder="ex: TERM-001" className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Arrivée</label>
          <input type="text" value={endId} onChange={(e) => setEndId(e.target.value.toUpperCase())} placeholder="ex: CLIENT-001" className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Exclure (optionnel)</label>
          <input type="text" value={excludeId} onChange={(e) => setExcludeId(e.target.value.toUpperCase())} placeholder="ex: PIPE-001" className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500" />
        </div>
        <button type="submit" disabled={isSubmitting || loading} className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2">
          {isSubmitting || loading ? <LoadingSpinner size="small" color="white" /> : <><FiSearch className="w-4 h-4" /><span>Rechercher</span></>}
        </button>
      </form>
    </div>
  );
}

// --- RouteMap ---
function RouteMap({ data, onAlternative, isLoadingAlternative }) {
  if (!data || !data.nodes) {
    return <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500">🗺️ Aucune route sélectionnée</div>;
  }

  const getStatusColor = (status) => {
    const s = status?.toLowerCase() || 'unknown';
    switch (s) {
      case 'ok': case 'actif': case 'up': return 'bg-green-100 text-green-800 border-green-200';
      case 'critique': case 'incident': case 'down': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': case 'maintenance': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusEmoji = (status) => {
    const s = status?.toLowerCase() || 'unknown';
    switch (s) {
      case 'ok': case 'actif': case 'up': return '🟢';
      case 'critique': case 'incident': case 'down': return '🔴';
      case 'warning': case 'maintenance': return '🟡';
      default: return '⚪';
    }
  };

  const reliability = data.reliability_score || 0;
  let reliabilityColor = 'bg-green-500';
  let reliabilityText = 'Route très fiable';
  
  if (reliability < 40) {
    reliabilityColor = 'bg-red-500';
    reliabilityText = 'Route dangereuse';
  } else if (reliability < 70) {
    reliabilityColor = 'bg-orange-500';
    reliabilityText = 'Route risquée';
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">🗺️ Itinéraire</h3>
        <button
          onClick={onAlternative}
          disabled={isLoadingAlternative}
          className="px-3 py-1.5 bg-yellow-500 text-white text-sm rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {isLoadingAlternative ? <LoadingSpinner size="small" /> : <FiRefreshCcw className="w-4 h-4" />}
          <span>{isLoadingAlternative ? 'Recherche...' : '🔄 Route alternative'}</span>
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        {data.nodes.map((node, i) => (
          <div key={i} className="flex items-center">
            <div className={`px-3 py-2 rounded-lg text-sm font-mono border ${getStatusColor(node.status)} flex items-center gap-2`}>
              <span>{getStatusEmoji(node.status)}</span>
              <span>{node.id}</span>
              {node.status && <span className="text-[10px] opacity-70 hidden sm:inline">({node.status})</span>}
            </div>
            {i < data.nodes.length - 1 && <span className="mx-2 text-gray-400">→</span>}
          </div>
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-500">Distance: {data.distance || 0} sauts</div>

      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">🛡️ Indice de fiabilité</span>
          <span className={`text-sm font-bold ${reliabilityColor.replace('bg-', 'text-')}`}>
            {reliability}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
          <div 
            className={`h-2.5 rounded-full ${reliabilityColor}`} 
            style={{ width: `${reliability}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-500 mt-2">{reliabilityText}</p>
      </div>
    </div>
  );
}

// --- SupplyChainGraph ---
function SupplyChainGraph({ data }) {
  const containerRef = useRef(null);
  
  const graphData = data && data.length > 0 ? data : [
    { source: 'TotalEnergies', target: 'Fos-sur-Mer', type: 'Fournisseur' },
    { source: 'Fos-sur-Mer', target: 'Nord-Sud', type: 'Terminal' },
    { source: 'Nord-Sud', target: 'EDF', type: 'Pipeline' }
  ];

  useEffect(() => {
    if (!containerRef.current) return;

    const loadCytoscape = async () => {
      const cytoscape = (await import('cytoscape')).default;
      const dagre = (await import('cytoscape-dagre')).default;
      cytoscape.use(dagre);

      const elements = [];
      const nodeMap = new Map();

      graphData.forEach((link) => {
        if (!nodeMap.has(link.source)) {
          nodeMap.set(link.source, true);
          elements.push({ 
            data: { id: link.source, label: link.source }, 
            style: { 'background-color': '#3B82F6', 'color': 'white' }
          });
        }
        if (!nodeMap.has(link.target)) {
          nodeMap.set(link.target, true);
          elements.push({ 
            data: { id: link.target, label: link.target }, 
            style: { 'background-color': '#10B981', 'color': 'white' }
          });
        }
        elements.push({
          data: { 
            id: `${link.source}-${link.target}`, 
            source: link.source, 
            target: link.target, 
            label: link.type || '' 
          }
        });
      });

      const cy = cytoscape({
        container: containerRef.current,
        elements: elements,
        style: [
          { selector: 'node', style: { 'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'width': '80px', 'height': '80px', 'font-size': '12px', 'shape': 'round-rectangle', 'border-width': 2, 'border-color': '#fff' } },
          { selector: 'edge', style: { 'width': 3, 'line-color': '#9CA3AF', 'target-arrow-color': '#9CA3AF', 'target-arrow-shape': 'triangle', 'label': 'data(label)', 'font-size': '10px', 'text-rotation': 'autorotate', 'curve-style': 'bezier' } }
        ],
        layout: { name: 'dagre', animate: true, padding: 30 }
      });

      cy.on('layoutstop', () => {
        try { cy.fit(); cy.center(); } catch (e) { console.warn("Erreur de centrage ignorée:", e); }
      });
    };

    loadCytoscape();
  }, [graphData]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">📦 Graphe de la chaîne d'approvisionnement</h3>
      <div ref={containerRef} className="w-full h-[400px] bg-gray-50 dark:bg-gray-700/30 rounded-lg" />
      <p className="text-xs text-gray-500 mt-2 text-center">Visualisation interactive du flux Fournisseur ➔ Client</p>
    </div>
  );
}

// --- RiskHeatmap (VERSION CORRIGÉE) ---
function RiskHeatmap({ data, loading }) {
  if (loading) return <div className="flex justify-center py-8"><LoadingSpinner /></div>;
  if (!data || data.length === 0) return <div className="text-center py-8 text-gray-500">Aucune donnée de risque disponible.</div>;

  const chartData = {
    labels: data.map(p => p.id),
    datasets: [
      {
        label: 'Score de fiabilité (%)',
        data: data.map(p => p.reliability),
        backgroundColor: data.map(p => p.reliability < 40 ? '#EF4444' : p.reliability < 70 ? '#F59E0B' : '#10B981'),
        borderColor: data.map(p => p.reliability < 40 ? '#DC2626' : p.reliability < 70 ? '#D97706' : '#059669'),
        borderWidth: 1,
      },
    ],
  };

  // OPTIONS CORRIGÉES AVEC RESIZE
  const options = {
    responsive: true,
    maintainAspectRatio: false, // IMPORTANT : Évite l'écrasement
    resizeDelay: 100, // Donne le temps au DOM de se mettre à jour
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            return label + ': ' + context.parsed.y + '%';
          }
        }
      }
    },
    scales: {
      y: { 
        min: 0, 
        max: 100, 
        ticks: { callback: function(value) { return value + '%'; } },
        grid: { color: 'rgba(0,0,0,0.05)' }
      },
      x: { grid: { display: false } }
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">📈 Carte thermique des risques (Score de fiabilité)</h3>
      <div className="h-[250px] w-full relative">
        <Bar data={chartData} options={options} />
      </div>
      <div className="flex justify-center gap-6 mt-4 text-xs">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500"></span> Fiable (70-100%)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-orange-500"></span> À surveiller (40-69%)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500"></span> Critique (0-39%)</span>
      </div>
    </div>
  );
}

// --- Main Page ---
export default function LogisticsPage() {
  const [activeTab, setActiveTab] = useState('routes');
  const [loading, setLoading] = useState(false);
  const [routeData, setRouteData] = useState(null);
  const [supplyChain, setSupplyChain] = useState([]);
  const [impactData, setImpactData] = useState(null);
  const [riskHeatmapData, setRiskHeatmapData] = useState([]);
  const [loadingHeatmap, setLoadingHeatmap] = useState(false);

  // États pour l'onglet Impact
  const [impactSearchId, setImpactSearchId] = useState('');
  const [impactReport, setImpactReport] = useState(null);

  // États pour l'IA et l'Alternative
  const [iaAnalysis, setIaAnalysis] = useState('');
  const [loadingIa, setLoadingIa] = useState(false);
  const [loadingAlternative, setLoadingAlternative] = useState(false);

  const { api, get, post } = useApi();

  const tabs = [
    { id: 'routes', label: '🗺️ Routes', icon: FiNavigation },
    { id: 'supply', label: '📦 Chaîne', icon: FiTruck },
    { id: 'impact', label: '📊 Impact', icon: FiAnchor },
  ];

  const mockSupplyChain = [
    { source: 'TotalEnergies', target: 'Fos-sur-Mer', type: 'Fournisseur' },
    { source: 'Fos-sur-Mer', target: 'Nord-Sud', type: 'Terminal' },
    { source: 'Nord-Sud', target: 'EDF', type: 'Pipeline' }
  ];

  const mockData = {
    supply: mockSupplyChain,
    impact: { equipment_name: 'Nord-Sud', niveau_impact: 'ÉLEVÉ', clients_impactes: ['EDF'], incidents_count: 1 },
    route: { 
      nodes: [
        { id: 'TERM-001', status: 'ok' },
        { id: 'PIPE-001', status: 'critique' },
        { id: 'CLIENT-001', status: 'ok' }
      ], 
      distance: 2 
    }
  };

  useEffect(() => {
    if (activeTab === 'supply') { 
      setSupplyChain(mockData.supply); 
    }
    if (activeTab === 'impact') { 
      loadRiskHeatmap();
    }
  }, [activeTab]);

  const loadRiskHeatmap = async () => {
    setLoadingHeatmap(true);
    try {
      const data = await get('/api/logistics/risk-heatmap');
      setRiskHeatmapData(data);
    } catch (error) {
      console.warn("Erreur carte thermique:", error);
      // Données mock pour tester
      setRiskHeatmapData([
        { id: 'PIPE-001', nom: 'Nord-Sud', reliability: 20, statut: 'critique', incidents: 3 },
        { id: 'PIPE-002', nom: 'Est-Ouest', reliability: 85, statut: 'ok', incidents: 0 },
        { id: 'PIPE-003', nom: 'Gazoduc Sud', reliability: 45, statut: 'warning', incidents: 1 },
      ]);
    } finally {
      setLoadingHeatmap(false);
    }
  };

  const handleRouteSearch = async (params) => {
    setLoading(true);
    try {
      const response = await post('/api/logistics/route', params);
      let routeToDisplay = null;
      if (response && typeof response === 'object' && response.raw_data) {
        routeToDisplay = response.raw_data;
      } else if (response && typeof response === 'object' && response.nodes) {
        routeToDisplay = response;
      } else {
        routeToDisplay = {
          nodes: [
            { id: params.start_id, status: 'ok' },
            { id: 'PIPE-001', status: 'ok' },
            { id: params.end_id, status: 'ok' }
          ],
          distance: 1
        };
        toast.success('Route trouvée (Mode secours)');
      }
      setRouteData(routeToDisplay);
      toast.success('Route trouvée !');
    } catch (error) {
      console.error("Erreur lors de la recherche de route :", error);
      toast.error("Erreur lors de la recherche de la route");
    } finally {
      setLoading(false);
    }
  };

  const handleImpactSearch = async () => {
    if (!impactSearchId) return toast.error("Veuillez entrer un ID d'équipement");
    
    setImpactReport(null);
    try {
      const response = await post('/api/agents/logistics', {
        query: `Analyse en profondeur l'impact potentiel de l'équipement ${impactSearchId}. Donne un rapport stratégique avec des recommandations concrètes.`,
        params: { equipment_id: impactSearchId }
      });
      setImpactReport(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      toast.success('Rapport d\'impact généré par l\'IA !');
    } catch (error) {
      toast.error('Erreur lors de l\'analyse d\'impact');
    }
  };

  const handleAlternativeRoute = async () => {
    if (!routeData || !routeData.nodes || routeData.nodes.length < 2) {
      toast.error("Veuillez d'abord rechercher une route.");
      return;
    }

    const startId = routeData.nodes[0].id;
    const endId = routeData.nodes[routeData.nodes.length - 1].id;
    const nodeToExclude = routeData.nodes.find(n => n.status === 'critique' || n.status === 'down')?.id;

    if (!nodeToExclude) {
      toast.info("Aucun nœud critique trouvé sur cette route. L'alternative est identique.");
    }

    setLoadingAlternative(true);
    try {
      const response = await post('/api/agents/logistics', {
        query: "Trouve une route alternative",
        params: {
          find_alternative: true,
          start: startId,
          end: endId,
          exclude: nodeToExclude
        }
      });

      if (response && response.raw_data && response.raw_data.distance === -1) {
        toast.error("Aucune route alternative trouvée dans la base de données.");
      } 
      else if (response && typeof response === 'object' && response.raw_data) {
        setRouteData(response.raw_data);
        toast.success('Route alternative trouvée !');
      } else {
        toast.error("Aucune route alternative trouvée.");
      }
    } catch (error) {
      console.error("Erreur route alternative:", error);
      toast.error("Erreur lors de la recherche de l'alternative");
    } finally {
      setLoadingAlternative(false);
    }
  };

  const handleLogisticsAI = async () => {
    setLoadingIa(true);
    setIaAnalysis('');
    try {
      const response = await post('/api/agents/logistics', {
        query: "Analyse la route actuelle, identifie les points de vigilance et donne des recommandations d'optimisation stratégiques.",
        params: { route: routeData }
      });
      if (typeof response === 'object' && response.text) {
        setIaAnalysis(response.text);
      } else {
        setIaAnalysis(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
      }
      toast.success('Analyse IA générée !');
    } catch (error) {
      console.error("Erreur IA Logistique:", error);
      toast.error('Erreur lors de la génération IA');
      setIaAnalysis('Impossible de générer l\'analyse pour le moment.');
    } finally {
      setLoadingIa(false);
    }
  };

  const handleRefresh = () => { window.location.reload(); };
  const handleExport = () => { toast.success('Export en cours...'); };

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">🗺️ Logistique GNL</h1>
            <p className="text-sm text-gray-500">Optimisation des routes et analyse logistique</p>
          </div>
          <div className="flex space-x-2">
            <button onClick={handleRefresh} className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
              <FiRefreshCw className="w-5 h-5" />
            </button>
            <button onClick={handleExport} className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center space-x-2">
              <FiDownload className="w-4 h-4" /><span>Exporter</span>
            </button>
          </div>
        </div>

        {/* Affichage IA (s'il y en a) */}
        {iaAnalysis && (
          <div className="mb-4 p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <FiCpu className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                {iaAnalysis}
              </div>
            </div>
          </div>
        )}

        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8">
            {tabs.map(tab => (
              <button 
                key={tab.id} 
                onClick={() => setActiveTab(tab.id)} 
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${activeTab === tab.id ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}
              >
                <tab.icon className="w-4 h-4" /><span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {loading ? <div className="flex justify-center py-12"><LoadingSpinner size="large" /></div> : (
          <>
            {activeTab === 'routes' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1"><RouteFinder onSearch={handleRouteSearch} loading={loading} /></div>
                
                <div className="lg:col-span-2 space-y-4">
                  {/* Bouton IA pour l'itinéraire */}
                  <div className="flex justify-end">
                    <button
                      onClick={handleLogisticsAI}
                      disabled={loadingIa || !routeData}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
                    >
                      {loadingIa ? <LoadingSpinner size="small" /> : <FiCpu className="w-4 h-4" />}
                      <span>{loadingIa ? 'Analyse en cours...' : '🧠 Analyser l\'itinéraire'}</span>
                    </button>
                  </div>

                  <RouteMap 
                    data={routeData || mockData.route} 
                    onAlternative={handleAlternativeRoute}
                    isLoadingAlternative={loadingAlternative}
                  />
                </div>
              </div>
            )}
            
            {activeTab === 'supply' && <SupplyChainGraph data={supplyChain} />}
            
            {activeTab === 'impact' && (
              <div className="space-y-8">
                
                {/* 1. Carte thermique (Via le composant, pas de wrapper en double) */}
                <RiskHeatmap data={riskHeatmapData} loading={loadingHeatmap} />
                
                {/* 2. Analyseur d'impact intelligent */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <FiSearch className="w-5 h-5 text-blue-500" /> Analyseur d'impact intelligent
                  </h3>
                  
                  <div className="flex flex-col sm:flex-row gap-3">
                    <input 
                      type="text" 
                      value={impactSearchId} 
                      onChange={(e) => setImpactSearchId(e.target.value.toUpperCase())} 
                      placeholder="ex: PIPE-001" 
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 outline-none" 
                    />
                    <button 
                      onClick={handleImpactSearch} 
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 whitespace-nowrap"
                    >
                      <FiSearch className="w-4 h-4" /> Analyser avec l'IA
                    </button>
                  </div>
                </div>

                {/* 3. Affichage du rapport IA */}
                {impactReport && (
                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl shadow-sm border border-purple-200 dark:border-purple-800 p-4">
                    <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-purple-800 dark:text-purple-300">
                      <FiCpu className="w-5 h-5" /> Rapport d'impact stratégique (IA)
                    </h3>
                    <div className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-line leading-relaxed">
                      {impactReport}
                    </div>
                  </div>
                )}

              </div>
            )}
          </>
        )}
      </div>
    </ErrorBoundary>
  );
}