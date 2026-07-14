"""
Router pour le health check
Version corrigée avec imports FastAPI
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import logging

from ..schemas.responses import HealthResponse
from ...core.config import settings
from ...core.constants import __version__

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def health_check() -> Dict[str, Any]:
    """
    Vérifie l'état de l'API et des services
    """
    services = {}
    
    # Vérifier Neo4j
    try:
        from ...infrastructure.neo4j.client import Neo4jClient
        neo4j = Neo4jClient()
        health = neo4j.health_check()
        services['neo4j'] = health.get('connected', False)
        neo4j.close()
        logger.info("✅ Neo4j connecté")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j non disponible: {e}")
        services['neo4j'] = False
    
    # Vérifier Redis
    try:
        from ...infrastructure.redis.client import RedisClient
        redis = RedisClient()
        health = redis.health_check()
        services['redis'] = health.get('status') == 'healthy'
        redis.close()
        logger.info("✅ Redis connecté")
    except Exception as e:
        logger.warning(f"⚠️ Redis non disponible: {e}")
        services['redis'] = False
    
    # Vérifier Qdrant
    try:
        from ...infrastructure.qdrant.client import QdrantClient
        qdrant = QdrantClient()
        health = qdrant.health_check()
        services['qdrant'] = health.get('status') == 'healthy'
        qdrant.close()
        logger.info("✅ Qdrant connecté")
    except Exception as e:
        logger.warning(f"⚠️ Qdrant non disponible: {e}")
        services['qdrant'] = False
    
    # Vérifier Kafka
    try:
        from ...infrastructure.kafka.admin import KafkaAdmin
        kafka = KafkaAdmin()
        connected = kafka.connect()
        services['kafka'] = connected
        kafka.close()
        logger.info("✅ Kafka connecté")
    except Exception as e:
        logger.warning(f"⚠️ Kafka non disponible: {e}")
        services['kafka'] = False
    
    all_healthy = all(services.values())
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version=__version__,
        timestamp=time.time(),
        services=services
    )

@router.get("/live")
async def liveness_check():
    """Check de liveness pour Kubernetes"""
    return {"status": "alive", "timestamp": time.time()}

@router.get("/ready")
async def readiness_check():
    """Check de readiness pour Kubernetes"""
    try:
        health = await health_check()
        if health.status == "healthy":
            return {"status": "ready", "timestamp": time.time()}
        return {"status": "not_ready", "reason": "services_unhealthy", "timestamp": time.time()}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e), "timestamp": time.time()}