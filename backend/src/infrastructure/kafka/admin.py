"""
Administration de Kafka - Gestion des topics et partitions
"""

import json
import logging
from typing import Dict, List, Optional, Any
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
from kafka.errors import TopicAlreadyExistsError, UnknownTopicOrPartitionError
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaAdmin:
    """
    Administrateur Kafka pour la gestion des topics
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None):
        """
        Initialise l'admin Kafka
        
        Args:
            bootstrap_servers: Serveurs Kafka (ex: localhost:9092)
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            'KAFKA_BOOTSTRAP_SERVERS', 
            'localhost:9092'
        )
        self.admin_client = None
        logger.info(f"🔗 Bootstrap servers : {self.bootstrap_servers}")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Kafka
        """
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='gnl-knowledge-graph-admin'
            )
            logger.info("✅ Connecté à Kafka Admin")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Kafka : {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.admin_client:
            self.admin_client.close()
            logger.info("🔒 Connexion Kafka fermée")
    
    def create_topic(self, 
                     topic_name: str, 
                     num_partitions: int = 6, 
                     replication_factor: int = 1,
                     config: Optional[Dict] = None) -> bool:
        """
        Crée un topic Kafka
        
        Args:
            topic_name: Nom du topic
            num_partitions: Nombre de partitions
            replication_factor: Facteur de réplication
            config: Configuration supplémentaire (retention, compression, etc.)
        """
        if not self.admin_client:
            if not self.connect():
                return False
        
        try:
            # Configuration par défaut
            default_config = {
                'cleanup.policy': 'delete',
                'retention.ms': '604800000',  # 7 jours
                'compression.type': 'snappy',
                'segment.bytes': '1073741824',  # 1 Go
            }
            
            if config:
                default_config.update(config)
            
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs=default_config
            )
            
            self.admin_client.create_topics([new_topic])
            logger.info(f"✅ Topic créé : {topic_name} (partitions: {num_partitions})")
            return True
            
        except TopicAlreadyExistsError:
            logger.warning(f"⚠️ Topic existe déjà : {topic_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur création topic {topic_name} : {e}")
            return False
    
    def delete_topic(self, topic_name: str) -> bool:
        """
        Supprime un topic Kafka
        """
        if not self.admin_client:
            if not self.connect():
                return False
        
        try:
            self.admin_client.delete_topics([topic_name])
            logger.info(f"🗑️ Topic supprimé : {topic_name}")
            return True
        except UnknownTopicOrPartitionError:
            logger.warning(f"⚠️ Topic inexistant : {topic_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur suppression topic {topic_name} : {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """
        Liste tous les topics
        """
        if not self.admin_client:
            if not self.connect():
                return []
        
        try:
            topics = self.admin_client.list_topics()
            logger.info(f"📋 Topics : {len(topics)}")
            return topics
        except Exception as e:
            logger.error(f"❌ Erreur liste topics : {e}")
            return []
    
    def get_topic_config(self, topic_name: str) -> Dict:
        """
        Récupère la configuration d'un topic
        """
        if not self.admin_client:
            if not self.connect():
                return {}
        
        try:
            resource = ConfigResource(
                resource_type=ConfigResourceType.TOPIC,
                name=topic_name
            )
            configs = self.admin_client.describe_configs([resource])
            return {config.name: config.value for config in configs[resource]}
        except Exception as e:
            logger.error(f"❌ Erreur config topic {topic_name} : {e}")
            return {}
    
    def alter_topic_config(self, topic_name: str, config: Dict) -> bool:
        """
        Modifie la configuration d'un topic
        """
        if not self.admin_client:
            if not self.connect():
                return False
        
        try:
            resource = ConfigResource(
                resource_type=ConfigResourceType.TOPIC,
                name=topic_name,
                configs=config
            )
            self.admin_client.alter_configs([resource])
            logger.info(f"✅ Configuration modifiée pour {topic_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur modification config {topic_name} : {e}")
            return False
    
    def get_topic_partitions(self, topic_name: str) -> int:
        """
        Récupère le nombre de partitions d'un topic
        """
        config = self.get_topic_config(topic_name)
        # La méthode exacte dépend de la version de Kafka
        return 6  # Valeur par défaut
    
    def create_topics_batch(self, topics_config: Dict[str, Dict]) -> Dict[str, bool]:
        """
        Crée plusieurs topics en batch
        
        Args:
            topics_config: {topic_name: {num_partitions: 6, replication_factor: 1, config: {...}}}
        """
        results = {}
        for topic_name, config in topics_config.items():
            results[topic_name] = self.create_topic(
                topic_name=topic_name,
                num_partitions=config.get('num_partitions', 6),
                replication_factor=config.get('replication_factor', 1),
                config=config.get('config', {})
            )
        return results

if __name__ == "__main__":
    # Test de l'admin Kafka
    admin = KafkaAdmin()
    
    # Créer les topics
    topics = {
        'gnl_iot': {'num_partitions': 6, 'replication_factor': 1},
        'gnl_tracking': {'num_partitions': 4, 'replication_factor': 1},
        'gnl_incidents': {'num_partitions': 3, 'replication_factor': 1},
        'gnl_pipelines': {'num_partitions': 3, 'replication_factor': 1},
    }
    
    results = admin.create_topics_batch(topics)
    print("Résultats :", results)
    
    # Lister les topics
    print("Topics existants :", admin.list_topics())
    
    admin.close()