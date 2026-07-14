"""
Agent spécialisé dans l'analyse des incidents
Phase 3 - Gestion des incidents
"""

from ..base_agent import BaseAgent
import logging

# IMPORTANT : Importez votre outil LLM ici
from ..tools.llm_tools import LLMTools

logger = logging.getLogger(__name__)

class IncidentAgent(BaseAgent):
    """
    Agent pour l'analyse des incidents
    """
    
    def __init__(self):
        super().__init__(name="IncidentAgent")
        # Initialisation de l'outil LLM
        self.llm_tools = LLMTools()
    
    # --- MÉTHODE AJOUTÉE POUR CORRIGER L'ERREUR ---
    def generate_with_llm(self, prompt: str, context: dict = None) -> str:
        """
        Méthode connectant l'agent à l'outil LLM (Groq/OpenAI)
        """
        # Conversion du contexte dict en string pour le LLM
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        return self.llm_tools.generate_response(prompt, context_str)
    # -------------------------------------------------

    def execute(self, query: str, params: dict = None) -> str:
        """Exécute l'analyse"""
        # On vérifie si equipment_id est passé dans params
        equipment_id = params.get('equipment_id') if params else None
        return self.list_incidents(equipment_id)
    
    def list_incidents(self, equipment_id: str = None) -> str:
        """
        Liste les incidents et génère une analyse enrichie
        """
        # Récupération des incidents via GraphTools
        incidents = self.graph_tools.get_incident_history(equipment_id)
        
        if not incidents:
            # Si aucun incident, on demande quand même une analyse préventive au LLM
            return self.generate_with_llm(
                f"Le réseau GNL est actuellement sain (0 incident pour l'équipement {equipment_id if equipment_id else 'global'}). " 
                "Que me conseillez-vous comme recommandations préventives ?"
            )
        
        # Préparer un résumé structuré pour le LLM
        summary = f"""
📋 LISTE DES INCIDENTS
{'='*50}

Total : {len(incidents)} incidents
"""
        # On liste les 10 premiers pour ne pas surcharger le contexte du LLM
        for inc in incidents[:10]:
            summary += f"""
🚨 {inc.get('id', 'Inconnu')} - {inc.get('description', 'Non définie')}
   📅 Date : {inc.get('date', 'Non renseignée')}
   ⚠️ Gravité : {inc.get('gravite', 'Inconnue')}
   🛠️ Cause : {inc.get('cause', 'Inconnue')}
   📍 Équipement : {inc.get('equipment_name', 'Inconnu')}
"""
        
        # Formuler la question pour le LLM
        question = f"""
Voici la liste des incidents du réseau GNL :

{summary}

Analyse ces incidents et fournis :
1. **Un résumé global** de la situation.
2. **Les points critiques** (les incidents les plus graves ou les causes récurrentes).
3. **Des recommandations opérationnelles** pour prévenir de futurs incidents similaires.
4. **Un plan d'action** priorisé pour les prochaines 24 heures.
"""
        
        # Retourner la réponse enrichie par le LLM
        return self.generate_with_llm(question, {'incidents_summary': summary})