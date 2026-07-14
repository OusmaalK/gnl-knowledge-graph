"""
Extracteur de liens entre entités (LLM-based)
"""

import logging
import json
from typing import List, Dict, Any, Optional
from ...models.llm.llama import LlamaModel

logger = logging.getLogger(__name__)

class LinkExtractor:
    """
    Extracteur de liens utilisant un LLM
    """
    
    def __init__(self, model_name: str = "llama3:70b"):
        self.model = LlamaModel(model_name)
        self._loaded = False
        logger.info(f"✅ LinkExtractor initialisé (modèle: {model_name})")
    
    def load(self):
        """Charge le modèle"""
        if not self._loaded:
            self._loaded = self.model.load()
            if self._loaded:
                logger.info("✅ Modèle chargé")
    
    def extract(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extrait les liens entre entités
        """
        self.load()
        
        if not self._loaded:
            logger.warning("⚠️ Modèle non disponible, extraction pattern")
            return self._extract_pattern(text, entities)
        
        # Préparer le prompt
        entity_list = "\n".join([f"- {e['id']} ({e['type']})" for e in entities])
        
        prompt = f"""
        Analyse le texte suivant et identifie les relations entre les entités GNL.
        
        Entités identifiées :
        {entity_list}
        
        Texte :
        {text}
        
        Relations possibles : AFFECTE, CAUSE, DEPEND_DE, ALIMENTE, DESSERT, FOURNIT, STOCKE
        
        Retourne une liste JSON des relations trouvées au format :
        [{{"source": "id_source", "target": "id_cible", "type": "TYPE_RELATION", "confidence": 0.9}}]
        """
        
        try:
            response = self.model.generate(prompt, max_tokens=500)
            
            # Essayer d'extraire le JSON
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                relations = json.loads(json_match.group())
                return relations
            else:
                logger.warning("⚠️ Aucun JSON trouvé dans la réponse")
                return self._extract_pattern(text, entities)
                
        except Exception as e:
            logger.error(f"❌ Erreur extraction: {e}")
            return self._extract_pattern(text, entities)
    
    def _extract_pattern(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extraction par patterns (fallback)
        """
        from .relation_extractor import RelationExtractor
        extractor = RelationExtractor()
        return extractor.extract(text, entities)
    
    def extract_batch(self, texts: List[str], entities_list: List[List[Dict]]) -> List[List[Dict]]:
        """
        Extrait les liens de plusieurs textes
        """
        results = []
        for text, entities in zip(texts, entities_list):
            results.append(self.extract(text, entities))
        return results

if __name__ == "__main__":
    # Test de l'extracteur
    extractor = LinkExtractor()
    
    text = "L'incident INC-001 affecte le pipeline PIPE-001."
    entities = [
        {'type': 'incident', 'id': 'INC-001'},
        {'type': 'pipeline', 'id': 'PIPE-001'}
    ]
    
    relations = extractor.extract(text, entities)
    print("Relations extraites:", relations)