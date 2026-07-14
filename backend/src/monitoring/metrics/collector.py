"""
Collecteur de métriques pour le monitoring du système GNL
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Métrique individuelle"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    type: str = "gauge"  # gauge, counter, histogram

class MetricsCollector:
    """
    Collecteur de métriques pour le système GNL
    """
    
    def __init__(self):
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = time.time()
        logger.info("✅ MetricsCollector initialisé")
    
    # ============================================================
    # COUNTERS
    # ============================================================
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict] = None):
        """
        Incrémente un compteur
        """
        with self._lock:
            key = self._build_key(name, labels)
            self._counters[key] += value
            self._record_metric(name, float(self._counters[key]), labels, "counter")
    
    def get_counter(self, name: str, labels: Optional[Dict] = None) -> int:
        """
        Récupère la valeur d'un compteur
        """
        key = self._build_key(name, labels)
        return self._counters.get(key, 0)
    
    # ============================================================
    # GAUGES
    # ============================================================
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict] = None):
        """
        Définit une jauge
        """
        with self._lock:
            key = self._build_key(name, labels)
            self._gauges[key] = value
            self._record_metric(name, value, labels, "gauge")
    
    def get_gauge(self, name: str, labels: Optional[Dict] = None) -> float:
        """
        Récupère la valeur d'une jauge
        """
        key = self._build_key(name, labels)
        return self._gauges.get(key, 0.0)
    
    # ============================================================
    # HISTOGRAMS
    # ============================================================
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict] = None):
        """
        Enregistre une observation dans un histogramme
        """
        with self._lock:
            key = self._build_key(name, labels)
            self._histograms[key].append(value)
            self._record_metric(name, value, labels, "histogram")
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict] = None) -> Dict:
        """
        Récupère les statistiques d'un histogramme
        """
        key = self._build_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p50": self._percentile(sorted_values, 50),
            "p95": self._percentile(sorted_values, 95),
            "p99": self._percentile(sorted_values, 99)
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calcule un percentile"""
        if not sorted_values:
            return 0
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    # ============================================================
    # MÉTRIQUES SYSTÈME
    # ============================================================
    
    def record_uptime(self):
        """Enregistre le temps de fonctionnement"""
        uptime = time.time() - self._start_time
        self.set_gauge("system_uptime", uptime)
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """
        Enregistre une requête API
        """
        labels = {"endpoint": endpoint, "status": str(status_code)}
        
        # Compter les requêtes
        self.increment_counter("api_requests_total", labels=labels)
        
        # Durée de la requête
        self.observe_histogram("api_request_duration_seconds", duration, labels)
        
        # Compter par statut
        self.increment_counter(f"api_requests_status_{status_code}", labels={"endpoint": endpoint})
    
    def record_graph_query(self, query_type: str, duration: float, records: int):
        """
        Enregistre une requête Neo4j
        """
        labels = {"query_type": query_type}
        
        self.increment_counter("graph_queries_total", labels=labels)
        self.observe_histogram("graph_query_duration_seconds", duration, labels)
        self.set_gauge("graph_query_records", float(records), labels)
    
    def record_agent_usage(self, agent_name: str, duration: float, success: bool):
        """
        Enregistre l'utilisation d'un agent
        """
        labels = {"agent": agent_name, "success": str(success)}
        
        self.increment_counter("agent_calls_total", labels=labels)
        self.observe_histogram("agent_duration_seconds", duration, labels)
        
        if not success:
            self.increment_counter("agent_errors_total", labels={"agent": agent_name})
    
    def record_cache_hit(self, cache_name: str, hit: bool):
        """
        Enregistre un hit/miss de cache
        """
        labels = {"cache": cache_name, "hit": str(hit)}
        self.increment_counter("cache_requests_total", labels=labels)
        
        if hit:
            self.increment_counter("cache_hits_total", labels={"cache": cache_name})
        else:
            self.increment_counter("cache_misses_total", labels={"cache": cache_name})
    
    def record_ingestion(self, source: str, records: int, duration: float):
        """
        Enregistre une ingestion de données
        """
        labels = {"source": source}
        
        self.increment_counter("ingestion_total", value=records, labels=labels)
        self.observe_histogram("ingestion_duration_seconds", duration, labels)
        self.set_gauge("ingestion_records", float(records), labels)
    
    def _build_key(self, name: str, labels: Optional[Dict] = None) -> str:
        """Construit une clé unique pour une métrique avec labels"""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}|{label_str}"
        return name
    
    def _record_metric(self, name: str, value: float, labels: Optional[Dict], metric_type: str):
        """Enregistre une métrique dans l'historique"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            type=metric_type
        )
        self._metrics[name].append(metric)
        
        # Limiter l'historique
        if len(self._metrics[name]) > 10000:
            self._metrics[name] = self._metrics[name][-5000:]
    
    # ============================================================
    # EXPORT
    # ============================================================
    
    def get_all_metrics(self) -> Dict:
        """
        Récupère toutes les métriques
        """
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: self.get_histogram_stats(name) 
                    for name in self._histograms.keys()
                }
            }
    
    def get_metrics_summary(self) -> Dict:
        """
        Récupère un résumé des métriques
        """
        return {
            "counters_count": len(self._counters),
            "gauges_count": len(self._gauges),
            "histograms_count": len(self._histograms),
            "total_metrics": len(self._metrics),
            "uptime": time.time() - self._start_time
        }
    
    def reset(self):
        """Réinitialise toutes les métriques"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._metrics.clear()
            logger.info("🔄 Métriques réinitialisées")

if __name__ == "__main__":
    # Test du collecteur
    collector = MetricsCollector()
    
    # Enregistrer quelques métriques
    collector.increment_counter("test_counter", 5)
    collector.set_gauge("test_gauge", 42.5)
    collector.observe_histogram("test_histogram", 1.2)
    collector.observe_histogram("test_histogram", 2.3)
    collector.observe_histogram("test_histogram", 0.8)
    
    print("Métriques:", collector.get_all_metrics())
    print("Résumé:", collector.get_metrics_summary())