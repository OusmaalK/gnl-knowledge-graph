/**
 * Graph Store - Gestion d'état du graphe
 * ============================================================================
 * Description: Store Zustand pour la gestion du graphe
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useGraphStore = create(
  devtools(
    immer((set, get) => ({
      // État
      nodes: [],
      edges: [],
      selectedNode: null,
      selectedEdge: null,
      loading: false,
      error: null,
      layout: 'cose',
      zoom: 1,
      pan: { x: 0, y: 0 },
      highlightedNodes: [],
      highlightedEdges: [],
      filters: {
        nodeTypes: [],
        search: '',
      },

      // Actions - Nodes
      setNodes: (nodes) => set({ nodes }),
      addNode: (node) => set((state) => {
        state.nodes.push(node);
      }),
      updateNode: (nodeId, updates) => set((state) => {
        const index = state.nodes.findIndex(n => n.id === nodeId);
        if (index !== -1) {
          state.nodes[index] = { ...state.nodes[index], ...updates };
        }
      }),
      removeNode: (nodeId) => set((state) => {
        state.nodes = state.nodes.filter(n => n.id !== nodeId);
      }),
      selectNode: (nodeId) => set({ selectedNode: nodeId }),
      clearSelectedNode: () => set({ selectedNode: null }),

      // Actions - Edges
      setEdges: (edges) => set({ edges }),
      addEdge: (edge) => set((state) => {
        state.edges.push(edge);
      }),
      removeEdge: (edgeId) => set((state) => {
        state.edges = state.edges.filter(e => e.id !== edgeId);
      }),
      selectEdge: (edgeId) => set({ selectedEdge: edgeId }),
      clearSelectedEdge: () => set({ selectedEdge: null }),

      // Actions - Highlight
      highlightNodes: (nodeIds) => set({ highlightedNodes: nodeIds }),
      highlightEdges: (edgeIds) => set({ highlightedEdges: edgeIds }),
      clearHighlights: () => set({ highlightedNodes: [], highlightedEdges: [] }),

      // Actions - View
      setLayout: (layout) => set({ layout }),
      setZoom: (zoom) => set({ zoom }),
      setPan: (pan) => set({ pan }),
      resetView: () => set({ zoom: 1, pan: { x: 0, y: 0 } }),

      // Actions - Filters
      setNodeTypeFilter: (nodeTypes) => set((state) => {
        state.filters.nodeTypes = nodeTypes;
      }),
      setSearchFilter: (search) => set((state) => {
        state.filters.search = search;
      }),
      clearFilters: () => set({
        filters: { nodeTypes: [], search: '' }
      }),

      // Actions - API
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),

      // Actions - Import/Export
      importGraph: (data) => set({
        nodes: data.nodes || [],
        edges: data.edges || [],
      }),
      exportGraph: () => {
        const { nodes, edges } = get();
        return { nodes, edges };
      },

      // Actions - Reset
      reset: () => set({
        nodes: [],
        edges: [],
        selectedNode: null,
        selectedEdge: null,
        loading: false,
        error: null,
        highlightedNodes: [],
        highlightedEdges: [],
        filters: { nodeTypes: [], search: '' },
      }),

      // Selectors (computed)
      getFilteredNodes: () => {
        const { nodes, filters } = get();
        let filtered = nodes;
        
        if (filters.nodeTypes.length > 0) {
          filtered = filtered.filter(n => 
            filters.nodeTypes.includes(n.type)
          );
        }
        
        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filtered = filtered.filter(n =>
            n.id?.toLowerCase().includes(searchLower) ||
            n.label?.toLowerCase().includes(searchLower) ||
            n.name?.toLowerCase().includes(searchLower)
          );
        }
        
        return filtered;
      },

      getNode: (nodeId) => {
        const { nodes } = get();
        return nodes.find(n => n.id === nodeId);
      },

      getNeighbors: (nodeId) => {
        const { nodes, edges } = get();
        const neighborIds = new Set();
        edges.forEach(edge => {
          if (edge.source === nodeId) neighborIds.add(edge.target);
          if (edge.target === nodeId) neighborIds.add(edge.source);
        });
        return nodes.filter(n => neighborIds.has(n.id));
      },
    }))
  )
);