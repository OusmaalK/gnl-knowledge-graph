'use client';

import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Footer } from './Footer';
import { Toaster } from 'react-hot-toast';

export function ClientLayout({ children }) {
  const pathname = usePathname();

  const isAuthPage = pathname?.startsWith('/auth');

  // Les pages d'auth ne doivent PAS être enfermées dans le layout principal
  if (isAuthPage) {
    return (
      <>
        {children}

        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">

      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">

        <Header />

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>

        <Footer />

      </div>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />

    </div>
  );
}