"""
Gestionnaires de contexte pour le projet GNL
"""

import time
import logging
import sys
from contextlib import contextmanager
from typing import Any, Generator, Optional, Callable

logger = logging.getLogger(__name__)

class Timer:
    """
    Gestionnaire de contexte pour mesurer le temps
    """
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start = None
        self.end = None
    
    def __enter__(self):
        self.start = time.time()
        logger.info(f"⏱️ Début: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        duration = self.end - self.start
        if duration < 60:
            logger.info(f"⏱️ Fin: {self.name} - {duration:.2f}s")
        else:
            minutes = duration / 60
            logger.info(f"⏱️ Fin: {self.name} - {minutes:.2f}m")
    
    def elapsed(self) -> float:
        """Retourne le temps écoulé"""
        if self.start is None:
            return 0
        return time.time() - self.start

@contextmanager
def suppress_exceptions(raise_on_error: bool = False, default_return: Any = None):
    """
    Gestionnaire de contexte pour supprimer les exceptions
    """
    try:
        yield
    except Exception as e:
        logger.warning(f"⚠️ Exception supprimée: {e}")
        if raise_on_error:
            raise
        return default_return

@contextmanager
def safe_execute(operation: str = "Operation"):
    """
    Gestionnaire de contexte pour exécution sécurisée
    """
    try:
        yield
    except Exception as e:
        logger.error(f"❌ Erreur lors de {operation}: {e}")
        raise

@contextmanager
def change_log_level(level: int):
    """
    Gestionnaire de contexte pour changer temporairement le niveau de log
    """
    root_logger = logging.getLogger()
    old_level = root_logger.level
    root_logger.setLevel(level)
    try:
        yield
    finally:
        root_logger.setLevel(old_level)

@contextmanager
def temporary_env(var_name: str, value: str):
    """
    Gestionnaire de contexte pour modifier temporairement une variable d'environnement
    """
    import os
    old_value = os.environ.get(var_name)
    os.environ[var_name] = value
    try:
        yield
    finally:
        if old_value is None:
            del os.environ[var_name]
        else:
            os.environ[var_name] = old_value

class ConnectionPool:
    """
    Gestionnaire de pool de connexions
    """
    
    def __init__(self, max_size: int = 10, timeout: float = 30.0):
        self.max_size = max_size
        self.timeout = timeout
        self._pool = []
        self._in_use = []
    
    def acquire(self) -> Any:
        """Acquiert une connexion du pool"""
        import threading
        start = time.time()
        
        while True:
            # Vérifier les connexions disponibles
            if self._pool:
                conn = self._pool.pop()
                self._in_use.append(conn)
                return conn
            
            # Vérifier si on peut créer une nouvelle connexion
            if len(self._in_use) < self.max_size:
                conn = self._create_connection()
                self._in_use.append(conn)
                return conn
            
            # Attendre
            if time.time() - start > self.timeout:
                raise TimeoutError("Pool de connexions saturé")
            
            time.sleep(0.1)
    
    def release(self, conn: Any):
        """Libère une connexion dans le pool"""
        if conn in self._in_use:
            self._in_use.remove(conn)
            self._pool.append(conn)
    
    def _create_connection(self) -> Any:
        """Crée une nouvelle connexion"""
        # À implémenter par les classes filles
        return object()

class BatchProcessor:
    """
    Gestionnaire de traitement par lots
    """
    
    def __init__(self, process_func: Callable, batch_size: int = 100):
        self.process_func = process_func
        self.batch_size = batch_size
        self._batch = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._batch:
            self.flush()
    
    def add(self, item: Any):
        """Ajoute un élément au lot"""
        self._batch.append(item)
        if len(self._batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Traite le lot actuel"""
        if not self._batch:
            return
        
        batch = self._batch
        self._batch = []
        return self.process_func(batch)

if __name__ == "__main__":
    # Test des context managers
    
    with Timer("Test"):
        time.sleep(0.1)
    
    with suppress_exceptions():
        raise ValueError("Test error")
    
    with change_log_level(logging.WARNING):
        logger.info("Ceci ne devrait pas apparaître")