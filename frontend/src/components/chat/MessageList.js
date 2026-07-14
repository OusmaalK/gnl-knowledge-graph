// frontend/src/components/chat/MessageList.js

import { FiUser, FiCpu } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

export function MessageList({ messages, loading }) {
  if (!messages || messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500">
        <FiCpu className="w-12 h-12 mb-4" />
        <p className="text-lg font-medium">Aucun message</p>
        <p className="text-sm">Commencez une conversation avec l'assistant IA</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg, index) => {
        // ✅ Utiliser `index` comme fallback si msg.id est manquant
        const key = msg.id || `msg-${index}-${Date.now()}-${Math.random()}`;
        const isUser = msg.role === 'user';
        const isError = msg.role === 'error';
        const isSystem = msg.role === 'system';
        const isAgent = msg.role === 'agent';

        return (
          <div
            key={key}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[85%] rounded-xl p-4
                ${isUser
                  ? 'bg-blue-600 text-white dark:bg-blue-700'
                  : isError
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border border-red-200 dark:border-red-800'
                  : isSystem
                  ? 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                }
              `}
            >
              {/* En-tête du message */}
              <div className="flex items-center space-x-2 mb-1">
                {isUser && (
                  <>
                    <FiUser className="w-4 h-4" />
                    <span className="text-xs font-medium">Vous</span>
                  </>
                )}
                {isAgent && (
                  <>
                    <FiCpu className="w-4 h-4" />
                    <span className="text-xs font-medium">Assistant GNL</span>
                  </>
                )}
                {isSystem && (
                  <span className="text-xs font-medium">Système</span>
                )}
                {isError && (
                  <span className="text-xs font-medium">⚠️ Erreur</span>
                )}
                <span className="text-xs opacity-50 ml-auto">
                  {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString('fr-FR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  }) : ''}
                </span>
              </div>

              {/* Contenu du message */}
              {isAgent || isSystem ? (
                <ReactMarkdown
                  className="prose prose-sm max-w-none dark:prose-invert"
                  components={{
                    code: ({ node, inline, className, children, ...props }) => {
                      return inline ? (
                        <code className="px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded" {...props}>
                          {children}
                        </code>
                      ) : (
                        <pre className="p-3 bg-gray-800 text-white rounded-lg overflow-x-auto">
                          <code {...props}>{children}</code>
                        </pre>
                      );
                    },
                  }}
                >
                  {msg.content || ''}
                </ReactMarkdown>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content || ''}</p>
              )}
            </div>
          </div>
        );
      })}

      {loading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}