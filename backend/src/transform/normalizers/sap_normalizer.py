"""
Normalisateur pour les données SAP
"""

from typing import Dict, List, Any
import logging
from .base import BaseNormalizer

logger = logging.getLogger(__name__)

class SAPNormalizer(BaseNormalizer):
    """
    Normalisateur pour les données SAP
    """
    
    def __init__(self):
        super().__init__(name="SAPNormalizer")
    
    def normalize(self, data: List[Dict]) -> List[Dict]:
        """
        Normalise les données SAP
        """
        logger.info(f"🔄 {self.name} - Normalisation de {len(data)} enregistrements")
        
        normalized = []
        
        for record in data:
            try:
                # Détecter le type de nœud
                if 'fournisseur_id' in record:
                    normalized.append(self._normalize_fournisseur(record))
                elif 'terminal_id' in record:
                    normalized.append(self._normalize_terminal(record))
                elif 'pipeline_id' in record:
                    normalized.append(self._normalize_pipeline(record))
                else:
                    logger.warning(f"⚠️ Type non reconnu: {record}")
                    self._increment_warning()
                    continue
                
                self._increment_processed()
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation: {e}")
                self._increment_error()
        
        logger.info(f"✅ {self.name} - {len(normalized)} enregistrements normalisés")
        return normalized
    
    def _normalize_fournisseur(self, record: Dict) -> Dict:
        """Normalise un fournisseur"""
        return {
            'type': 'Fournisseur',
            'properties': {
                'id': self._normalize_id(record.get('fournisseur_id', '')),
                'nom': self._normalize_string(record.get('nom', '')),
                'pays': self._normalize_string(record.get('pays', '')),
                'ville': self._normalize_string(record.get('ville', '')),
                'adresse': self._normalize_string(record.get('adresse', '')),
                'contact': self._normalize_string(record.get('contact', '')),
                'email': record.get('email', '').strip(),
                'statut': self._normalize_enum(
                    record.get('statut', 'actif'),
                    ['actif', 'inactif', 'suspendu']
                )
            },
            'relationships': []
        }
    
    def _normalize_terminal(self, record: Dict) -> Dict:
        """Normalise un terminal"""
        relationships = []
        
        # Relation avec le fournisseur exploitant
        if record.get('exploitant_id'):
            relationships.append({
                'type': 'EXPLOITE_PAR',
                'target': {
                    'type': 'Fournisseur',
                    'id': self._normalize_id(record.get('exploitant_id'))
                }
            })
        
        return {
            'type': 'Terminal',
            'properties': {
                'id': self._normalize_id(record.get('terminal_id', '')),
                'nom': self._normalize_string(record.get('nom', '')),
                'localisation': self._normalize_string(record.get('localisation', '')),
                'capacite_m3': self._normalize_number(record.get('capacite_m3', 0)),
                'type': self._normalize_enum(
                    record.get('type', 'LNG'),
                    ['LNG', 'CNG', 'LPG']
                ),
                'statut': self._normalize_enum(
                    record.get('statut', 'actif'),
                    ['actif', 'en_construction', 'maintenance', 'hors_service']
                )
            },
            'relationships': relationships
        }
    
    def _normalize_pipeline(self, record: Dict) -> Dict:
        """Normalise un pipeline"""
        relationships = []
        
        # Relation de départ
        if record.get('depart'):
            relationships.append({
                'type': 'DEPART_DE',
                'target': {
                    'type': 'Terminal',
                    'id': self._normalize_id(record.get('depart'))
                }
            })
        
        # Relation d'arrivée
        if record.get('arrivee'):
            relationships.append({
                'type': 'ARRIVE_A',
                'target': {
                    'type': 'Terminal',
                    'id': self._normalize_id(record.get('arrivee'))
                }
            })
        
        return {
            'type': 'Pipeline',
            'properties': {
                'id': self._normalize_id(record.get('pipeline_id', '')),
                'nom': self._normalize_string(record.get('nom', '')),
                'longueur_km': self._normalize_number(record.get('longueur_km', 0)),
                'depart': self._normalize_id(record.get('depart', '')),
                'arrivee': self._normalize_id(record.get('arrivee', '')),
                'pression_max_bar': self._normalize_number(record.get('pression_max_bar', 0)),
                'statut': self._normalize_enum(
                    record.get('statut', 'actif'),
                    ['actif', 'en_test', 'maintenance', 'hors_service']
                )
            },
            'relationships': relationships
        }

if __name__ == "__main__":
    # Test du normalisateur
    normalizer = SAPNormalizer()
    
    test_data = [
        {
            'fournisseur_id': 'four-001',
            'nom': 'totalenergies',
            'pays': 'france',
            'ville': 'paris',
            'statut': 'actif'
        },
        {
            'terminal_id': 'term-001',
            'nom': 'fos-sur-mer',
            'capacite_m3': '500000',
            'exploitant_id': 'four-001'
        }
    ]
    
    result = normalizer.normalize(test_data)
    print("Résultat:", result)