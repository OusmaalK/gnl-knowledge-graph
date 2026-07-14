/**
 * RiskHistory - Historique des risques
 * ============================================================================
 * Description: Graphique d'évolution des risques dans le temps
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { FiCalendar, FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

export function RiskHistory({ equipment, history }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Générer des données historiques simulées
    const labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'];
    const riskData = [];
    const incidentData = [];
    
    // Générer des données progressives
    let baseRisk = 30;
    let baseIncident = 1;
    
    for (let i = 0; i < 7; i++) {
      riskData.push(baseRisk + Math.floor(Math.random() * 20));
      incidentData.push(baseIncident + Math.floor(Math.random() * 3));
      baseRisk += 5;
      baseIncident += 0.5;
    }

    setData({
      labels,
      riskData,
      incidentData,
      trend: riskData[riskData.length - 1] > riskData[0] ? 'hausse' : 'baisse',
      average: Math.round(riskData.reduce((a, b) => a + b, 0) / riskData.length),
      peak: Math.max(...riskData),
      peakMonth: labels[riskData.indexOf(Math.max(...riskData))],
    });
  }, []);

  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 text-center text-gray-500">
        <p>Chargement de l'historique...</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.riskData) + 10;
  const minValue = Math.min(...data.riskData) - 10;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          📈 Évolution des risques
        </h3>
        <div className="flex items-center space-x-2 text-sm">
          <span className="flex items-center space-x-1">
            <span className="w-3 h-0.5 bg-blue-500"></span>
            <span className="text-gray-500 dark:text-gray-400">Risque</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-0.5 bg-red-500"></span>
            <span className="text-gray-500 dark:text-gray-400">Incidents</span>
          </span>
        </div>
      </div>

      {/* Graphique simple avec des barres */}
      <div className="h-48 flex items-end justify-between gap-1">
        {data.labels.map((label, index) => {
          const riskHeight = (data.riskData[index] / maxValue) * 100;
          const incidentHeight = (data.incidentData[index] / 10) * 100;
          
          return (
            <div key={index} className="flex flex-col items-center flex-1">
              <div className="flex items-end gap-1 w-full justify-center">
                <div 
                  className="w-3 bg-blue-500 rounded-t transition-all duration-500"
                  style={{ height: `${Math.max(riskHeight, 5)}%`, minHeight: '4px' }}
                />
                <div 
                  className="w-3 bg-red-500 rounded-t transition-all duration-500"
                  style={{ height: `${Math.max(incidentHeight, 5)}%`, minHeight: '4px' }}
                />
              </div>
              <span className="text-xs text-gray-500 mt-2">{label}</span>
            </div>
          );
        })}
      </div>

      {/* Statistiques */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs text-gray-500 dark:text-gray-400">Tendance</p>
          <div className="flex items-center space-x-1">
            {data.trend === 'hausse' ? (
              <FiTrendingUp className="w-4 h-4 text-red-500" />
            ) : (
              <FiTrendingDown className="w-4 h-4 text-green-500" />
            )}
            <span className={`font-medium ${data.trend === 'hausse' ? 'text-red-600' : 'text-green-600'}`}>
              {data.trend === 'hausse' ? 'En hausse' : 'En baisse'}
            </span>
          </div>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs text-gray-500 dark:text-gray-400">Risque moyen</p>
          <p className="font-medium text-gray-900 dark:text-white">{data.average}</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs text-gray-500 dark:text-gray-400">Pic de risque</p>
          <p className="font-medium text-gray-900 dark:text-white">{data.peak} ({data.peakMonth})</p>
        </div>
        <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-xs text-gray-500 dark:text-gray-400">Incidents totaux</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {data.incidentData.reduce((a, b) => a + b, 0)}
          </p>
        </div>
      </div>
    </div>
  );
}