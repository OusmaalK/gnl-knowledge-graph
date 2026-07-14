"""
Producteur Kafka pour l'envoi de données en streaming
"""

from kafka import KafkaProducer as KafkaBase
from kafka.errors import KafkaError
import json
import os
import logging
from typing import Dict, List, Any, Optional, Callable
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaProducer:
    """
    Producteur Kafka pour l'envoi de données
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None):
        """
        Initialise le producteur Kafka
        
        Args:
            bootstrap_servers: Serveurs Kafka
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            'KAFKA_BOOTSTRAP_SERVERS', 
            'localhost:9092'
        )
        self.producer = None
        self._is_connected = False
        logger.info(f"🔗 Kafka Producer : {self.bootstrap_servers}")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Kafka
        """
        try:
            self.producer = KafkaBase(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                max_in_flight_requests_per_connection=1
            )
            self._is_connected = True
            logger.info("✅ Connecté à Kafka Producer")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Kafka : {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            self.producer = None
            self._is_connected = False
            logger.info("🔒 Connexion Kafka fermée")
    
    def send_message(self, topic: str, message: Dict, key: Optional[str] = None, 
                     callback: Optional[Callable] = None) -> bool:
        """
        Envoie un message vers un topic Kafka
        
        Args:
            topic: Topic de destination
            message: Message à envoyer
            key: Clé du message (optionnel)
            callback: Fonction de callback (optionnel)
        """
        if not self._is_connected:
            if not self.connect():
                return False
        
        try:
            future = self.producer.send(topic, value=message, key=key)
            
            if callback:
                future.add_callback(callback)
                future.add_errback(lambda e: logger.error(f"❌ Erreur envoi : {e}"))
            
            self.producer.flush()
            logger.info(f"📤 Message envoyé - Topic: {topic} ({message.get('id', 'N/A')})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi message : {e}")
            return False
    
    def send_batch(self, topic: str, messages: List[Dict], key_func: Optional[Callable] = None) -> Dict:
        """
        Envoie un lot de messages
        
        Args:
            topic: Topic de destination
            messages: Liste des messages à envoyer
            key_func: Fonction pour générer les clés (optionnel)
            
        Returns:
            Dict avec statistiques d'envoi
        """
        if not self._is_connected:
            if not self.connect():
                return {"success": False, "sent": 0, "failed": len(messages)}
        
        sent = 0
        failed = 0
        
        for message in messages:
            key = key_func(message) if key_func else message.get('id')
            if self.send_message(topic, message, key):
                sent += 1
            else:
                failed += 1
        
        logger.info(f"📊 Batch envoyé - Topic: {topic} ({sent} envoyés, {failed} échoués)")
        return {"success": sent > 0, "sent": sent, "failed": failed}
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état du producteur
        """
        try:
            if self.producer:
                self.producer.partitions_for('test')
                return {
                    "status": "healthy",
                    "bootstrap_servers": self.bootstrap_servers,
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
    # Test du producteur
    producer = KafkaProducer()
    
    # Envoyer un message de test
    test_message = {
        "id": "TEST-001",
        "timestamp": "2026-07-10T12:00:00Z",
        "type": "test",
        "data": {"value": 42}
    }
    
    # producer.send_message('gnl_test', test_message, key='TEST-001')
    print("✅ Producteur Kafka prêt")
    print(producer.health_check())
    
    producer.disconnect()