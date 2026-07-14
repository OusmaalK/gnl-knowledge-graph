/**
 * Constants - Constantes globales
 * ============================================================================
 * Description: Constantes utilisées dans toute l'application
 * ============================================================================
 */

// Types de nœuds
export const NODE_TYPES = {
    FOURNISSEUR: 'Fournisseur',
    TERMINAL: 'Terminal',
    METHANIER: 'Méthanier',
    PIPELINE: 'Pipeline',
    CLIENT: 'Client',
    STOCKAGE: 'Stockage',
    COMPRESSEUR: 'Compresseur',
    COMMANDE: 'Commande',
    INCIDENT: 'Incident',
    MAINTENANCE: 'Maintenance',
  };
  
  export const NODE_TYPES_LIST = Object.values(NODE_TYPES);
  
  export const NODE_COLORS = {
    Fournisseur: '#3B82F6',
    Terminal: '#10B981',
    Méthanier: '#8B5CF6',
    Pipeline: '#F59E0B',
    Client: '#EF4444',
    Stockage: '#6366F1',
    Compresseur: '#EC4899',
    Commande: '#F472B6',
    Incident: '#DC2626',
    Maintenance: '#8B5CF6',
  };
  
  export const NODE_ICONS = {
    Fournisseur: '🏭',
    Terminal: '🏗️',
    Méthanier: '🚢',
    Pipeline: '🔴',
    Client: '👤',
    Stockage: '📦',
    Compresseur: '⚙️',
    Commande: '📋',
    Incident: '🚨',
    Maintenance: '🔧',
  };
  
  // Types de relations
  export const RELATION_TYPES = {
    FOURNIT: 'FOURNIT',
    LIVRE_A: 'LIVRE_A',
    ALIMENTE: 'ALIMENTE',
    DESSERT: 'DESSERT',
    STOCKE: 'STOCKE',
    DEPEND_DE: 'DEPEND_DE',
    HISTORIQUE: 'HISTORIQUE',
    AFFECTE: 'AFFECTE',
    CAUSE: 'CAUSE',
    EXPLOITE_PAR: 'EXPLOITE_PAR',
    DEPART_DE: 'DEPART_DE',
    ARRIVE_A: 'ARRIVE_A',
  };
  
  export const RELATION_TYPES_LIST = Object.values(RELATION_TYPES);
  
  // Gravités des incidents
  export const INCIDENT_SEVERITIES = {
    CRITIQUE: 'critique',
    MAJEUR: 'majeur',
    MINEUR: 'mineur',
  };
  
  export const INCIDENT_SEVERITIES_LIST = Object.values(INCIDENT_SEVERITIES);
  
  export const INCIDENT_SEVERITY_COLORS = {
    [INCIDENT_SEVERITIES.CRITIQUE]: '#EF4444',
    [INCIDENT_SEVERITIES.MAJEUR]: '#F59E0B',
    [INCIDENT_SEVERITIES.MINEUR]: '#EAB308',
  };
  
  // Statuts
  export const STATUS = {
    ACTIF: 'actif',
    INACTIF: 'inactif',
    MAINTENANCE: 'maintenance',
    HORS_SERVICE: 'hors_service',
    EN_CONSTRUCTION: 'en_construction',
    EN_TEST: 'en_test',
    OUVERT: 'ouvert',
    EN_COURS: 'en_cours',
    RESOLU: 'resolu',
    FERME: 'ferme',
    PLANIFIE: 'planifie',
    TERMINE: 'termine',
    ANNULE: 'annule',
  };
  
  export const STATUS_COLORS = {
    [STATUS.ACTIF]: '#22C55E',
    [STATUS.INACTIF]: '#6B7280',
    [STATUS.MAINTENANCE]: '#F59E0B',
    [STATUS.HORS_SERVICE]: '#EF4444',
    [STATUS.EN_CONSTRUCTION]: '#3B82F6',
    [STATUS.EN_TEST]: '#8B5CF6',
    [STATUS.OUVERT]: '#EF4444',
    [STATUS.EN_COURS]: '#3B82F6',
    [STATUS.RESOLU]: '#22C55E',
    [STATUS.FERME]: '#6B7280',
    [STATUS.PLANIFIE]: '#3B82F6',
    [STATUS.TERMINE]: '#22C55E',
    [STATUS.ANNULE]: '#6B7280',
  };
  
  // Types d'agents
  export const AGENT_TYPES = {
    DIAGNOSTIC: 'diagnostic',
    INCIDENT: 'incident',
    LOGISTICS: 'logistics',
    MAINTENANCE: 'maintenance',
  };
  
  export const AGENT_NAMES = {
    [AGENT_TYPES.DIAGNOSTIC]: '🔍 Diagnostic',
    [AGENT_TYPES.INCIDENT]: '📋 Incidents',
    [AGENT_TYPES.LOGISTICS]: '🗺️ Logistique',
    [AGENT_TYPES.MAINTENANCE]: '🔧 Maintenance',
  };
  
  export const AGENT_DESCRIPTIONS = {
    [AGENT_TYPES.DIAGNOSTIC]: 'Analyse et diagnostic des incidents',
    [AGENT_TYPES.INCIDENT]: 'Gestion et historique des incidents',
    [AGENT_TYPES.LOGISTICS]: 'Routes et optimisation logistique',
    [AGENT_TYPES.MAINTENANCE]: 'Maintenance prédictive et risques',
  };
  
  // Limites par défaut
  export const DEFAULT_LIMIT = 20;
  export const MAX_LIMIT = 1000;
  
  // Durées de cache
  export const CACHE_TTL = {
    SHORT: 60, // 1 minute
    MEDIUM: 3600, // 1 heure
    LONG: 86400, // 24 heures
    VERY_LONG: 604800, // 7 jours
  };
  
  // Périodes de date
  export const DATE_RANGES = {
    '24h': { label: '24h', days: 1 },
    '7d': { label: '7 jours', days: 7 },
    '30d': { label: '30 jours', days: 30 },
    '90d': { label: '90 jours', days: 90 },
    all: { label: 'Tous', days: 0 },
  };
  
  // Layouts de graphe
  export const GRAPH_LAYOUTS = {
    cose: 'Cose',
    circle: 'Cercle',
    grid: 'Grille',
    concentric: 'Concentrique',
    breadthfirst: 'Largeur d\'abord',
    dagre: 'Dagre',
    random: 'Aléatoire',
  };
  
  // Messages d'erreur
  export const ERROR_MESSAGES = {
    NETWORK: 'Erreur de réseau. Vérifiez votre connexion.',
    UNAUTHORIZED: 'Vous devez être connecté pour accéder à cette ressource.',
    FORBIDDEN: 'Vous n\'avez pas les permissions nécessaires.',
    NOT_FOUND: 'La ressource demandée n\'existe pas.',
    SERVER_ERROR: 'Erreur interne du serveur. Veuillez réessayer plus tard.',
    VALIDATION: 'Des erreurs de validation sont présentes.',
    TIMEOUT: 'La requête a expiré. Veuillez réessayer.',
  };
  
  // Routes
  export const ROUTES = {
    HOME: '/',
    CHAT: '/chat',
    INCIDENTS: '/incidents',
    LOGISTICS: '/logistics',
    MAINTENANCE: '/maintenance',
    ANALYSIS: '/analysis',
    ADMIN: '/admin',
    LOGIN: '/login',
    REGISTER: '/register',
    PROFILE: '/profile',
    SETTINGS: '/settings',
  };
  
  export default {
    NODE_TYPES,
    NODE_TYPES_LIST,
    NODE_COLORS,
    NODE_ICONS,
    RELATION_TYPES,
    RELATION_TYPES_LIST,
    INCIDENT_SEVERITIES,
    INCIDENT_SEVERITIES_LIST,
    INCIDENT_SEVERITY_COLORS,
    STATUS,
    STATUS_COLORS,
    AGENT_TYPES,
    AGENT_NAMES,
    AGENT_DESCRIPTIONS,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    CACHE_TTL,
    DATE_RANGES,
    GRAPH_LAYOUTS,
    ERROR_MESSAGES,
    ROUTES,
  };