"""
Décorateurs pour le projet GNL
"""

import time
import functools
import logging
from typing import Any, Callable, Optional
from .helpers import Helpers

logger = logging.getLogger(__name__)

def timeit(func: Callable) -> Callable:
    """
    Décorateur pour mesurer le temps d'exécution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"⏱️ {func.__name__} - {Helpers.format_duration(duration)}")
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Décorateur pour réessayer une fonction
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"⚠️ Tentative {attempt+1}/{max_attempts} échouée: {e}")
                        time.sleep(delay * (attempt + 1))
            logger.error(f"❌ Échec après {max_attempts} tentatives: {last_exception}")
            raise last_exception
        return wrapper
    return decorator

def log_execution(func: Callable) -> Callable:
    """
    Décorateur pour logger l'exécution d'une fonction
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"🚀 Exécution de {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"✅ {func.__name__} terminé")
            return result
        except Exception as e:
            logger.error(f"❌ {func.__name__} - Erreur: {e}")
            raise
    return wrapper

def cache_result(ttl: Optional[int] = None, prefix: str = "cache"):
    """
    Décorateur pour mettre en cache les résultats
    """
    from .context_manager import suppress_exceptions
    
    _cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé
            key_parts = [prefix, func.__name__]
            key_parts.extend([str(a) for a in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            key = "_".join(key_parts)
            
            # Vérifier le cache
            with suppress_exceptions():
                if key in _cache:
                    timestamp, value = _cache[key]
                    if ttl is None or (time.time() - timestamp) < ttl:
                        logger.debug(f"💾 Cache hit: {key}")
                        return value
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Stocker dans le cache
            _cache[key] = (time.time(), result)
            logger.debug(f"💾 Cache miss: {key}")
            
            return result
        return wrapper
    return decorator

def validate_input(validator_func: Callable):
    """
    Décorateur pour valider les entrées
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Appliquer le validateur aux arguments
            for arg in args:
                if not validator_func(arg):
                    raise ValueError(f"Validation échouée pour {arg}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test des décorateurs
    
    @timeit
    @log_execution
    def test_function():
        time.sleep(0.5)
        return "OK"
    
    print(test_function())
    
    @retry(max_attempts=3, delay=0.5, exceptions=(ValueError,))
    def test_retry():
        import random
        if random.random() > 0.5:
            raise ValueError("Test error")
        return "Success"
    
    print(test_retry())