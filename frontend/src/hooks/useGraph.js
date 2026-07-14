/**
 * useGraph - Hook pour la gestion du graphe
 * ============================================================================
 * Description: Hook personnalisé pour les opérations sur le graphe
 * ============================================================================
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useApi } from './useApi';

export function useGraph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [layout, setLayout] = useState('cose');
  const { get, post, put, delete: del } = useApi();

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await get('/api/graph');
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    } catch (err) {
      setError(err.message);
      console.error('Erreur chargement graphe:', err);
    } finally {
      setLoading(false);
    }
  }, [get]);

  const getNode = useCallback(async (nodeId) => {
    try {
      const data = await get(`/api/graph/nodes/${nodeId}`);
      return data;
    } catch (err) {
      console.error('Erreur récupération nœud:', err);
      throw err;
    }
  }, [get]);

  const createNode = useCallback(async (nodeData) => {
    try {
      const data = await post('/api/graph/nodes', nodeData);
      await loadGraph();
      return data;
    } catch (err) {
      console.error('Erreur création nœud:', err);
      throw err;
    }
  }, [post, loadGraph]);

  const updateNode = useCallback(async (nodeId, nodeData) => {
    try {
      const data = await put(`/api/graph/nodes/${nodeId}`, nodeData);
      await loadGraph();
      return data;
    } catch (err) {
      console.error('Erreur mise à jour nœud:', err);
      throw err;
    }
  }, [put, loadGraph]);

  const deleteNode = useCallback(async (nodeId) => {
    try {
      await del(`/api/graph/nodes/${nodeId}`);
      await loadGraph();
      return true;
    } catch (err) {
      console.error('Erreur suppression nœud:', err);
      throw err;
    }
  }, [del, loadGraph]);

  const createEdge = useCallback(async (edgeData) => {
    try {
      const data = await post('/api/graph/edges', edgeData);
      await loadGraph();
      return data;
    } catch (err) {
      console.error('Erreur création relation:', err);
      throw err;
    }
  }, [post, loadGraph]);

  const deleteEdge = useCallback(async (edgeId) => {
    try {
      await del(`/api/graph/edges/${edgeId}`);
      await loadGraph();
      return true;
    } catch (err) {
      console.error('Erreur suppression relation:', err);
      throw err;
    }
  }, [del, loadGraph]);

  const getNeighbors = useCallback(async (nodeId) => {
    try {
      const data = await get(`/api/graph/nodes/${nodeId}/neighbors`);
      return data;
    } catch (err) {
      console.error('Erreur récupération voisins:', err);
      throw err;
    }
  }, [get]);

  const findShortestPath = useCallback(async (startId, endId) => {
    try {
      const data = await get(`/api/graph/path/${startId}/${endId}`);
      return data;
    } catch (err) {
      console.error('Erreur recherche chemin:', err);
      throw err;
    }
  }, [get]);

  const getStatistics = useCallback(async () => {
    try {
      const data = await get('/api/graph/statistics');
      return data;
    } catch (err) {
      console.error('Erreur statistiques:', err);
      throw err;
    }
  }, [get]);

  const exportGraph = useCallback(async (format = 'json') => {
    try {
      const data = await get(`/api/graph/export?format=${format}`);
      return data;
    } catch (err) {
      console.error('Erreur export:', err);
      throw err;
    }
  }, [get]);

  // Chargement initial
  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  return {
    nodes,
    edges,
    selectedNode,
    setSelectedNode,
    selectedEdge,
    setSelectedEdge,
    loading,
    error,
    layout,
    setLayout,
    loadGraph,
    getNode,
    createNode,
    updateNode,
    deleteNode,
    createEdge,
    deleteEdge,
    getNeighbors,
    findShortestPath,
    getStatistics,
    exportGraph,
  };
}