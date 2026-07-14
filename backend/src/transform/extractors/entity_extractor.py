"""
Extracteur d'entités à partir de textes
"""

import re
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class EntityExtractor:
    """
    Extracteur d'entités pour les textes GNL
    """
    
    def __init__(self):
        self._patterns = {
            'incident_id': re.compile(r'INC-[\d]{3,4}', re.IGNORECASE),
            'pipeline_id': re.compile(r'PIPE-[\d]{3,4}', re.IGNORECASE),
            'terminal_id': re.compile(r'TERM-[\d]{3,4}', re.IGNORECASE),
            'fournisseur_id': re.compile(r'FOUR-[\d]{3,4}', re.IGNORECASE),
            'client_id': re.compile(r'CLIENT-[\d]{3,4}', re.IGNORECASE),
            'compresseur_id': re.compile(r'COMP-[\d]{3,4}', re.IGNORECASE),
            'stockage_id': re.compile(r'STOCK-[\d]{3,4}', re.IGNORECASE)
        }
        
        self._entity_types = {
            'incident': ['incident', 'panne', 'fuite', 'problème', 'défaillance'],
            'pipeline': ['pipeline', 'canalisation', 'conduite'],
            'terminal': ['terminal', 'port', 'site'],
            'fournisseur': ['fournisseur', 'producteur', 'exploitant'],
            'client': ['client', 'consommateur', 'utilisateur'],
            'compresseur': ['compresseur', 'pompe'],
            'stockage': ['stockage', 'réservoir', 'citerne']
        }
        
        logger.info("✅ EntityExtractor initialisé")
    
    def extract(self, text: str) -> List[Dict]:
        """
        Extrait les entités d'un texte
        """
        entities = []
        
        # Extraire par patterns
        for entity_type, pattern in self._patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                entities.append({
                    'type': self._get_entity_type(entity_type),
                    'id': match,
                    'value': match,
                    'source': 'pattern'
                })
        
        # Extraire par mots-clés
        for entity_type, keywords in self._entity_types.items():
            for keyword in keywords:
                pattern = re.compile(rf'(\b{keyword}\s+[A-Za-z0-9_-]+)', re.IGNORECASE)
                matches = pattern.findall(text)
                for match in matches:
                    value = match.split(' ', 1)[-1]
                    entities.append({
                        'type': entity_type,
                        'id': value,
                        'value': value,
                        'source': 'keyword'
                    })
        
        # Supprimer les doublons
        unique_entities = []
        seen = set()
        for entity in entities:
            key = (entity['type'], entity['id'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _get_entity_type(self, pattern_type: str) -> str:
        """Convertit le type de pattern en type d'entité"""
        type_mapping = {
            'incident_id': 'incident',
            'pipeline_id': 'pipeline',
            'terminal_id': 'terminal',
            'fournisseur_id': 'fournisseur',
            'client_id': 'client',
            'compresseur_id': 'compresseur',
            'stockage_id': 'stockage'
        }
        return type_mapping.get(pattern_type, pattern_type)
    
    def extract_batch(self, texts: List[str]) -> List[List[Dict]]:
        """
        Extrait les entités de plusieurs textes
        """
        return [self.extract(text) for text in texts]

if __name__ == "__main__":
    # Test de l'extracteur
    extractor = EntityExtractor()
    
    text = """
    L'incident INC-001 concerne le pipeline PIPE-001 (Nord-Sud).
    Le terminal TERM-001 (Fos-sur-Mer) est alimenté par TotalEnergies.
    """
    
    entities = extractor.extract(text)
    print("Entités extraites:", entities)