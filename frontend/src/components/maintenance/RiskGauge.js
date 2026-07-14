/**
 * RiskGauge - Jauge de risque maintenance
 * ============================================================================
 * Description: Jauge de risque pour la maintenance prédictive
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { FiAlertCircle, FiClock, FiUsers } from 'react-icons/fi';

export function RiskGauge({ equipment, riskData }) {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (equipment) {
      // Générer des données de risque basées sur l'équipement
      const incidents = equipment.incidents || 0;
      const baseScore = Math.min(20 + incidents * 20 + Math.floor(Math.random() * 20), 95);
      
      const riskLevel = baseScore >= 70 ? 'CRITIQUE' :
                       baseScore >= 50 ? 'ELEVE' :
                       baseScore >= 30 ? 'MOYEN' : 'FAIBLE';
      
      setRisk({
        score: baseScore,
        niveau: riskLevel,
        incidents_count: incidents,
        clients_count: 1,
        last_maintenance: '2026-06-15',
        next_maintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        recommendations: [
          'Inspection programmée dans 30 jours',
          'Vérifier les joints de sécurité',
          'Surveillance des paramètres de pression',
        ],
      });
      setLoading(false);
    }
  }, [equipment]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!risk) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>Aucune donnée de risque disponible</p>
      </div>
    );
  }

  const getColor = (score) => {
    if (score >= 70) return { bg: '#EF4444', text: 'text-red-600', border: 'border-red-500' };
    if (score >= 50) return { bg: '#F59E0B', text: 'text-orange-600', border: 'border-orange-500' };
    if (score >= 30) return { bg: '#EAB308', text: 'text-yellow-600', border: 'border-yellow-500' };
    return { bg: '#22C55E', text: 'text-green-600', border: 'border-green-500' };
  };

  const colors = getColor(risk.score);
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (risk.score / 100) * circumference;

  const getNiveauClasses = () => {
    if (risk.score >= 70) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    if (risk.score >= 50) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
    if (risk.score >= 30) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
  };

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white">
            {equipment?.nom || equipment?.id || 'Équipement'}
          </h4>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Score de risque
          </p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getNiveauClasses()}`}>
          {risk.niveau || 'FAIBLE'}
        </div>
      </div>

      <div className="relative flex justify-center">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="10"
            className="dark:stroke-gray-700"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={colors.bg}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 80 80)"
            className="transition-all duration-1000"
          />
          <text
            x="80"
            y="80"
            textAnchor="middle"
            dominantBaseline="central"
            className="text-2xl font-bold text-gray-900 dark:text-white"
          >
            {risk.score}
          </text>
          <text
            x="80"
            y="105"
            textAnchor="middle"
            dominantBaseline="central"
            className="text-xs text-gray-500 dark:text-gray-400"
          >
            / 100
          </text>
        </svg>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Incidents</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {risk.incidents_count || 0}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Clients impactés</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {risk.clients_count || 0}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Dernière maintenance</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {risk.last_maintenance || 'N/A'}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Prochaine maintenance</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {risk.next_maintenance || 'N/A'}
          </span>
        </div>
      </div>

      {risk.recommendations && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-sm font-medium text-blue-800 dark:text-blue-300">💡 Recommandations</p>
          <ul className="mt-1 space-y-1 text-sm text-blue-700 dark:text-blue-400">
            {risk.recommendations.map((rec, index) => (
              <li key={index}>• {rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}