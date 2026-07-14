/**
 * useDebounce - Hook pour le debounce
 * ============================================================================
 * Description: Hook personnalisé pour debouncer une valeur
 * ============================================================================
 */

'use client';

import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}