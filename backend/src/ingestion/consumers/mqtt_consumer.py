"""
Consommateur MQTT pour les données IoT
"""

import paho.mqtt.client as mqtt
import json
import os
import logging
from typing import Dict, List, Any, Optional, Callable
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTConsumer:
    """
    Consommateur MQTT pour les données IoT
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialise le consommateur MQTT
        
        Args:
            host: Hôte MQTT
            port: Port MQTT
        """
        self.host = host or os.getenv('MQTT_HOST', 'localhost')
        self.port = port or int(os.getenv('MQTT_PORT', 1883))
        self.client = None
        self._is_connected = False
        self._callbacks = {}
        logger.info(f"🔗 MQTT : {self.host}:{self.port}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback de connexion
        """
        if rc == 0:
            self._is_connected = True
            logger.info("✅ Connecté au broker MQTT")
            # S'abonner aux topics configurés
            for topic in self._callbacks.keys():
                client.subscribe(topic)
                logger.info(f"📋 Abonné au topic : {topic}")
        else:
            logger.error(f"❌ Erreur de connexion MQTT (code: {rc})")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback de réception de message
        """
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"📥 Message reçu - Topic: {msg.topic}")
            
            # Traiter le message
            if msg.topic in self._callbacks:
                try:
                    data = json.loads(payload)
                    self._callbacks[msg.topic](data)
                except json.JSONDecodeError:
                    self._callbacks[msg.topic](payload)
            else:
                logger.warning(f"⚠️ Topic non configuré : {msg.topic}")
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement message : {e}")
    
    def connect(self) -> bool:
        """
        Établit la connexion au broker MQTT
        """
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion MQTT : {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
            self._is_connected = False
            logger.info("🔒 Connexion MQTT fermée")
    
    def subscribe(self, topic: str, callback: Callable[[Dict], None]):
        """
        S'abonne à un topic MQTT
        
        Args:
            topic: Topic à écouter
            callback: Fonction de traitement des messages
        """
        self._callbacks[topic] = callback
        
        if self.client and self._is_connected:
            self.client.subscribe(topic)
            logger.info(f"📋 Abonné au topic : {topic}")
    
    def unsubscribe(self, topic: str):
        """
        Se désabonne d'un topic
        """
        if topic in self._callbacks:
            del self._callbacks[topic]
            if self.client and self._is_connected:
                self.client.unsubscribe(topic)
                logger.info(f"🔕 Désabonné du topic : {topic}")
    
    def publish(self, topic: str, message: Dict):
        """
        Publie un message sur un topic
        """
        if not self.client or not self._is_connected:
            logger.error("❌ Non connecté au broker MQTT")
            return False
        
        try:
            payload = json.dumps(message) if isinstance(message, dict) else message
            self.client.publish(topic, payload)
            logger.info(f"📤 Message publié - Topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur publication : {e}")
            return False
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état du consommateur MQTT
        """
        return {
            "status": "healthy" if self._is_connected else "disconnected",
            "host": self.host,
            "port": self.port,
            "connected": self._is_connected,
            "topics": list(self._callbacks.keys())
        }

if __name__ == "__main__":
    # Test du consommateur
    consumer = MQTTConsumer()
    
    def process_iot_data(data: Dict):
        print(f"📥 Données IoT : {data}")
    
    # Simuler une connexion
    # consumer.connect()
    # consumer.subscribe('gnl/iot/pipeline', process_iot_data)
    
    print("✅ Consommateur MQTT prêt")
    print(consumer.health_check())