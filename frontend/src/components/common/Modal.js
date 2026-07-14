/**
 * Modal - Composant de modale
 * ============================================================================
 * Description: Modale réutilisable
 * ============================================================================
 */

'use client';

import { useEffect, useRef } from 'react';
import { FiX } from 'react-icons/fi';

export function Modal({ isOpen, onClose, title, children, size = 'medium', actions }) {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizes = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    xlarge: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div
        ref={modalRef}
        className={`
          bg-white dark:bg-gray-800 rounded-xl shadow-2xl
          w-full ${sizes[size] || sizes.medium}
          max-h-[90vh] overflow-hidden
          animate-fade-in
        `}
      >
        {/* En-tête */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <FiX className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Contenu */}
        <div className="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
          {children}
        </div>

        {/* Actions */}
        {actions && (
          <div className="flex items-center justify-end space-x-2 p-4 border-t border-gray-200 dark:border-gray-700">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}