"""
Consommateur Kafka pour l'ingestion de données en streaming
"""

from kafka import KafkaConsumer as KafkaBase
from kafka.errors import KafkaError
import json
import os
import logging
from typing import Dict, List, Any, Optional, Callable
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumer:
    """
    Consommateur Kafka pour les données en streaming
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None, group_id: Optional[str] = None):
        """
        Initialise le consommateur Kafka
        
        Args:
            bootstrap_servers: Serveurs Kafka
            group_id: ID du groupe de consommation
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            'KAFKA_BOOTSTRAP_SERVERS', 
            'localhost:9092'
        )
        self.group_id = group_id or os.getenv('KAFKA_GROUP_ID', 'gnl-ingestion-group')
        self.consumer = None
        self._is_running = False
        logger.info(f"🔗 Kafka Consumer : {self.bootstrap_servers}")
    
    def connect(self, topics: List[str]) -> bool:
        """
        Établit la connexion à Kafka
        """
        try:
            self.consumer = KafkaBase(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda m: m.decode('utf-8') if m else None
            )
            logger.info(f"✅ Connecté à Kafka - Topics: {topics}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Kafka : {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            self._is_running = False
            logger.info("🔒 Connexion Kafka fermée")
    
    def consume(self, callback: Callable[[Dict], None], topics: List[str], max_messages: int = 100):
        """
        Consomme les messages de Kafka
        
        Args:
            callback: Fonction de traitement des messages
            topics: Liste des topics à consommer
            max_messages: Nombre max de messages par poll
        """
        if not self.connect(topics):
            return
        
        self._is_running = True
        logger.info(f"🔄 Début de la consommation - Topics: {topics}")
        
        try:
            while self._is_running:
                messages = self.consumer.poll(max_records=max_messages, timeout_ms=1000)
                
                for topic_partition, records in messages.items():
                    for record in records:
                        try:
                            value = record.value
                            if value:
                                logger.info(f"📥 Message reçu - Topic: {topic_partition.topic}")
                                callback(value)
                        except Exception as e:
                            logger.error(f"❌ Erreur traitement message : {e}")
                
        except KeyboardInterrupt:
            logger.info("⏹️ Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la consommation : {e}")
        finally:
            self.disconnect()
    
    def consume_single(self, topic: str, timeout: int = 5000) -> Optional[Dict]:
        """
        Consomme un seul message
        """
        if not self.connect([topic]):
            return None
        
        try:
            messages = self.consumer.poll(timeout_ms=timeout, max_records=1)
            for records in messages.values():
                for record in records:
                    return record.value
        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
        finally:
            self.disconnect()
        
        return None
    
    def stop(self):
        """Arrête la consommation"""
        self._is_running = False
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état du consommateur
        """
        try:
            if self.consumer:
                # Tenter d'obtenir les métadonnées
                self.consumer.topics()
                return {
                    "status": "healthy",
                    "bootstrap_servers": self.bootstrap_servers,
                    "group_id": self.group_id,
                    "connected": True
                }
            return {
                "status": "disconnected",
                "bootstrap_servers": self.bootstrap_servers,
                "connected": False
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "bootstrap_servers": self.bootstrap_servers,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test du consommateur
    consumer = KafkaConsumer()
    
    def process_message(message: Dict):
        print(f"📥 Message reçu : {message}")
    
    # Démarrer la consommation (appuyez sur Ctrl+C pour arrêter)
    # consumer.consume(process_message, ['gnl_iot'], max_messages=10)
    
    print("✅ Consommateur Kafka prêt")
    print(consumer.health_check())