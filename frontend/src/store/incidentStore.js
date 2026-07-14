/**
 * Incident Store - Gestion d'état des incidents
 * ============================================================================
 * Description: Store Zustand pour la gestion des incidents
 * ============================================================================
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useIncidentStore = create(
  devtools(
    immer((set, get) => ({
      // État
      incidents: [],
      selectedIncident: null,
      loading: false,
      error: null,
      filters: {
        severity: 'all',
        status: 'all',
        dateRange: '30d',
        search: '',
        equipment: '',
        cause: '',
      },
      pagination: {
        page: 1,
        limit: 20,
        total: 0,
        totalPages: 0,
      },
      statistics: null,
      diagnostic: null,

      // Actions - Incidents
      setIncidents: (incidents) => set({ incidents }),
      addIncident: (incident) => set((state) => {
        state.incidents.unshift(incident);
      }),
      updateIncident: (incidentId, updates) => set((state) => {
        const index = state.incidents.findIndex(i => i.id === incidentId);
        if (index !== -1) {
          state.incidents[index] = { ...state.incidents[index], ...updates };
        }
      }),
      removeIncident: (incidentId) => set((state) => {
        state.incidents = state.incidents.filter(i => i.id !== incidentId);
      }),
      selectIncident: (incidentId) => {
        const { incidents } = get();
        const incident = incidents.find(i => i.id === incidentId);
        set({ selectedIncident: incident });
      },
      clearSelectedIncident: () => set({ selectedIncident: null }),

      // Actions - Filters
      setFilters: (newFilters) => set((state) => {
        state.filters = { ...state.filters, ...newFilters };
        state.pagination.page = 1; // Reset pagination on filter change
      }),
      clearFilters: () => set({
        filters: {
          severity: 'all',
          status: 'all',
          dateRange: '30d',
          search: '',
          equipment: '',
          cause: '',
        },
        pagination: { ...get().pagination, page: 1 },
      }),

      // Actions - Pagination
      setPagination: (pagination) => set({ pagination }),
      setPage: (page) => set((state) => {
        state.pagination.page = page;
      }),
      nextPage: () => set((state) => {
        if (state.pagination.page < state.pagination.totalPages) {
          state.pagination.page += 1;
        }
      }),
      prevPage: () => set((state) => {
        if (state.pagination.page > 1) {
          state.pagination.page -= 1;
        }
      }),

      // Actions - Statistics
      setStatistics: (statistics) => set({ statistics }),
      clearStatistics: () => set({ statistics: null }),

      // Actions - Diagnostic
      setDiagnostic: (diagnostic) => set({ diagnostic }),
      clearDiagnostic: () => set({ diagnostic: null }),

      // Actions - UI
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),

      // Actions - Reset
      reset: () => set({
        incidents: [],
        selectedIncident: null,
        loading: false,
        error: null,
        diagnostic: null,
        statistics: null,
        filters: {
          severity: 'all',
          status: 'all',
          dateRange: '30d',
          search: '',
          equipment: '',
          cause: '',
        },
        pagination: {
          page: 1,
          limit: 20,
          total: 0,
          totalPages: 0,
        },
      }),

      // Selectors (computed)
      getFilteredIncidents: () => {
        const { incidents, filters } = get();
        let filtered = incidents;

        if (filters.severity !== 'all') {
          filtered = filtered.filter(i => i.gravite === filters.severity);
        }

        if (filters.status !== 'all') {
          filtered = filtered.filter(i => i.statut === filters.status);
        }

        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filtered = filtered.filter(i =>
            i.id?.toLowerCase().includes(searchLower) ||
            i.description?.toLowerCase().includes(searchLower) ||
            i.cause?.toLowerCase().includes(searchLower)
          );
        }

        if (filters.equipment) {
          filtered = filtered.filter(i =>
            i.equipment_id === filters.equipment ||
            i.equipment_name?.toLowerCase().includes(filters.equipment.toLowerCase())
          );
        }

        if (filters.cause) {
          filtered = filtered.filter(i =>
            i.cause?.toLowerCase().includes(filters.cause.toLowerCase())
          );
        }

        return filtered;
      },

      getIncidentStats: () => {
        const { incidents } = get();
        return {
          total: incidents.length,
          bySeverity: {
            critique: incidents.filter(i => i.gravite === 'critique').length,
            majeur: incidents.filter(i => i.gravite === 'majeur').length,
            mineur: incidents.filter(i => i.gravite === 'mineur').length,
          },
          byStatus: {
            ouvert: incidents.filter(i => i.statut === 'ouvert').length,
            en_cours: incidents.filter(i => i.statut === 'en_cours').length,
            resolu: incidents.filter(i => i.statut === 'resolu').length,
            ferme: incidents.filter(i => i.statut === 'ferme').length,
          },
        };
      },

      getRecentIncidents: (limit = 5) => {
        const { incidents } = get();
        return [...incidents]
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, limit);
      },
    }))
  )
);