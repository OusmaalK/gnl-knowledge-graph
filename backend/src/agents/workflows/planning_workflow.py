"""
Workflow de planification des routes
Phase 3 - Workflow complet pour la planification logistique
"""

from .base import BaseWorkflow
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class PlanningWorkflow(BaseWorkflow):
    """
    Workflow pour la planification des routes
    """
    
    def __init__(self):
        super().__init__(name="PlanningWorkflow")
        self._setup_steps()
    
    def _setup_steps(self):
        """Configure les étapes du workflow"""
        self.add_step("analysis", "Analyse du réseau")
        self.add_step("route_selection", "Sélection de la route")
        self.add_step("alternative_check", "Vérification des alternatives")
        self.add_step("impact_assessment", "Évaluation d'impact")
        self.add_step("recommendation", "Recommandation finale")
    
    def get_steps(self) -> List[str]:
        """Retourne la liste des étapes"""
        return [s['step'] for s in self.steps]
    
    def execute(self, start_id: str = None, end_id: str = None, blocked_id: str = None, **kwargs) -> str:
        """
        Exécute le workflow de planification
        """
        if not start_id or not end_id:
            return "❌ Veuillez spécifier start_id et end_id"
        
        logger.info(f"🚀 Début du workflow planning : {start_id} → {end_id}")
        
        result = []
        
        # Étape 1: Analyse du réseau
        logger.info("📝 Étape 1: Analyse du réseau")
        network_status = self._analyze_network()
        result.append(f"📊 ÉTAT DU RÉSEAU :\n{network_status}")
        
        # Étape 2: Sélection de la route
        logger.info("📝 Étape 2: Sélection de la route")
        main_route = self._find_route(start_id, end_id, blocked_id)
        if not main_route:
            return f"❌ Aucune route trouvée entre {start_id} et {end_id}"
        result.append(f"🗺️ ROUTE PRINCIPALE : {self._format_route(main_route)}")
        
        # Étape 3: Vérification des alternatives
        logger.info("📝 Étape 3: Vérification des alternatives")
        alternatives = self._find_alternatives(start_id, end_id, blocked_id)
        if alternatives:
            result.append(f"🔄 ROUTES ALTERNATIVES : {len(alternatives)} trouvées")
            result.append(self._format_alternatives(alternatives))
        else:
            result.append("⚠️ Aucune route alternative disponible")
        
        # Étape 4: Évaluation d'impact
        logger.info("📝 Étape 4: Évaluation d'impact")
        impact = self._assess_impact(start_id, end_id, main_route)
        result.append(f"📊 IMPACT :\n{impact}")
        
        # Étape 5: Recommandation finale
        logger.info("📝 Étape 5: Recommandation finale")
        recommendation = self._get_recommendation(main_route, alternatives, impact)
        result.append(f"💡 RECOMMANDATION :\n{recommendation}")
        
        # Marquer toutes les étapes comme terminées
        for step in self.steps:
            step['done'] = True
        
        return "\n".join(result)
    
    def _analyze_network(self) -> str:
        """
        Analyse l'état du réseau
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
        results = self.execute_query(query)
        
        if not results:
            return "   Aucun pipeline trouvé"
        
        status = []
        for item in results:
            statut = item.get('statut', 'inconnu')
            emoji = "🟢" if statut == 'actif' else "🔴"
            status.append(f"   {emoji} {item.get('nom')} - {statut} (incidents: {item.get('incidents', 0)})")
        
        return "\n".join(status)
    
    def _find_route(self, start_id: str, end_id: str, blocked_id: str = None) -> Dict:
        """
        Trouve une route
        """
        query = """
        MATCH path = shortestPath(
            (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
        )
        RETURN [n in nodes(path) | n.id] as path,
               [n in nodes(path) | labels(n)[0]] as types,
               length(path) as distance
        """
        results = self.execute_query(query, {"start_id": start_id, "end_id": end_id})
        return results[0] if results else {}
    
    def _find_alternatives(self, start_id: str, end_id: str, blocked_id: str = None) -> List[Dict]:
        """
        Trouve des routes alternatives
        """
        query = """
        MATCH path = (start {id: $start_id})-[:ALIMENTE|DESSERT*1..5]-(end {id: $end_id})
        RETURN [n in nodes(path) | n.id] as path,
               length(path) as distance
        ORDER BY distance ASC
        LIMIT 3
        """
        return self.execute_query(query, {"start_id": start_id, "end_id": end_id})
    
    def _format_route(self, route: Dict) -> str:
        """
        Formate une route
        """
        path = route.get('path', [])
        distance = route.get('distance', 0)
        types = route.get('types', [])
        
        formatted = []
        for i, (node, node_type) in enumerate(zip(path, types)):
            if i == 0:
                formatted.append(f"   {i}. 🚀 {node} ({node_type})")
            elif i == len(path) - 1:
                formatted.append(f"   {i}. 🏁 {node} ({node_type})")
            else:
                formatted.append(f"   {i}. 📍 {node} ({node_type})")
        
        return f"\n".join(formatted) + f"\n   📏 Distance : {distance} sauts"
    
    def _format_alternatives(self, alternatives: List[Dict]) -> str:
        """
        Formate les routes alternatives
        """
        result = []
        for i, alt in enumerate(alternatives):
            path = alt.get('path', [])
            distance = alt.get('distance', 0)
            result.append(f"   Alternative {i+1} : {' → '.join(path)} ({distance} sauts)")
        return "\n".join(result)
    
    def _assess_impact(self, start_id: str, end_id: str, route: Dict) -> str:
        """
        Évalue l'impact de la route
        """
        path = route.get('path', [])
        
        # Vérifier les équipements sur le chemin
        equipments = []
        for node_id in path:
            query = """
            MATCH (n {id: $node_id})
            OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(n)
            RETURN n.id as id, n.nom as nom, count(DISTINCT i) as incidents
            """
            results = self.execute_query(query, {"node_id": node_id})
            if results:
                equipments.append(results[0])
        
        impact = []
        for eq in equipments:
            incidents = eq.get('incidents', 0)
            if incidents > 0:
                impact.append(f"   ⚠️ {eq.get('nom', eq.get('id'))} - {incidents} incidents")
            else:
                impact.append(f"   ✅ {eq.get('nom', eq.get('id'))} - Aucun incident")
        
        return "\n".join(impact) if impact else "   ✅ Aucun impact identifié"
    
    def _get_recommendation(self, route: Dict, alternatives: List[Dict], impact: str) -> str:
        """
        Génère une recommandation
        """
        if not route:
            return "❌ Aucune route disponible"
        
        distance = route.get('distance', 0)
        has_alternatives = len(alternatives) > 0
        
        recommendation = []
        
        if distance <= 2:
            recommendation.append("✅ Route optimale - Recommandée")
        else:
            recommendation.append("⚠️ Route longue - Autre alternative recommandée")
        
        if has_alternatives:
            recommendation.append("🔄 Prévoir une route de secours")
        
        if "⚠️" in impact:
            recommendation.append("🔍 Surveillance renforcée recommandée")
        
        return "\n".join([f"   {r}" for r in recommendation])