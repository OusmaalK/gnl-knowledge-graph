/**
 * Incidents API - Gestion des incidents
 * ============================================================================
 * Description: Fonctions d'appel API pour la gestion des incidents
 * ============================================================================
 */

import { apiClient } from './client';

/**
 * Récupère la liste des incidents
 */
export const getIncidents = async (params = {}) => {
  const response = await apiClient.get('/api/incidents', { params });
  return response.data;
};

/**
 * Récupère un incident par son ID
 */
export const getIncident = async (id) => {
  const response = await apiClient.get(`/api/incidents/${id}`);
  return response.data;
};

/**
 * Crée un nouvel incident
 */
export const createIncident = async (incidentData) => {
  const response = await apiClient.post('/api/incidents', incidentData);
  return response.data;
};

/**
 * Met à jour un incident
 */
export const updateIncident = async (id, incidentData) => {
  const response = await apiClient.put(`/api/incidents/${id}`, incidentData);
  return response.data;
};

/**
 * Supprime un incident
 */
export const deleteIncident = async (id) => {
  const response = await apiClient.delete(`/api/incidents/${id}`);
  return response.data;
};

/**
 * Récupère le diagnostic d'un incident
 */
export const getDiagnostic = async (id) => {
  const response = await apiClient.get(`/api/incidents/${id}/diagnostic`);
  return response.data;
};

/**
 * Récupère les statistiques des incidents
 */
export const getIncidentStatistics = async () => {
  const response = await apiClient.get('/api/incidents/statistics');
  return response.data;
};

/**
 * Exporte les incidents
 */
export const exportIncidents = async (params = {}) => {
  const response = await apiClient.get('/api/incidents/export', {
    params,
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Récupère l'historique des incidents par équipement
 */
export const getIncidentHistory = async (equipmentId, params = {}) => {
  const response = await apiClient.get(`/api/incidents/history/${equipmentId}`, { params });
  return response.data;
};

export default {
  getIncidents,
  getIncident,
  createIncident,
  updateIncident,
  deleteIncident,
  getDiagnostic,
  getIncidentStatistics,
  exportIncidents,
  getIncidentHistory,
};