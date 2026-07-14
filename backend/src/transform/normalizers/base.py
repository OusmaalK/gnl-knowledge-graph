"""
Normalisateur de base pour les données GNL
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class BaseNormalizer(ABC):
    """
    Classe abstraite de base pour tous les normalisateurs
    """
    
    def __init__(self, name: str = "BaseNormalizer"):
        self.name = name
        self._stats = {
            'processed': 0,
            'errors': 0,
            'warnings': 0
        }
        logger.info(f"🔧 {self.name} initialisé")
    
    @abstractmethod
    def normalize(self, data: List[Dict]) -> List[Dict]:
        """
        Normalise les données
        """
        pass
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalise une date au format ISO
        """
        if not date_str:
            return None
        
        try:
            # Essayer différents formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y%m%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat() + 'Z'
                except ValueError:
                    continue
            
            logger.warning(f"⚠️ Format de date non reconnu: {date_str}")
            return date_str
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur normalisation date: {e}")
            return date_str
    
    def _normalize_string(self, value: str) -> str:
        """
        Normalise une chaîne de caractères
        """
        if not value:
            return ''
        
        # Supprimer les espaces multiples
        value = re.sub(r'\s+', ' ', value.strip())
        
        # Capitaliser
        return value
    
    def _normalize_id(self, value: str) -> str:
        """
        Normalise un identifiant
        """
        if not value:
            return ''
        
        # Mettre en majuscules
        value = value.upper().strip()
        
        # Remplacer les espaces par des underscores
        value = re.sub(r'\s+', '_', value)
        
        # Supprimer les caractères spéciaux
        value = re.sub(r'[^A-Z0-9_-]', '', value)
        
        return value
    
    def _normalize_number(self, value: Any) -> Optional[float]:
        """
        Normalise un nombre
        """
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            # Supprimer les espaces et caractères
            cleaned = re.sub(r'[^\d.,-]', '', str(value))
            cleaned = cleaned.replace(',', '.')
            
            return float(cleaned)
            
        except (ValueError, TypeError):
            return None
    
    def _normalize_boolean(self, value: Any) -> Optional[bool]:
        """
        Normalise un booléen
        """
        if value is None:
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        if isinstance(value, str):
            true_values = ['true', '1', 'yes', 'oui', 'vrai', 'actif']
            false_values = ['false', '0', 'no', 'non', 'faux', 'inactif']
            
            value_lower = value.lower().strip()
            if value_lower in true_values:
                return True
            if value_lower in false_values:
                return False
        
        return None
    
    def _normalize_enum(self, value: str, allowed: List[str]) -> str:
        """
        Normalise une valeur enum
        """
        if not value:
            return allowed[0] if allowed else ''
        
        value_lower = value.lower().strip()
        
        for allowed_value in allowed:
            if allowed_value.lower() == value_lower:
                return allowed_value
        
        return allowed[0] if allowed else value
    
    def _get_stats(self) -> Dict:
        """Récupère les statistiques"""
        return self._stats
    
    def _reset_stats(self):
        """Réinitialise les statistiques"""
        self._stats = {'processed': 0, 'errors': 0, 'warnings': 0}
    
    def _increment_processed(self):
        self._stats['processed'] += 1
    
    def _increment_error(self):
        self._stats['errors'] += 1
    
    def _increment_warning(self):
        self._stats['warnings'] += 1