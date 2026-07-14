/**
 * ChatHistory - Historique des conversations
 * ============================================================================
 * Description: Liste des conversations précédentes
 * ============================================================================
 */

import { useState } from 'react';
import { FiMessageSquare, FiChevronRight, FiTrash2 } from 'react-icons/fi';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export function ChatHistory({ conversations, onSelect, selectedId }) {
  const [hoveredId, setHoveredId] = useState(null);

  if (conversations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 dark:text-gray-500">
        <FiMessageSquare className="w-8 h-8 mx-auto mb-2" />
        <p className="text-sm">Aucune conversation</p>
      </div>
    );
  }

  return (
    <div className="space-y-1 p-2">
      {conversations.map((conv) => {
        const isSelected = conv.id === selectedId;
        const time = formatDistanceToNow(new Date(conv.updated_at), {
          addSuffix: true,
          locale: fr,
        });

        return (
          <div
            key={conv.id}
            className={`
              relative group flex items-center p-3 rounded-lg cursor-pointer transition-all
              ${isSelected
                ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800'
                : 'hover:bg-gray-50 dark:hover:bg-gray-700'
              }
            `}
            onClick={() => onSelect(conv.id)}
            onMouseEnter={() => setHoveredId(conv.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {conv.title || 'Conversation sans titre'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {conv.last_message || 'Aucun message'}
              </p>
              <p className="text-xs text-gray-400 mt-0.5">{time}</p>
            </div>
            
            <div className="flex items-center space-x-1">
              {isSelected && (
                <FiChevronRight className="w-4 h-4 text-blue-500" />
              )}
              {hoveredId === conv.id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Supprimer la conversation
                  }}
                  className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                >
                  <FiTrash2 className="w-3 h-3 text-red-500" />
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}