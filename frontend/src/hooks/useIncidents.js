/**
 * useIncidents - Hook pour la gestion des incidents
 * ============================================================================
 * Description: Hook personnalisé pour la gestion des incidents
 * ============================================================================
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useApi } from './useApi';

export function useIncidents() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    severity: 'all',
    status: 'all',
    dateRange: '30d',
    search: '',
    equipment: '',
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
  });
  const { get, post, put, del } = useApi();

  const loadIncidents = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = {
        ...filters,
        ...params,
        page: params.page || pagination.page,
        limit: params.limit || pagination.limit,
      };
      const data = await get('/api/incidents', queryParams);
      setIncidents(data.items || []);
      setPagination({
        page: data.page || 1,
        limit: data.limit || 20,
        total: data.total || 0,
        totalPages: data.totalPages || 0,
      });
    } catch (err) {
      setError(err.message);
      console.error('Erreur chargement incidents:', err);
    } finally {
      setLoading(false);
    }
  }, [get, filters, pagination.page, pagination.limit]);

  const getIncident = useCallback(async (id) => {
    try {
      const data = await get(`/api/incidents/${id}`);
      return data;
    } catch (err) {
      console.error('Erreur récupération incident:', err);
      throw err;
    }
  }, [get]);

  const createIncident = useCallback(async (incidentData) => {
    try {
      const data = await post('/api/incidents', incidentData);
      await loadIncidents();
      return data;
    } catch (err) {
      console.error('Erreur création incident:', err);
      throw err;
    }
  }, [post, loadIncidents]);

  const updateIncident = useCallback(async (id, incidentData) => {
    try {
      const data = await put(`/api/incidents/${id}`, incidentData);
      await loadIncidents();
      return data;
    } catch (err) {
      console.error('Erreur mise à jour incident:', err);
      throw err;
    }
  }, [put, loadIncidents]);

  const deleteIncident = useCallback(async (id) => {
    try {
      await del(`/api/incidents/${id}`);
      await loadIncidents();
      return true;
    } catch (err) {
      console.error('Erreur suppression incident:', err);
      throw err;
    }
  }, [del, loadIncidents]);

  const diagnoseIncident = useCallback(async (id) => {
    try {
      const data = await get(`/api/incidents/${id}/diagnostic`);
      return data;
    } catch (err) {
      console.error('Erreur diagnostic incident:', err);
      throw err;
    }
  }, [get]);

  const getIncidentStatistics = useCallback(async () => {
    try {
      const data = await get('/api/incidents/statistics');
      return data;
    } catch (err) {
      console.error('Erreur statistiques incidents:', err);
      throw err;
    }
  }, [get]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const goToPage = useCallback((page) => {
    setPagination(prev => ({ ...prev, page }));
  }, []);

  const nextPage = useCallback(() => {
    if (pagination.page < pagination.totalPages) {
      setPagination(prev => ({ ...prev, page: prev.page + 1 }));
    }
  }, [pagination.page, pagination.totalPages]);

  const prevPage = useCallback(() => {
    if (pagination.page > 1) {
      setPagination(prev => ({ ...prev, page: prev.page - 1 }));
    }
  }, [pagination.page]);

  // Chargement initial
  useEffect(() => {
    loadIncidents();
  }, [filters, pagination.page]);

  return {
    incidents,
    selectedIncident,
    setSelectedIncident,
    loading,
    error,
    filters,
    pagination,
    loadIncidents,
    getIncident,
    createIncident,
    updateIncident,
    deleteIncident,
    diagnoseIncident,
    getIncidentStatistics,
    updateFilters,
    goToPage,
    nextPage,
    prevPage,
  };
}