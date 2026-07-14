"""
Normalisateur pour les données de tracking maritime
"""

from typing import Dict, List, Any
import logging
from .base import BaseNormalizer

logger = logging.getLogger(__name__)

class TrackingNormalizer(BaseNormalizer):
    """
    Normalisateur pour les données AIS (tracking maritime)
    """
    
    def __init__(self):
        super().__init__(name="TrackingNormalizer")
    
    def normalize(self, data: List[Dict]) -> List[Dict]:
        """
        Normalise les données de tracking
        """
        logger.info(f"🔄 {self.name} - Normalisation de {len(data)} enregistrements")
        
        normalized = []
        
        for record in data:
            try:
                normalized.append(self._normalize_vessel(record))
                self._increment_processed()
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation: {e}")
                self._increment_error()
        
        logger.info(f"✅ {self.name} - {len(normalized)} enregistrements normalisés")
        return normalized
    
    def _normalize_vessel(self, record: Dict) -> Dict:
        """Normalise un navire"""
        return {
            'type': 'Méthanier',
            'properties': {
                'id': self._normalize_id(record.get('vessel_id', '')),
                'nom': self._normalize_string(record.get('name', record.get('nom', ''))),
                'type_navire': self._normalize_string(record.get('type', 'Méthanier')),
                'capacite_m3': self._normalize_number(record.get('capacite_m3', 0)),
                'statut': self._normalize_enum(
                    record.get('statut', 'en_croisiere'),
                    ['en_croisiere', 'a_quai', 'en_chargement', 'en_dechargement']
                ),
                'port_actuel': self._normalize_string(record.get('current_port', record.get('port', ''))),
                'latitude': self._normalize_number(record.get('latitude', 0)),
                'longitude': self._normalize_number(record.get('longitude', 0)),
                'vitesse_noeuds': self._normalize_number(record.get('vitesse_noeuds', 0)),
                'cap_deg': self._normalize_number(record.get('cap_deg', 0)),
                'last_update': self._normalize_date(record.get('last_update', ''))
            },
            'relationships': []
        }

if __name__ == "__main__":
    # Test du normalisateur
    normalizer = TrackingNormalizer()
    
    test_data = [
        {
            'vessel_id': 'vessel-001',
            'name': 'GNL Explorer',
            'capacite_m3': 150000,
            'statut': 'en_croisiere',
            'latitude': 43.43,
            'longitude': 4.87
        }
    ]
    
    result = normalizer.normalize(test_data)
    print("Résultat:", result)