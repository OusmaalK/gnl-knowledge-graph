from langgraph.graph import StateGraph, END
from typing import Dict, List, Any
import json
import os

class RelationExtractor:
    """
    Extrait les relations entre entités à partir de textes non structurés
    en utilisant un LLM via LangGraph.
    """
    
    def __init__(self, model_name: str = "llama3:70b"):
        self.model_name = model_name
        self.llm = None
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Construit le graphe d'extraction avec LangGraph"""
        builder = StateGraph(dict)
        
        def extract_entities(state: Dict) -> Dict:
            """Extrait les entités du domaine GNL"""
            text = state.get("text", "")
            # Prompt d'extraction des entités
            prompt = f"""
            Extrait les entités du domaine GNL mentionnées dans ce texte.
            Entités possibles : Pipeline, Terminal, Fournisseur, Client, Incident, Compresseur.
            
            Texte : {text}
            
            Retourne une liste JSON : {{"entities": [{{"type": "...", "name": "...", "id": "..."}}]}}
            """
            # Simuler une extraction (à remplacer par l'appel réel au LLM)
            entities = [
                {"type": "Pipeline", "name": "Nord-Sud", "id": "PIPE-001"},
                {"type": "Incident", "name": "Fuite", "id": "INC-001"}
            ]
            state["entities"] = entities
            return state
        
        def extract_relationships(state: Dict) -> Dict:
            """Extrait les relations entre les entités"""
            text = state.get("text", "")
            entities = state.get("entities", [])
            
            # Simuler l'extraction des relations
            relationships = [
                {"source": "PIPE-001", "target": "INC-001", "type": "CONCERNE"}
            ]
            state["relationships"] = relationships
            return state
        
        builder.add_node("extract_entities", extract_entities)
        builder.add_node("extract_relationships", extract_relationships)
        builder.add_edge("extract_entities", "extract_relationships")
        builder.set_entry_point("extract_entities")
        builder.add_edge("extract_relationships", END)
        
        return builder.compile()
    
    def process(self, text: str) -> Dict:
        """Traite un texte et retourne les entités et relations extraites"""
        result = self.graph.invoke({"text": text})
        return {
            "entities": result.get("entities", []),
            "relationships": result.get("relationships", [])
        }

if __name__ == "__main__":
    # Test de l'extracteur
    extractor = RelationExtractor()
    text = "Le pipeline Nord-Sud a subi une fuite importante le 08/07/2026."
    result = extractor.process(text)
    print("Entités extraites :", result["entities"])
    print("Relations extraites :", result["relationships"])