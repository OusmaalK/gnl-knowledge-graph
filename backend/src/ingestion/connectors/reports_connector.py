"""
Connecteur pour les rapports d'incidents
Récupère les rapports depuis des fichiers JSON/PDF
"""

from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class ReportsConnector(BaseConnector):
    """
    Connecteur pour les rapports d'incidents et maintenance
    """
    
    def __init__(self, reports_dir: str = "data/raw/reports"):
        super().__init__(name="ReportsConnector")
        self.reports_dir = reports_dir
        self._reports_cache = []
        logger.info(f"📂 {self.name} - Dossier rapports : {reports_dir}")
    
    def connect(self) -> bool:
        """Établit la connexion au système de rapports"""
        logger.info(f"🔗 {self.name} - Connexion au système de rapports")
        
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, exist_ok=True)
        
        self._is_connected = True
        return True
    
    def disconnect(self) -> bool:
        """Ferme la connexion"""
        logger.info(f"🔒 {self.name} - Déconnexion du système de rapports")
        self._is_connected = False
        return True
    
    def _read_json_file(self, filename: str) -> List[Dict]:
        """
        Lit un fichier JSON
        """
        filepath = os.path.join(self.reports_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️ Fichier non trouvé : {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get('items', data.get('incidents', []))
        except Exception as e:
            logger.error(f"❌ Erreur lecture {filename} : {e}")
        
        return []
    
    def fetch_data(self, **kwargs) -> List[Dict]:
        """
        Récupère les rapports
        """
        logger.info(f"📥 {self.name} - Récupération des rapports")
        
        reports = []
        
        # Lire les fichiers JSON
        json_files = [f for f in os.listdir(self.reports_dir) if f.endswith('.json')]
        for filename in json_files:
            data = self._read_json_file(filename)
            reports.extend(data)
        
        self._reports_cache = reports
        return reports
    
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les rapports selon l'ontologie GNL
        """
        logger.info(f"🔄 {self.name} - Normalisation des rapports")
        
        normalized = []
        
        for record in raw_data:
            try:
                # Détection du type de rapport
                if 'incident_id' in record:
                    node_type = 'Incident'
                    properties = {
                        'id': record.get('incident_id'),
                        'description': record.get('description'),
                        'gravite': record.get('gravite', 'mineur'),
                        'date': record.get('date', datetime.now().isoformat()),
                        'cause': record.get('cause', 'inconnue'),
                        'action': record.get('action', ''),
                        'duree_min': record.get('duree_min', 0),
                        'status': record.get('status', 'ouvert')
                    }
                    relationships = []
                    
                    if record.get('equipement_id'):
                        relationships.append({
                            'type': 'AFFECTE',
                            'target': {
                                'type': 'Equipement',
                                'id': record.get('equipement_id')
                            }
                        })
                    
                    normalized.append({
                        'type': node_type,
                        'properties': properties,
                        'relationships': relationships
                    })
                    self._update_stats(True)
                
                elif 'maintenance_id' in record:
                    node_type = 'Maintenance'
                    properties = {
                        'id': record.get('maintenance_id'),
                        'description': record.get('description'),
                        'type': record.get('type', 'preventive'),
                        'date_prevue': record.get('date_prevue'),
                        'date_realisee': record.get('date_realisee'),
                        'statut': record.get('statut', 'planifiee')
                    }
                    normalized.append({
                        'type': node_type,
                        'properties': properties,
                        'relationships': []
                    })
                    self._update_stats(True)
                
                else:
                    logger.warning(f"⚠️ Type de rapport inconnu")
                    self._update_stats(False)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation rapport : {e}")
                self._update_stats(False)
        
        return normalized

if __name__ == "__main__":
    # Test du connecteur
    connector = ReportsConnector()
    data = connector.run()
    print(f"✅ {len(data)} rapports normalisés")
    if data:
        print("Exemple :", json.dumps(data[0], indent=2))