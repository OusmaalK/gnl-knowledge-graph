/**
 * MaintenancePlan - Plan de maintenance
 * ============================================================================
 * Description: Visualisation et gestion du plan de maintenance
 * ============================================================================
 */

'use client';

import { useState } from 'react';
import { FiCalendar, FiClock, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

export function MaintenancePlan({ equipment, onPlan }) {
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);

  const generatePlan = async () => {
    if (!equipment) {
      alert('Veuillez sélectionner un équipement');
      return;
    }
    setLoading(true);
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onPlan) {
        await onPlan(equipment.id);
      }
      
      // Générer un plan basé sur l'équipement
      const riskLevel = equipment.risk_level || 'MOYEN';
      const baseFrequency = riskLevel === 'CRITIQUE' ? 'Hebdomadaire' : 
                           riskLevel === 'ÉLEVÉ' ? 'Mensuelle' : 'Trimestrielle';
      
      setPlan({
        equipment: equipment.id,
        name: equipment.nom || equipment.id,
        schedule: [
          { task: 'Inspection visuelle', frequency: baseFrequency, priority: riskLevel === 'CRITIQUE' ? 'Critique' : 'Haute' },
          { task: 'Contrôle de pression', frequency: riskLevel === 'CRITIQUE' ? 'Hebdomadaire' : 'Mensuelle', priority: riskLevel === 'CRITIQUE' ? 'Critique' : 'Haute' },
          { task: 'Vérification des joints', frequency: riskLevel === 'CRITIQUE' ? 'Mensuelle' : 'Trimestrielle', priority: 'Moyenne' },
          { task: 'Test de performance', frequency: riskLevel === 'CRITIQUE' ? 'Mensuelle' : 'Semestrielle', priority: 'Haute' },
          { task: 'Maintenance préventive', frequency: riskLevel === 'CRITIQUE' ? 'Trimestrielle' : 'Annuelle', priority: 'Moyenne' },
        ],
        next_maintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        estimated_duration: riskLevel === 'CRITIQUE' ? '6 heures' : riskLevel === 'ÉLEVÉ' ? '4 heures' : '2 heures',
        resources: ['Équipe technique', 'Pièces de rechange', 'Outil de diagnostic'],
        notes: `Plan basé sur le niveau de risque : ${riskLevel}`,
      });
    } catch (error) {
      console.error('Erreur génération plan:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!equipment) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400">
        <div className="text-4xl mb-4">📋</div>
        <p className="text-lg font-medium">Aucun équipement sélectionné</p>
        <p className="text-sm">Sélectionnez un équipement pour générer un plan</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              📋 Plan de maintenance
            </h3>
            <p className="text-sm text-gray-500">
              {equipment.nom || equipment.id} - {equipment.type || 'Équipement'}
            </p>
          </div>
          <button
            onClick={generatePlan}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Génération...</span>
              </>
            ) : (
              <>
                <FiCalendar className="w-4 h-4" />
                <span>Générer le plan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {plan && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
              <p className="text-xs font-medium text-gray-500 uppercase">Prochaine maintenance</p>
              <p className="font-semibold text-gray-900 dark:text-white">{plan.next_maintenance}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
              <p className="text-xs font-medium text-gray-500 uppercase">Durée estimée</p>
              <p className="font-semibold text-gray-900 dark:text-white">{plan.estimated_duration}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
              <p className="text-xs font-medium text-gray-500 uppercase">Tâches</p>
              <p className="font-semibold text-gray-900 dark:text-white">{plan.schedule.length}</p>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">📋 Tâches de maintenance</h4>
            <div className="space-y-2">
              {plan.schedule.map((task, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {task.priority === 'Critique' ? (
                      <FiAlertCircle className="w-4 h-4 text-red-500" />
                    ) : (
                      <FiCheckCircle className="w-4 h-4 text-green-500" />
                    )}
                    <span className="font-medium text-gray-900 dark:text-white">{task.task}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">{task.frequency}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      task.priority === 'Critique' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                      task.priority === 'Haute' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">🔧 Ressources nécessaires</h4>
            <div className="flex flex-wrap gap-2">
              {plan.resources.map((resource, index) => (
                <span key={index} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg text-sm">
                  {resource}
                </span>
              ))}
            </div>
          </div>

          {plan.notes && (
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-500">📝 {plan.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}