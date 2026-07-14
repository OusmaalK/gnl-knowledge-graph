"""
Producteurs pour l'ingestion des données
"""

from .kafka_producer import KafkaProducer

__all__ = [
    'KafkaProducer'
]