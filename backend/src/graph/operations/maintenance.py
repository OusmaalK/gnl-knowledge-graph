"""
Opérations de maintenance du graphe
Phase 3 - Nettoyage, optimisation et maintenance
"""

from .crud import GraphCRUD
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GraphMaintenance(GraphCRUD):
    """
    Opérations de maintenance sur le graphe Neo4j
    """
    
    def __init__(self):
        super().__init__()

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup_orphan_nodes(self) -> Dict:
        """
        Supprime les nœuds orphelins (sans relations)
        """
        query = """
        MATCH (n)
        WHERE NOT (n)-[]-()
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        results = self.execute_query(query)
        count = results[0].get('deleted', 0) if results else 0
        
        logger.info(f"🗑️ {count} nœuds orphelins supprimés")
        return {"success": True, "deleted": count}

    def cleanup_duplicates(self) -> Dict:
        """
        Supprime les doublons de nœuds
        """
        query = """
        MATCH (n)
        WITH n.id as id, collect(n) as nodes
        WHERE size(nodes) > 1
        FOREACH (node IN nodes[1..] | 
            DETACH DELETE node
        )
        RETURN count(DISTINCT id) as duplicates
        """
        results = self.execute_query(query)
        count = results[0].get('duplicates', 0) if results else 0
        
        logger.info(f"🗑️ {count} doublons supprimés")
        return {"success": True, "deleted": count}

    def cleanup_old_incidents(self, days: int = 365) -> Dict:
        """
        Supprime les incidents plus vieux que X jours
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        query = """
        MATCH (i:Incident)
        WHERE datetime(i.date) < datetime($cutoff)
        DETACH DELETE i
        RETURN count(i) as deleted
        """
        results = self.execute_query(query, {"cutoff": cutoff.isoformat()})
        count = results[0].get('deleted', 0) if results else 0
        
        logger.info(f"🗑️ {count} incidents supprimés (>{days} jours)")
        return {"success": True, "deleted": count}

    # ============================================================
    # VALIDATION
    # ============================================================

    def validate_graph(self) -> Dict:
        """
        Valide l'intégrité du graphe
        """
        issues = []
        
        # Vérifier les relations avec des nœuds inexistants
        query = """
        MATCH (n)-[r]->(m)
        WHERE NOT n IS NOT NULL OR NOT m IS NOT NULL
        RETURN count(r) as invalid
        """
        results = self.execute_query(query)
        invalid = results[0].get('invalid', 0) if results else 0
        
        if invalid > 0:
            issues.append(f"Relations invalides : {invalid}")
        
        # Vérifier les nœuds sans propriétés
        query = """
        MATCH (n)
        WHERE size(keys(n)) = 0
        RETURN count(n) as empty
        """
        results = self.execute_query(query)
        empty = results[0].get('empty', 0) if results else 0
        
        if empty > 0:
            issues.append(f"Nœuds sans propriétés : {empty}")
        
        return {
            "success": True,
            "issues": issues,
            "has_issues": len(issues) > 0
        }

    def repair_graph(self) -> Dict:
        """
        Répare les problèmes d'intégrité
        """
        results = self.validate_graph()
        
        if not results.get('has_issues'):
            return {"success": True, "message": "Aucune réparation nécessaire"}
        
        # Supprimer les relations invalides
        query = """
        MATCH (n)-[r]->(m)
        WHERE NOT n IS NOT NULL OR NOT m IS NOT NULL
        DELETE r
        RETURN count(r) as deleted
        """
        repair_results = self.execute_query(query)
        deleted = repair_results[0].get('deleted', 0) if repair_results else 0
        
        logger.info(f"🔧 {deleted} relations invalides supprimées")
        return {"success": True, "repaired": deleted}

    # ============================================================
    # INDEX MANAGEMENT
    # ============================================================

    def get_indexes(self) -> List[Dict]:
        """
        Liste les indexes existants
        """
        query = """
        SHOW INDEXES
        """
        return self.execute_query(query)

    def drop_index(self, index_name: str) -> Dict:
        """
        Supprime un index
        """
        query = f"""
        DROP INDEX {index_name}
        """
        try:
            self.execute_query(query)
            logger.info(f"🗑️ Index supprimé : {index_name}")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============================================================
    # BACKUP
    # ============================================================

    def export_graph(self, filepath: str = "backup.json") -> Dict:
        """
        Exporte le graphe en JSON
        """
        import json
        
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN 
            n as source,
            labels(n) as source_labels,
            r as relation,
            m as target,
            labels(m) as target_labels
        """
        results = self.execute_query(query)
        
        data = []
        for record in results:
            data.append({
                "source": record.get('source'),
                "source_labels": record.get('source_labels'),
                "relation": record.get('relation'),
                "target": record.get('target'),
                "target_labels": record.get('target_labels')
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 Graphe exporté vers {filepath}")
        return {"success": True, "count": len(data), "file": filepath}

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_database_stats(self) -> Dict:
        """
        Récupère les statistiques de la base
        """
        stats = {}
        
        queries = [
            ("total_nodes", "MATCH (n) RETURN count(n) as total"),
            ("total_relationships", "MATCH ()-[r]->() RETURN count(r) as total"),
            ("total_labels", "MATCH (n) RETURN count(DISTINCT labels(n)) as total"),
            ("total_relationship_types", "MATCH ()-[r]->() RETURN count(DISTINCT type(r)) as total"),
        ]
        
        for name, query in queries:
            results = self.execute_query(query)
            stats[name] = results[0].get('total', 0) if results else 0
        
        return stats

    def run_full_maintenance(self) -> Dict:
        """
        Exécute toutes les opérations de maintenance
        """
        logger.info("🚀 Début de la maintenance complète")
        
        results = {
            "cleanup": self.cleanup_orphan_nodes(),
            "duplicates": self.cleanup_duplicates(),
            "validation": self.validate_graph(),
            "repair": self.repair_graph(),
            "stats": self.get_database_stats()
        }
        
        logger.info("✅ Maintenance terminée")
        return results