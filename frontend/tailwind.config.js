/**
 * Tailwind CSS Configuration
 * ============================================================================
 * Description: Configuration de Tailwind CSS pour le frontend
 * ============================================================================
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
      './src/components/**/*.{js,ts,jsx,tsx,mdx}',
      './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    
    theme: {
      extend: {
        // Couleurs personnalisées
        colors: {
          // Couleurs principales GNL
          gnl: {
            blue: {
              50: '#eff6ff',
              100: '#dbeafe',
              200: '#bfdbfe',
              300: '#93c5fd',
              400: '#60a5fa',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
              800: '#1e40af',
              900: '#1e3a8a',
            },
            green: {
              50: '#f0fdf4',
              100: '#dcfce7',
              200: '#bbf7d0',
              300: '#86efac',
              400: '#4ade80',
              500: '#22c55e',
              600: '#16a34a',
              700: '#15803d',
              800: '#166534',
              900: '#14532d',
            },
            amber: {
              50: '#fffbeb',
              100: '#fef3c7',
              200: '#fde68a',
              300: '#fcd34d',
              400: '#fbbf24',
              500: '#f59e0b',
              600: '#d97706',
              700: '#b45309',
              800: '#92400e',
              900: '#78350f',
            },
            red: {
              50: '#fef2f2',
              100: '#fee2e2',
              200: '#fecaca',
              300: '#fca5a5',
              400: '#f87171',
              500: '#ef4444',
              600: '#dc2626',
              700: '#b91c1c',
              800: '#991b1b',
              900: '#7f1d1d',
            },
            purple: {
              50: '#faf5ff',
              100: '#f3e8ff',
              200: '#e9d5ff',
              300: '#d8b4fe',
              400: '#c084fc',
              500: '#a855f7',
              600: '#9333ea',
              700: '#7e22ce',
              800: '#6b21a8',
              900: '#581c87',
            },
          },
        },
        
        // Polices
        fontFamily: {
          sans: ['Inter', 'system-ui', 'sans-serif'],
          mono: ['JetBrains Mono', 'monospace'],
        },
        
        // Animations
        keyframes: {
          'fade-in': {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
          'slide-in': {
            '0%': { transform: 'translateX(-100%)' },
            '100%': { transform: 'translateX(0)' },
          },
          'pulse-slow': {
            '0%, 100%': { opacity: '1' },
            '50%': { opacity: '0.5' },
          },
          'bounce-slow': {
            '0%, 100%': { transform: 'translateY(0)' },
            '50%': { transform: 'translateY(-10px)' },
          },
          'spin-slow': {
            '0%': { transform: 'rotate(0deg)' },
            '100%': { transform: 'rotate(360deg)' },
          },
        },
        
        animation: {
          'fade-in': 'fade-in 0.5s ease-in-out',
          'slide-in': 'slide-in 0.3s ease-out',
          'pulse-slow': 'pulse-slow 3s ease-in-out infinite',
          'bounce-slow': 'bounce-slow 2s ease-in-out infinite',
          'spin-slow': 'spin-slow 3s linear infinite',
        },
        
        // Breakpoints
        screens: {
          xs: '475px',
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1280px',
          '2xl': '1536px',
          '3xl': '1920px',
        },
        
        // Spacing
        spacing: {
          '18': '4.5rem',
          '88': '22rem',
          '120': '30rem',
          '128': '32rem',
          '144': '36rem',
        },
        
        // Border radius
        borderRadius: {
          '4xl': '2rem',
          '5xl': '2.5rem',
        },
        
        // Box shadow
        boxShadow: {
          'card': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          'card-hover': '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
          'glow': '0 0 20px rgba(59, 130, 246, 0.3)',
          'glow-green': '0 0 20px rgba(34, 197, 94, 0.3)',
          'glow-red': '0 0 20px rgba(239, 68, 68, 0.3)',
        },
        
        // Gradient
        backgroundImage: {
          'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
          'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
          'gnl-gradient': 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%)',
          'gnl-gradient-dark': 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1d4ed8 100%)',
          'gnl-gradient-success': 'linear-gradient(135deg, #14532d 0%, #22c55e 50%, #4ade80 100%)',
          'gnl-gradient-danger': 'linear-gradient(135deg, #7f1d1d 0%, #ef4444 50%, #f87171 100%)',
        },
      },
    },
    
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/aspect-ratio'),
      require('tailwindcss-animate'),
    ],
  };