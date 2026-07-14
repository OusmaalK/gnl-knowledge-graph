"""
Workflow d'analyse des incidents
Phase 3 - Workflow complet pour l'analyse des incidents
"""

from .base import BaseWorkflow
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class IncidentWorkflow(BaseWorkflow):
    """
    Workflow pour l'analyse complète des incidents
    """
    
    def __init__(self):
        super().__init__(name="IncidentWorkflow")
        self._setup_steps()
    
    def _setup_steps(self):
        """Configure les étapes du workflow"""
        self.add_step("identification", "Identification de l'incident")
        self.add_step("diagnostic", "Diagnostic de la cause")
        self.add_step("impact", "Analyse d'impact")
        self.add_step("recommendation", "Recommandations")
        self.add_step("reporting", "Génération du rapport")
    
    def get_steps(self) -> List[str]:
        """Retourne la liste des étapes"""
        return [s['step'] for s in self.steps]
    
    def execute(self, incident_id: str = None, **kwargs) -> str:
        """
        Exécute le workflow d'analyse d'incident
        """
        if not incident_id:
            return "❌ Veuillez spécifier un incident_id"
        
        logger.info(f"🚀 Début du workflow incident pour {incident_id}")
        
        result = []
        
        # Étape 1: Identification
        logger.info("📝 Étape 1: Identification")
        incident_data = self._identify_incident(incident_id)
        if not incident_data:
            return f"❌ Incident {incident_id} non trouvé"
        result.append(f"📋 IDENTIFICATION : {incident_data['id']} - {incident_data['description']}")
        
        # Étape 2: Diagnostic
        logger.info("📝 Étape 2: Diagnostic")
        diagnosis = self._diagnose_incident(incident_data)
        result.append(f"🔍 DIAGNOSTIC : {diagnosis}")
        
        # Étape 3: Impact
        logger.info("📝 Étape 3: Analyse d'impact")
        impact = self._analyze_impact(incident_data)
        result.append(f"📊 IMPACT : {impact}")
        
        # Étape 4: Recommandations
        logger.info("📝 Étape 4: Recommandations")
        recommendations = self._get_recommendations(incident_data)
        result.append(f"💡 RECOMMANDATIONS :\n{recommendations}")
        
        # Étape 5: Rapport
        logger.info("📝 Étape 5: Génération du rapport")
        report = self._generate_report(incident_data, diagnosis, impact, recommendations)
        result.append(report)
        
        # Marquer toutes les étapes comme terminées
        for step in self.steps:
            step['done'] = True
        
        return "\n".join(result)
    
    def _identify_incident(self, incident_id: str) -> Dict:
        """
        Identifie un incident
        """
        query = """
        MATCH (i:Incident {id: $incident_id})
        RETURN 
            i.id as id,
            i.description as description,
            i.gravite as gravite,
            i.date as date,
            i.cause as cause,
            i.duree_min as duree
        """
        results = self.execute_query(query, {"incident_id": incident_id})
        return results[0] if results else {}
    
    def _diagnose_incident(self, incident_data: Dict) -> str:
        """
        Diagnostique un incident
        """
        cause = incident_data.get('cause', 'inconnue')
        gravite = incident_data.get('gravite', 'inconnue')
        
        return f"""
⚠️ Gravité : {gravite.upper()}
🛠️ Cause : {cause}
📅 Date : {incident_data.get('date', 'inconnue')}
⏱️ Durée : {incident_data.get('duree', 0)} minutes
"""
    
    def _analyze_impact(self, incident_data: Dict) -> str:
        """
        Analyse l'impact d'un incident
        """
        query = """
        MATCH (i:Incident {id: $incident_id})
        OPTIONAL MATCH (i)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN 
            e.id as equipment_id,
            e.nom as equipment_name,
            collect(DISTINCT c.nom) as clients_impactes
        """
        results = self.execute_query(query, {"incident_id": incident_data.get('id')})
        
        if not results:
            return "Aucun impact identifié"
        
        data = results[0]
        clients = data.get('clients_impactes', [])
        
        return f"""
📍 ÉQUIPEMENT : {data.get('equipment_name', data.get('equipment_id', 'inconnu'))}
👥 CLIENTS IMPACTÉS : {', '.join(clients) if clients else 'Aucun'}
"""
    
    def _get_recommendations(self, incident_data: Dict) -> str:
        """
        Génère des recommandations
        """
        cause = incident_data.get('cause', '').lower()
        gravite = incident_data.get('gravite', '').lower()
        
        recommendations = []
        
        if gravite == 'critique':
            recommendations.append("🔴 Action immédiate requise")
            recommendations.append("🔴 Isoler l'équipement concerné")
            recommendations.append("🔴 Notification des parties prenantes")
        
        if 'corrosion' in cause:
            recommendations.append("🟡 Inspection détaillée de corrosion")
            recommendations.append("🟡 Programme de surveillance renforcé")
        elif 'mécanique' in cause or 'panne' in cause:
            recommendations.append("🟡 Maintenance préventive planifiée")
            recommendations.append("🟡 Remplacement des pièces défectueuses")
        else:
            recommendations.append("🟡 Analyse approfondie de la cause")
            recommendations.append("🟡 Documenter l'incident pour référence")
        
        recommendations.append("✅ Surveillance continue")
        
        return "\n".join([f"   {r}" for r in recommendations])
    
    def _generate_report(self, incident: Dict, diagnosis: str, impact: str, recommendations: str) -> str:
        """
        Génère un rapport complet
        """
        return f"""
📋 RAPPORT COMPLET
{'='*50}

🚨 INCIDENT : {incident.get('id')}
📌 DESCRIPTION : {incident.get('description')}

{diagnosis}

{impact}

{recommendations}

📅 DATE DU RAPPORT : {incident.get('date', 'N/A')}
✅ ANALYSE COMPLÈTE
"""