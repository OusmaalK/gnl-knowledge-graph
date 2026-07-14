/**
 * ImpactAnalysis - Analyse d'impact
 * ============================================================================
 * Description: Analyse de l'impact des pannes sur le réseau
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiSearch, FiAlertTriangle, FiUsers, FiLink } from 'react-icons/fi';
import { LoadingSpinner } from '../common/LoadingSpinner';

// Données simulées par défaut
const defaultData = {
  equipment_id: 'PIPE-001',
  equipment_name: 'Nord-Sud',
  equipment_type: 'Pipeline',
  statut: 'actif',
  niveau_impact: 'ÉLEVÉ',
  clients_impactes: ['EDF', 'Engie'],
  dependances_critiques: ['Compresseur Nord'],
  incidents_count: 1,
  gravites: ['critique'],
  recommendations: '🔴 Action immédiate requise\n1. Isoler l\'équipement\n2. Planifier la réparation d\'urgence\n3. Notifier les clients impactés'
};

export function ImpactAnalysis({ onAnalyze, data, loading }) {
  const [equipmentId, setEquipmentId] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!equipmentId.trim()) {
      setError('Veuillez spécifier un ID d\'équipement');
      return;
    }
    setError('');
    await onAnalyze(equipmentId.toUpperCase());
  };

  const impactData = data || defaultData;

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📊 Analyse d'impact
        </h3>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
          <input
            type="text"
            value={equipmentId}
            onChange={(e) => setEquipmentId(e.target.value.toUpperCase())}
            placeholder="ID de l'équipement (ex: PIPE-001)"
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
          >
            <FiSearch className="w-4 h-4" />
            <span>Analyser</span>
          </button>
        </form>
        {error && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
            <FiAlertTriangle className="w-5 h-5 mx-auto text-yellow-500 mb-1" />
            <p className="text-xs font-medium text-gray-500 uppercase">Niveau d'impact</p>
            <p className={`text-lg font-bold ${
              impactData.niveau_impact === 'CRITIQUE' ? 'text-red-600' :
              impactData.niveau_impact === 'ÉLEVÉ' ? 'text-orange-600' :
              impactData.niveau_impact === 'MODERE' ? 'text-yellow-600' :
              'text-green-600'
            }`}>
              {impactData.niveau_impact || 'N/A'}
            </p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
            <FiUsers className="w-5 h-5 mx-auto text-blue-500 mb-1" />
            <p className="text-xs font-medium text-gray-500 uppercase">Clients impactés</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {impactData.clients_impactes?.length || 0}
            </p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
            <FiLink className="w-5 h-5 mx-auto text-purple-500 mb-1" />
            <p className="text-xs font-medium text-gray-500 uppercase">Dépendances</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {impactData.dependances_critiques?.length || 0}
            </p>
          </div>
        </div>

        {impactData.equipment_name && (
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg mb-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              🔍 Équipement analysé
            </p>
            <p className="text-gray-900 dark:text-white">
              {impactData.equipment_name} ({impactData.equipment_id})
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Type: {impactData.equipment_type}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Statut: {impactData.statut || 'N/A'}</p>
          </div>
        )}

        {impactData.clients_impactes?.length > 0 && impactData.clients_impactes[0] !== 'N/A' && (
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg mb-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">👥 Clients impactés</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {impactData.clients_impactes.map((client, index) => (
                <span key={index} className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm">
                  {client}
                </span>
              ))}
            </div>
          </div>
        )}

        {impactData.dependances_critiques?.length > 0 && impactData.dependances_critiques[0] !== 'N/A' && (
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg mb-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">🔧 Dépendances critiques</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {impactData.dependances_critiques.map((dep, index) => (
                <span key={index} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg text-sm">
                  {dep}
                </span>
              ))}
            </div>
          </div>
        )}

        {impactData.incidents_count > 0 && (
          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 mb-3">
            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300">⚠️ Incidents associés</p>
            <p className="text-sm text-yellow-700 dark:text-yellow-400">
              {impactData.incidents_count} incident(s) sur cet équipement
            </p>
            {impactData.gravites?.length > 0 && impactData.gravites[0] !== 'N/A' && (
              <p className="text-sm text-yellow-600 dark:text-yellow-500">
                Gravités: {impactData.gravites.join(', ')}
              </p>
            )}
          </div>
        )}

        {impactData.recommendations && (
          <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-sm font-medium text-green-800 dark:text-green-300">💡 Recommandations</p>
            <pre className="text-sm text-green-700 dark:text-green-400 whitespace-pre-wrap mt-1">
              {impactData.recommendations}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// ✅ EXPORT PAR DÉFAUT (AJOUTER)
export default ImpactAnalysis;