"""
Outil d'analyse d'impact - Version enrichie
Phase 3 - Analyse des impacts des pannes
"""

from .base import BaseTool
from .graph_tools import GraphTools
from .llm_tools import LLMTools
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ImpactAnalyzer(BaseTool):
    """
    Outil pour analyser l'impact des pannes d'équipements
    """
    
    def __init__(self):
        super().__init__(name="ImpactAnalyzer")
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
    
    def execute(self, equipment_id: Optional[str] = None, **kwargs) -> Dict:
        """
        Analyse l'impact d'un équipement avec enrichissement LLM
        """
        if not equipment_id:
            return {"error": "equipment_id est requis"}
        
        impact = self.graph_tools.get_impact_analysis(equipment_id)
        
        if not impact:
            return {"error": f"Équipement {equipment_id} non trouvé"}
        
        # Calculer un niveau d'impact
        clients = len(impact.get('clients_impactes', []))
        incidents = impact.get('incidents_count', 0)
        
        niveau = "FAIBLE"
        if incidents > 2 or clients > 3:
            niveau = "CRITIQUE"
        elif incidents > 0 or clients > 1:
            niveau = "MODERE"
        
        # Construire le contexte pour le LLM
        context = f"""
📍 Équipement : {impact.get('equipment_name', equipment_id)}
📋 Type : {impact.get('equipment_type', 'Inconnu')}
📌 Statut : {impact.get('statut', 'Inconnu')}
👥 Clients impactés : {', '.join(impact.get('clients_impactes', ['Aucun']))}
🔧 Dépendances critiques : {', '.join(impact.get('dependances_critiques', ['Aucune']))}
🚨 Incidents : {incidents}
📊 Niveau d'impact : {niveau}
"""

        # Générer des recommandations enrichies
        recommendations = self._get_recommendations(niveau, incidents, clients)
        
        # Enrichir avec le LLM
        question = f"""
Analyse l'impact de cet équipement sur le réseau GNL :

{context}

Fournis :
1. Une évaluation détaillée de l'impact
2. Les risques potentiels
3. Un plan d'action prioritaire
4. Des recommandations stratégiques
"""
        
        enriched_analysis = self.llm_tools.generate_response(question, context)
        
        result = {
            "equipment_id": impact.get('equipment_id'),
            "equipment_name": impact.get('equipment_name'),
            "equipment_type": impact.get('equipment_type'),
            "statut": impact.get('statut', 'Inconnu'),
            "clients_impactes": impact.get('clients_impactes', []),
            "dependances_critiques": impact.get('dependances_critiques', []),
            "incidents_count": incidents,
            "niveau_impact": niveau,
            "recommendations": recommendations,
            "analysis": enriched_analysis
        }
        
        return result
    
    def _get_recommendations(self, niveau: str, incidents: int, clients: int) -> str:
        """
        Génère des recommandations basées sur l'impact
        """
        if niveau == "CRITIQUE":
            return """🔴 ACTION IMMÉDIATE REQUISE
1. Isoler l'équipement
2. Planifier la réparation d'urgence
3. Notifier les clients impactés
4. Mettre en place le plan de continuité
5. Mobiliser l'équipe d'intervention"""
        elif niveau == "MODERE":
            return """🟡 SURVEILLANCE RENFORCÉE
1. Planifier une inspection approfondie
2. Préparer un plan de secours
3. Informer les parties prenantes
4. Renforcer le monitoring"""
        else:
            return """✅ SURVEILLANCE STANDARD
1. Maintenance préventive régulière
2. Surveillance continue
3. Aucune action urgente
4. Planifier la prochaine inspection"""
    
    def get_description(self) -> str:
        """
        Retourne la description de l'outil
        """
        return """
📊 ANALYSE D'IMPACT

Cet outil analyse l'impact d'une panne d'équipement sur le réseau GNL.

Paramètres :
- equipment_id : ID de l'équipement à analyser

Résultats :
- Clients impactés
- Dépendances critiques
- Nombre d'incidents
- Niveau d'impact
- Recommandations
- Analyse enrichie
"""