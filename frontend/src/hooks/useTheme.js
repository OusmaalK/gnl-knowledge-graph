/**
 * useTheme - Hook pour le thème
 * ============================================================================
 * Description: Hook personnalisé pour la gestion du thème (clair/sombre)
 * ============================================================================
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';

export function useTheme() {
  const [theme, setTheme] = useLocalStorage('theme', 'system');
  const [resolvedTheme, setResolvedTheme] = useState('light');

  const resolveTheme = useCallback(() => {
    if (theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme;
  }, [theme]);

  const applyTheme = useCallback((newTheme) => {
    const resolved = newTheme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      : newTheme;

    setResolvedTheme(resolved);
    document.documentElement.classList.toggle('dark', resolved === 'dark');
  }, []);

  const toggleTheme = useCallback(() => {
    const currentResolved = resolveTheme();
    const nextTheme = currentResolved === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    applyTheme(nextTheme);
  }, [resolveTheme, setTheme, applyTheme]);

  const setThemeMode = useCallback((newTheme) => {
    setTheme(newTheme);
    applyTheme(newTheme);
  }, [setTheme, applyTheme]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        applyTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, applyTheme]);

  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  return {
    theme,
    resolvedTheme,
    toggleTheme,
    setTheme: setThemeMode,
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
  };
}