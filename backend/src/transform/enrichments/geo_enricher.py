"""
Enrichisseur géographique
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class GeoEnricher:
    """
    Enrichit les données avec des informations géographiques
    """
    
    def __init__(self):
        self._geo_data = {
            'Fos-sur-Mer': {'lat': 43.43, 'lon': 4.87, 'region': 'Provence-Alpes-Côte d\'Azur'},
            'Montoir': {'lat': 47.28, 'lon': -2.15, 'region': 'Pays de la Loire'},
            'Dunkerque': {'lat': 51.03, 'lon': 2.37, 'region': 'Hauts-de-France'},
            'Le Havre': {'lat': 49.49, 'lon': 0.10, 'region': 'Normandie'},
            'Paris': {'lat': 48.86, 'lon': 2.35, 'region': 'Île-de-France'},
            'Marseille': {'lat': 43.30, 'lon': 5.37, 'region': 'Provence-Alpes-Côte d\'Azur'},
            'Londres': {'lat': 51.51, 'lon': -0.13, 'region': 'Grand Londres'},
            'Stavanger': {'lat': 58.97, 'lon': 5.73, 'region': 'Rogaland'}
        }
        
        logger.info("✅ GeoEnricher initialisé")
    
    def enrich(self, data: List[Dict]) -> List[Dict]:
        """
        Enrichit les données avec des informations géographiques
        """
        enriched = []
        
        for item in data:
            enriched_item = item.copy()
            
            # Enrichir les propriétés
            properties = item.get('properties', {})
            
            # Vérifier les champs de localisation
            for location_field in ['localisation', 'ville', 'port_actuel', 'adresse']:
                if location_field in properties:
                    location = properties.get(location_field)
                    geo_info = self._get_geo_info(location)
                    if geo_info:
                        properties[f'{location_field}_geo'] = geo_info
            
            enriched_item['properties'] = properties
            enriched.append(enriched_item)
        
        return enriched
    
    def _get_geo_info(self, location: str) -> Optional[Dict]:
        """
        Récupère les informations géographiques d'une localisation
        """
        if not location:
            return None
        
        # Recherche exacte
        if location in self._geo_data:
            return self._geo_data[location]
        
        # Recherche partielle
        for key, value in self._geo_data.items():
            if key.lower() in location.lower() or location.lower() in key.lower():
                return value
        
        return None
    
    def get_distance(self, loc1: str, loc2: str) -> Optional[float]:
        """
        Calcule la distance entre deux localisations
        """
        geo1 = self._get_geo_info(loc1)
        geo2 = self._get_geo_info(loc2)
        
        if not geo1 or not geo2:
            return None
        
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(geo1['lat']), radians(geo1['lon'])
        lat2, lon2 = radians(geo2['lat']), radians(geo2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return 6371 * c  # Rayon de la Terre en km

if __name__ == "__main__":
    # Test de l'enrichisseur
    enricher = GeoEnricher()
    
    data = [
        {
            'properties': {
                'localisation': 'Fos-sur-Mer',
                'ville': 'Marseille'
            }
        }
    ]
    
    enriched = enricher.enrich(data)
    print("Enrichi:", enriched)