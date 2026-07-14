"""
Enrichisseur de risque
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RiskEnricher:
    """
    Enrichit les données avec des informations de risque
    """
    
    def __init__(self):
        self._risk_factors = {
            'critique': {'score': 90, 'niveau': 'CRITIQUE', 'couleur': '#EF4444'},
            'eleve': {'score': 70, 'niveau': 'ÉLEVÉ', 'couleur': '#F59E0B'},
            'moyen': {'score': 50, 'niveau': 'MOYEN', 'couleur': '#3B82F6'},
            'faible': {'score': 20, 'niveau': 'FAIBLE', 'couleur': '#10B981'}
        }
        
        logger.info("✅ RiskEnricher initialisé")
    
    def enrich(self, data: List[Dict]) -> List[Dict]:
        """
        Enrichit les données avec des informations de risque
        """
        enriched = []
        
        for item in data:
            enriched_item = item.copy()
            properties = item.get('properties', {})
            
            # Calculer le risque si des informations sont disponibles
            if 'statut' in properties or 'gravite' in properties:
                risk_info = self._calculate_risk(properties)
                if risk_info:
                    properties['risk_score'] = risk_info['score']
                    properties['risk_niveau'] = risk_info['niveau']
                    properties['risk_couleur'] = risk_info['couleur']
            
            enriched_item['properties'] = properties
            enriched.append(enriched_item)
        
        return enriched
    
    def _calculate_risk(self, properties: Dict) -> Optional[Dict]:
        """
        Calcule le risque à partir des propriétés
        """
        score = 0
        factors = []
        
        # Facteur 1: Statut
        statut = properties.get('statut', '')
        if statut in ['critique', 'hors_service']:
            score += 40
            factors.append('Statut critique')
        elif statut in ['alerte', 'maintenance']:
            score += 20
            factors.append('Statut alerte')
        
        # Facteur 2: Gravité
        gravite = properties.get('gravite', '')
        if gravite == 'critique':
            score += 30
            factors.append('Gravité critique')
        elif gravite == 'majeur':
            score += 20
            factors.append('Gravité majeure')
        elif gravite == 'mineur':
            score += 10
            factors.append('Gravité mineure')
        
        # Facteur 3: Durée (pour les incidents)
        duree = properties.get('duree_min', 0)
        if duree > 180:
            score += 10
            factors.append('Longue durée')
        
        # Facteur 4: Incidents récents
        if 'incidents_count' in properties:
            count = properties.get('incidents_count', 0)
            if count > 3:
                score += 20
                factors.append('Incidents multiples')
            elif count > 1:
                score += 10
                factors.append('Incidents récents')
        
        # Déterminer le niveau
        if score >= 70:
            return self._risk_factors['critique']
        elif score >= 50:
            return self._risk_factors['eleve']
        elif score >= 30:
            return self._risk_factors['moyen']
        else:
            return self._risk_factors['faible']

if __name__ == "__main__":
    # Test de l'enrichisseur
    enricher = RiskEnricher()
    
    data = [
        {
            'properties': {
                'statut': 'critique',
                'gravite': 'critique',
                'duree_min': 240,
                'incidents_count': 2
            }
        }
    ]
    
    enriched = enricher.enrich(data)
    print("Enrichi:", enriched)