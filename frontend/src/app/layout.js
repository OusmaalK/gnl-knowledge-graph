import { Inter } from 'next/font/google';
import './globals.css';

import { Providers } from '@/components/providers/Providers';
import { ClientLayout } from '@/components/layout/ClientLayout';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata = {
  title: 'GNL Knowledge Graph',
  description: "Plateforme d'intelligence artificielle GNL",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr" className={inter.variable}>
      {/* 
         Retrait de 'min-h-screen' sur le body pour éviter les conflits de hauteur. 
         Le ClientLayout gère désormais la hauteur (h-screen) pour toutes les pages.
      */}
      <body className="bg-gray-50 antialiased">
        <Providers>
          <ClientLayout>
            {children}
          </ClientLayout>
        </Providers>
      </body>
    </html>
  );
}