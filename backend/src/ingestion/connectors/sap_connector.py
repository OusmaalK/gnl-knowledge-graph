"""
Connecteur pour les données SAP (ERP)
Récupère les données des fournisseurs, terminaux, pipelines
"""

from typing import Dict, List, Any, Optional
import json
import csv
import os
from datetime import datetime
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)

class SAPConnector(BaseConnector):
    """
    Connecteur pour les données SAP ERP
    """
    
    def __init__(self, data_dir: str = "data/raw/sap"):
        super().__init__(name="SAPConnector")
        self.data_dir = data_dir
        self._data_cache = {}
        logger.info(f"📂 {self.name} - Dossier données : {data_dir}")
    
    def connect(self) -> bool:
        """Établit la connexion à SAP"""
        logger.info(f"🔗 {self.name} - Connexion à SAP")
        
        # Vérifier que le dossier existe
        if not os.path.exists(self.data_dir):
            logger.warning(f"⚠️ Dossier {self.data_dir} inexistant")
            os.makedirs(self.data_dir, exist_ok=True)
        
        self._is_connected = True
        return True
    
    def disconnect(self) -> bool:
        """Ferme la connexion"""
        logger.info(f"🔒 {self.name} - Déconnexion de SAP")
        self._is_connected = False
        return True
    
    def _read_csv(self, filename: str) -> List[Dict]:
        """
        Lit un fichier CSV et retourne les données
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️ Fichier non trouvé : {filepath}")
            return []
        
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            logger.info(f"📥 {filename} : {len(data)} enregistrements")
        except Exception as e:
            logger.error(f"❌ Erreur lecture {filename} : {e}")
        
        return data
    
    def fetch_data(self, **kwargs) -> List[Dict]:
        """
        Récupère les données SAP
        """
        logger.info(f"📥 {self.name} - Récupération des données SAP")
        
        data_type = kwargs.get('data_type', 'all')
        data = []
        
        if data_type in ['all', 'fournisseurs']:
            fournisseurs = self._read_csv('fournisseurs.csv')
            data.extend(fournisseurs)
        
        if data_type in ['all', 'terminaux']:
            terminaux = self._read_csv('terminaux.csv')
            data.extend(terminaux)
        
        if data_type in ['all', 'pipelines']:
            pipelines = self._read_csv('pipelines.csv')
            data.extend(pipelines)
        
        return data
    
    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalise les données SAP selon l'ontologie GNL
        """
        logger.info(f"🔄 {self.name} - Normalisation des données SAP")
        
        normalized = []
        
        for record in raw_data:
            try:
                # Détecter le type de nœud
                if 'fournisseur_id' in record:
                    node_type = 'Fournisseur'
                    properties = {
                        'id': record.get('fournisseur_id'),
                        'nom': record.get('nom'),
                        'pays': record.get('pays'),
                        'ville': record.get('ville'),
                        'adresse': record.get('adresse'),
                        'contact': record.get('contact'),
                        'email': record.get('email'),
                        'statut': record.get('statut', 'actif')
                    }
                    relationships = []
                
                elif 'terminal_id' in record:
                    node_type = 'Terminal'
                    properties = {
                        'id': record.get('terminal_id'),
                        'nom': record.get('nom'),
                        'localisation': record.get('localisation'),
                        'capacite_m3': int(record.get('capacite_m3', 0)),
                        'type': record.get('type', 'LNG'),
                        'statut': record.get('statut', 'actif')
                    }
                    relationships = []
                    
                    # Relation avec le fournisseur exploitant
                    if record.get('exploitant_id'):
                        relationships.append({
                            'type': 'EXPLOITE_PAR',
                            'target': {
                                'type': 'Fournisseur',
                                'id': record.get('exploitant_id')
                            }
                        })
                
                elif 'pipeline_id' in record:
                    node_type = 'Pipeline'
                    properties = {
                        'id': record.get('pipeline_id'),
                        'nom': record.get('nom'),
                        'longueur_km': int(record.get('longueur_km', 0)),
                        'depart': record.get('depart'),
                        'arrivee': record.get('arrivee'),
                        'pression_max_bar': int(record.get('pression_max_bar', 0)),
                        'statut': record.get('statut', 'actif')
                    }
                    relationships = [
                        {
                            'type': 'DEPART_DE',
                            'target': {
                                'type': 'Terminal',
                                'id': record.get('depart')
                            }
                        },
                        {
                            'type': 'ARRIVE_A',
                            'target': {
                                'type': 'Terminal',
                                'id': record.get('arrivee')
                            }
                        }
                    ]
                else:
                    continue
                
                normalized.append({
                    'type': node_type,
                    'properties': properties,
                    'relationships': relationships
                })
                
                self._update_stats(True)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur normalisation SAP : {e}")
                self._update_stats(False)
        
        return normalized

if __name__ == "__main__":
    # Test du connecteur
    connector = SAPConnector()
    data = connector.run(data_type='fournisseurs')
    print(f"✅ {len(data)} enregistrements SAP normalisés")
    if data:
        print("Exemple :", json.dumps(data[0], indent=2))