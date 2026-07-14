/**
 * Agents API - Appels aux agents IA
 * ============================================================================
 * Description: Fonctions d'appel API pour les agents IA
 * ============================================================================
 */

import { apiClient } from './client';

/**
 * Envoie un message à un agent (chat)
 */
export const chat = async (message) => {
  const response = await apiClient.post('/api/agents/chat', message);
  return response.data;
};

/**
 * Diagnostique un incident
 */
export const diagnoseIncident = async (incidentId) => {
  const response = await apiClient.post(`/api/agents/diagnostic`, { incident_id: incidentId });
  return response.data;
};

/**
 * Analyse les patterns d'incidents
 */
export const analyzePatterns = async () => {
  const response = await apiClient.get('/api/agents/diagnostic/patterns');
  return response.data;
};

/**
 * Trouve une route optimale
 */
export const findRoute = async (params) => {
  const response = await apiClient.post('/api/agents/routes', params);
  return response.data;
};

/**
 * Trouve une route alternative
 */
export const findAlternativeRoute = async (params) => {
  const response = await apiClient.post('/api/agents/routes/alternative', params);
  return response.data;
};

/**
 * Analyse le risque d'un équipement
 */
export const analyzeRisk = async (equipmentId) => {
  const response = await apiClient.post(`/api/agents/risk`, { equipment_id: equipmentId });
  return response.data;
};

/**
 * Récupère les équipements critiques
 */
export const getCriticalEquipment = async () => {
  const response = await apiClient.get('/api/agents/risk/critical');
  return response.data;
};

/**
 * Planifie la maintenance d'un équipement
 */
export const planMaintenance = async (equipmentId) => {
  const response = await apiClient.post(`/api/agents/risk/maintenance`, { equipment_id: equipmentId });
  return response.data;
};

/**
 * Récupère la chaîne d'approvisionnement
 */
export const getSupplyChain = async () => {
  const response = await apiClient.get('/api/agents/supply-chain');
  return response.data;
};

/**
 * Analyse l'impact d'un équipement
 */
export const analyzeImpact = async (equipmentId) => {
  const response = await apiClient.get(`/api/agents/impact/${equipmentId}`);
  return response.data;
};

export default {
  chat,
  diagnoseIncident,
  analyzePatterns,
  findRoute,
  findAlternativeRoute,
  analyzeRisk,
  getCriticalEquipment,
  planMaintenance,
  getSupplyChain,
  analyzeImpact,
};