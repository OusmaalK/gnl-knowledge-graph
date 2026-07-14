"""
Outil d'analyse des incidents - Version enrichie
Phase 3 - Analyse et diagnostic des incidents
"""

from .base import BaseTool
from .graph_tools import GraphTools
from .llm_tools import LLMTools
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IncidentAnalyzer(BaseTool):
    """
    Outil pour analyser et diagnostiquer les incidents
    """
    
    def __init__(self):
        super().__init__(name="IncidentAnalyzer")
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
    
    def execute(self, incident_id: Optional[str] = None, **kwargs) -> Dict:
        """
        Analyse un incident spécifique avec enrichissement LLM
        """
        if not incident_id:
            return {"error": "incident_id est requis"}
        
        # Récupérer les détails de l'incident
        query = """
        MATCH (i:Incident {id: $incident_id})
        OPTIONAL MATCH (i)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN 
            i.id as id,
            i.description as description,
            i.gravite as gravite,
            i.date as date,
            i.cause as cause,
            i.duree_min as duree,
            e.id as equipment_id,
            e.nom as equipment_name,
            collect(DISTINCT c.nom) as clients
        """
        results = self.graph_tools.execute_query(query, {"incident_id": incident_id})
        
        if not results:
            return {"error": f"Incident {incident_id} non trouvé"}
        
        data = results[0]
        
        # Construire le contexte pour le LLM
        clients = ', '.join(data.get('clients', ['Aucun client']))
        equip_name = data.get('equipment_name', data.get('equipment_id', 'Inconnu'))
        
        context = f"""
🔍 Incident : {data.get('id')}
📋 Description : {data.get('description')}
⚠️ Gravité : {data.get('gravite', 'Inconnue')}
📅 Date : {data.get('date')}
🛠️ Cause : {data.get('cause', 'Inconnue')}
⏱️ Durée : {data.get('duree_min')} minutes
📍 Équipement : {equip_name}
👥 Clients impactés : {clients}
"""

        # Générer un diagnostic enrichi
        diagnostic = self._generate_diagnostic(data)
        recommendations = self._get_recommendations(data.get('cause', ''))
        
        # Enrichir avec le LLM
        question = f"""
Analyse en profondeur cet incident :

{context}

Fournis :
1. Une analyse détaillée des causes
2. L'impact sur le réseau et les clients
3. Des recommandations spécifiques
4. Un plan de prévention
"""
        
        enriched_analysis = self.llm_tools.generate_response(question, context)
        
        return {
            "incident_id": data.get('id'),
            "description": data.get('description'),
            "gravite": data.get('gravite'),
            "date": data.get('date'),
            "cause": data.get('cause'),
            "duree_min": data.get('duree'),
            "equipment_id": data.get('equipment_id'),
            "equipment_name": data.get('equipment_name'),
            "clients_impactes": data.get('clients', []),
            "diagnostic": diagnostic,
            "recommandations": recommendations,
            "analysis": enriched_analysis
        }
    
    def _generate_diagnostic(self, data: Dict) -> str:
        """
        Génère un diagnostic à partir des données
        """
        diagnostic = f"""
🔍 DIAGNOSTIC : {data.get('id')}
⚠️ GRAVITÉ : {data.get('gravite', 'Inconnue').upper()}
🛠️ CAUSE : {data.get('cause', 'Inconnue')}
📍 ÉQUIPEMENT : {data.get('equipment_name', data.get('equipment_id', 'Inconnu'))}
👥 CLIENTS : {', '.join(data.get('clients', ['Aucun']))}
📊 IMPACT : Impact {data.get('gravite', 'inconnu')} sur le réseau
"""
        return diagnostic
    
    def _get_recommendations(self, cause: str) -> str:
        """
        Génère des recommandations basées sur la cause
        """
        cause_lower = cause.lower()
        
        if 'corrosion' in cause_lower:
            return """
🔧 RECOMMANDATIONS (Corrosion) :
1. Inspection détaillée de l'équipement
2. Programme de surveillance de la corrosion
3. Planification du remplacement des sections affectées
4. Traitement anticorrosion supplémentaire
5. Analyse des causes profondes
"""
        elif 'mécanique' in cause_lower or 'panne' in cause_lower:
            return """
🔧 RECOMMANDATIONS (Panne mécanique) :
1. Inspection complète de l'équipement
2. Remplacement des pièces défectueuses
3. Révision du planning de maintenance
4. Test de performance post-réparation
5. Analyse de fiabilité
"""
        else:
            return """
🔧 RECOMMANDATIONS (Cause non identifiée) :
1. Analyse de la cause profonde
2. Investigation technique approfondie
3. Documentation complète de l'incident
4. Mise en place de mesures préventives
5. Revue des procédures
"""
    
    def get_description(self) -> str:
        """
        Retourne la description de l'outil
        """
        return """
🔍 ANALYSE D'INCIDENT

Cet outil analyse un incident spécifique et fournit un diagnostic.

Paramètres :
- incident_id : ID de l'incident (ex: INC-001)

Résultats :
- Description de l'incident
- Gravité
- Cause
- Équipement concerné
- Clients impactés
- Diagnostic complet
- Recommandations
- Analyse enrichie
"""