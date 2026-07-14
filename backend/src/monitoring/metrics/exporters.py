"""
Exporteurs de métriques vers différents systèmes
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from .collector import MetricsCollector

logger = logging.getLogger(__name__)

class MetricsExporter:
    """
    Exporteur de métriques vers Prometheus et autres systèmes
    """
    
    def __init__(self, collector: Optional[MetricsCollector] = None):
        """
        Initialise l'exporteur
        
        Args:
            collector: Instance du collecteur de métriques
        """
        self.collector = collector or MetricsCollector()
        self._prometheus_metrics = {}
        self._enabled = True
        logger.info("✅ MetricsExporter initialisé")
    
    # ============================================================
    # EXPORT PROMETHEUS
    # ============================================================
    
    def create_prometheus_metrics(self):
        """
        Crée les métriques Prometheus
        """
        # API Metrics
        self._prometheus_metrics['api_requests'] = Counter(
            'gnl_api_requests_total',
            'Total des requêtes API',
            ['endpoint', 'status']
        )
        
        self._prometheus_metrics['api_duration'] = Histogram(
            'gnl_api_request_duration_seconds',
            'Durée des requêtes API',
            ['endpoint']
        )
        
        # Graph Metrics
        self._prometheus_metrics['graph_queries'] = Counter(
            'gnl_graph_queries_total',
            'Total des requêtes graphe',
            ['query_type']
        )
        
        self._prometheus_metrics['graph_duration'] = Histogram(
            'gnl_graph_query_duration_seconds',
            'Durée des requêtes graphe',
            ['query_type']
        )
        
        # Agent Metrics
        self._prometheus_metrics['agent_calls'] = Counter(
            'gnl_agent_calls_total',
            'Total des appels agents',
            ['agent', 'success']
        )
        
        self._prometheus_metrics['agent_errors'] = Counter(
            'gnl_agent_errors_total',
            'Total des erreurs agents',
            ['agent']
        )
        
        # Cache Metrics
        self._prometheus_metrics['cache_requests'] = Counter(
            'gnl_cache_requests_total',
            'Total des requêtes cache',
            ['cache', 'hit']
        )
        
        # Ingestion Metrics
        self._prometheus_metrics['ingestion_records'] = Counter(
            'gnl_ingestion_records_total',
            'Total des enregistrements ingérés',
            ['source']
        )
        
        # System Metrics
        self._prometheus_metrics['system_uptime'] = Gauge(
            'gnl_system_uptime_seconds',
            'Temps de fonctionnement du système'
        )
        
        self._prometheus_metrics['system_memory'] = Gauge(
            'gnl_system_memory_bytes',
            'Mémoire utilisée'
        )
        
        self._prometheus_metrics['system_cpu'] = Gauge(
            'gnl_system_cpu_percent',
            'Utilisation CPU'
        )
        
        logger.info("✅ Métriques Prometheus créées")
    
    def export_to_prometheus(self, metrics: Dict) -> bytes:
        """
        Exporte les métriques au format Prometheus
        """
        # Mettre à jour les métriques
        self._update_prometheus_metrics(metrics)
        
        # Générer le format Prometheus
        return generate_latest(REGISTRY)
    
    def _update_prometheus_metrics(self, metrics: Dict):
        """
        Met à jour les métriques Prometheus
        """
        # Mettre à jour les métriques système
        if 'system_uptime' in metrics:
            self._prometheus_metrics['system_uptime'].set(metrics['system_uptime'])
    
    # ============================================================
    # EXPORT JSON
    # ============================================================
    
    def export_to_json(self, metrics: Dict) -> str:
        """
        Exporte les métriques au format JSON
        """
        return json.dumps(metrics, indent=2)
    
    # ============================================================
    # EXPORT INFLUXDB
    # ============================================================
    
    def export_to_influxdb(self, metrics: Dict, measurement: str = "gnl_metrics"):
        """
        Exporte les métriques au format InfluxDB
        """
        lines = []
        timestamp = int(time.time() * 1_000_000_000)
        
        for key, value in metrics.get('gauges', {}).items():
            lines.append(f"{measurement},metric={key} value={value} {timestamp}")
        
        for key, value in metrics.get('counters', {}).items():
            lines.append(f"{measurement}_counter,metric={key} value={value} {timestamp}")
        
        return "\n".join(lines)
    
    # ============================================================
    # HEALTH CHECK
    # ============================================================
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état de l'exporteur
        """
        return {
            "status": "healthy",
            "collector": self.collector.get_metrics_summary(),
            "prometheus_metrics": len(self._prometheus_metrics),
            "enabled": self._enabled
        }

if __name__ == "__main__":
    # Test de l'exporteur
    exporter = MetricsExporter()
    exporter.create_prometheus_metrics()
    
    print("Health:", exporter.health_check())