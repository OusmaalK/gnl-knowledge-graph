"""
Dépendances pour les clients de base de données
"""

from typing import Generator
from ...infrastructure.neo4j.client import Neo4jClient
from ...infrastructure.redis.client import RedisClient

def get_neo4j_client() -> Generator[Neo4jClient, None, None]:
    """
    Fournit un client Neo4j
    """
    client = Neo4jClient()
    try:
        client.connect()
        yield client
    finally:
        client.close()

def get_redis_client() -> Generator[RedisClient, None, None]:
    """
    Fournit un client Redis
    """
    client = RedisClient()
    try:
        client.connect()
        yield client
    finally:
        client.close()