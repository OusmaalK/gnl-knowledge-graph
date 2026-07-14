"""
Configuration du logging pour le projet GNL
"""

import logging
import logging.config
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class LoggingConfig:
    """
    Configuration du logging avec structure JSON
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise la configuration
        
        Args:
            config_path: Chemin du fichier de configuration
        """
        self.config_path = config_path or "config/shared/logging.yaml"
        self._configured = False
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configurer les handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure les handlers de logging"""
        # Format JSON pour les logs structurés
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Ajouter les exceptions
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                # Ajouter les attributs supplémentaires
                for key, value in record.__dict__.items():
                    if key not in ['args', 'asctime', 'created', 'exc_info', 
                                   'exc_text', 'filename', 'funcName', 'levelname',
                                   'levelno', 'lineno', 'module', 'msecs', 'msg',
                                   'name', 'pathname', 'process', 'processName',
                                   'relativeCreated', 'stack_info', 'thread', 
                                   'threadName', 'taskName']:
                        log_entry[key] = value
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        # Configuration par défaut
        self.default_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    '()': JsonFormatter
                },
                'console': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'console',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'json',
                    'filename': f"{self.log_dir}/gnl_app.log",
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 10
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'json',
                    'filename': f"{self.log_dir}/gnl_errors.log",
                    'maxBytes': 10485760,
                    'backupCount': 5
                }
            },
            'loggers': {
                'src': {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'src.ingestion': {
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'src.agents': {
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'src.graph': {
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'src.api': {
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file', 'error_file']
            }
        }
    
    def configure(self, config: Optional[Dict] = None):
        """
        Applique la configuration
        """
        if config:
            # Fusionner avec la config par défaut
            merged = self._merge_configs(self.default_config, config)
        else:
            # Charger depuis un fichier
            merged = self._load_from_file()
        
        try:
            logging.config.dictConfig(merged)
            self._configured = True
            logger = logging.getLogger(__name__)
            logger.info("✅ Logging configuré")
        except Exception as e:
            # Fallback à la config de base
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️ Erreur configuration logging: {e}")
    
    def _load_from_file(self) -> Dict:
        """
        Charge la configuration depuis un fichier
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️ Impossible de charger {self.config_path}: {e}")
            return self.default_config
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Fusionne deux configurations
        """
        merged = base.copy()
        
        for key, value in override.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Récupère un logger
        """
        if not self._configured:
            self.configure()
        
        return logging.getLogger(name)
    
    def get_structured_logger(self, name: str) -> 'StructuredLogger':
        """
        Récupère un logger structuré
        """
        return StructuredLogger(self.get_logger(name))

class StructuredLogger:
    """
    Logger avec support pour les logs structurés
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info avec données structurées"""
        extra = kwargs
        self.logger.info(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug avec données structurées"""
        extra = kwargs
        self.logger.debug(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning avec données structurées"""
        extra = kwargs
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error avec données structurées"""
        extra = kwargs
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, **kwargs):
        """Log critical avec données structurées"""
        extra = kwargs
        self.logger.critical(message, extra=extra)
    
    def exception(self, message: str, **kwargs):
        """Log exception avec données structurées"""
        extra = kwargs
        self.logger.exception(message, extra=extra)

# Configuration singleton
_config = None

def get_logger(name: str) -> StructuredLogger:
    """
    Récupère un logger structuré (singleton)
    """
    global _config
    if _config is None:
        _config = LoggingConfig()
        _config.configure()
    
    return _config.get_structured_logger(name)

if __name__ == "__main__":
    # Test de la configuration
    logger = get_logger("test")
    logger.info("Test message", user="admin", action="test", status="ok")
    print("✅ Logging configuré")