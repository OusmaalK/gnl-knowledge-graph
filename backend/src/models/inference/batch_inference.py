"""
Inférence par lots pour le traitement de grandes quantités de données
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from tqdm import tqdm
import time
from ..llm.llama import LlamaModel
from ..llm.embedding import EmbeddingModel

logger = logging.getLogger(__name__)

class BatchInference:
    """
    Gestion de l'inférence par lots pour les modèles LLM
    """
    
    def __init__(self, model_name: str = "llama3:70b", batch_size: int = 8):
        """
        Initialise l'inférence par lots
        
        Args:
            model_name: Nom du modèle
            batch_size: Taille du lot
        """
        self.model = LlamaModel(model_name)
        self.batch_size = batch_size
        self.embedding_model = EmbeddingModel()
        logger.info(f"📊 Batch Inference - Modèle: {model_name}, Taille: {batch_size}")
    
    def process(self, items: List[Dict], prompt_template: str, 
                output_key: str = 'output', **kwargs) -> List[Dict]:
        """
        Traite un lot d'éléments
        
        Args:
            items: Liste d'éléments à traiter
            prompt_template: Template du prompt avec {placeholders}
            output_key: Clé pour stocker la réponse
            **kwargs: Paramètres de génération supplémentaires
        """
        if not self.model.is_loaded():
            self.model.load()
        
        logger.info(f"🚀 Traitement de {len(items)} éléments")
        
        results = []
        
        for i in tqdm(range(0, len(items), self.batch_size)):
            batch = items[i:i+self.batch_size]
            batch_results = self._process_batch(batch, prompt_template, output_key, **kwargs)
            results.extend(batch_results)
        
        logger.info(f"✅ Traitement terminé : {len(results)} éléments")
        return results
    
    def _process_batch(self, batch: List[Dict], prompt_template: str, 
                       output_key: str, **kwargs) -> List[Dict]:
        """
        Traite un lot
        """
        prompts = []
        for item in batch:
            try:
                prompt = prompt_template.format(**item)
                prompts.append(prompt)
            except KeyError as e:
                logger.error(f"❌ Clé manquante dans le template : {e}")
                item[output_key] = f"❌ Erreur: {e}"
                continue
        
        if not prompts:
            return batch
        
        responses = self.model.batch_generate(prompts, **kwargs)
        
        for item, response in zip(batch, responses):
            item[output_key] = response
        
        return batch
    
    def classify_batch(self, texts: List[str], labels: List[str]) -> List[Dict]:
        """
        Classification par lots
        """
        prompt_template = """
        Classez le texte suivant dans l'une des catégories suivantes : {labels}
        
        Texte : {text}
        
        Catégorie (uniquement le nom) :
        """
        
        items = [{'text': text, 'labels': ', '.join(labels)} for text in texts]
        results = self.process(items, prompt_template, 'label')
        
        return results
    
    def summarize_batch(self, texts: List[str], max_length: int = 150) -> List[Dict]:
        """
        Résumé par lots
        """
        prompt_template = """
        Résumez le texte suivant en quelques phrases (max {max_length} caractères) :
        
        Texte : {text}
        
        Résumé :
        """
        
        items = [{'text': text, 'max_length': max_length} for text in texts]
        results = self.process(items, prompt_template, 'summary')
        
        return results
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Génère des embeddings par lots
        """
        if not self.embedding_model.is_loaded():
            self.embedding_model.load()
        
        logger.info(f"🔤 Génération d'embeddings pour {len(texts)} textes")
        return self.embedding_model.embed_batch(texts)

if __name__ == "__main__":
    # Test de l'inférence par lots
    inference = BatchInference()
    
    # Test de classification
    texts = [
        "Fuite sur le pipeline Nord-Sud",
        "Maintenance préventive du compresseur",
        "Délai de livraison du GNL"
    ]
    labels = ["incident", "maintenance", "logistique"]
    
    results = inference.classify_batch(texts, labels)
    print(results)