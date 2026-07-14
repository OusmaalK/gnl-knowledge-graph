/**
 * GraphControls - Contrôles du graphe
 * ============================================================================
 * Description: Boutons de contrôle pour l'interaction avec le graphe
 * ============================================================================
 */

'use client';

import { useState, useRef } from 'react';
import {
  FiZoomIn,
  FiZoomOut,
  FiMaximize,
  FiDownload,
  FiRefreshCw,
  FiGrid,
  FiMove,
  FiRotateCw,
} from 'react-icons/fi';

export function GraphControls({ 
  onZoomIn, 
  onZoomOut, 
  onFit, 
  onReset, 
  onExport, 
  onLayout,
  onRotate,
  onPan,
  isLoading = false 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTool, setActiveTool] = useState(null);
  const fileInputRef = useRef(null);

  const handleExport = () => {
    if (onExport) {
      onExport();
    }
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (file && onExport) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          // Importer les données du graphe
          console.log('Import data:', data);
        } catch (error) {
          console.error('Erreur import:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  const tools = [
    { id: 'zoomIn', icon: FiZoomIn, label: 'Zoom avant', action: onZoomIn },
    { id: 'zoomOut', icon: FiZoomOut, label: 'Zoom arrière', action: onZoomOut },
    { id: 'fit', icon: FiMaximize, label: 'Adapter à l\'écran', action: onFit },
    { id: 'reset', icon: FiRefreshCw, label: 'Réinitialiser', action: onReset },
    { id: 'pan', icon: FiMove, label: 'Déplacer', action: onPan },
    { id: 'rotate', icon: FiRotateCw, label: 'Rotation', action: onRotate },
    { id: 'layout', icon: FiGrid, label: 'Changer le layout', action: onLayout },
  ];

  return (
    <div className="absolute top-4 right-4 flex flex-col space-y-2 z-10">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-2 flex flex-col space-y-1">
        {tools.map((tool) => {
          const Icon = tool.icon;
          const isActive = activeTool === tool.id;
          
          return (
            <button
              key={tool.id}
              onClick={() => {
                setActiveTool(isActive ? null : tool.id);
                if (tool.action) tool.action();
              }}
              className={`
                p-2 rounded-lg transition-colors relative group
                ${isActive 
                  ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                }
                ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              title={tool.label}
              disabled={isLoading}
            >
              <Icon className="w-4 h-4" />
              <span className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                {tool.label}
              </span>
            </button>
          );
        })}

        <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>

        {/* Exporter */}
        <button
          onClick={handleExport}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-600 dark:text-gray-300 group relative"
          title="Exporter"
        >
          <FiDownload className="w-4 h-4" />
          <span className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            Exporter
          </span>
        </button>

        {/* Importer */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-600 dark:text-gray-300 group relative"
          title="Importer"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          <span className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            Importer
          </span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleImport}
          className="hidden"
        />
      </div>

      {/* Indicateur de zoom */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-xs text-gray-500 dark:text-gray-400 text-center">
        <span>100%</span>
      </div>
    </div>
  );
}