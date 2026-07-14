/**
 * Footer - Pied de page
 * ============================================================================
 * Description: Pied de page avec informations légales
 * ============================================================================
 */

export function Footer() {
    const currentYear = new Date().getFullYear();
  
    return (
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-3">
        <div className="flex flex-wrap items-center justify-between text-sm text-gray-500 dark:text-gray-400">
          <div>
            © {currentYear} GNL Knowledge Graph. Tous droits réservés.
          </div>
          <div className="flex items-center space-x-6">
            <a href="#" className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
              Mentions légales
            </a>
            <a href="#" className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
              Politique de confidentialité
            </a>
            <a href="#" className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
              Contact
            </a>
            <span className="flex items-center space-x-1">
              <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span>Services opérationnels</span>
            </span>
          </div>
        </div>
      </footer>
    );
  }