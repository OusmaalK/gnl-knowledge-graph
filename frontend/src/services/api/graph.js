/**
 * Graph API - Opérations sur le graphe
 * ============================================================================
 * Description: Fonctions d'appel API pour les opérations sur le graphe
 * ============================================================================
 */

import { apiClient } from './client';

/**
 * Récupère le graphe complet
 */
export const getGraph = async (params = {}) => {
  const response = await apiClient.get('/api/graph', { params });
  return response.data;
};

/**
 * Récupère les nœuds du graphe
 */
export const getNodes = async (params = {}) => {
  const response = await apiClient.get('/api/graph/nodes', { params });
  return response.data;
};

/**
 * Récupère un nœud par son ID
 */
export const getNode = async (id) => {
  const response = await apiClient.get(`/api/graph/nodes/${id}`);
  return response.data;
};

/**
 * Crée un nouveau nœud
 */
export const createNode = async (nodeData) => {
  const response = await apiClient.post('/api/graph/nodes', nodeData);
  return response.data;
};

/**
 * Met à jour un nœud
 */
export const updateNode = async (id, nodeData) => {
  const response = await apiClient.put(`/api/graph/nodes/${id}`, nodeData);
  return response.data;
};

/**
 * Supprime un nœud
 */
export const deleteNode = async (id) => {
  const response = await apiClient.delete(`/api/graph/nodes/${id}`);
  return response.data;
};

/**
 * Récupère les voisins d'un nœud
 */
export const getNeighbors = async (id) => {
  const response = await apiClient.get(`/api/graph/nodes/${id}/neighbors`);
  return response.data;
};

/**
 * Récupère les relations du graphe
 */
export const getEdges = async (params = {}) => {
  const response = await apiClient.get('/api/graph/edges', { params });
  return response.data;
};

/**
 * Crée une nouvelle relation
 */
export const createEdge = async (edgeData) => {
  const response = await apiClient.post('/api/graph/edges', edgeData);
  return response.data;
};

/**
 * Supprime une relation
 */
export const deleteEdge = async (id) => {
  const response = await apiClient.delete(`/api/graph/edges/${id}`);
  return response.data;
};

/**
 * Récupère les statistiques du graphe
 */
export const getStatistics = async () => {
  const response = await apiClient.get('/api/graph/statistics');
  return response.data;
};

/**
 * Trouve le plus court chemin entre deux nœuds
 */
export const findShortestPath = async (startId, endId) => {
  const response = await apiClient.get(`/api/graph/path/${startId}/${endId}`);
  return response.data;
};

/**
 * Exporte le graphe
 */
export const exportGraph = async (format = 'json') => {
  const response = await apiClient.get(`/api/graph/export`, {
    params: { format },
    responseType: format === 'json' ? 'json' : 'blob',
  });
  return response.data;
};

/**
 * Importe un graphe
 */
export const importGraph = async (data) => {
  const response = await apiClient.post('/api/graph/import', data);
  return response.data;
};

export default {
  getGraph,
  getNodes,
  getNode,
  createNode,
  updateNode,
  deleteNode,
  getNeighbors,
  getEdges,
  createEdge,
  deleteEdge,
  getStatistics,
  findShortestPath,
  exportGraph,
  importGraph,
};