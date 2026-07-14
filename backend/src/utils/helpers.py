"""
Fonctions helpers pour le projet
"""

import json
import hashlib
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import re

class Helpers:
    """
    Fonctions helper pour le projet GNL
    """
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Dict]:
        """
        Charge un fichier JSON
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur chargement JSON {filepath}: {e}")
            return None
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2):
        """
        Sauvegarde des données en JSON
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def hash_string(text: str) -> str:
        """
        Génère un hash d'une chaîne
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Nettoie un texte
        """
        if not text:
            return ''
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Supprimer les caractères spéciaux
        text = re.sub(r'[^\w\s\-:.,;!?()\'"@/]', '', text)
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 200) -> str:
        """
        Tronque un texte
        """
        if not text:
            return ''
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Récupère le timestamp actuel
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Formate une durée en secondes
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.0f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Divise une liste en chunks
        """
        return [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
    
    @staticmethod
    def get_env(key: str, default: Optional[Any] = None) -> Any:
        """
        Récupère une variable d'environnement
        """
        return os.getenv(key, default)
    
    @staticmethod
    def to_camel_case(text: str) -> str:
        """
        Convertit un texte en camelCase
        """
        if not text:
            return ''
        parts = text.split('_')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        """
        Convertit un texte en snake_case
        """
        if not text:
            return ''
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
        return text.lower()

if __name__ == "__main__":
    # Test des helpers
    print("Clean:", Helpers.clean_text("  Hello   World!  "))
    print("Truncate:", Helpers.truncate_text("Very long text" * 10, 50))
    print("Duration:", Helpers.format_duration(125))