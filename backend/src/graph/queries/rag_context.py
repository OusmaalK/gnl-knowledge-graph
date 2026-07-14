"""
Préparation du contexte pour les agents IA (GraphRAG)
Phase 2 - Structuration des données pour les LLM
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphRAGContext:
    """Construit le contexte pour les agents IA"""
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None
        
    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
    def close(self):
        if self.driver:
            self.driver.close()
    
    def get_network_summary(self):
        """Résumé du réseau pour un prompt initial"""
        query = """
        MATCH (n)
        WITH count(n) as total_nodes
        MATCH ()-[r]->()
        RETURN total_nodes, count(r) as total_relations
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()
    
    def get_equipment_context(self, equipment_id):
        """
        Contexte complet d'un équipement pour l'IA
        """
        query = """
        MATCH (e {id: $equipment_id})
        OPTIONAL MATCH (e)-[:DESSERT]->(c:Client)
        OPTIONAL MATCH (e)-[:DEPEND_DE]->(comp:Compresseur)
        OPTIONAL MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN e.id as Id,
               labels(e)[0] as Type,
               e.nom as Nom,
               e.statut as Statut,
               collect(DISTINCT c.nom) as Clients,
               comp.nom as Compresseur,
               collect(DISTINCT i.description) as Incidents,
               count(DISTINCT i) as NombreIncidents
        """
        
        with self.driver.session() as session:
            result = session.run(query, equipment_id=equipment_id)
            return result.single()
    
    def build_prompt_context(self, equipment_id="PIPE-001"):
        """
        Construit un contexte textuel pour l'IA
        """
        context = self.get_equipment_context(equipment_id)
        if not context:
            return "Équipement non trouvé"
        
        prompt = f"""
=== CONTEXTE RÉSEAU GNL ===

📌 ÉQUIPEMENT : {context['Nom']} ({context['Type']})
   ID : {context['Id']}
   Statut : {context['Statut']}

👥 CLIENTS DESSERVIS :
   {', '.join(context['Clients']) if context['Clients'] else 'Aucun'}

🔧 DÉPENDANCES :
   Compresseur : {context['Compresseur'] if context['Compresseur'] else 'Aucun'}

⚠️ INCIDENTS RÉCENTS :
   {', '.join(context['Incidents']) if context['Incidents'] else 'Aucun incident'}
   Nombre d'incidents : {context['NombreIncidents']}

📊 ANALYSE :
   - {context['Type']} en statut {context['Statut']}
   - {context['NombreIncidents']} incident(s) enregistré(s)
   - {len(context['Clients']) if context['Clients'] else 0} client(s) impacté(s)
"""
        return prompt
    
    def get_chain_context(self):
        """
        Contexte complet de la chaîne d'approvisionnement
        """
        query = """
        MATCH path = (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)-[:DESSERT]->(c:Client)
        RETURN f.nom as Fournisseur,
               t.nom as Terminal,
               p.nom as Pipeline,
               c.nom as Client,
               p.statut as StatutPipeline
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def export_context_for_llm(self, equipment_id="PIPE-001", output_file="context_llm.json"):
        """
        Exporte le contexte pour les LLM
        """
        context = self.get_equipment_context(equipment_id)
        chain = self.get_chain_context()
        summary = self.get_network_summary()
        
        data = {
            "network_summary": {
                "total_nodes": summary['total_nodes'] if summary else 0,
                "total_relations": summary['total_relations'] if summary else 0
            },
            "equipment_context": {
                "id": context['Id'] if context else None,
                "type": context['Type'] if context else None,
                "nom": context['Nom'] if context else None,
                "statut": context['Statut'] if context else None,
                "clients": context['Clients'] if context else [],
                "incidents": context['Incidents'] if context else [],
                "nombre_incidents": context['NombreIncidents'] if context else 0
            },
            "supply_chain": chain
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Contexte exporté vers {output_file}")
        return data
    
    def run(self):
        """Exécute la préparation du contexte"""
        self.connect()
        
        logger.info("\n" + "="*60)
        logger.info("🤖 PRÉPARATION CONTEXTE IA (GraphRAG)")
        logger.info("="*60)
        
        # Contexte pour PIPE-001
        prompt = self.build_prompt_context("PIPE-001")
        logger.info("\n📝 CONTEXTE IA :")
        logger.info(prompt)
        
        # Export JSON
        self.export_context_for_llm()
        
        self.close()

if __name__ == "__main__":
    rag = GraphRAGContext()
    rag.run()