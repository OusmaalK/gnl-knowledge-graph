/**
 * GraphEditor - Éditeur du graphe
 * ============================================================================
 * Description: Éditeur pour ajouter/modifier/supprimer des nœuds et relations
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  FiPlus, 
  FiEdit, 
  FiTrash2, 
  FiSave, 
  FiX, 
  FiLink,
  FiUser,
  FiMapPin,
  FiAlertTriangle,
  FiCheck,
  FiInfo 
} from 'react-icons/fi';

const nodeTypes = [
  { value: 'Fournisseur', label: '🏭 Fournisseur', color: '#3B82F6' },
  { value: 'Terminal', label: '🏗️ Terminal', color: '#10B981' },
  { value: 'Méthanier', label: '🚢 Méthanier', color: '#8B5CF6' },
  { value: 'Pipeline', label: '🔴 Pipeline', color: '#F59E0B' },
  { value: 'Client', label: '👤 Client', color: '#EF4444' },
  { value: 'Stockage', label: '📦 Stockage', color: '#6366F1' },
  { value: 'Compresseur', label: '⚙️ Compresseur', color: '#EC4899' },
  { value: 'Incident', label: '🚨 Incident', color: '#DC2626' },
  { value: 'Commande', label: '📋 Commande', color: '#F472B6' },
];

const relationTypes = [
  { value: 'FOURNIT', label: 'FOURNIT', description: 'Fournisseur → Terminal' },
  { value: 'LIVRE_A', label: 'LIVRE_A', description: 'Méthanier → Terminal' },
  { value: 'ALIMENTE', label: 'ALIMENTE', description: 'Terminal → Pipeline' },
  { value: 'DESSERT', label: 'DESSERT', description: 'Pipeline → Client' },
  { value: 'STOCKE', label: 'STOCKE', description: 'Terminal → Stockage' },
  { value: 'DEPEND_DE', label: 'DEPEND_DE', description: 'Pipeline → Compresseur' },
  { value: 'AFFECTE', label: 'AFFECTE', description: 'Incident → Équipement' },
];

export function GraphEditor({ onSave, onCancel, onDelete, editMode = false, initialData = null }) {
  const [mode, setMode] = useState(editMode ? 'edit' : 'add');
  const [nodeType, setNodeType] = useState(initialData?.type || 'Pipeline');
  const [properties, setProperties] = useState(initialData?.properties || {});
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState('node');

  const validateForm = () => {
    const newErrors = {};
    if (!properties.id) {
      newErrors.id = 'L\'ID est requis';
    } else if (!/^[A-Z]+-\d{3,4}$/.test(properties.id)) {
      newErrors.id = 'Format invalide (ex: PIPE-001)';
    }
    if (!properties.nom) {
      newErrors.nom = 'Le nom est requis';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) return;

    const data = {
      type: nodeType,
      properties: {
        id: properties.id.toUpperCase(),
        nom: properties.nom,
        statut: properties.statut || 'actif',
        ...properties,
      },
    };

    if (onSave) {
      onSave(data);
    }
  };

  const handleDelete = () => {
    if (onDelete && window.confirm('Voulez-vous vraiment supprimer cet élément ?')) {
      onDelete(properties.id);
    }
  };

  const handlePropertyChange = (key, value) => {
    setProperties(prev => ({ ...prev, [key]: value }));
    if (errors[key]) {
      setErrors(prev => ({ ...prev, [key]: null }));
    }
  };

  const getRequiredFields = () => {
    const fields = ['id', 'nom'];
    if (nodeType === 'Pipeline') {
      fields.push('longueur_km');
    }
    if (nodeType === 'Incident') {
      fields.push('gravite');
    }
    return fields;
  };

  const getPlaceholder = (field) => {
    const placeholders = {
      id: 'ex: PIPE-001',
      nom: 'Nom de l\'entité',
      longueur_km: 'ex: 200',
      pression_max_bar: 'ex: 80',
      capacite_m3: 'ex: 500000',
      gravite: 'critique, majeur, mineur',
      cause: 'Cause de l\'incident',
      description: 'Description détaillée',
    };
    return placeholders[field] || '';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 max-w-md w-full">
      {/* En-tête */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {mode === 'add' ? '✏️ Ajouter' : '📝 Modifier'} 
          </h3>
          {editMode && (
            <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full">
              Édition
            </span>
          )}
        </div>
        <button
          onClick={onCancel}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <FiX className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
        <button
          onClick={() => setActiveTab('node')}
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'node'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
          }`}
        >
          <FiUser className="inline mr-1" />
          Nœud
        </button>
        <button
          onClick={() => setActiveTab('relation')}
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'relation'
              ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
          }`}
        >
          <FiLink className="inline mr-1" />
          Relation
        </button>
      </div>

      {/* Contenu */}
      <div className="space-y-4">
        {activeTab === 'node' ? (
          <>
            {/* Type de nœud */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Type de nœud <span className="text-red-500">*</span>
              </label>
              <select
                value={nodeType}
                onChange={(e) => setNodeType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {nodeTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={properties.id || ''}
                onChange={(e) => handlePropertyChange('id', e.target.value)}
                placeholder={getPlaceholder('id')}
                className={`w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.id ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.id && (
                <p className="mt-1 text-xs text-red-500">{errors.id}</p>
              )}
            </div>

            {/* Nom */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nom <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={properties.nom || ''}
                onChange={(e) => handlePropertyChange('nom', e.target.value)}
                placeholder={getPlaceholder('nom')}
                className={`w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.nom ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.nom && (
                <p className="mt-1 text-xs text-red-500">{errors.nom}</p>
              )}
            </div>

            {/* Statut */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Statut
              </label>
              <select
                value={properties.statut || 'actif'}
                onChange={(e) => handlePropertyChange('statut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="actif">✅ Actif</option>
                <option value="inactif">⛔ Inactif</option>
                <option value="maintenance">🔧 Maintenance</option>
                <option value="hors_service">❌ Hors service</option>
                <option value="en_construction">🚧 En construction</option>
              </select>
            </div>

            {/* Champs supplémentaires selon le type */}
            {nodeType === 'Pipeline' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Longueur (km)
                </label>
                <input
                  type="number"
                  value={properties.longueur_km || ''}
                  onChange={(e) => handlePropertyChange('longueur_km', parseFloat(e.target.value))}
                  placeholder={getPlaceholder('longueur_km')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}

            {nodeType === 'Incident' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Gravité
                  </label>
                  <select
                    value={properties.gravite || 'mineur'}
                    onChange={(e) => handlePropertyChange('gravite', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="critique">🔴 Critique</option>
                    <option value="majeur">🟠 Majeur</option>
                    <option value="mineur">🟡 Mineur</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    value={properties.description || ''}
                    onChange={(e) => handlePropertyChange('description', e.target.value)}
                    placeholder={getPlaceholder('description')}
                    rows="2"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </>
            )}

            {nodeType === 'Terminal' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Capacité (m³)
                </label>
                <input
                  type="number"
                  value={properties.capacite_m3 || ''}
                  onChange={(e) => handlePropertyChange('capacite_m3', parseFloat(e.target.value))}
                  placeholder={getPlaceholder('capacite_m3')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
          </>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <FiInfo className="inline mr-1" />
                Les relations seront créées en sélectionnant les nœuds dans le graphe.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Type de relation
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {relationTypes.map((rel) => (
                  <option key={rel.value} value={rel.value}>
                    {rel.label} - {rel.description}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Source
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Sélectionner...</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Cible
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Sélectionner...</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Boutons d'action */}
      <div className="flex space-x-2 pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={handleSave}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
        >
          <FiSave className="w-4 h-4" />
          <span>{editMode ? 'Mettre à jour' : 'Ajouter'}</span>
        </button>
        
        {editMode && onDelete && (
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
          >
            <FiTrash2 className="w-4 h-4" />
            <span>Supprimer</span>
          </button>
        )}
        
        <button
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Annuler
        </button>
      </div>

      {/* Indicateur de champs requis */}
      <p className="mt-3 text-xs text-gray-400 dark:text-gray-500">
        <span className="text-red-500">*</span> Champs obligatoires
      </p>
    </div>
  );
}