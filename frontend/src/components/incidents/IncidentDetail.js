/**
 * IncidentDetail - Détail d'un incident
 * ============================================================================
 * Description: Affichage détaillé d'un incident
 * ============================================================================
 */

'use client';

import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { FiClock, FiMapPin, FiUser, FiAlertTriangle, FiInfo } from 'react-icons/fi';

export function IncidentDetail({ incident }) {
  if (!incident) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FiInfo className="w-8 h-8 mx-auto mb-2" />
        <p>Aucun incident sélectionné</p>
      </div>
    );
  }

  // --- FONCTION SÉCURISÉE POUR FORMATER LES DATES ---
  const formatDateSafe = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      // Vérification supplémentaire : si la date est invalide (NaN), on retourne 'N/A'
      if (isNaN(d.getTime())) return 'N/A';
      return format(d, 'dd/MM/yyyy HH:mm', { locale: fr });
    } catch (e) {
      return 'N/A';
    }
  };
  // ----------------------------------------------------

  const date = formatDateSafe(incident.date);
  const created = formatDateSafe(incident.created_at);
  const updated = formatDateSafe(incident.updated_at);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">ID</p>
          <p className="font-mono text-gray-900 dark:text-white">{incident.id}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">Gravité</p>
          <p className={`font-medium capitalize ${
            incident.gravite === 'critique' ? 'text-red-600' :
            incident.gravite === 'majeur' ? 'text-orange-600' :
            'text-yellow-600'
          }`}>
            {incident.gravite || 'N/A'}
          </p>
        </div>
      </div>

      <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <p className="text-xs font-medium text-gray-500 uppercase">Description</p>
        <p className="text-gray-900 dark:text-white">{incident.description || 'N/A'}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase flex items-center space-x-1">
            <FiClock className="w-3 h-3" />
            <span>Date</span>
          </p>
          <p className="text-gray-900 dark:text-white">{date}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase flex items-center space-x-1">
            <FiAlertTriangle className="w-3 h-3" />
            <span>Durée</span>
          </p>
          <p className="text-gray-900 dark:text-white">{incident.duree_min ? `${incident.duree_min} minutes` : 'N/A'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase flex items-center space-x-1">
            <FiMapPin className="w-3 h-3" />
            <span>Équipement</span>
          </p>
          <p className="text-gray-900 dark:text-white">{incident.equipment_name || incident.equipment_id || 'N/A'}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase flex items-center space-x-1">
            <FiUser className="w-3 h-3" />
            <span>Cause</span>
          </p>
          <p className="text-gray-900 dark:text-white">{incident.cause || 'N/A'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">Action</p>
          <p className="text-gray-900 dark:text-white">{incident.action || 'Aucune action enregistrée'}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">Statut</p>
          <p className={`font-medium capitalize ${
            incident.statut === 'resolu' ? 'text-green-600' :
            incident.statut === 'en_cours' ? 'text-blue-600' :
            'text-red-600'
          }`}>
            {incident.statut || 'N/A'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">Créé le</p>
          <p className="text-sm text-gray-900 dark:text-white">{created}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs font-medium text-gray-500 uppercase">Mis à jour le</p>
          <p className="text-sm text-gray-900 dark:text-white">{updated}</p>
        </div>
      </div>
    </div>
  );
}