"""
Agent spécialisé dans la maintenance - Version enrichie et connectée
"""

from ..base_agent import BaseAgent
import logging

# IMPORTANT : Importez votre outil LLM ici
from ..tools.llm_tools import LLMTools 

logger = logging.getLogger(__name__)

class MaintenanceAgent(BaseAgent):
    """
    Agent pour la maintenance prédictive
    """
    
    def __init__(self):
        super().__init__(name="MaintenanceAgent")
        self.llm_tools = LLMTools()
    
    def generate_with_llm(self, prompt: str, context: dict = None) -> str:
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        return self.llm_tools.generate_response(prompt, context_str)

    def execute(self, query: str, params: dict = None) -> str:
        """
        Point d'entrée de l'agent. 
        Analyse la demande et oriente vers la méthode appropriée.
        """
        # 1. Analyse globale du réseau (via l'IA)
        if params and params.get('equipment') and params.get('riskData'):
            return self.analyze_global_network(params.get('equipment'), params.get('riskData'))
            
        # 2. Génération d'un plan de maintenance pour un équipement spécifique
        if params and params.get('action') == 'plan':
            return self.plan_maintenance(params.get('equipment_id'))
            
        # 3. Analyse de risque standard (si ID fourni)
        if params and params.get('equipment_id'):
            return self.analyze_risk(params.get('equipment_id'))
            
        return self.general_analysis()

    def analyze_global_network(self, equipment_list, risk_data) -> str:
        """
        Génère un résumé stratégique de l'état de santé du réseau.
        """
        # Construire un résumé textuel des données pour le LLM
        context_summary = f"""
📊 ÉTAT GLOBAL DU RÉSEAU :
   - Équipements critiques : {risk_data.get('critical', 0)}
   - Risques élevés : {risk_data.get('high', 0)}
   - Maintenances planifiées : {risk_data.get('planned', 0)}
   - Temps moyen de résolution : {risk_data.get('avgResolution', 'N/A')}
   
📋 LISTE DES ÉQUIPEMENTS PRINCIPAUX :
"""
        for eq in equipment_list:
            context_summary += f"   - {eq.get('id')} ({eq.get('nom')}) : Risque {eq.get('risk_level')}, Incidents: {eq.get('incidents')}\n"

        question = f"""
Analyse l'état de santé global du réseau GNL en te basant sur ces données :

{context_summary}

Fournis un rapport stratégique concis incluant :
1. Une évaluation générale de la santé du réseau.
2. Les 2 principaux points de vigilance.
3. Une recommandation stratégique prioritaire pour les 7 prochains jours.
"""
        return self.generate_with_llm(question, {'context': context_summary})

    def analyze_risk(self, equipment_id: str) -> str:
        if not equipment_id:
            return self.generate_with_llm("Explique-moi les facteurs de risque dans un réseau GNL.")
        
        risk = self.graph_tools.get_risk_score(equipment_id)
        
        if not risk:
            return self.generate_with_llm(f"Équipement {equipment_id} non trouvé.")
        
        graph_context = f"""
📍 Équipement : {risk.get('equipment_name', equipment_id)}
📈 Score : {risk.get('score', 0)}/100
⚠️ Niveau : {risk.get('niveau', 'N/A')}
🚨 Incidents : {risk.get('incidents_count', 0)}
👥 Clients : {risk.get('clients_count', 0)}
"""
        question = f"""
Analyse le risque de l'équipement suivant :

{graph_context}

Fournis :
1. Une évaluation détaillée du risque.
2. Les facteurs de risque identifiés.
3. Un plan d'action prioritaire.
"""
        return self.generate_with_llm(question, {'risk': risk})
    
    def plan_maintenance(self, equipment_id: str) -> str:
        if not equipment_id:
            return self.generate_with_llm("Explique-moi comment planifier une maintenance préventive pour un réseau GNL.")
        
        info = self.graph_tools.get_equipment_info(equipment_id)
        risk = self.graph_tools.get_risk_score(equipment_id)
        
        if not info:
            return self.generate_with_llm(f"Équipement {equipment_id} non trouvé.")
        
        # Calcul du niveau de risque pour le prompt
        niveau_risque = risk.get('niveau', 'FAIBLE') if risk else 'FAIBLE'
        incidents_count = info.get('nombre_incidents', 0)
        
        graph_context = f"""
📍 Équipement : {info.get('nom', equipment_id)}
📋 Type : {info.get('type', 'N/A')}
📌 Statut : {info.get('statut', 'N/A')}
⚠️ Niveau de risque : {niveau_risque}
🚨 Nombre d'incidents récents : {incidents_count}
"""
        question = f"""
Élabore un plan de maintenance détaillé et professionnel pour l'équipement suivant :

{graph_context}

Inclus impérativement :
1. Une liste de 5 tâches de maintenance spécifiques avec leur priorité (Haute, Moyenne, Basse).
2. Un planning recommandé (fréquence : Mensuelle, Trimestrielle, etc.).
3. Une durée estimée pour l'intervention.
4. Des mesures préventives à appliquer.
"""
        return self.generate_with_llm(question, {'equipment': info, 'risk': risk})
    
    def general_analysis(self) -> str:
        stats = self.graph_tools.get_statistics()
        graph_context = f"""
📊 Statistiques globales du réseau :
   - Pipelines : {stats.get('total_pipelines', 0)}
   - Clients : {stats.get('total_clients', 0)}
   - Incidents : {stats.get('total_incidents', 0)}
"""
        question = f"""
Analyse l'état général de la maintenance du réseau GNL :

{graph_context}

Donne un bref résumé des actions recommandées.
"""
        return self.generate_with_llm(question, {'statistics': stats})