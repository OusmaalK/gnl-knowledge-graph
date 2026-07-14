"""
Configuration des topics Kafka pour le projet GNL
"""

# Configuration des topics
TOPICS = {
    # Données IoT (capteurs)
    'gnl_iot': {
        'description': 'Données des capteurs IoT (pression, débit, température)',
        'num_partitions': 6,
        'replication_factor': 1,
        'config': {
            'cleanup.policy': 'delete',
            'retention.ms': '604800000',  # 7 jours
            'compression.type': 'snappy',
        }
    },
    
    # Tracking maritime (AIS)
    'gnl_tracking': {
        'description': 'Données de tracking des méthaniers (AIS)',
        'num_partitions': 4,
        'replication_factor': 1,
        'config': {
            'cleanup.policy': 'delete',
            'retention.ms': '259200000',  # 3 jours
            'compression.type': 'snappy',
        }
    },
    
    # Incidents et rapports
    'gnl_incidents': {
        'description': 'Rapports d\'incidents et maintenance',
        'num_partitions': 3,
        'replication_factor': 1,
        'config': {
            'cleanup.policy': 'delete',
            'retention.ms': '31536000000',  # 1 an
            'compression.type': 'snappy',
        }
    },
    
    # Données pipelines
    'gnl_pipelines': {
        'description': 'Données des pipelines (état, pression, etc.)',
        'num_partitions': 3,
        'replication_factor': 1,
        'config': {
            'cleanup.policy': 'delete',
            'retention.ms': '604800000',  # 7 jours
            'compression.type': 'snappy',
        }
    },
    
    # Commandes et transactions
    'gnl_orders': {
        'description': 'Commandes et transactions GNL',
        'num_partitions': 3,
        'replication_factor': 1,
        'config': {
            'cleanup.policy': 'delete',
            'retention.ms': '31536000000',  # 1 an
            'compression.type': 'snappy',
        }
    }
}

def create_topics(admin_client, topics: dict = None):
    """
    Crée tous les topics configurés
    
    Args:
        admin_client: Instance de KafkaAdmin
        topics: Configuration des topics (utilise TOPICS par défaut)
    """
    from .admin import KafkaAdmin
    
    if not isinstance(admin_client, KafkaAdmin):
        admin_client = KafkaAdmin()
    
    topics_config = topics or TOPICS
    
    for topic_name, config in topics_config.items():
        admin_client.create_topic(
            topic_name=topic_name,
            num_partitions=config.get('num_partitions', 6),
            replication_factor=config.get('replication_factor', 1),
            config=config.get('config', {})
        )
    
    admin_client.close()

def get_topic_names() -> list:
    """
    Retourne la liste des noms de topics
    """
    return list(TOPICS.keys())

def get_topic_config(topic_name: str) -> dict:
    """
    Retourne la configuration d'un topic
    """
    return TOPICS.get(topic_name, {})

if __name__ == "__main__":
    from .admin import KafkaAdmin
    
    admin = KafkaAdmin()
    if admin.connect():
        create_topics(admin)
        print("✅ Topics créés avec succès")
        admin.close()