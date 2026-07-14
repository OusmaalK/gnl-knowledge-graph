"""
Normalisateur pour les données IoT
"""

from typing import Dict, List, Any
import logging
from .base import BaseNormalizer

logger = logging.getLogger(__name__)

class IoTNormalizer(BaseNormalizer):
    """
    Normalisateur pour les données IoT (capteurs)
    """
    
    def __init__(self):
        super().__init__(name="IoTNormalizer")
        self._field_mapping = {
            'pipeline_id': 'pipeline_id',
            'timestamp': 'timestamp',
            'pression_bar': 'pression_bar',
            'debit_m3_s': 'debit_m3_s',
            'temperature_c': 'temperature_c',
            'vibration_mm_s': 'vibration_mm_s',
            'statut': 'statut',
            'capteur_id': 'capteur_id'
        }
    
    def normalize(self, data: List[Dict]) -> List[Dict]:
        """
        Normalise les données IoT
        """
        logger.info(f"🔄 {self.name} - Normalisation de {len(data)} enregistrements")
        
        normalized = []
        
        for record in data:
            try:
                normalized_record = self._normalize_record(record)
                normalized.append(normalized_record)
                self._increment_processed()
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation: {e}")
                self._increment_error()
        
        logger.info(f"✅ {self.name} - {len(normalized)} enregistrements normalisés")
        return normalized
    
    def _normalize_record(self, record: Dict) -> Dict:
        """
        Normalise un enregistrement IoT
        """
        result = {
            'type': 'Mesure',
            'properties': {},
            'relationships': []
        }
        
        # Normaliser l'identifiant du pipeline
        pipeline_id = self._normalize_id(record.get('pipeline_id', ''))
        if pipeline_id:
            result['relationships'].append({
                'type': 'MESURE',
                'target': {
                    'type': 'Pipeline',
                    'id': pipeline_id
                }
            })
        
        # Normaliser les propriétés
        result['properties'] = {
            'timestamp': self._normalize_date(record.get('timestamp', '')),
            'pipeline_id': pipeline_id,
            'pression_bar': self._normalize_number(record.get('pression_bar')),
            'debit_m3_s': self._normalize_number(record.get('debit_m3_s')),
            'temperature_c': self._normalize_number(record.get('temperature_c')),
            'vibration_mm_s': self._normalize_number(record.get('vibration_mm_s')),
            'statut': self._normalize_enum(
                record.get('statut', 'actif'),
                ['actif', 'alerte', 'critique', 'hors_service']
            ),
            'capteur_id': self._normalize_id(record.get('capteur_id', ''))
        }
        
        # Filtrer les valeurs None
        result['properties'] = {
            k: v for k, v in result['properties'].items()
            if v is not None and v != ''
        }
        
        return result

if __name__ == "__main__":
    # Test du normalisateur
    normalizer = IoTNormalizer()
    
    test_data = [
        {
            'pipeline_id': 'pipe-001',
            'timestamp': '2026-07-10T12:00:00Z',
            'pression_bar': '75.5',
            'debit_m3_s': '45.2',
            'temperature_c': '22.5',
            'vibration_mm_s': '0.3',
            'statut': 'actif',
            'capteur_id': 'sensor-001'
        }
    ]
    
    result = normalizer.normalize(test_data)
    print("Résultat:", result)