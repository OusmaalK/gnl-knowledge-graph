"""
Connecteur pour les données IoT (capteurs)
Récupère les données des capteurs de pression, débit, température
"""

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime, timedelta
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class IoTConnector(BaseConnector):
    """
    Connecteur pour les données IoT des capteurs GNL
    """
    
    def __init__(self, pipeline_id: Optional[str] = None):
        super().__init__(name="IoTConnector")
        self.pipeline_id = pipeline_id or "PIPE-001"
        self._mock_data = []
        self._generate_mock_data()
    
    def connect(self) -> bool:
        """Établit la connexion au système IoT"""
        logger.info(f"🔗 {self.name} - Connexion au système IoT")
        self._is_connected = True
        return True
    
    def disconnect(self) -> bool:
        """Ferme la connexion"""
        logger.info(f"🔒 {self.name} - Déconnexion du système IoT")
        self._is_connected = False
        return True
    
    def _generate_mock_data(self, count: int = 100):
        """
        Génère des données IoT simulées pour les tests
        """
        logger.info(f"📊 {self.name} - Génération de {count} données simulées")
        
        self._mock_data = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            timestamp = base_time + timedelta(minutes=i * 15)
            self._mock_data.append({
                'pipeline_id': self.pipeline_id,
                'timestamp': timestamp.isoformat(),
                'pression_bar': round(random.uniform(60, 85), 1),
                'debit_m3_s': round(random.uniform(40, 60), 1),
                'temperature_c': round(random.uniform(15, 25), 1),
                'vibration_mm_s': round(random.uniform(0.1, 0.8), 2),
                'statut': random.choice(['actif', 'actif', 'actif', 'alerte']),
                'capteur_id': f"SENSOR-{random.randint(1, 10):03d}"
            })
    
    def fetch_data(self, **kwargs) -> List[Dict]:
        """
        Récupère les données IoT
        """
        logger.info(f"📥 {self.name} - Récupération des données IoT")
        
        # En production, remplacer par un appel API réel
        # Exemple : requests.get('http://iot-api/pipelines/{pipeline_id}/data')
        
        limit = kwargs.get('limit', 50)
        return self._mock_data[-limit:]
    
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données IoT selon l'ontologie GNL
        """
        logger.info(f"🔄 {self.name} - Normalisation des données IoT")
        
        normalized = []
        for record in raw_data:
            try:
                normalized.append({
                    'type': 'Mesure',
                    'properties': {
                        'timestamp': record.get('timestamp'),
                        'pipeline_id': record.get('pipeline_id'),
                        'pression_bar': float(record.get('pression_bar', 0)),
                        'debit_m3_s': float(record.get('debit_m3_s', 0)),
                        'temperature_c': float(record.get('temperature_c', 0)),
                        'vibration_mm_s': float(record.get('vibration_mm_s', 0)),
                        'statut': record.get('statut', 'inconnu'),
                        'capteur_id': record.get('capteur_id')
                    },
                    'relationships': [
                        {
                            'type': 'MESURE',
                            'target': {
                                'type': 'Pipeline',
                                'id': record.get('pipeline_id')
                            }
                        }
                    ]
                })
                self._update_stats(True)
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation IoT : {e}")
                self._update_stats(False)
        
        return normalized
    
    def get_real_data(self, pipeline_id: str, days: int = 1) -> List[Dict]:
        """
        Récupère les données réelles d'un pipeline
        À remplacer par un appel API réel
        """
        # Simulation pour l'exemple
        self.pipeline_id = pipeline_id
        self._generate_mock_data(days * 96)  # 96 mesures par jour (15 min)
        return self.fetch_data(limit=days * 96)

if __name__ == "__main__":
    # Test du connecteur
    connector = IoTConnector()
    data = connector.run(limit=20)
    print(f"✅ {len(data)} enregistrements IoT normalisés")
    if data:
        print("Exemple :", json.dumps(data[0], indent=2))