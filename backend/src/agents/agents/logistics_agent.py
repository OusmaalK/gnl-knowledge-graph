"""
Agent spécialisé dans la logistique - Version enrichie
"""

from ..base_agent import BaseAgent
import logging

# IMPORTANT : Importez votre outil LLM ici
from ..tools.llm_tools import LLMTools 

logger = logging.getLogger(__name__)

class LogisticsAgent(BaseAgent):
    """
    Agent pour la logistique et les routes
    """
    
    def __init__(self):
        super().__init__(name="LogisticsAgent")
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
        """Exécute la logistique"""
        if not params:
            return self.general_analysis()
        
        # --- SI ON DEMANDE UNE ROUTE ALTERNATIVE ---
        if params.get('find_alternative') and params.get('exclude'):
            # On appelle la nouvelle méthode
            route = self.find_alternative_route(
                params.get('start'), 
                params.get('end'), 
                params.get('exclude')
            )
            # On retourne les données formatées pour le frontend
            return self._format_route_data(route, params.get('start'), params.get('end'))
        
        if 'start' in params and 'end' in params:
            return self.find_best_route(params.get('start'), params.get('end'))
        if params.get('equipment_id'):
            return self.analyze_impact(params.get('equipment_id'))
        if params.get('route'):
            return self.general_analysis(params.get('route'))
        return self.general_analysis()

    def calculate_route_reliability(self, path_nodes):
        """
        Calcule un score de fiabilité pour une route donnée (liste de nœuds).
        Plus le score est élevé, plus la route est sûre.
        """
        if not path_nodes:
            return 0

        formatted_ids = "', '".join(path_nodes)
        
        # 1. Compter les incidents récents sur ces nœuds (ex: 30 derniers jours)
        # Et récupérer les statuts actuels
        query = f"""
        MATCH (n)
        WHERE n.id IN ['{formatted_ids}']
        OPTIONAL MATCH (n)<-[:AFFECTE]-(i:Incident)
        WHERE i.date >= date() - duration('P30D')  // Incidents des 30 derniers jours
        RETURN 
            n.id as id,
            n.statut as status,
            COUNT(i) as incident_count
        """
        
        try:
            results = self.graph_tools.execute_query(query)
        except Exception as e:
            logger.warning(f"⚠️ Impossible de calculer le score de risque: {e}")
            return 50 # Score par défaut en cas d'erreur

        total_incidents = sum(row['incident_count'] for row in results)
        
        # 2. Calcul du score (Logique simple)
        # Base de 100 points
        score = 100
        
        # Pénalité par incident
        score -= (total_incidents * 10)
        
        # Pénalité si un nœud est en 'critique'
        for row in results:
            if row['status'] == 'critique':
                score -= 20
            elif row['status'] == 'warning':
                score -= 10
        
        # S'assurer que le score reste entre 0 et 100
        return max(0, min(100, score))

    def _format_route_data(self, route, start_id, end_id):
        """
        Fonction utilitaire pour formater les données de la route, 
        récupérer les statuts ET calculer le score de fiabilité.
        """
        path = route.get('path', [])
        distance = route.get('distance', 0)

        # SI LA DISTANCE EST -1, ON RENVOIE UNE ERREUR IMMÉDIATEMENT
        if distance == -1:
            return {
                "text": f"Aucune route trouvée entre {start_id} et {end_id}.",
                "raw_data": {
                    "path": [],
                    "nodes": [],
                    "distance": -1
                }
            }

        # Récupérer les statuts des nœuds dans Neo4j
        formatted_ids = "', '".join(path)
        status_query = f"""
        MATCH (n)
        WHERE n.id IN ['{formatted_ids}']
        RETURN n.id as id, n.statut as status
        """
        
        try:
            status_results = self.graph_tools.execute_query(status_query)
            status_map = {row['id']: row['status'] for row in status_results}
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les statuts des nœuds: {e}")
            status_map = {node_id: None for node_id in path}

        nodes_with_status = []
        for node_id in path:
            nodes_with_status.append({
                'id': node_id,
                'status': status_map.get(node_id, None)
            })

        # --- CALCUL DU SCORE DE FIABILITÉ ---
        reliability_score = self.calculate_route_reliability(path)
        # ------------------------------------

        # Retourner la structure attendue par le Frontend
        return {
            "text": f"Route trouvée entre {start_id} et {end_id} (Distance: {distance} sauts)",
            "raw_data": {
                "path": path,
                "nodes": nodes_with_status,
                "distance": distance,
                "reliability_score": reliability_score  # <-- AJOUT AU FRONTEND
            }
        }
    
    def find_best_route(self, start_id: str, end_id: str) -> dict:
        """
        Trouve la meilleure route ET récupère le statut des nœuds pour les badges.
        """
        if not start_id or not end_id:
            return self.generate_with_llm(
                "Explique-moi comment optimiser les routes dans un réseau GNL."
            )
        
        route = self.graph_tools.get_alternative_route(start_id, end_id)
        
        if route.get('distance', -1) == -1:
            return self.generate_with_llm(
                f"Aucune route trouvée entre {start_id} et {end_id}. Que me conseillez-vous pour optimiser ce réseau ?"
            )
        
        # Retourner les données formatées
        return self._format_route_data(route, start_id, end_id)
    
    def find_alternative_route(self, start_id: str, end_id: str, exclude_id: str) -> dict:
        """
        Trouve une route alternative en évitant un nœud spécifique
        """
        # Requête Cypher qui utilise le paramètre `exclude_id`
        query = """
        MATCH (start {id: $start_id}), (end {id: $end_id})
        MATCH path = shortestPath((start)-[*]-(end))
        WHERE NONE(n IN nodes(path) WHERE n.id = $exclude_id)
        RETURN [n IN nodes(path) | n.id] as path, 
               [n IN nodes(path) | labels(n)[0]] as types,
               length(path) as distance
        """
        
        params = {
            'start_id': start_id,
            'end_id': end_id,
            'exclude_id': exclude_id
        }
        
        # Exécution de la requête
        result = self.graph_tools.execute_query(query, params)
        
        if not result:
            return {'distance': -1, 'path': [], 'types': []}
            
        data = result[0]
        return {
            'path': data.get('path', []),
            'types': data.get('types', []),
            'distance': data.get('distance', 0)
        }
    
    def analyze_impact(self, equipment_id: str) -> str:
        """
        Analyse l'impact d'un équipement avec enrichissement
        """
        if not equipment_id:
            return self.generate_with_llm(
                "Explique-moi les impacts potentiels des pannes sur le réseau GNL."
            )
        
        impact = self.graph_tools.get_impact_analysis(equipment_id)
        
        if not impact:
            return self.generate_with_llm(
                f"Équipement {equipment_id} non trouvé. Que me conseillez-vous pour l'analyse d'impact ?"
            )
        
        clients = ', '.join(impact.get('clients_impactes', ['Aucun']))
        deps = ', '.join(impact.get('dependances_critiques', ['Aucune']))
        
        graph_context = f"""
📍 Équipement : {impact.get('equipment_name', equipment_id)}
📋 Type : {impact.get('equipment_type')}
📌 Statut : {impact.get('statut', 'Inconnu')}
👥 Clients : {clients}
🔧 Dépendances : {deps}
🚨 Incidents : {impact.get('incidents_count', 0)}
"""

        question = f"""
Analyse l'impact de l'équipement suivant :

{graph_context}

Fournis :
1. Une évaluation complète de l'impact
2. Les risques potentiels
3. Des recommandations stratégiques
4. Un plan de continuité
"""
        
        return self.generate_with_llm(question, {'impact': impact})
    
    def general_analysis(self, route_data=None) -> str:
        """
        Analyse générale enrichie (ou analyse spécifique d'une route si fournie)
        """
        if route_data:
            nodes = route_data.get('nodes', [])
            graph_context = f"""
📍 ITINÉRAIRE SPÉCIFIQUE ANALYSÉ :
   - Départ : {nodes[0]['id'] if nodes else 'N/A'}
   - Arrivée : {nodes[-1]['id'] if nodes else 'N/A'}
   - Distance : {route_data.get('distance', 0)} sauts
"""
        else:
            stats = self.graph_tools.get_statistics()
            graph_context = f"""
📊 Statistiques globales du réseau :
   - Pipelines : {stats.get('total_pipelines', 0)}
   - Clients : {stats.get('total_clients', 0)}
   - Incidents : {stats.get('total_incidents', 0)}
   - Relations : {stats.get('total_relations', 0)}
"""
        
        question = f"""
Analyse l'état du réseau GNL (en se concentrant sur les données suivantes si fournies) :

{graph_context}

Fournis :
1. Une évaluation de la santé du réseau basée sur ces données
2. Les points de vigilance critiques
3. Des recommandations d'amélioration
4. Les tendances observées
"""
        
        return self.generate_with_llm(question, {'statistics': graph_context})