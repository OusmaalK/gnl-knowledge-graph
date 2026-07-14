"""
Connecteur de base pour l'ingestion des données
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """
    Classe abstraite de base pour tous les connecteurs
    """
    
    def __init__(self, name: str = "BaseConnector"):
        self.name = name
        self._is_connected = False
        self._stats = {
            'records_processed': 0,
            'records_failed': 0,
            'start_time': None,
            'end_time': None
        }
        logger.info(f"🔌 {self.name} initialisé")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Établit la connexion à la source de données
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Ferme la connexion à la source de données
        """
        pass
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict]:
        """
        Récupère les données de la source
        """
        pass
    
    @abstractmethod
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données selon l'ontologie GNL
        """
        pass
    
    def is_connected(self) -> bool:
        """Vérifie si le connecteur est connecté"""
        return self._is_connected
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques du connecteur"""
        return self._stats
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self._stats = {
            'records_processed': 0,
            'records_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _update_stats(self, success: bool = True):
        """Met à jour les statistiques"""
        if success:
            self._stats['records_processed'] += 1
        else:
            self._stats['records_failed'] += 1
    
    def start_timer(self):
        """Démarre le chronomètre"""
        self._stats['start_time'] = datetime.now()
    
    def stop_timer(self):
        """Arrête le chronomètre"""
        self._stats['end_time'] = datetime.now()
    
    def get_duration_seconds(self) -> Optional[float]:
        """Récupère la durée d'exécution en secondes"""
        if self._stats['start_time'] and self._stats['end_time']:
            return (self._stats['end_time'] - self._stats['start_time']).total_seconds()
        return None
    
    def run(self, **kwargs) -> List[Dict]:
        """
        Exécute le processus complet d'ingestion
        """
        self.start_timer()
        logger.info(f"🚀 {self.name} - Début de l'ingestion")
        
        try:
            if not self.is_connected():
                if not self.connect():
                    logger.error(f"❌ {self.name} - Échec de connexion")
                    self.stop_timer()
                    return []
            
            raw_data = self.fetch_data(**kwargs)
            logger.info(f"📥 {self.name} - {len(raw_data)} enregistrements récupérés")
            
            normalized_data = self.normalize_data(raw_data)
            logger.info(f"📊 {self.name} - {len(normalized_data)} enregistrements normalisés")
            
            self.stop_timer()
            logger.info(f"✅ {self.name} - Ingestion terminée ({self.get_duration_seconds():.2f}s)")
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"❌ {self.name} - Erreur : {e}")
            self.stop_timer()
            return []
        finally:
            self.disconnect()