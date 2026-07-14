"""
Construction et gestion des datasets pour le fine-tuning
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import random
from pathlib import Path

logger = logging.getLogger(__name__)

class DatasetBuilder:
    """
    Constructeur de datasets pour le fine-tuning
    """
    
    def __init__(self, data_dir: str = "data/fine_tuning"):
        """
        Initialise le constructeur de datasets
        
        Args:
            data_dir: Dossier des données
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Dataset builder - {self.data_dir}")
    
    def load_incidents_data(self) -> List[Dict]:
        """
        Charge les données d'incidents
        """
        # Récupérer les incidents existants
        from src.graph.operations.crud import GraphCRUD
        crud = GraphCRUD()
        incidents = crud.get_nodes_by_label('Incident')
        crud.close()
        return incidents
    
    def create_qa_pairs(self, incidents: List[Dict]) -> List[Dict]:
        """
        Crée des paires Q&A pour le fine-tuning
        """
        qa_pairs = []
        
        templates = [
            {
                'question': "Quel est le problème avec l'incident {id} ?",
                'answer': "L'incident {id} concerne {description}. Gravité : {gravite}."
            },
            {
                'question': "Pourquoi l'incident {id} s'est-il produit ?",
                'answer': "L'incident {id} a été causé par {cause}."
            },
            {
                'question': "Quelle action a été prise pour l'incident {id} ?",
                'answer': "Pour l'incident {id}, l'action suivante a été entreprise : {action}."
            }
        ]
        
        for incident in incidents:
            incident_data = incident.get('n', {})
            for template in templates:
                try:
                    question = template['question'].format(**incident_data)
                    answer = template['answer'].format(**incident_data)
                    qa_pairs.append({
                        'instruction': question,
                        'output': answer,
                        'input': incident_data.get('id', '')
                    })
                except KeyError:
                    continue
        
        return qa_pairs
    
    def create_instruction_dataset(self, data: List[Dict]) -> List[Dict]:
        """
        Crée un dataset au format instruction
        """
        dataset = []
        for item in data:
            dataset.append({
                'instruction': item.get('instruction', ''),
                'input': item.get('input', ''),
                'output': item.get('output', '')
            })
        return dataset
    
    def create_conversation_dataset(self, conversations: List[List[Dict]]) -> List[Dict]:
        """
        Crée un dataset de conversations
        """
        dataset = []
        for conv in conversations:
            formatted = []
            for turn in conv:
                role = turn.get('role', 'user')
                content = turn.get('content', '')
                formatted.append(f"<|{role}|>\n{content}")
            dataset.append({
                'conversation': '\n'.join(formatted)
            })
        return dataset
    
    def save_dataset(self, dataset: List[Dict], filename: str = "dataset.jsonl"):
        """
        Sauvegarde le dataset en format JSONL
        """
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        logger.info(f"✅ Dataset sauvegardé : {filepath} ({len(dataset)} entrées)")
        return str(filepath)
    
    def load_dataset(self, filename: str = "dataset.jsonl") -> List[Dict]:
        """
        Charge un dataset JSONL
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"⚠️ Fichier non trouvé : {filepath}")
            return []
        
        dataset = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        dataset.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return dataset
    
    def split_dataset(self, dataset: List[Dict], train_ratio: float = 0.8) -> Tuple[List[Dict], List[Dict]]:
        """
        Divise le dataset en train/test
        """
        random.shuffle(dataset)
        split_idx = int(len(dataset) * train_ratio)
        return dataset[:split_idx], dataset[split_idx:]

if __name__ == "__main__":
    # Test du constructeur
    builder = DatasetBuilder()
    
    # Créer des données d'exemple
    sample_data = [
        {'instruction': 'Diagnostiquer l\'incident', 'output': 'Incident de corrosion'},
        {'instruction': 'Analyser le pipeline', 'output': 'Pipeline actif'}
    ]
    
    builder.save_dataset(sample_data, 'test_dataset.jsonl')
    loaded = builder.load_dataset('test_dataset.jsonl')
    print(f"✅ Dataset chargé : {len(loaded)} entrées")