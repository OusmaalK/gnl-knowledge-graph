/**
 * IncidentDiagnostic - Diagnostic d'un incident avec IA
 * ============================================================================
 * Description: Analyse l'incident avec Groq (via l'API)
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  FiAlertCircle, 
  FiCheckCircle, 
  FiClock, 
  FiThumbsUp, 
  FiCpu 
} from 'react-icons/fi';

import { useApi } from '@/hooks/useApi';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export function IncidentDiagnostic({ incident }) {
  const [diagnostic, setDiagnostic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [iaReport, setIaReport] = useState(null); // Pour stocker la réponse IA
  const [loadingIa, setLoadingIa] = useState(false);
  
  const { get, post } = useApi();

  // Charger le diagnostic IA au chargement du composant
  useEffect(() => {
    if (incident) {
      loadDiagnostic();
    }
  }, [incident]);

  // --- FONCTION DIAGNOSTIC IA (GROQ VIA BACKEND) ---
  const loadDiagnostic = async () => {
    setLoading(true);
    try {
      // 1. Essayer de récupérer un diagnostic via l'IA
      setLoadingIa(true);
      const response = await post('/api/agents/diagnostic', {
        query: `Analyse l'incident ${incident.id} en profondeur. Donne un diagnostic stratégique, identifie la cause racine, et propose des actions concrètes.`,
        params: { incident_id: incident.id }
      });

      // 2. Si l'IA répond, on utilise son rapport
      // IMPORTANT : On vérifie aussi que la réponse ne contient pas le mot "Fallback"
      if (response && typeof response === 'string' && !response.includes('Fallback')) {
        const iaText = response;
        setIaReport(iaText);
        
        setDiagnostic({
          summary: `Incident ${incident.id} - Analyse par IA`,
          severity: incident.gravite || 'N/A',
          cause: incident.cause || 'Cause non identifiée',
          impact: `Impact sur l'équipement ${incident.equipment_name || incident.equipment_id}`,
          recommendations: [
            '📋 Consulter le rapport complet ci-dessous pour les recommandations détaillées.',
            '🤖 L\'intelligence artificielle a généré une analyse stratégique.'
          ],
          resolution_time: incident.duree_min ? `${incident.duree_min} minutes` : 'N/A',
          status: incident.statut || 'En cours d\'analyse',
          confidence: 'Élevé (Basé sur IA)',
          elapsed_time: 'Calculé en temps réel',
        });
      } 
      // Si la réponse est un objet JSON, on le traite aussi
      else if (response && typeof response === 'object') {
        const iaText = JSON.stringify(response, null, 2);
        setIaReport(iaText);
        setDiagnostic({
          summary: `Incident ${incident.id} - Analyse par IA`,
          severity: incident.gravite || 'N/A',
          cause: incident.cause || 'Cause non identifiée',
          impact: `Impact sur l'équipement ${incident.equipment_name || incident.equipment_id}`,
          recommendations: ['🤖 Consulter le rapport IA ci-dessous.'],
          resolution_time: incident.duree_min ? `${incident.duree_min} minutes` : 'N/A',
          status: incident.statut || 'En cours d\'analyse',
          confidence: 'Élevé',
          elapsed_time: 'Calculé en temps réel',
        });
      }
      else {
        // Si l'IA n'a pas répondu correctement, on lance une erreur pour déclencher le fallback
        throw new Error("Réponse IA invalide ou mode fallback détecté");
      }
    } catch (error) {
      console.warn('⚠️ IA non disponible, utilisation du diagnostic simulé');
      
      // 3. Fallback (Diagnostic simulé) si l'IA est en panne
      const recommendations = [];
      if (incident.cause === 'corrosion') {
        recommendations.push(
          '🔧 Inspecter la section corrodée du pipeline',
          '📋 Planifier un programme de lutte contre la corrosion',
          '🔬 Analyser les échantillons pour déterminer l\'étendue des dégâts'
        );
      } else if (incident.cause === 'panne mécanique') {
        recommendations.push(
          '🔧 Remplacer les pièces défectueuses',
          '📋 Planifier une maintenance préventive',
          '🔬 Effectuer des tests de performance post-réparation'
        );
      } else {
        recommendations.push(
          '🔍 Analyser la cause profonde de l\'incident',
          '📋 Documenter l\'incident pour analyse future',
          '🔧 Mettre en place des mesures préventives'
        );
      }

      setDiagnostic({
        summary: `Incident ${incident.id} - ${incident.description}`,
        severity: incident.gravite,
        cause: incident.cause || 'Cause non identifiée',
        impact: `Impact sur l'équipement ${incident.equipment_name || incident.equipment_id}`,
        recommendations: recommendations,
        resolution_time: incident.duree_min ? `${incident.duree_min} minutes` : 'N/A',
        status: incident.statut || 'En cours d\'analyse',
        confidence: 'Moyen (Mode secours)',
        elapsed_time: '2 heures',
      });

      // On affiche un message pour informer l'utilisateur du mode secours
      setIaReport("⚠️ L'intelligence artificielle est actuellement indisponible. Un diagnostic structuré a été généré en mode secours.");
    } finally {
      setLoading(false);
      setLoadingIa(false);
    }
  };
  // ------------------------------------------------

  if (loading) {
    return <LoadingSpinner size="large" />;
  }

  if (!diagnostic) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FiAlertCircle className="w-8 h-8 mx-auto mb-2" />
        <p>Diagnostic non disponible</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      
      {/* --- RAPPORT IA (EN HAUT DU PANNEAU) --- */}
      {loadingIa && <LoadingSpinner size="medium" />}
      
      {iaReport && (
        <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
          <div className="flex items-start gap-3 mb-2">
            <FiCpu className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
            <h4 className="font-semibold text-purple-900 dark:text-purple-300">🧠 Diagnostic stratégique (IA)</h4>
          </div>
          <div className="text-sm text-purple-800 dark:text-purple-400 whitespace-pre-line leading-relaxed">
            {iaReport}
          </div>
        </div>
      )}
      {/* ------------------------------------ */}

      {/* Résumé classique */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <h4 className="font-semibold text-blue-900 dark:text-blue-300">📋 Résumé du diagnostic</h4>
        <p className="text-blue-800 dark:text-blue-400 mt-1">{diagnostic.summary}</p>
      </div>

      {/* Cartes de métriques */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <p className="text-xs font-medium text-gray-500 uppercase">Gravité</p>
          <p className={`text-lg font-bold ${
            diagnostic.severity === 'critique' ? 'text-red-600' :
            diagnostic.severity === 'majeur' ? 'text-orange-600' :
            'text-yellow-600'
          }`}>
            {diagnostic.severity || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <p className="text-xs font-medium text-gray-500 uppercase">Statut</p>
          <p className={`text-lg font-bold ${
            diagnostic.status === 'resolu' ? 'text-green-600' :
            diagnostic.status === 'en_cours' ? 'text-blue-600' :
            'text-red-600'
          }`}>
            {diagnostic.status || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <p className="text-xs font-medium text-gray-500 uppercase">Temps de résolution</p>
          <p className="text-lg font-bold text-gray-900 dark:text-white">
            {diagnostic.resolution_time || 'N/A'}
          </p>
        </div>
      </div>

      {/* Cause */}
      <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <h4 className="font-semibold text-gray-900 dark:text-white">🛠️ Cause identifiée</h4>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{diagnostic.cause}</p>
      </div>

      {/* Impact */}
      <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <h4 className="font-semibold text-gray-900 dark:text-white">📊 Impact</h4>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{diagnostic.impact}</p>
      </div>

      {/* Recommandations (Simulées si l'IA n'a pas donné de tâches spécifiques) */}
      <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <h4 className="font-semibold text-green-900 dark:text-green-300">💡 Recommandations</h4>
        <ul className="mt-2 space-y-1">
          {diagnostic.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start space-x-2 text-green-800 dark:text-green-400">
              <FiCheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Métriques */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <FiClock className="w-5 h-5 mx-auto text-gray-400 mb-1" />
          <p className="text-xs font-medium text-gray-500 uppercase">Temps écoulé</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {diagnostic.elapsed_time || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <FiThumbsUp className="w-5 h-5 mx-auto text-gray-400 mb-1" />
          <p className="text-xs font-medium text-gray-500 uppercase">Niveau de confiance</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {diagnostic.confidence || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
          <FiAlertCircle className="w-5 h-5 mx-auto text-gray-400 mb-1" />
          <p className="text-xs font-medium text-gray-500 uppercase">Actions recommandées</p>
          <p className="font-semibold text-gray-900 dark:text-white">
            {diagnostic.recommendations?.length || 0}
          </p>
        </div>
      </div>
    </div>
  );
}