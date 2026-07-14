"""
Workflow de maintenance prédictive
Phase 3 - Workflow complet pour la maintenance
"""

from .base import BaseWorkflow
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class MaintenanceWorkflow(BaseWorkflow):
    """
    Workflow pour la maintenance prédictive et la gestion des risques
    """
    
    def __init__(self):
        super().__init__(name="MaintenanceWorkflow")
        self._setup_steps()
    
    def _setup_steps(self):
        """Configure les étapes du workflow"""
        self.add_step("risk_assessment", "Évaluation du risque")
        self.add_step("history_analysis", "Analyse de l'historique")
        self.add_step("critical_check", "Vérification de criticité")
        self.add_step("maintenance_plan", "Plan de maintenance")
        self.add_step("schedule", "Planification")
    
    def get_steps(self) -> List[str]:
        """Retourne la liste des étapes"""
        return [s['step'] for s in self.steps]
    
    def execute(self, equipment_id: str = None, **kwargs) -> str:
        """
        Exécute le workflow de maintenance
        """
        if not equipment_id:
            return "❌ Veuillez spécifier un equipment_id"
        
        logger.info(f"🚀 Début du workflow maintenance pour {equipment_id}")
        
        result = []
        
        # Étape 1: Évaluation du risque
        logger.info("📝 Étape 1: Évaluation du risque")
        risk = self._assess_risk(equipment_id)
        result.append(f"📊 ÉVALUATION DU RISQUE :\n{risk}")
        
        # Étape 2: Analyse de l'historique
        logger.info("📝 Étape 2: Analyse de l'historique")
        history = self._analyze_history(equipment_id)
        result.append(f"📋 HISTORIQUE :\n{history}")
        
        # Étape 3: Vérification de criticité
        logger.info("📝 Étape 3: Vérification de criticité")
        critical = self._check_criticality(equipment_id)
        result.append(f"⚠️ CRITICITÉ :\n{critical}")
        
        # Étape 4: Plan de maintenance
        logger.info("📝 Étape 4: Plan de maintenance")
        plan = self._create_maintenance_plan(equipment_id, risk, critical)
        result.append(f"🔧 PLAN DE MAINTENANCE :\n{plan}")
        
        # Étape 5: Planification
        logger.info("📝 Étape 5: Planification")
        schedule = self._create_schedule(risk, critical)
        result.append(f"📅 PLANIFICATION :\n{schedule}")
        
        # Marquer toutes les étapes comme terminées
        for step in self.steps:
            step['done'] = True
        
        return "\n".join(result)
    
    def _assess_risk(self, equipment_id: str) -> str:
        """
        Évalue le risque d'un équipement
        """
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        RETURN 
            e.id as id,
            e.nom as nom,
            labels(e)[0] as type,
            e.statut as statut,
            count(DISTINCT i) as incidents,
            count(DISTINCT c) as clients
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        
        if not results:
            return f"   ❌ Équipement {equipment_id} non trouvé"
        
        data = results[0]
        incidents = data.get('incidents', 0)
        
        # Calcul du score de risque
        score = 20  # Score de base
        if incidents >= 3:
            score = 90
        elif incidents >= 1:
            score = 60
        
        niveau = "FAIBLE"
        if score >= 70:
            niveau = "CRITIQUE"
        elif score >= 50:
            niveau = "ELEVE"
        
        return f"""
   ID : {data.get('id')}
   Nom : {data.get('nom')}
   Type : {data.get('type')}
   Statut : {data.get('statut', 'inconnu')}
   Score : {score}/100
   Niveau : {niveau}
   Incidents : {incidents}
   Clients : {data.get('clients', 0)}
"""
    
    def _analyze_history(self, equipment_id: str) -> str:
        """
        Analyse l'historique des incidents
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e {id: $equipment_id})
        RETURN 
            i.id as id,
            i.description as description,
            i.gravite as gravite,
            i.date as date,
            i.cause as cause
        ORDER BY i.date DESC
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        
        if not results:
            return "   ✅ Aucun incident enregistré"
        
        history = []
        for item in results[:5]:
            history.append(f"   - {item.get('id')} : {item.get('description')}")
            history.append(f"     Gravité : {item.get('gravite')} | Cause : {item.get('cause')}")
        
        return "\n".join(history)
    
    def _check_criticality(self, equipment_id: str) -> str:
        """
        Vérifie la criticité d'un équipement
        """
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (e)-[:DEPEND_DE]->(comp:Compresseur)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN 
            count(DISTINCT c) as clients,
            count(DISTINCT comp) as dependances,
            count(DISTINCT i) as incidents
        """
        results = self.execute_query(query, {"equipment_id": equipment_id})
        
        if not results:
            return "   ❌ Équipement non trouvé"
        
        data = results[0]
        clients = data.get('clients', 0)
        dependances = data.get('dependances', 0)
        incidents = data.get('incidents', 0)
        
        if clients > 1 and incidents > 0:
            niveau = "CRITIQUE"
        elif clients > 0 or dependances > 0:
            niveau = "ÉLEVÉE"
        else:
            niveau = "MODÉRÉE"
        
        return f"""
   Clients : {clients}
   Dépendances : {dependances}
   Incidents : {incidents}
   Niveau de criticité : {niveau}
"""
    
    def _create_maintenance_plan(self, equipment_id: str, risk: str, critical: str) -> str:
        """
        Crée un plan de maintenance
        """
        # Extraire le niveau de risque
        risk_level = "FAIBLE"
        if "CRITIQUE" in risk:
            risk_level = "CRITIQUE"
        elif "ELEVE" in risk:
            risk_level = "ELEVE"
        
        plan = []
        
        if risk_level == "CRITIQUE":
            plan.append("🔴 PLAN D'URGENCE")
            plan.append("   1. Inspection immédiate")
            plan.append("   2. Plan de réparation d'urgence")
            plan.append("   3. Notification des parties prenantes")
            plan.append("   4. Mise en place de mesures temporaires")
        elif risk_level == "ELEVE":
            plan.append("🟡 PLAN PRÉVENTIF")
            plan.append("   1. Inspection dans les 30 jours")
            plan.append("   2. Maintenance programmée")
            plan.append("   3. Surveillance renforcée")
            plan.append("   4. Plan de secours préparé")
        else:
            plan.append("✅ PLAN STANDARD")
            plan.append("   1. Maintenance préventive régulière")
            plan.append("   2. Surveillance standard")
            plan.append("   3. Inspection annuelle")
        
        return "\n".join(plan)
    
    def _create_schedule(self, risk: str, critical: str) -> str:
        """
        Crée un calendrier de maintenance
        """
        # Déterminer la fréquence
        if "CRITIQUE" in risk or "CRITIQUE" in critical:
            freq = "30 jours"
            detail = "🔴 Inspection complète"
        elif "ELEVE" in risk or "ÉLEVÉE" in critical:
            freq = "60 jours"
            detail = "🟡 Maintenance préventive"
        else:
            freq = "90 jours"
            detail = "✅ Inspection standard"
        
        return f"""
   Fréquence : {freq}
   Type : {detail}
   Prochaine action : Planifier immédiatement
"""
    
    def get_all_critical_equipment(self) -> str:
        """
        Liste tous les équipements critiques
        """
        query = """
        MATCH (e)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        WITH e, count(DISTINCT i) as incidents, count(DISTINCT c) as clients
        WHERE clients > 0 OR incidents > 0
        RETURN 
            e.id as id,
            e.nom as nom,
            labels(e)[0] as type,
            incidents,
            clients,
            CASE 
                WHEN incidents >= 3 OR clients > 2 THEN 'CRITIQUE'
                WHEN incidents >= 1 OR clients > 0 THEN 'ELEVE'
                ELSE 'MODERE'
            END as niveau
        ORDER BY incidents DESC, clients DESC
        LIMIT 10
        """
        results = self.execute_query(query)
        
        if not results:
            return "✅ Aucun équipement critique détecté"
        
        output = ["📍 LISTE DES ÉQUIPEMENTS CRITIQUES"]
        for item in results:
            output.append(f"   - {item.get('nom')} ({item.get('type')})")
            output.append(f"     Niveau : {item.get('niveau')}")
            output.append(f"     Incidents : {item.get('incidents')} | Clients : {item.get('clients')}")
        
        return "\n".join(output)