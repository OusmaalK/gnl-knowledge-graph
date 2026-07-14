"""
Enrichisseur de contexte
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextEnricher:
    """
    Enrichit les données avec du contexte
    """
    
    def __init__(self):
        self._context_data = {
            'PIPE-001': {
                'nom': 'Nord-Sud',
                'type': 'Pipeline principal',
                'importance': 'élevée'
            },
            'TERM-001': {
                'nom': 'Fos-sur-Mer',
                'type': 'Terminal principal',
                'importance': 'critique'
            },
            'COMP-001': {
                'nom': 'Compresseur Nord',
                'type': 'Compresseur principal',
                'importance': 'élevée'
            }
        }
        
        logger.info("✅ ContextEnricher initialisé")
    
    def enrich(self, data: List[Dict]) -> List[Dict]:
        """
        Enrichit les données avec du contexte
        """
        enriched = []
        
        for item in data:
            enriched_item = item.copy()
            properties = item.get('properties', {})
            
            # Ajouter le contexte basé sur l'ID
            entity_id = properties.get('id')
            if entity_id and entity_id in self._context_data:
                context = self._context_data[entity_id]
                properties['context_nom'] = context.get('nom')
                properties['context_type'] = context.get('type')
                properties['context_importance'] = context.get('importance')
            
            # Ajouter le contexte temporel
            if 'timestamp' in properties or 'date' in properties:
                date_str = properties.get('timestamp') or properties.get('date')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        properties['context_jour'] = dt.strftime('%A')
                        properties['context_mois'] = dt.strftime('%B')
                        properties['context_annee'] = dt.year
                        properties['context_heure'] = dt.hour
                    except:
                        pass
            
            enriched_item['properties'] = properties
            enriched.append(enriched_item)
        
        return enriched

if __name__ == "__main__":
    # Test de l'enrichisseur
    enricher = ContextEnricher()
    
    data = [
        {
            'properties': {
                'id': 'PIPE-001',
                'timestamp': '2026-07-10T12:00:00Z'
            }
        }
    ]
    
    enriched = enricher.enrich(data)
    print("Enrichi:", enriched)