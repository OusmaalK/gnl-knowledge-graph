/**
 * Queries API - Requêtes avancées et analyses
 * ============================================================================
 * Description: Fonctions d'appel API pour les requêtes avancées
 * ============================================================================
 */

import { apiClient } from './client';

/**
 * Analyse l'impact d'un équipement
 */
export const analyzeImpact = async (equipmentId) => {
  const response = await apiClient.get('/api/queries/impact', {
    params: { equipment_id: equipmentId },
  });
  return response.data;
};

/**
 * Récupère la chaîne d'impact complète
 */
export const getImpactChain = async () => {
  const response = await apiClient.get('/api/queries/impact/chain');
  return response.data;
};

/**
 * Récupère l'historique des incidents
 */
export const getHistory = async (params = {}) => {
  const response = await apiClient.get('/api/queries/history/incidents', { params });
  return response.data;
};

/**
 * Récupère les statistiques des incidents
 */
export const getHistoryStatistics = async () => {
  const response = await apiClient.get('/api/queries/history/statistics');
  return response.data;
};

/**
 * Prédit le risque d'un équipement
 */
export const predictRisk = async (equipmentId) => {
  const response = await apiClient.get('/api/queries/risk/predict', {
    params: { equipment_id: equipmentId },
  });
  return response.data;
};

/**
 * Récupère les alertes de risque
 */
export const getRiskAlerts = async () => {
  const response = await apiClient.get('/api/queries/risk/alerts');
  return response.data;
};

/**
 * Trouve une route entre deux nœuds
 */
export const findRoute = async (params) => {
  const response = await apiClient.get('/api/queries/routes', { params });
  return response.data;
};

/**
 * Exécute une requête Cypher personnalisée
 */
export const executeCypher = async (query, params = {}) => {
  const response = await apiClient.post('/api/queries/cypher', { query, params });
  return response.data;
};

export default {
  analyzeImpact,
  getImpactChain,
  getHistory,
  getHistoryStatistics,
  predictRisk,
  getRiskAlerts,
  findRoute,
  executeCypher,
};