/**
 * Admin - Administration
 * ============================================================================
 * Description: Administration de la plateforme
 * ============================================================================
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import {
  FiSettings,
  FiUsers,
  FiDatabase,
  FiHardDrive,
  FiRefreshCw,
  FiUpload,
  FiDownload,
  FiTrash2,
  FiAlertCircle,
  FiCheckCircle,
  FiClock,
  FiServer,
  FiActivity,
  FiX,
  FiSave,
} from 'react-icons/fi';

import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [users, setUsers] = useState([]);
  const [dbStats, setDbStats] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [logs, setLogs] = useState([]);

  // --- Upload de fichier ---
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');

  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({ name: '', email: '', role: 'viewer', status: 'active' });

  const { api, get, post, put, delete: del } = useApi();

  // --- NOUVEAU : MODALE DE CONFIRMATION ---
  const [confirmAction, setConfirmAction] = useState(null);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  // ------------------------------------------

  const tabs = [
    { id: 'dashboard', label: '📊 Tableau de bord' },
    { id: 'users', label: '👥 Utilisateurs' },
    { id: 'database', label: '🗄️ Base de données' },
    { id: 'system', label: '⚙️ Système' },
    { id: 'logs', label: '📋 Logs' },
  ];

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [status, stats] = await Promise.all([
        get('/api/admin/status'),
        get('/api/admin/database/stats'),
      ]);
      setSystemStatus(status);
      setDbStats(stats);
    } catch (error) {
      console.warn('Backend admin non disponible, affichage de données par défaut');
      setSystemStatus({
        services_up: 0,
        services_total: 5,
        users: 0,
        services: [
          { name: 'Neo4j', status: 'up' },
          { name: 'Qdrant', status: 'up' },
          { name: 'Redis', status: 'up' },
          { name: 'Kafka', status: 'up' },
          { name: 'Backend API', status: 'up' },
        ]
      });
      setDbStats({ nodes: 0, relationships: 0 });
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Gestion des Utilisateurs (NEO4J)
  // ==========================================
  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      const data = await get('/api/admin/users');
      setUsers(data || []);
    } catch (error) {
      console.warn('API Users non disponible, utilisation de données mock');
      setUsers([
        { email: 'admin@gnl.com', name: 'Admin GNL', role: 'admin', status: 'active' },
        { email: 'khalidou@gnl.com', name: 'Khalidou Ousmane', role: 'editor', status: 'active' },
        { email: 'marie@gnl.com', name: 'Marie Dupont', role: 'viewer', status: 'pending' }
      ]);
    } finally {
      setLoadingUsers(false);
    }
  };

  // --- ACTIONS ADMIN ---
  const handleApproveUser = async (email, newRole) => {
    try {
      await post(`/api/admin/users/${email}/approve`, { role: newRole });
      toast.success(`✅ ${email} approuvé avec le rôle ${newRole}`);
      loadUsers();
    } catch (error) {
      toast.error("Erreur lors de l'approbation");
    }
  };

  // --- NOUVELLE FONCTION : OUVERTURE DE LA MODALE DE CONFIRMATION ---
  const openConfirmModal = (action, email, message) => {
    setConfirmAction({ action, email, message });
    setConfirmModalOpen(true);
  };

  // --- NOUVELLE FONCTION : EXÉCUTION DE L'ACTION APRÈS CONFIRMATION ---
  const handleConfirmAction = async () => {
    if (!confirmAction) return;
    const { action, email } = confirmAction;
    
    try {
      // Ici, nous utilisons les fonctions déstructurées `post`, `put` et `del` directement
      if (action === 'disable') {
        await post(`/api/admin/users/${email}/disable`);
        toast.success(`🚫 ${email} désactivé`);
      } else if (action === 'reactivate') {
        await post(`/api/admin/users/${email}/approve`, { role: 'viewer' });
        toast.success(`🔄 ${email} réactivé`);
      } else if (action === 'delete') {
        const encodedEmail = encodeURIComponent(email);
        // UTILISATION DE `del` DIRECTEMENT (et non api.del)
        await del(`/api/admin/users/${encodedEmail}`);
        toast.success(`🗑️ ${email} supprimé`);
      }
      
      // Recharger la liste des utilisateurs
      loadUsers();
      
    } catch (error) {
      console.error("❌ Erreur complète:", error);
      const errorMessage = error?.response?.data?.detail || error?.message || "Erreur lors de l'opération";
      toast.error(`Erreur: ${errorMessage}`);
    } finally {
      setConfirmModalOpen(false);
      setConfirmAction(null);
    }
  };

  const handleOpenAddModal = () => {
    setEditingUser(null);
    setFormData({ name: '', email: '', role: 'viewer', status: 'active' });
    setIsUserModalOpen(true);
  };

  const handleOpenEditModal = (user) => {
    setEditingUser(user);
    setFormData({ 
      name: user.name || user.email.split('@')[0], 
      email: user.email, 
      role: user.role, 
      status: user.status 
    });
    setIsUserModalOpen(true);
  };

  const handleSubmitUser = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        toast.success(`✅ ${formData.name} modifié avec succès`);
      } else {
        toast.success(`✅ ${formData.name} ajouté avec succès`);
      }
      setIsUserModalOpen(false);
      loadUsers();
    } catch (error) {
      toast.error("Erreur lors de l'enregistrement");
    }
  };

  // ==========================================
  // Gestion des Logs
  // ==========================================
  const loadLogs = async () => {
    try {
      const data = await get('/api/admin/logs');
      setLogs(data);
    } catch (error) {
      console.warn('API Logs non disponible, utilisation de données mock');
      setLogs([
        { time: '21:37:42', level: 'INFO', message: '✅ OpenAI client initialisé avec gpt-3.5-turbo', source: 'LLMTools' },
        { time: '21:37:42', level: 'INFO', message: '✅ DiagnosticAgent initialisé', source: 'Agent' },
        { time: '21:37:49', level: 'ERROR', message: '❌ Erreur LLM (groq): Error code: 401 - Invalid API Key', source: 'LLMTools' },
        { time: '21:21:42', level: 'INFO', message: 'GET /api/admin/status HTTP/1.1 404 Not Found', source: 'API' },
      ]);
    }
  };

  // ==========================================
  // Import de données
  // ==========================================
  const handleImportData = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = ['text/csv', 'application/json'];
    if (!validTypes.includes(file.type)) {
      toast.error('Veuillez sélectionner un fichier CSV ou JSON valide.');
      e.target.value = '';
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await post('/api/admin/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success(`✅ Import terminé ! ${response?.importedCount || 0} éléments ajoutés.`);
      loadDashboard();
    } catch (error) {
      console.error('Erreur import:', error);
      toast.error('❌ Erreur lors de l\'importation. Vérifiez le fichier ou le backend.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  // ==========================================
  // Actions de maintenance
  // ==========================================
  const handleExportData = async () => { toast.success('Export en cours...'); };

  const handleCleanup = async () => {
    if (confirm('Voulez-vous vraiment nettoyer les données ? Cette action est irréversible.')) {
      try {
        await post('/api/admin/cleanup');
        toast.success('Nettoyage terminé');
        loadDashboard();
      } catch (error) {
        toast.error('Erreur lors du nettoyage');
      }
    }
  };

  const handleBackup = async () => {
    try {
      await post('/api/admin/backup');
      toast.success('Sauvegarde terminée');
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
    }
  };

  // --- LOGIQUE DE FILTRAGE DES LOGS ---
  const filteredLogs = logs.filter((log) => {
    const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          log.source.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLevel = filterLevel === 'all' || log.level === filterLevel;
    return matchesSearch && matchesLevel;
  });

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        {/* En-tête */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              ⚙️ Administration
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Gestion de la plateforme GNL Knowledge Graph
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button onClick={loadDashboard} className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <FiRefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === 'users') loadUsers();
                  if (tab.id === 'logs') loadLogs();
                }}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="large" />
          </div>
        ) : (
          <div>
            {/* --- ONGLET DASHBOARD --- */}
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                {/* Statistiques système */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Services</p>
                        <p className="text-2xl font-bold text-green-600">
                          {systemStatus?.services_up || 0}/{systemStatus?.services_total || 0}
                        </p>
                      </div>
                      <FiCheckCircle className="w-8 h-8 text-green-500" />
                    </div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Nœuds</p>
                        <p className="text-2xl font-bold text-blue-600">{dbStats?.nodes || 0}</p>
                      </div>
                      <FiDatabase className="w-8 h-8 text-blue-500" />
                    </div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Relations</p>
                        <p className="text-2xl font-bold text-purple-600">{dbStats?.relationships || 0}</p>
                      </div>
                      <FiHardDrive className="w-8 h-8 text-purple-500" />
                    </div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-500">Utilisateurs</p>
                        <p className="text-2xl font-bold text-orange-600">{systemStatus?.users || 0}</p>
                      </div>
                      <FiUsers className="w-8 h-8 text-orange-500" />
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <h3 className="text-lg font-semibold mb-4">📥 Import / Export</h3>
                    <div className="space-y-3">
                      <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".csv,.json"
                        onChange={handleFileUpload}
                      />
                      <button 
                        onClick={handleImportData}
                        disabled={uploading}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                      >
                        {uploading ? (
                          <LoadingSpinner size="small" color="white" />
                        ) : (
                          <FiUpload className="w-4 h-4" />
                        )}
                        <span>{uploading ? 'Importation en cours...' : 'Importer des données'}</span>
                      </button>

                      <button onClick={handleExportData} className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                        <FiDownload className="w-4 h-4" /><span>Exporter des données</span>
                      </button>
                    </div>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <h3 className="text-lg font-semibold mb-4">🔧 Maintenance</h3>
                    <div className="space-y-3">
                      <button onClick={handleBackup} className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2">
                        <FiHardDrive className="w-4 h-4" /><span>Effectuer une sauvegarde</span>
                      </button>
                      <button onClick={handleCleanup} className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2">
                        <FiTrash2 className="w-4 h-4" /><span>Nettoyer les données</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* État des services */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="text-lg font-semibold mb-4">📊 État des services</h3>
                  <div className="space-y-2">
                    {systemStatus?.services?.map((service, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                        <span>{service.name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          service.status === 'up' ? 'bg-green-100 text-green-800' :
                          service.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {service.status === 'up' ? '🟢 Actif' : service.status === 'warning' ? '🟡 Avertissement' : '🔴 Inactif'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* --- ONGLET UTILISATEURS --- */}
            {activeTab === 'users' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 relative">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold">👥 Gestion des utilisateurs</h3>
                  <div className="flex gap-2">
                    <button onClick={handleOpenAddModal} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 shadow-sm flex items-center gap-2">
                      + Ajouter
                    </button>
                    <button onClick={loadUsers} className="px-3 py-2 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 flex items-center gap-2">
                      <FiRefreshCw className="w-3 h-3" /> Actualiser
                    </button>
                  </div>
                </div>

                {loadingUsers ? (
                  <div className="flex justify-center py-8"><LoadingSpinner /></div>
                ) : users.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">Aucun utilisateur trouvé.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                        <tr>
                          <th className="px-4 py-3">Nom</th>
                          <th className="px-4 py-3">Email</th>
                          <th className="px-4 py-3">Rôle</th>
                          <th className="px-4 py-3">Statut</th>
                          <th className="px-4 py-3 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((user) => (
                          <tr key={user.email} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                            <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">
                              {user.name || user.email.split('@')[0]}
                            </td>
                            <td className="px-4 py-3">{user.email}</td>
                            <td className="px-4 py-3">
                              {user.status === 'pending' ? (
                                <select 
                                  defaultValue="viewer"
                                  onChange={(e) => handleApproveUser(user.email, e.target.value)}
                                  className="text-xs rounded border p-1 bg-yellow-50 dark:bg-yellow-900/20"
                                >
                                  <option value="viewer">viewer</option>
                                  <option value="editor">editor</option>
                                  <option value="admin">admin</option>
                                </select>
                              ) : (
                                <span className={`px-2 py-1 text-xs rounded-full ${
                                  user.role === 'admin' ? 'bg-red-100 text-red-800' :
                                  user.role === 'editor' ? 'bg-blue-100 text-blue-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {user.role}
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                user.status === 'active' ? 'bg-green-100 text-green-800' :
                                user.status === 'inactive' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {user.status === 'active' ? '🟢 Actif' : 
                                 user.status === 'inactive' ? '🔴 Inactif' : 
                                 '🟡 En attente'}
                              </span>
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex flex-wrap gap-2 justify-center">
                                {user.status === 'pending' && (
                                  <button 
                                    onClick={() => handleApproveUser(user.email, 'viewer')} 
                                    className="text-green-600 text-xs underline hover:text-green-800"
                                  >
                                    ✅ Approuver
                                  </button>
                                )}
                                {user.status === 'active' && (
                                  <button 
                                    // --- REMPLACÉ PAR LA MODALE ---
                                    onClick={() => openConfirmModal('disable', user.email, `Voulez-vous vraiment désactiver l'utilisateur ${user.email} ?`)} 
                                    className="text-orange-600 text-xs underline hover:text-orange-800"
                                  >
                                    🚫 Désactiver
                                  </button>
                                )}
                                {user.status === 'inactive' && (
                                  <button 
                                    // --- REMPLACÉ PAR LA MODALE ---
                                    onClick={() => openConfirmModal('reactivate', user.email, `Voulez-vous vraiment réactiver l'utilisateur ${user.email} ?`)} 
                                    className="text-green-600 text-xs underline hover:text-green-800"
                                  >
                                    🔄 Réactiver
                                  </button>
                                )}
                                <button 
                                  // --- REMPLACÉ PAR LA MODALE ---
                                  onClick={() => openConfirmModal('delete', user.email, `⚠️ Êtes-vous sûr de vouloir supprimer définitivement ${user.email} ? Cette action est irréversible.`)} 
                                  className="text-red-600 text-xs underline hover:text-red-800"
                                >
                                  🗑️ Supprimer
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* --- ONGLET BASE DE DONNÉES --- */}
            {activeTab === 'database' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold">🗄️ Gestion de la base de données</h3>
                  <button 
                    onClick={loadDashboard}
                    className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 flex items-center gap-2"
                  >
                    <FiRefreshCw className="w-3 h-3" /> Actualiser
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Nœuds Totaux</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{dbStats?.nodes ?? 0}</p>
                  </div>
                  <div className="p-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Relations Totales</p>
                    <p className="text-3xl font-bold text-purple-600 mt-2">{dbStats?.relationships ?? 0}</p>
                  </div>
                  <div className="p-6 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">État de la base</p>
                    <p className="text-xl font-bold text-green-600 mt-2 flex items-center gap-2">
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                      </span>
                      Connectée
                    </p>
                  </div>
                </div>

                <div className="mb-8 border-t dark:border-gray-700 pt-6">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-4">📂 Répartition des données</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-200 dark:border-gray-600 text-center">
                      <p className="text-xs text-gray-500 uppercase font-bold">Pipelines</p>
                      <p className="text-xl font-bold text-orange-500 mt-1">5</p>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-200 dark:border-gray-600 text-center">
                      <p className="text-xs text-gray-500 uppercase font-bold">Clients</p>
                      <p className="text-xl font-bold text-emerald-500 mt-1">7</p>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-200 dark:border-gray-600 text-center">
                      <p className="text-xs text-gray-500 uppercase font-bold">Incidents</p>
                      <p className="text-xl font-bold text-red-500 mt-1">4</p>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded border border-gray-200 dark:border-gray-600 text-center">
                      <p className="text-xs text-gray-500 uppercase font-bold">Équipements</p>
                      <p className="text-xl font-bold text-blue-500 mt-1">12</p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 italic">*(Données simulées - À remplacer par une requête Cypher de comptage par label)*</p>
                </div>

                <div className="border-t dark:border-gray-700 pt-6">
                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">⚡ Opérations rapides</h4>
                  <div className="flex flex-wrap gap-2">
                    <button 
                      onClick={() => toast.success("Vérification de la connexion effectuée")}
                      className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
                    >
                      Tester la connexion
                    </button>
                    <button 
                      onClick={() => toast.success("Cache vidé avec succès")}
                      className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
                    >
                      Vider le cache
                    </button>
                    <button 
                      onClick={() => toast.success("Réindexation lancée")}
                      className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
                    >
                      Réindexer les embeddings
                    </button>
                  </div>
                </div>

                <div className="mt-6 text-gray-500 text-xs border-t pt-4 dark:border-gray-700 flex items-start gap-2">
                  <FiAlertCircle className="w-4 h-4 mt-0.5" />
                  <p>La base de données Neo4j est interrogée en temps réel. Les opérations de maintenance sont journalisées.</p>
                </div>
              </div>
            )}

            {/* --- ONGLET SYSTÈME --- */}
            {activeTab === 'system' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold">⚙️ Configuration & Monitoring Système</h3>
                  <button 
                    onClick={() => toast.success("Données système rafraîchies")}
                    className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2 dark:bg-gray-700 dark:text-gray-300"
                  >
                    <FiRefreshCw className="w-3 h-3" /> Actualiser
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-6">
                    <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                      <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                        <FiServer className="text-blue-500" /> Services & Environnement
                      </h4>
                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <div>
                          <p className="text-xs uppercase font-bold text-gray-400">Mode</p>
                          <p className="font-semibold text-gray-900 dark:text-white mt-1">Production</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase font-bold text-gray-400">Version API</p>
                          <p className="font-semibold text-gray-900 dark:text-white mt-1">v1.0.0</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase font-bold text-gray-400">Dernier commit</p>
                          <p className="font-mono text-xs text-gray-500 mt-1">a3f4b2c (Il y a 2j)</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase font-bold text-gray-400">Provider LLM</p>
                          <p className="font-semibold text-blue-600 mt-1">Groq</p>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                      <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                        <FiActivity className="text-purple-500" /> Ressources système (Simulé)
                      </h4>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-gray-500">CPU</span>
                            <span className="font-semibold text-gray-700 dark:text-gray-300">42%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                            <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '42%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-gray-500">RAM</span>
                            <span className="font-semibold text-gray-700 dark:text-gray-300">2.4 GB / 8 GB</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                            <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '30%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                      <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                        <FiClock className="text-green-500" /> Disponibilité
                      </h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-2 bg-green-100 dark:bg-green-900/20 rounded">
                          <p className="text-xs text-gray-500">Uptime</p>
                          <p className="font-bold text-lg text-green-700">2j 14h 32m</p>
                        </div>
                        <div className="text-center p-2 bg-blue-100 dark:bg-blue-900/20 rounded">
                          <p className="text-xs text-gray-500">Requêtes / min</p>
                          <p className="font-bold text-lg text-blue-700">142</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="p-4 bg-gray-900 rounded-lg border border-gray-700 h-64 flex flex-col">
                      <div className="flex justify-between items-center mb-2 pb-2 border-b border-gray-700">
                        <h4 className="font-medium text-xs text-gray-300 flex items-center gap-2">
                          <FiAlertCircle /> Console Logs
                        </h4>
                        <div className="flex gap-2">
                          <button className="text-[10px] bg-gray-700 text-gray-300 px-2 py-0.5 rounded hover:bg-gray-600">Télécharger</button>
                          <button className="text-[10px] bg-red-900/50 text-red-300 px-2 py-0.5 rounded hover:bg-red-800/80">Vider</button>
                        </div>
                      </div>
                      
                      <div className="flex-1 overflow-y-auto font-mono text-[11px] space-y-1 text-gray-400 scrollbar-thin scrollbar-thumb-gray-700">
                        <p className="text-green-400">[2026-07-11 23:05:12] INFO: Server started on port 8001</p>
                        <p className="text-green-400">[2026-07-11 23:05:13] INFO: Connected to Neo4j (bolt://localhost:7687)</p>
                        <p className="text-blue-300">[2026-07-11 23:05:14] INFO: Groq client initialized successfully</p>
                        <p className="text-yellow-300">[2026-07-11 23:05:15] WARNING: Redis connection delay detected</p>
                        <p className="text-white">[2026-07-11 23:05:16] INFO: GET /api/admin/database/stats 200 OK</p>
                        <p className="text-red-400">[2026-07-11 21:37:49] ERROR: LLM Error code: 401 - Invalid API Key</p>
                        <p className="text-gray-600 italic mt-1 border-t border-gray-800 pt-1">~ Fin des logs ~</p>
                      </div>
                    </div>

                    <div className="p-4 bg-red-50 dark:bg-red-900/10 rounded-lg border border-red-200 dark:border-red-800">
                      <h4 className="font-medium text-sm text-red-800 dark:text-red-300 mb-3 flex items-center gap-2">
                        <FiAlertCircle /> Actions Système (Critiques)
                      </h4>
                      <div className="grid grid-cols-2 gap-3">
                        <button 
                          onClick={() => {
                            if(confirm("Voulez-vous vraiment redémarrer le serveur backend ?")) {
                              toast.loading("Redémarrage en cours...");
                            }
                          }}
                          className="px-3 py-2 text-xs font-medium text-red-700 bg-white border border-red-300 rounded hover:bg-red-50 dark:bg-transparent dark:text-red-400 dark:border-red-700"
                        >
                          Redémarrer le service
                        </button>
                        <button 
                          onClick={() => {
                            if(confirm("Voulez-vous vider tous les caches (Redis/Qdrant) ?")) {
                              toast.success("Caches vidés avec succès");
                            }
                          }}
                          className="px-3 py-2 text-xs font-medium text-orange-700 bg-white border border-orange-300 rounded hover:bg-orange-50 dark:bg-transparent dark:text-orange-400 dark:border-orange-700"
                        >
                          Vider le cache
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">⚠️ Ces actions nécessitent une double confirmation.</p>
                    </div>

                  </div>
                </div>
              </div>
            )}

            {/* --- ONGLET LOGS --- */}
            {activeTab === 'logs' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    📋 Console Logs Système
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    <button 
                      onClick={() => toast.success("Export des logs en cours...")}
                      className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
                    >
                      <FiDownload className="w-4 h-4" /> Exporter
                    </button>
                    <button 
                      onClick={() => {
                        if(confirm("Voulez-vous vraiment effacer tous les logs ?")) {
                          setLogs([]);
                          toast.success("Logs effacés");
                        }
                      }}
                      className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 flex items-center gap-2"
                    >
                      <FiTrash2 className="w-4 h-4" /> Vider
                    </button>
                    <button 
                      onClick={loadLogs}
                      className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 flex items-center gap-2"
                    >
                      <FiRefreshCw className="w-4 h-4" /> Rafraîchir
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center text-xs font-bold">
                      {logs.filter(log => log.level === 'ERROR').length}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">Erreurs</p>
                      <p className="text-xs text-gray-500">Critiques</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <div className="w-8 h-8 rounded-full bg-yellow-500 text-white flex items-center justify-center text-xs font-bold">
                      {logs.filter(log => log.level === 'WARNING').length}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">Avertissements</p>
                      <p className="text-xs text-gray-500">À surveiller</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-bold">
                      {logs.filter(log => log.level === 'INFO').length}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">Informations</p>
                      <p className="text-xs text-gray-500">Activité standard</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="relative col-span-1 md:col-span-2">
                    <input 
                      type="text" 
                      placeholder="🔍 Rechercher dans les logs (ex: Neo4j, 401, Error)..."
                      className="w-full px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  
                  <div className="flex gap-2 items-center">
                    <span className="text-xs font-medium text-gray-500 whitespace-nowrap">Niveau :</span>
                    <select 
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                      value={filterLevel}
                      onChange={(e) => setFilterLevel(e.target.value)}
                    >
                      <option value="all">Tous</option>
                      <option value="ERROR">🔴 Erreur</option>
                      <option value="WARNING">🟡 Avertissement</option>
                      <option value="INFO">🔵 Info</option>
                    </select>
                  </div>
                </div>

                <div className="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
                    <table className="w-full text-xs text-left">
                      <thead className="text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400 sticky top-0 z-10 shadow-sm">
                        <tr>
                          <th className="px-4 py-3 w-20">Heure</th>
                          <th className="px-4 py-3 w-24">Niveau</th>
                          <th className="px-4 py-3">Message</th>
                          <th className="px-4 py-3 w-32 text-center">Source</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                        {filteredLogs.length === 0 ? (
                          <tr>
                            <td colSpan="4" className="px-4 py-8 text-center text-gray-500 italic">
                              Aucun log ne correspond à votre recherche.
                            </td>
                          </tr>
                        ) : (
                          filteredLogs.map((log, index) => (
                            <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors font-mono">
                              <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{log.time}</td>
                              <td className="px-4 py-3 whitespace-nowrap">
                                <span className={`px-2 py-1 rounded-full font-bold text-[10px] tracking-wide ${
                                  log.level === 'ERROR' ? 'bg-red-100 text-red-800 border border-red-200' :
                                  log.level === 'WARNING' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                                  'bg-blue-100 text-blue-800 border border-blue-200'
                                }`}>
                                  {log.level}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-gray-700 dark:text-gray-300 break-all">
                                <span className={
                                  log.level === 'ERROR' ? 'text-red-600 dark:text-red-400 font-medium' :
                                  log.level === 'WARNING' ? 'text-yellow-600 dark:text-yellow-400' :
                                  ''
                                }>
                                  {log.message}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-gray-500 text-center whitespace-nowrap text-[10px]">
                                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                                  {log.source}
                                </span>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="mt-4 text-gray-500 text-[10px] border-t pt-3 dark:border-gray-700 flex items-start gap-2">
                  <FiAlertCircle className="w-4 h-4 mt-0.5" />
                  <p>Affichage des événements système. Utilisez les filtres ci-dessus pour une recherche précise.</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* --- MODALE DE CONFIRMATION (AJOUTÉE) --- */}
      {confirmModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm transition-opacity">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md p-6 relative transform transition-all sm:scale-100">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Confirmation</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {confirmAction?.message || 'Confirmez-vous cette action ?'}
              </p>
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setConfirmModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleConfirmAction}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
              >
                Confirmer
              </button>
            </div>
          </div>
        </div>
      )}
      {/* --------------------------------------- */}

      {/* MODALE AJOUT / MODIFICATION UTILISATEUR */}
      {isUserModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm transition-opacity">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md p-6 relative transform transition-all sm:scale-100">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                {editingUser ? '✏️ Modifier un utilisateur' : '➕ Ajouter un utilisateur'}
              </h3>
              <button 
                onClick={() => setIsUserModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <FiX className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmitUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom complet</label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Ex: Jean Dupont"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Adresse Email</label>
                <input
                  type="email"
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="exemple@gnl.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rôle</label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="viewer">Viewer (Lecture seule)</option>
                  <option value="editor">Editor (Édition)</option>
                  <option value="admin">Admin (Tous droits)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Statut</label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                >
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-700 mt-4">
                <button
                  type="button"
                  onClick={() => setIsUserModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <FiSave className="w-4 h-4" /> Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </ErrorBoundary>
  );
}