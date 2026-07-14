/**
 * AgentSelector - Sélecteur d'agent IA
 * ============================================================================
 * Description: Composant pour sélectionner l'agent IA à utiliser
 * ============================================================================
 */

import { useState } from 'react';
import { FiChevronDown } from 'react-icons/fi';

const agents = [
  {
    id: 'diagnostic',
    name: '🔍 Diagnostic',
    description: 'Analyse et diagnostic des incidents',
  },
  {
    id: 'incident',
    name: '📋 Incidents',
    description: 'Gestion et historique des incidents',
  },
  {
    id: 'logistics',
    name: '🗺️ Logistique',
    description: 'Routes et optimisation logistique',
  },
  {
    id: 'maintenance',
    name: '🔧 Maintenance',
    description: 'Maintenance prédictive et risques',
  },
];

export function AgentSelector({ value, onChange }) {
  const [isOpen, setIsOpen] = useState(false);

  const selected = agents.find((a) => a.id === value) || agents[0];

  const handleSelect = (id) => {
    onChange(id);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {selected.name}
        </span>
        <FiChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
          <div className="p-1">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => handleSelect(agent.id)}
                className={`
                  w-full text-left px-3 py-2 rounded-lg transition-colors
                  ${agent.id === value
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                  }
                `}
              >
                <div className="text-sm font-medium">{agent.name}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {agent.description}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}