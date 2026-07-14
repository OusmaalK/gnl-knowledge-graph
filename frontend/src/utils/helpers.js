/**
 * Helpers - Fonctions utilitaires
 * ============================================================================
 * Description: Fonctions helper pour l'application
 * ============================================================================
 */

import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import { v4 as uuidv4 } from 'uuid';

/**
 * Formate une date
 */
export const formatDate = (date, formatStr = 'dd/MM/yyyy HH:mm') => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, formatStr, { locale: fr });
  } catch {
    return 'N/A';
  }
};

/**
 * Formate une date relative (ex: "il y a 2 heures")
 */
export const formatRelativeDate = (date) => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: fr });
  } catch {
    return 'N/A';
  }
};

/**
 * Tronque un texte
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Capitalise une chaîne
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Génère un ID unique
 */
export const generateId = () => {
  return uuidv4();
};

/**
 * Génère un ID court
 */
export const generateShortId = (length = 8) => {
  return Math.random().toString(36).substring(2, 2 + length).toUpperCase();
};

/**
 * Vérifie si une chaîne est un ID valide
 */
export const isValidId = (id) => {
  if (!id) return false;
  const patterns = [
    /^FOUR-\d{3,4}$/i,
    /^TERM-\d{3,4}$/i,
    /^PIPE-\d{3,4}$/i,
    /^CLIENT-\d{3,4}$/i,
    /^COMP-\d{3,4}$/i,
    /^STOCK-\d{3,4}$/i,
    /^INC-\d{3,4}$/i,
    /^CMD-\d{3,4}$/i,
    /^METH-\d{3,4}$/i,
  ];
  return patterns.some(pattern => pattern.test(id));
};

/**
 * Extrait les IDs d'un texte
 */
export const extractIds = (text) => {
  if (!text) return [];
  const patterns = [
    /FOUR-\d{3,4}/gi,
    /TERM-\d{3,4}/gi,
    /PIPE-\d{3,4}/gi,
    /CLIENT-\d{3,4}/gi,
    /COMP-\d{3,4}/gi,
    /STOCK-\d{3,4}/gi,
    /INC-\d{3,4}/gi,
    /CMD-\d{3,4}/gi,
    /METH-\d{3,4}/gi,
  ];
  const ids = [];
  patterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      ids.push(...matches);
    }
  });
  return [...new Set(ids)];
};

/**
 * Groupe un tableau par clé
 */
export const groupBy = (array, key) => {
  if (!array || !key) return {};
  return array.reduce((acc, item) => {
    const groupKey = item[key];
    if (!acc[groupKey]) {
      acc[groupKey] = [];
    }
    acc[groupKey].push(item);
    return acc;
  }, {});
};

/**
 * Trie un tableau
 */
export const sortBy = (array, key, order = 'asc') => {
  if (!array) return [];
  const sorted = [...array];
  return sorted.sort((a, b) => {
    const aVal = a[key] ?? '';
    const bVal = b[key] ?? '';
    if (order === 'asc') {
      return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
    } else {
      return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
    }
  });
};

/**
 * Filtre un tableau par recherche
 */
export const filterBySearch = (array, search, fields) => {
  if (!array || !search) return array;
  const searchLower = search.toLowerCase();
  return array.filter(item => {
    return fields.some(field => {
      const value = String(item[field] || '').toLowerCase();
      return value.includes(searchLower);
    });
  });
};

/**
 * Debounce une fonction
 */
export const debounce = (func, delay = 300) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
};

/**
 * Throttle une fonction
 */
export const throttle = (func, limit = 300) => {
  let inThrottle = false;
  return (...args) => {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
};

/**
 * Classe CSS conditionnelle
 */
export const classNames = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

/**
 * Copie dans le presse-papiers
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    } catch {
      document.body.removeChild(textarea);
      return false;
    }
  }
};

/**
 * Télécharge un fichier
 */
export const downloadFile = (content, filename, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Parse un paramètre de requête
 */
export const parseQueryParams = (search) => {
  if (!search) return {};
  const params = new URLSearchParams(search);
  const result = {};
  params.forEach((value, key) => {
    result[key] = value;
  });
  return result;
};

/**
 * Construit une chaîne de requête
 */
export const buildQueryString = (params) => {
  if (!params) return '';
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
};

/**
 * Vérifie si l'application est en mode développement
 */
export const isDevelopment = () => {
  return process.env.NODE_ENV === 'development';
};

/**
 * Vérifie si l'application est en mode production
 */
export const isProduction = () => {
  return process.env.NODE_ENV === 'production';
};

/**
 * Obtient l'URL de base de l'API
 */
export const getApiBaseUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

/**
 * Obtient l'URL de base du WebSocket
 */
export const getWsBaseUrl = () => {
  return process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
};

/**
 * Convertit un texte en slug
 */
export const slugify = (text) => {
  if (!text) return '';
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

export default {
  formatDate,
  formatRelativeDate,
  truncateText,
  capitalize,
  generateId,
  generateShortId,
  isValidId,
  extractIds,
  groupBy,
  sortBy,
  filterBySearch,
  debounce,
  throttle,
  classNames,
  copyToClipboard,
  downloadFile,
  parseQueryParams,
  buildQueryString,
  isDevelopment,
  isProduction,
  getApiBaseUrl,
  getWsBaseUrl,
  slugify,
};