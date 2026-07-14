/**
 * RiskGauge - Jauge de risque
 * ============================================================================
 * Description: Visualisation du niveau de risque d'un équipement
 * ============================================================================
 */

export function RiskGauge({ equipmentId = 'PIPE-001' }) {
  const score = 65;
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getNiveau = () => {
    if (score >= 70) return 'CRITIQUE';
    if (score >= 50) return 'ÉLEVÉ';
    if (score >= 30) return 'MOYEN';
    return 'FAIBLE';
  };

  const getNiveauClasses = () => {
    if (score >= 70) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    if (score >= 50) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
    if (score >= 30) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white">
            {equipmentId}
          </h4>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Score de risque
          </p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getNiveauClasses()}`}>
          {getNiveau()}
        </div>
      </div>

      <div className="relative flex justify-center">
        <svg width="200" height="200" viewBox="0 0 200 200">
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="12"
            className="dark:stroke-gray-700"
          />
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#F59E0B"
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 100 100)"
            className="transition-all duration-1000"
          />
          <text
            x="100"
            y="95"
            textAnchor="middle"
            dominantBaseline="central"
            className="text-3xl font-bold text-gray-900 dark:text-white"
          >
            {score}
          </text>
          <text
            x="100"
            y="125"
            textAnchor="middle"
            dominantBaseline="central"
            className="text-sm text-gray-500 dark:text-gray-400"
          >
            / 100
          </text>
        </svg>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg text-center">
          <p className="text-gray-500 dark:text-gray-400">Incidents</p>
          <p className="font-semibold text-gray-900 dark:text-white">2</p>
        </div>
        <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg text-center">
          <p className="text-gray-500 dark:text-gray-400">Clients</p>
          <p className="font-semibold text-gray-900 dark:text-white">1</p>
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
        <p className="font-medium">💡 Recommandation</p>
        <p className="mt-1">Surveillance renforcée - Inspection dans les 30 jours</p>
      </div>
    </div>
  );
}