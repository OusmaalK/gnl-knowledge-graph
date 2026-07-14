"""
Handlers personnalisés pour le logging
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading
from collections import deque

class CustomHandler(logging.Handler):
    """
    Handler personnalisé pour les logs structurés
    """
    
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._buffer = deque(maxlen=10000)
        self._lock = threading.Lock()
    
    def emit(self, record):
        """
        Émet un enregistrement de log
        """
        try:
            # Créer une entrée structurée
            log_entry = self._format_record(record)
            
            with self._lock:
                self._buffer.append(log_entry)
                
        except Exception:
            self.handleError(record)
    
    def _format_record(self, record: logging.LogRecord) -> Dict:
        """
        Formate un enregistrement en dictionnaire structuré
        """
        entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread
        }
        
        # Ajouter les attributs supplémentaires
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 
                           'exc_text', 'filename', 'funcName', 'levelname',
                           'levelno', 'lineno', 'module', 'msecs', 'msg',
                           'name', 'pathname', 'process', 'processName',
                           'relativeCreated', 'stack_info', 'thread', 
                           'threadName', 'taskName']:
                entry[key] = value
        
        # Ajouter l'exception si présente
        if record.exc_info:
            entry["exception"] = self.format(record)
        
        return entry
    
    def get_buffer(self) -> list:
        """
        Récupère le buffer de logs
        """
        with self._lock:
            return list(self._buffer)
    
    def clear_buffer(self):
        """
        Vide le buffer
        """
        with self._lock:
            self._buffer.clear()
    
    def get_stats(self) -> Dict:
        """
        Récupère les statistiques du handler
        """
        with self._lock:
            return {
                "buffer_size": len(self._buffer),
                "max_size": self._buffer.maxlen
            }

class BufferHandler(CustomHandler):
    """
    Handler qui maintient un buffer de logs en mémoire
    """
    
    def __init__(self, max_size: int = 10000, level=logging.NOTSET):
        super().__init__(level)
        self._buffer = deque(maxlen=max_size)
    
    def emit(self, record):
        """Ajoute le log au buffer"""
        super().emit(record)
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> list:
        """
        Récupère les logs avec filtrage
        """
        logs = self.get_buffer()
        
        if level:
            logs = [l for l in logs if l.get('level') == level.upper()]
        
        return logs[-limit:]

class FileHandler(logging.FileHandler):
    """
    Handler de fichier avec rotation et formatage JSON
    """
    
    def __init__(self, filename: str, max_bytes: int = 10485760, backup_count: int = 5):
        super().__init__(filename, 'a', 'utf-8')
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._formatter = logging.Formatter('%(message)s')
    
    def emit(self, record):
        """
        Émet un enregistrement au format JSON
        """
        try:
            # Formater en JSON
            log_entry = self._format_record(record)
            json_line = json.dumps(log_entry, ensure_ascii=False) + '\n'
            
            # Écrire dans le fichier
            with open(self.baseFilename, 'a', encoding='utf-8') as f:
                f.write(json_line)
            
            # Vérifier la taille pour rotation
            if os.path.getsize(self.baseFilename) > self.max_bytes:
                self._rotate()
                
        except Exception:
            self.handleError(record)
    
    def _format_record(self, record: logging.LogRecord) -> Dict:
        """Formate un enregistrement"""
        entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        return entry
    
    def _rotate(self):
        """Effectue la rotation du fichier"""
        if os.path.exists(self.baseFilename):
            for i in range(self.backup_count - 1, 0, -1):
                src = f"{self.baseFilename}.{i}"
                dst = f"{self.baseFilename}.{i+1}"
                if os.path.exists(src):
                    os.rename(src, dst)
            os.rename(self.baseFilename, f"{self.baseFilename}.1")