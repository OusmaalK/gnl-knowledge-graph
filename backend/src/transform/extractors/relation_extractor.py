"""
Extracteur de relations entre entités
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class RelationExtractor:
    """
    Extracteur de relations entre entités dans les textes
    """
    
    def __init__(self):
        self._relation_patterns = {
            'AFFECTE': [
                (r'(\S+)\s+(affecte|impacte|touche)\s+(\S+)', 1, 3),
                (r'(\S+)\s+est\s+(affecté|impacté|touché)\s+par\s+(\S+)', 3, 1),
            ],
            'CAUSE': [
                (r'(\S+)\s+(cause|provoque|entraîne)\s+(\S+)', 1, 3),
                (r'(\S+)\s+est\s+(causé|provoqué|entraîné)\s+par\s+(\S+)', 3, 1),
            ],
            'DEPEND_DE': [
                (r'(\S+)\s+(dépend|dépend de)\s+(\S+)', 1, 3),
            ],
            'ALIMENTE': [
                (r'(\S+)\s+(alimente|fournit|approvisionne)\s+(\S+)', 1, 3),
            ],
            'DESSERT': [
                (r'(\S+)\s+(dessert|sert|fournit)\s+(\S+)', 1, 3),
            ]
        }
        
        self._relation_words = {
            'affecte': 'AFFECTE',
            'impacte': 'AFFECTE',
            'touche': 'AFFECTE',
            'cause': 'CAUSE',
            'provoque': 'CAUSE',
            'entraîne': 'CAUSE',
            'dépend': 'DEPEND_DE',
            'alimente': 'ALIMENTE',
            'fournit': 'ALIMENTE',
            'dessert': 'DESSERT',
            'sert': 'DESSERT'
        }
        
        logger.info("✅ RelationExtractor initialisé")
    
    def extract(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extrait les relations entre entités
        """
        relations = []
        
        # Créer un dictionnaire des entités par ID
        entity_map = {e['id']: e for e in entities if e.get('id')}
        
        # Extraire les relations par patterns
        for rel_type, patterns in self._relation_patterns.items():
            for pattern, source_idx, target_idx in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 3:
                        source_id = match[source_idx - 1]
                        target_id = match[target_idx - 1]
                        
                        # Vérifier que les entités existent
                        if source_id in entity_map and target_id in entity_map:
                            relations.append({
                                'type': rel_type,
                                'source': source_id,
                                'target': target_id,
                                'confidence': 0.7,
                                'source_text': ' '.join(match)
                            })
        
        # Extraire les relations par mots-clés
        for word, rel_type in self._relation_words.items():
            pattern = re.compile(
                rf'(\S+)\s+{word}\s+(\S+)',
                re.IGNORECASE
            )
            matches = pattern.findall(text)
            for source_id, target_id in matches:
                if source_id in entity_map and target_id in entity_map:
                    relations.append({
                        'type': rel_type,
                        'source': source_id,
                        'target': target_id,
                        'confidence': 0.5,
                        'source_text': f'{source_id} {word} {target_id}'
                    })
        
        # Supprimer les doublons
        unique_relations = []
        seen = set()
        for rel in relations:
            key = (rel['type'], rel['source'], rel['target'])
            if key not in seen:
                seen.add(key)
                unique_relations.append(rel)
        
        return unique_relations

if __name__ == "__main__":
    # Test de l'extracteur
    extractor = RelationExtractor()
    
    text = "L'incident INC-001 affecte le pipeline PIPE-001."
    entities = [
        {'type': 'incident', 'id': 'INC-001'},
        {'type': 'pipeline', 'id': 'PIPE-001'}
    ]
    
    relations = extractor.extract(text, entities)
    print("Relations extraites:", relations)