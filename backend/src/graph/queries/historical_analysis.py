"""
Analyse historique des incidents GNL
Phase 2 - Historique et tendances
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalAnalysis:
    """
    Analyse l'historique des incidents pour identifier
    les tendances, les corrélations et les patterns temporels.
    """
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'GnL_Neo4j_2026_Secure!')
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        logger.info("✅ Connecté à Neo4j")
        return True

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("🔒 Connexion fermée")

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Exécute une requête Cypher"""
        if not self.driver:
            self.connect()
        
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    # ============================================================
    # ANALYSE TEMPORELLE
    # ============================================================

    def get_incidents_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Incidents sur une période donnée
        """
        query = """
        MATCH (i:Incident)
        WHERE datetime(i.date) >= datetime($start_date)
          AND datetime(i.date) <= datetime($end_date)
        RETURN i.id as id,
               i.description as description,
               i.date as date,
               i.gravite as gravite,
               i.cause as cause,
               i.duree_min as duree
        ORDER BY i.date DESC
        """
        return self.execute_query(query, {"start_date": start_date, "end_date": end_date})

    def get_incident_timeline(self) -> List[Dict]:
        """
        Chronologie des incidents par date
        """
        query = """
        MATCH (i:Incident)
        RETURN i.date as date,
               count(i) as nombre_incidents
        ORDER BY date ASC
        """
        return self.execute_query(query)

    def get_incidents_by_month(self, year: int) -> List[Dict]:
        """
        Incidents par mois pour une année donnée
        """
        query = """
        MATCH (i:Incident)
        WHERE datetime(i.date).year = $year
        RETURN datetime(i.date).month as mois,
               count(i) as nombre_incidents
        ORDER BY mois ASC
        """
        return self.execute_query(query, {"year": year})

    # ============================================================
    # ANALYSE DES CAUSES
    # ============================================================

    def get_causes_distribution(self) -> List[Dict]:
        """
        Distribution des causes d'incidents
        """
        query = """
        MATCH (i:Incident)
        RETURN i.cause as cause,
               count(i) as nombre,
               collect(i.id) as incidents
        ORDER BY nombre DESC
        """
        return self.execute_query(query)

    def get_gravite_distribution(self) -> List[Dict]:
        """
        Distribution des gravités d'incidents
        """
        query = """
        MATCH (i:Incident)
        RETURN i.gravite as gravite,
               count(i) as nombre
        ORDER BY 
            CASE i.gravite
                WHEN 'critique' THEN 1
                WHEN 'majeur' THEN 2
                WHEN 'mineur' THEN 3
            END
        """
        return self.execute_query(query)

    def get_cause_by_equipment(self) -> List[Dict]:
        """
        Causes par type d'équipement
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN labels(e)[0] as equipment_type,
               i.cause as cause,
               count(i) as nombre
        ORDER BY equipment_type, nombre DESC
        """
        return self.execute_query(query)

    # ============================================================
    # ANALYSE DE CORRÉLATION
    # ============================================================

    def get_correlation_incidents_equipment(self) -> List[Dict]:
        """
        Corrélation entre incidents et équipements
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN e.id as equipment_id,
               labels(e)[0] as equipment_type,
               e.nom as equipment_name,
               count(i) as nombre_incidents,
               collect(i.gravite) as gravites,
               collect(i.cause) as causes
        ORDER BY nombre_incidents DESC
        """
        return self.execute_query(query)

    def get_incident_duration_analysis(self) -> List[Dict]:
        """
        Analyse des durées d'incidents par type
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        RETURN labels(e)[0] as equipment_type,
               avg(i.duree_min) as duree_moyenne,
               max(i.duree_min) as duree_max,
               min(i.duree_min) as duree_min,
               count(i) as nombre_incidents
        ORDER BY duree_moyenne DESC
        """
        return self.execute_query(query)

    def get_recurring_incidents(self, min_occurrences: int = 2) -> List[Dict]:
        """
        Incidents récurrents (même cause, même équipement)
        """
        query = """
        MATCH (i:Incident)-[:AFFECTE]->(e)
        WITH e, i.cause as cause, count(i) as occurrences
        WHERE occurrences >= $min_occurrences
        RETURN e.id as equipment_id,
               e.nom as equipment_name,
               cause,
               occurrences
        ORDER BY occurrences DESC
        """
        return self.execute_query(query, {"min_occurrences": min_occurrences})

    # ============================================================
    # ANALYSE DE TENDANCES
    # ============================================================

    def get_incident_trend(self, period: str = 'month') -> List[Dict]:
        """
        Tendance des incidents (jour, mois, année)
        """
        query = """
        MATCH (i:Incident)
        WITH 
            datetime(i.date).year as year,
            datetime(i.date).month as month,
            count(i) as nombre
        RETURN year, month, nombre
        ORDER BY year, month
        """
        return self.execute_query(query)

    def get_high_risk_periods(self) -> List[Dict]:
        """
        Périodes à haut risque (concentration d'incidents)
        """
        query = """
        MATCH (i:Incident)
        WITH 
            datetime(i.date).year as year,
            datetime(i.date).month as month,
            count(i) as nombre
        WHERE nombre > 1
        RETURN year, month, nombre
        ORDER BY nombre DESC
        """
        return self.execute_query(query)

    # ============================================================
    # RAPPORTS
    # ============================================================

    def get_full_historical_report(self) -> Dict:
        """
        Génère un rapport historique complet
        """
        return {
            'total_incidents': len(self.get_nodes_by_type('Incident')),
            'causes_distribution': self.get_causes_distribution(),
            'gravite_distribution': self.get_gravite_distribution(),
            'correlation_equipment': self.get_correlation_incidents_equipment(),
            'recurring_incidents': self.get_recurring_incidents(),
            'duration_analysis': self.get_incident_duration_analysis(),
            'trend': self.get_incident_trend()
        }

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Retourne tous les nœuds d'un type donné"""
        query = f"""
        MATCH (n:{node_type})
        RETURN n
        """
        return self.execute_query(query)

    # ============================================================
    # EXÉCUTION
    # ============================================================

    def run_all_analyses(self):
        """Exécute toutes les analyses historiques"""
        self.connect()
        
        logger.info("\n" + "="*60)
        logger.info("📈 ANALYSE HISTORIQUE DES INCIDENTS")
        logger.info("="*60)
        
        try:
            # 1. Statistiques générales
            logger.info("\n1️⃣ STATISTIQUES GÉNÉRALES :")
            total = len(self.get_nodes_by_type('Incident'))
            logger.info(f"   Total incidents : {total}")
            
            # 2. Distribution des causes
            logger.info("\n2️⃣ DISTRIBUTION DES CAUSES :")
            causes = self.get_causes_distribution()
            for item in causes:
                logger.info(f"   {item['cause']:20} : {item['nombre']} (incidents: {item['incidents']})")
            
            # 3. Distribution des gravités
            logger.info("\n3️⃣ DISTRIBUTION DES GRAVITÉS :")
            gravites = self.get_gravite_distribution()
            for item in gravites:
                logger.info(f"   {item['gravite']:15} : {item['nombre']}")
            
            # 4. Corrélation équipements
            logger.info("\n4️⃣ ÉQUIPEMENTS LES PLUS IMPACTÉS :")
            correlations = self.get_correlation_incidents_equipment()
            for item in correlations[:5]:
                logger.info(f"   {item['equipment_name']} : {item['nombre_incidents']} incidents")
            
            # 5. Incidents récurrents
            logger.info("\n5️⃣ INCIDENTS RÉCURRENTS :")
            recurring = self.get_recurring_incidents(2)
            if recurring:
                for item in recurring:
                    logger.info(f"   {item['equipment_name']} - {item['cause']} : {item['occurrences']} fois")
            else:
                logger.info("   Aucun incident récurrent détecté")
            
            # 6. Analyse des durées
            logger.info("\n6️⃣ ANALYSE DES DURÉES :")
            durations = self.get_incident_duration_analysis()
            for item in durations:
                logger.info(f"   {item['equipment_type']:15} : moyenne {item['duree_moyenne']:.0f} min")
            
            # 7. Tendance
            logger.info("\n7️⃣ TENDANCE MENSUELLE :")
            trend = self.get_incident_trend()
            for item in trend[:12]:  # Derniers mois
                logger.info(f"   {item['year']}-{item['month']:02d} : {item['nombre']} incidents")
            
            logger.info("\n" + "="*60)
            logger.info("✅ ANALYSE HISTORIQUE TERMINÉE")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
        finally:
            self.close()


if __name__ == "__main__":
    analysis = HistoricalAnalysis()
    analysis.run_all_analyses()