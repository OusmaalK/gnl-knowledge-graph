"""
Validation des données
"""

import re
from typing import Any, Optional, List, Dict
from datetime import datetime

class Validators:
    """
    Classe de validation pour les données GNL
    """
    
    @staticmethod
    def validate_id(value: str) -> bool:
        """
        Valide un identifiant GNL
        """
        if not value:
            return False
        
        patterns = [
            r'^FOUR-\d{3,4}$',
            r'^TERM-\d{3,4}$',
            r'^PIPE-\d{3,4}$',
            r'^CLIENT-\d{3,4}$',
            r'^COMP-\d{3,4}$',
            r'^STOCK-\d{3,4}$',
            r'^INC-\d{3,4}$',
            r'^CMD-\d{3,4}$',
            r'^METH-\d{3,4}$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valide un email
        """
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """
        Valide une date ISO
        """
        if not date_str:
            return False
        
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    @staticmethod
    def validate_number(value: Any) -> bool:
        """
        Valide un nombre
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_enum(value: str, allowed: List[str]) -> bool:
        """
        Valide une valeur enum
        """
        if not value:
            return False
        return value in allowed
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Valide des coordonnées GPS
        """
        if not Validators.validate_number(lat) or not Validators.validate_number(lon):
            return False
        
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @staticmethod
    def validate_pipeline_data(data: Dict) -> Dict:
        """
        Valide les données d'un pipeline
        """
        errors = []
        
        # Vérifier l'ID
        if not data.get('id'):
            errors.append("ID manquant")
        elif not Validators.validate_id(data['id']):
            errors.append(f"ID invalide: {data['id']}")
        
        # Vérifier le nom
        if not data.get('nom'):
            errors.append("Nom manquant")
        
        # Vérifier la longueur
        if data.get('longueur_km'):
            if not Validators.validate_number(data['longueur_km']):
                errors.append(f"Longueur invalide: {data['longueur_km']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_incident_data(data: Dict) -> Dict:
        """
        Valide les données d'un incident
        """
        errors = []
        
        if not data.get('id'):
            errors.append("ID manquant")
        
        if not data.get('description'):
            errors.append("Description manquante")
        
        if data.get('gravite'):
            allowed = ['critique', 'majeur', 'mineur']
            if not Validators.validate_enum(data['gravite'], allowed):
                errors.append(f"Gravité invalide: {data['gravite']}")
        
        if data.get('date'):
            if not Validators.validate_date(data['date']):
                errors.append(f"Date invalide: {data['date']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

if __name__ == "__main__":
    # Test des validateurs
    print("ID valide:", Validators.validate_id('PIPE-001'))
    print("Email valide:", Validators.validate_email('test@example.com'))
    print("Date valide:", Validators.validate_date('2026-07-10T12:00:00Z'))