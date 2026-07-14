/**
 * API - Export centralisé
 * ============================================================================
 * Description: Export de tous les modules API
 * ============================================================================
 */

export { apiClient } from './client';
export * as graphAPI from './graph';
export * as agentsAPI from './agents';
export * as incidentsAPI from './incidents';
export * as queriesAPI from './queries';

export default {
  client: apiClient,
  graph: graphAPI,
  agents: agentsAPI,
  incidents: incidentsAPI,
  queries: queriesAPI,
};