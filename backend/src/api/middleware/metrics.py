
"""
Middleware de métriques
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict

from ...monitoring.metrics.collector import MetricsCollector

logger = logging.getLogger(__name__)

# Collecteur global
metrics_collector = MetricsCollector()

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour collecter les métriques des requêtes
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Traite la requête avec collecte de métriques
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Durée de la requête
            duration = (time.time() - start_time) * 1000
            
            # Enregistrer la métrique
            metrics_collector.record_request(
                endpoint=request.url.path,
                duration=duration / 1000,
                status_code=response.status_code
            )
            
            return response
            
        except Exception as e:
            # Enregistrer l'erreur
            metrics_collector.record_request(
                endpoint=request.url.path,
                duration=(time.time() - start_time) * 1000 / 1000,
                status_code=500
            )
            raise
    
    @staticmethod
    def get_metrics() -> Dict:
        """
        Récupère les métriques collectées
        """
        return metrics_collector.get_all_metrics()