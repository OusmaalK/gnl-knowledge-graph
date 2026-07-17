/**
 * IoT Settings - Paramétrage des capteurs IoT
 * ============================================================================
 * Description: Configuration du broker MQTT, des seuils d'alerte,
 * contrôle de l'écouteur et simulateur de capteur.
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { FiSave, FiRefreshCw, FiPlay, FiSquare, FiSend } from 'react-icons/fi';
import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export default function IoTSettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Formulaire
  const [formData, setFormData] = useState({
    mqtt_broker: 'localhost',
    mqtt_port: 1883,
    mqtt_topic: 'gnl/+/sensors',
    neo4j_label: 'SensorData',
    alert_threshold_temperature: 80,
    alert_threshold_pression: 20,
  });

  // États pour le contrôle de l'écouteur IoT
  const [iotStatus, setIotStatus] = useState('unknown');
  const [loadingIot, setLoadingIot] = useState(false);

  // États pour le simulateur de capteur
  const [simData, setSimData] = useState({
    equipment_id: 'PIPE-001',
    temperature: 45.5,
    pression: 12.3,
  });
  const [sendingSim, setSendingSim] = useState(false);

  const { api, get, post } = useApi();

  // Charger la configuration existante et l'état de l'écouteur
  useEffect(() => {
    loadSettings();
    checkIotStatus();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await get('/api/settings/iot');
      if (data) {
        setFormData({
          mqtt_broker: data.mqtt_broker || 'localhost',
          mqtt_port: data.mqtt_port || 1883,
          mqtt_topic: data.mqtt_topic || 'gnl/+/sensors',
          neo4j_label: data.neo4j_label || 'SensorData',
          alert_threshold_temperature: data.alert_threshold_temperature || 80,
          alert_threshold_pression: data.alert_threshold_pression || 20,
        });
      }
    } catch (error) {
      console.warn('Utilisation des valeurs par défaut pour les paramètres IoT');
    } finally {
      setLoading(false);
    }
  };

  // Fonctions pour piloter l'écouteur IoT
  const checkIotStatus = async () => {
    try {
      const res = await post('/api/iot/control', { action: 'status' });
      setIotStatus(res.running ? 'running' : 'stopped');
    } catch (e) { 
      setIotStatus('unknown'); 
    }
  };

  const toggleIot = async () => {
  setLoadingIot(true);
  const action = iotStatus === 'running' ? 'stop' : 'start';
  try {
    const res = await post('/api/iot/control', { action: action });
    if(res.status === 'started' || res.status === 'stopped') {
      toast.success(res.message);
      // --- CORRECTION : On attend 3 secondes avant de vérifier l'état ---
      setTimeout(async () => {
        await checkIotStatus();
      }, 3000); // 3 secondes
      // ----------------------------------------------------------------
    } else {
      toast.error(res.message);
    }
  } catch (e) {
    toast.error('Erreur de communication');
  } finally {
    setLoadingIot(false);
  }
};

  // Fonction pour envoyer la donnée de test
  const handleSimulate = async () => {
    if (iotStatus !== 'running') {
      toast.error("L'écouteur IoT doit être actif pour recevoir la donnée.");
      return;
    }
    setSendingSim(true);
    try {
      await post('/api/iot/simulate', simData);
      toast.success(`Donnée envoyée pour ${simData.equipment_id}`);
    } catch (error) {
      toast.error("Erreur lors de l'envoi de la donnée de test");
    } finally {
      setSendingSim(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await post('/api/settings/iot', formData);
      toast.success('Configuration enregistrée avec succès !');
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement de la configuration');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-6 p-6 max-w-2xl mx-auto">
        {/* En-tête */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              📡 Paramétrage IoT
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Configuration du broker MQTT et contrôle de l'écouteur
            </p>
          </div>
          <button 
            onClick={() => { loadSettings(); checkIotStatus(); }} 
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            <FiRefreshCw className="w-5 h-5" />
          </button>
        </div>

        {/* Formulaire de configuration */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="space-y-6">
            
            {/* Section MQTT */}
            <div>
              <h3 className="text-lg font-semibold mb-4 border-b pb-2">🔌 Configuration du Broker MQTT</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Adresse du broker</label>
                  <input
                    type="text"
                    value={formData.mqtt_broker}
                    onChange={(e) => setFormData({...formData, mqtt_broker: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Port</label>
                  <input
                    type="number"
                    value={formData.mqtt_port}
                    onChange={(e) => setFormData({...formData, mqtt_port: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="mt-2">
                <label className="block text-sm font-medium mb-1">Topic racine (ex: gnl/+/sensors)</label>
                <input
                  type="text"
                  value={formData.mqtt_topic}
                  onChange={(e) => setFormData({...formData, mqtt_topic: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Section Neo4j */}
            <div>
              <h3 className="text-lg font-semibold mb-4 border-b pb-2">🗄️ Base de données</h3>
              <div>
                <label className="block text-sm font-medium mb-1">Label Neo4j pour les données capteurs</label>
                <input
                  type="text"
                  value={formData.neo4j_label}
                  onChange={(e) => setFormData({...formData, neo4j_label: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Section Seuils d'alerte */}
            <div>
              <h3 className="text-lg font-semibold mb-4 border-b pb-2">🚨 Seuils d'alerte (Déclenchement incident)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Température max (°C)</label>
                  <input
                    type="number"
                    value={formData.alert_threshold_temperature}
                    onChange={(e) => setFormData({...formData, alert_threshold_temperature: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Pression max (bar)</label>
                  <input
                    type="number"
                    value={formData.alert_threshold_pression}
                    onChange={(e) => setFormData({...formData, alert_threshold_pression: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Bouton Enregistrer */}
            <div className="pt-4 border-t">
              <button
                onClick={handleSave}
                disabled={saving}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {saving ? <LoadingSpinner size="small" color="white" /> : <FiSave className="w-4 h-4" />}
                <span>{saving ? 'Enregistrement...' : 'Enregistrer la configuration'}</span>
              </button>
            </div>

          </div>
        </div>

        {/* SECTION CONTRÔLE DE L'ÉCOUTEUR IOT */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4 border-b pb-2">⚙️ Gestion de l'écouteur IoT</h3>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">État :</span>
              <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                iotStatus === 'running' ? 'bg-green-100 text-green-800' :
                iotStatus === 'stopped' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {iotStatus === 'running' ? '🟢 Actif' : iotStatus === 'stopped' ? '🔴 Arrêté' : '⚪ Inconnu'}
              </span>
            </div>
            <button
              onClick={toggleIot}
              disabled={loadingIot || iotStatus === 'unknown'}
              className={`px-4 py-2 text-white rounded-lg transition-colors ${
                iotStatus === 'running' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
              } disabled:opacity-50 flex items-center gap-2`}
            >
              {loadingIot ? <LoadingSpinner size="small" /> : iotStatus === 'running' ? <FiSquare className="w-4 h-4" /> : <FiPlay className="w-4 h-4" />}
              <span>{loadingIot ? 'Chargement...' : iotStatus === 'running' ? 'Arrêter l\'écouteur' : 'Démarrer l\'écouteur'}</span>
            </button>
          </div>
        </div>

        {/* --- SECTION SIMULATEUR DE CAPTEUR --- */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4 border-b pb-2">🧪 Simulateur de capteur</h3>
          <p className="text-sm text-gray-500 mb-4">Envoyez une donnée de test directement depuis la plateforme.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Équipement</label>
              <input
                type="text"
                value={simData.equipment_id}
                onChange={(e) => setSimData({...simData, equipment_id: e.target.value.toUpperCase()})}
                placeholder="ex: PIPE-001"
                className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Température (°C)</label>
              <input
                type="number"
                value={simData.temperature}
                onChange={(e) => setSimData({...simData, temperature: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Pression (bar)</label>
              <input
                type="number"
                value={simData.pression}
                onChange={(e) => setSimData({...simData, pression: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <button
            onClick={handleSimulate}
            disabled={sendingSim}
            className="mt-4 w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {sendingSim ? <LoadingSpinner size="small" color="white" /> : <FiSend className="w-4 h-4" />}
            <span>{sendingSim ? 'Envoi en cours...' : '📤 Envoyer la donnée de test'}</span>
          </button>
        </div>
        {/* ---------------------------------------- */}

      </div>
    </ErrorBoundary>
  );
}
