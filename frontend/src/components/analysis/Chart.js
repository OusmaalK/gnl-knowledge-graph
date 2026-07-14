/**
 * Chart - Composant de graphique
 * ============================================================================
 * Description: Graphiques pour les analyses avancées
 * ============================================================================
 */

import { useEffect, useRef } from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { LoadingSpinner } from '../common/LoadingSpinner';

ChartJS.register(...registerables);

export function Chart({ title, type, data, loading }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (data && chartRef.current) {
      renderChart();
    }
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, type]);

  const renderChart = () => {
    if (!data) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');

    // Configuration selon le type
    const config = {
      type: type || 'bar',
      data: {
        labels: data.labels || [],
        datasets: data.datasets || [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 12,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0,0,0,0.05)',
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    };

    // Configuration spécifique pour les pie/doughnut
    if (type === 'pie' || type === 'doughnut') {
      config.options.scales = undefined;
      config.options.plugins.legend.position = 'right';
    }

    chartInstance.current = new ChartJS(ctx, config);
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 flex items-center justify-center h-64 text-gray-500">
        <p>Aucune donnée disponible</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      {title && (
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
          {title}
        </h4>
      )}
      <div className="h-64">
        <canvas ref={chartRef} />
      </div>
    </div>
  );
}