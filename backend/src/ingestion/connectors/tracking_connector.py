"""
Connecteur pour les données de tracking maritime (AIS)
Récupère les positions et statuts des méthaniers
"""

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime, timedelta
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class TrackingConnector(BaseConnector):
    """
    Connecteur pour les données de tracking maritime (AIS)
    """
    
    def __init__(self):
        super().__init__(name="TrackingConnector")
        self._mock_vessels = []
        self._generate_vessels()
    
    def _generate_vessels(self):
        """Génère des données de navires simulées"""
        vessel_names = [
            "GNL Explorer", "GNL Voyager", "GNL Pioneer",
            "GNL Discovery", "GNL Horizon", "GNL Navigator"
        ]
        
        ports = [
            {"name": "Fos-sur-Mer", "lat": 43.43, "lon": 4.87},
            {"name": "Montoir", "lat": 47.28, "lon": -2.15},
            {"name": "Dunkerque", "lat": 51.03, "lon": 2.37},
            {"name": "Le Havre", "lat": 49.49, "lon": 0.10},
            {"name": "Rotterdam", "lat": 51.92, "lon": 4.48},
            {"name": "Zeebrugge", "lat": 51.33, "lon": 3.20}
        ]
        
        for i, name in enumerate(vessel_names):
            port = ports[i % len(ports)]
            self._mock_vessels.append({
                'vessel_id': f'VESSEL-{i+1:03d}',
                'name': name,
                'type': 'Méthanier',
                'capacite_m3': random.randint(100000, 180000),
                'statut': random.choice(['en_croisiere', 'a_quai', 'en_chargement']),
                'current_port': port['name'],
                'latitude': port['lat'] + random.uniform(-0.5, 0.5),
                'longitude': port['lon'] + random.uniform(-0.5, 0.5),
                'vitesse_noeuds': round(random.uniform(0, 20), 1),
                'cap_deg': random.randint(0, 360)
            })
    
    def connect(self) -> bool:
        """Établit la connexion au système de tracking"""
        logger.info(f"🔗 {self.name} - Connexion au système AIS")
        self._is_connected = True
        return True
    
    def disconnect(self) -> bool:
        """Ferme la connexion"""
        logger.info(f"🔒 {self.name} - Déconnexion du système AIS")
        self._is_connected = False
        return True
    
    def _update_vessel_positions(self):
        """Met à jour les positions simulées des navires"""
        for vessel in self._mock_vessels:
            if vessel['statut'] == 'en_croisiere':
                vessel['latitude'] += random.uniform(-0.1, 0.1)
                vessel['longitude'] += random.uniform(-0.1, 0.1)
                vessel['vitesse_noeuds'] = round(random.uniform(10, 20), 1)
            else:
                vessel['vitesse_noeuds'] = 0
    
    def fetch_data(self, **kwargs) -> List[Dict]:
        """
        Récupère les données de tracking
        """
        logger.info(f"📥 {self.name} - Récupération des données AIS")
        
        self._update_vessel_positions()
        return self._mock_vessels
    
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données de tracking selon l'ontologie GNL
        """
        logger.info(f"🔄 {self.name} - Normalisation des données AIS")
        
        normalized = []
        for record in raw_data:
            try:
                normalized.append({
                    'type': 'Méthanier',
                    'properties': {
                        'id': record.get('vessel_id'),
                        'nom': record.get('name'),
                        'type_navire': record.get('type'),
                        'capacite_m3': record.get('capacite_m3', 0),
                        'statut': record.get('statut'),
                        'port_actuel': record.get('current_port'),
                        'latitude': record.get('latitude', 0),
                        'longitude': record.get('longitude', 0),
                        'vitesse_noeuds': record.get('vitesse_noeuds', 0),
                        'cap_deg': record.get('cap_deg', 0),
                        'last_update': datetime.now().isoformat()
                    },
                    'relationships': []
                })
                self._update_stats(True)
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation AIS : {e}")
                self._update_stats(False)
        
        return normalized
    
    def get_vessel_position(self, vessel_id: str) -> Optional[Dict]:
        """
        Récupère la position d'un navire spécifique
        """
        for vessel in self._mock_vessels:
            if vessel.get('vessel_id') == vessel_id:
                return {
                    'vessel_id': vessel['vessel_id'],
                    'name': vessel['name'],
                    'latitude': vessel['latitude'],
                    'longitude': vessel['longitude'],
                    'vitesse_noeuds': vessel['vitesse_noeuds'],
                    'statut': vessel['statut']
                }
        return None

if __name__ == "__main__":
    # Test du connecteur
    connector = TrackingConnector()
    data = connector.run()
    print(f"✅ {len(data)} enregistrements de tracking normalisés")
    if data:
        print("Exemple :", json.dumps(data[0], indent=2))