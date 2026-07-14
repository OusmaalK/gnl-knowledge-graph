/**
 * LoadingSpinner - Spinner de chargement
 * ============================================================================
 * Description: Spinner de chargement réutilisable
 * ============================================================================
 */

export function LoadingSpinner({ size = 'medium', color = 'blue' }) {
    const sizes = {
      small: 'w-4 h-4',
      medium: 'w-8 h-8',
      large: 'w-12 h-12',
    };
  
    const colors = {
      blue: 'border-blue-600',
      white: 'border-white',
      gray: 'border-gray-600',
    };
  
    return (
      <div className="flex items-center justify-center">
        <div className={`
          ${sizes[size] || sizes.medium}
          border-4
          ${colors[color] || colors.blue}
          border-t-transparent
          rounded-full
          animate-spin
        `} />
      </div>
    );
  }