"""
Modèle d'embedding pour le projet GNL
"""

from typing import List, Optional, Union
import logging
import os
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """
    Modèle d'embedding pour la recherche sémantique
    """
    
    def __init__(self, model_name: str = "BGE-M3"):
        """
        Initialise le modèle d'embedding
        
        Args:
            model_name: Nom du modèle d'embedding
        """
        self.model_name = model_name
        self.model = None
        self._is_loaded = False
        logger.info(f"🔤 Modèle d'embedding : {model_name}")
        
        # Map des noms de modèles vers les identifiants
        self.model_map = {
            "BGE-M3": "BAAI/bge-m3",
            "all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
            "all-mpnet-base-v2": "all-mpnet-base-v2",
            "sentence-transformers/all-MiniLM-L6-v2": "all-MiniLM-L6-v2"
        }
    
    def load(self) -> bool:
        """
        Charge le modèle d'embedding
        """
        try:
            model_id = self.model_map.get(self.model_name, self.model_name)
            self.model = SentenceTransformer(model_id)
            self._is_loaded = True
            logger.info(f"✅ Modèle d'embedding chargé : {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur chargement embedding : {e}")
            return False
    
    def embed(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Génère des embeddings pour un ou plusieurs textes
        
        Args:
            text: Texte ou liste de textes
            normalize: Normaliser les vecteurs
            
        Returns:
            Vecteur(s) d'embedding
        """
        if not self._is_loaded:
            if not self.load():
                return np.array([])
        
        try:
            if isinstance(text, str):
                text = [text]
            
            embeddings = self.model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=False
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Erreur generation embedding : {e}")
            return np.array([])
    
    def embed_batch(self, texts: List[str], batch_size: int = 32, normalize: bool = True) -> np.ndarray:
        """
        Génère des embeddings par lots
        """
        if not self._is_loaded:
            if not self.load():
                return np.array([])
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = self.embed(batch, normalize)
            if len(embeddings) > 0:
                all_embeddings.append(embeddings)
        
        if all_embeddings:
            return np.vstack(all_embeddings)
        return np.array([])
    
    def get_embedding_dimension(self) -> int:
        """
        Retourne la dimension des embeddings
        """
        if not self._is_loaded:
            self.load()
        
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 0
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes
        """
        embeddings = self.embed([text1, text2])
        if len(embeddings) == 2:
            from sklearn.metrics.pairwise import cosine_similarity
            sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(sim)
        return 0.0

if __name__ == "__main__":
    # Test du modèle d'embedding
    model = EmbeddingModel()
    if model.load():
        # Tester avec un texte
        text = "Pipeline Nord-Sud, incident de corrosion"
        embedding = model.embed(text)
        print(f"✅ Embedding généré : dimension {len(embedding)}")
        
        # Tester la similarité
        text2 = "Fuite sur le pipeline Nord-Sud"
        sim = model.similarity(text, text2)
        print(f"📊 Similarité : {sim:.4f}")