'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { AuthProvider } from '@/contexts/AuthContext'; // <-- IMPORTANT : Importer le contexte

export function Providers({ children }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {/* Envelopper toute l'application avec AuthProvider */}
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
}