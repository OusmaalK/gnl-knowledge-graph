"""
Agent de diagnostic des incidents - Version enrichie
"""

from ..base_agent import BaseAgent
import logging

# IMPORTANT : Importation de votre outil LLM
from ..tools.llm_tools import LLMTools 

# --- CORRECTION AJOUTÉE POUR CHARGER LE .ENV ---
from dotenv import load_dotenv
# import os

# Ce chemin remonte jusqu'à la racine du dossier 'backend' pour trouver le .env
# dotenv_path = os.path.join(os.path.dirname(__file__), '../../../../.env')
load_dotenv(override=True)
# ------------------------------------------------

logger = logging.getLogger(__name__)

class DiagnosticAgent(BaseAgent):
    """
    Agent spécialisé dans le diagnostic des incidents
    """
    
    def __init__(self):
        super().__init__(name="DiagnosticAgent")
        # Initialisation de l'outil LLM
        self.llm_tools = LLMTools()
    
    # --- MÉTHODE AJOUTÉE POUR CORRIGER L'ERREUR ---
    def generate_with_llm(self, prompt: str, context: dict = None) -> str:
        """
        Méthode connectant l'agent à l'outil LLM (OpenAI)
        """
        # Conversion du contexte dict en string pour le LLM
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        return self.llm_tools.generate_response(prompt, context_str)
    # -------------------------------------------------

    def execute(self, query: str, params: dict = None) -> str:
        """Exécute le diagnostic"""
        if params and params.get('incident_id'):
            return self.diagnose_incident(params.get('incident_id'))
        return self.analyze_pattern()
    
    def diagnose_incident(self, incident_id: str) -> str:
        """
        Diagnostique un incident spécifique avec enrichissement LLM
        """
        if not incident_id:
            return self.generate_with_llm("Explique-moi les incidents GNL en général.")
        
        query = """
        MATCH (i:Incident {id: $incident_id})
        OPTIONAL MATCH (i)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN 
            i.id as id,
            i.description as description,
            i.gravite as gravite,
            toString(i.date) as date,
            i.cause as cause,
            i.duree_min as duree,
            e.id as equipment_id,
            e.nom as equipment_name,
            collect(DISTINCT c.nom) as clients
        """
        results = self.graph_tools.execute_query(query, {"incident_id": incident_id})
        
        if not results:
            # Incident non trouvé, utiliser LLM pour expliquer
            return self.generate_with_llm(
                f"L'incident {incident_id} n'existe pas dans la base. Que puis-je vous dire sur les incidents GNL en général ?"
            )
        
        data = results[0]
        
        # Construire le contexte enrichi
        equip_name = data.get('equipment_name', data.get('equipment_id', 'Inconnu'))
        clients = ', '.join(data.get('clients', ['Aucun client']))
        
        graph_context = f"""
📋 Incident : {data['id']} - {data['description']}
📍 Équipement : {equip_name}
⚠️ Gravité : {data['gravite']}
🛠️ Cause : {data['cause']}
⏱️ Durée : {data['duree']} minutes
👥 Clients impactés : {clients}
"""
        
        # Utiliser le LLM pour enrichir le diagnostic
        question = f"""
Analyse l'incident suivant et fournis un diagnostic complet :

{graph_context}

Inclus :
1. Un résumé de l'incident
2. L'impact sur le réseau
3. Des recommandations détaillées
4. Des mesures préventives
5. Un plan d'action
"""
        
        # Note : On passe un dictionnaire comme contexte à notre nouvelle méthode
        return self.generate_with_llm(question, {'equipment': data})
    
    def analyze_pattern(self) -> str:
        """
        Analyse les patterns d'incidents avec enrichissement
        """
        incidents = self.graph_tools.get_incident_history()
        
        if not incidents:
            return self.generate_with_llm(
                "Aucun incident détecté. Que me conseillez-vous comme bonnes pratiques pour la gestion des incidents GNL ?"
            )
        
        # Analyse des patterns
        causes = {}
        gravites = {}
        equipments = {}
        
        for inc in incidents:
            cause = inc.get('cause', 'inconnue')
            causes[cause] = causes.get(cause, 0) + 1
            gravite = inc.get('gravite', 'inconnue')
            gravites[gravite] = gravites.get(gravite, 0) + 1
            equip = inc.get('equipment_name', 'inconnu')
            equipments[equip] = equipments.get(equip, 0) + 1
        
        # Construire le contexte pour le LLM
        analysis_context = f"""
📊 Analyse des patterns d'incidents

Total : {len(incidents)} incidents

🔍 Distribution des causes :
"""
        for cause, count in sorted(causes.items(), key=lambda x: -x[1]):
            analysis_context += f"   - {cause} : {count} ({count/len(incidents)*100:.1f}%)\n"
        
        analysis_context += f"\n⚠️ Distribution des gravités :\n"
        for grav, count in sorted(gravites.items(), key=lambda x: -x[1]):
            analysis_context += f"   - {grav} : {count} ({count/len(incidents)*100:.1f}%)\n"
        
        analysis_context += f"\n📍 Équipements les plus touchés :\n"
        for equip, count in sorted(equipments.items(), key=lambda x: -x[1])[:3]:
            analysis_context += f"   - {equip} : {count}\n"
        
        question = f"""
Analyse ces données et fournis une analyse complète des patterns d'incidents :

{analysis_context}

Inclus :
1. Les tendances principales
2. Les points critiques
3. Des recommandations stratégiques
4. Un plan d'amélioration
"""
        
        return self.generate_with_llm(question, {'incidents': incidents})