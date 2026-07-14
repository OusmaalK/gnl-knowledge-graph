/**
 * Auth Layout - Layout spécifique pour les pages d'authentification
 * ============================================================================
 * Description: Supprime la Sidebar, le Header et le Footer pour les pages Login/Register
 * ============================================================================
 */

export default function AuthLayout({ children }) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        {children}
      </div>
    );
  }