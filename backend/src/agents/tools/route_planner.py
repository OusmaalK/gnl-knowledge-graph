"""
Outil de planification des routes - Version enrichie
Phase 3 - Routes alternatives et optimisation
"""

from .base import BaseTool
from .graph_tools import GraphTools
from .llm_tools import LLMTools
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RoutePlanner(BaseTool):
    """
    Outil pour planifier et optimiser les routes
    """
    
    def __init__(self):
        super().__init__(name="RoutePlanner")
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
    
    def execute(self, start_id: Optional[str] = None, end_id: Optional[str] = None, 
                blocked_id: Optional[str] = None, **kwargs) -> Dict:
        """
        Planifie une route optimale avec enrichissement
        """
        if not start_id or not end_id:
            return {"error": "start_id et end_id sont requis"}
        
        # Trouver la meilleure route
        main_route = self.graph_tools.get_alternative_route(start_id, end_id)
        
        # Trouver une route alternative si bloquée
        alternate_route = None
        if blocked_id:
            alternate_route = self.graph_tools.get_alternative_route(start_id, end_id, blocked_id)
        
        # Obtenir l'état du réseau
        status = self._get_network_status()
        
        # Construire le contexte pour le LLM
        context = f"""
📍 Départ : {start_id}
📍 Arrivée : {end_id}
🚧 Équipement exclu : {blocked_id if blocked_id else 'Aucun'}

🗺️ Route principale :
   - Distance : {main_route.get('distance', -1)} sauts
   - Chemin : {' → '.join(main_route.get('path', []))}

🔄 Route alternative :
   - Disponible : {alternate_route.get('available', False) if alternate_route else 'Non'}
   - Distance : {alternate_route.get('distance', -1) if alternate_route else 'N/A'}
"""

        # Enrichir avec le LLM
        question = f"""
Analyse les routes disponibles dans le réseau GNL :

{context}

Fournis :
1. Une évaluation de la route principale
2. Les avantages/inconvénients
3. Des recommandations d'optimisation
4. Des alternatives stratégiques
"""
        
        enriched_analysis = self.llm_tools.generate_response(question, context)
        
        return {
            "start": start_id,
            "end": end_id,
            "main_route": {
                "path": main_route.get('path', []),
                "distance": main_route.get('distance', -1),
                "available": main_route.get('distance', -1) != -1
            },
            "alternative_route": {
                "path": alternate_route.get('path', []) if alternate_route else [],
                "distance": alternate_route.get('distance', -1) if alternate_route else -1,
                "available": alternate_route.get('distance', -1) != -1 if alternate_route else False
            } if blocked_id else None,
            "network_status": status,
            "recommendations": self._get_recommendations(main_route, alternate_route),
            "analysis": enriched_analysis
        }
    
    def _get_network_status(self) -> Dict:
        """
        Récupère l'état du réseau
        """
        query = """
        MATCH (p:Pipeline)
        OPTIONAL MATCH (p)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(p)
        RETURN 
            p.id as id,
            p.nom as nom,
            p.statut as statut,
            count(DISTINCT c) as clients,
            count(DISTINCT i) as incidents
        ORDER BY incidents DESC
        """
        results = self.graph_tools.execute_query(query)
        
        status = []
        for item in results:
            status.append({
                "id": item.get('id'),
                "nom": item.get('nom'),
                "statut": item.get('statut', 'inconnu'),
                "clients": item.get('clients', 0),
                "incidents": item.get('incidents', 0)
            })
        
        return {"pipelines": status}
    
    def _get_recommendations(self, main_route: Dict, alternate_route: Optional[Dict]) -> str:
        """
        Génère des recommandations
        """
        recommendations = []
        
        if main_route.get('distance', -1) == -1:
            recommendations.append("❌ Aucune route disponible")
            return "\n".join(recommendations)
        
        main_dist = main_route.get('distance', 0)
        recommendations.append(f"✅ Route principale disponible ({main_dist} sauts)")
        
        if alternate_route:
            alt_dist = alternate_route.get('distance', -1)
            if alternate_route.get('available', False):
                recommendations.append(f"🔄 Route alternative disponible ({alt_dist} sauts)")
                if alt_dist > main_dist:
                    recommendations.append(f"   ⚠️ Alternative plus longue de {alt_dist - main_dist} sauts")
                else:
                    recommendations.append(f"   ✅ Alternative plus courte de {main_dist - alt_dist} sauts")
            else:
                recommendations.append("⚠️ Aucune route alternative disponible")
                recommendations.append("   💡 Recommandation : Planifier une route de secours")
        
        # Ajouter des recommandations stratégiques
        if main_dist > 3:
            recommendations.append("📊 Route longue - Considérer une optimisation")
        
        return "\n".join(recommendations)
    
    def get_description(self) -> str:
        """
        Retourne la description de l'outil
        """
        return """
🗺️ PLANIFICATEUR DE ROUTES

Cet outil planifie des routes optimales dans le réseau GNL.

Paramètres :
- start_id : ID du nœud de départ
- end_id : ID du nœud d'arrivée
- blocked_id : ID d'un équipement à exclure (optionnel)

Résultats :
- Route principale
- Route alternative (si disponible)
- État du réseau
- Recommandations
- Analyse enrichie
"""