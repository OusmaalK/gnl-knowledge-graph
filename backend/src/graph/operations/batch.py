"""
Opérations par lots sur le graphe
Phase 3 - Traitement batch pour l'ingestion de données
"""

from .crud import GraphCRUD
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class BatchOperations(GraphCRUD):
    """
    Opérations par lots pour l'ingestion massive
    """
    
    def __init__(self, batch_size: int = 100):
        super().__init__()
        self.batch_size = batch_size
        self.current_batch = []

    def add_to_batch(self, operation: str, data: Dict) -> None:
        """
        Ajoute une opération au lot
        """
        self.current_batch.append({
            "operation": operation,
            "data": data
        })
        
        if len(self.current_batch) >= self.batch_size:
            return self.flush()
        
        return {"success": True, "pending": len(self.current_batch)}

    def flush(self) -> Dict:
        """
        Exécute toutes les opérations en lot
        """
        if not self.current_batch:
            return {"success": True, "message": "Aucune opération"}
        
        logger.info(f"🔄 Exécution de {len(self.current_batch)} opérations")
        
        results = {
            "success": True,
            "created": 0,
            "updated": 0,
            "deleted": 0,
            "errors": []
        }
        
        driver = self.connect()
        
        with driver.session() as session:
            tx = session.begin_transaction()
            
            try:
                for op in self.current_batch:
                    operation = op.get("operation")
                    data = op.get("data", {})
                    
                    if operation == "create_node":
                        result = self._batch_create_node(tx, data)
                    elif operation == "create_relationship":
                        result = self._batch_create_relationship(tx, data)
                    elif operation == "update_node":
                        result = self._batch_update_node(tx, data)
                    elif operation == "delete_node":
                        result = self._batch_delete_node(tx, data)
                    else:
                        results["errors"].append(f"Opération inconnue : {operation}")
                        continue
                    
                    if result and result.get("success"):
                        if operation in ["create_node", "create_relationship"]:
                            results["created"] += 1
                        elif operation == "update_node":
                            results["updated"] += 1
                        elif operation == "delete_node":
                            results["deleted"] += 1
                    else:
                        results["errors"].append(result.get("error", "Erreur inconnue"))
                
                tx.commit()
                self.current_batch = []
                logger.info(f"✅ Batch terminé : {results['created']} créés, {results['updated']} mis à jour")
                
                return results
                
            except Exception as e:
                tx.rollback()
                logger.error(f"❌ Erreur batch : {e}")
                self.current_batch = []
                return {"success": False, "error": str(e)}
            finally:
                self.close()

    def _batch_create_node(self, tx, data: Dict):
        """
        Crée un nœud en batch
        """
        label = data.get("label")
        properties = data.get("properties", {})
        
        if not label or 'id' not in properties:
            return {"success": False, "error": "Label ou id manquant"}
        
        query = f"""
        CREATE (n:{label} $properties)
        SET n.updated_at = datetime()
        RETURN n
        """
        result = tx.run(query, {"properties": properties})
        return {"success": True, "data": result.single()}

    def _batch_create_relationship(self, tx, data: Dict):
        """
        Crée une relation en batch
        """
        rel_type = data.get("type")
        source_id = data.get("source_id")
        target_id = data.get("target_id")
        properties = data.get("properties", {})
        
        if not all([rel_type, source_id, target_id]):
            return {"success": False, "error": "Paramètres manquants"}
        
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        CREATE (source)-[r:{rel_type} $properties]->(target)
        SET r.updated_at = datetime()
        RETURN r
        """
        result = tx.run(query, {
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties
        })
        return {"success": True, "data": result.single()}

    def _batch_update_node(self, tx, data: Dict):
        """
        Met à jour un nœud en batch
        """
        node_id = data.get("id")
        properties = data.get("properties", {})
        
        if not node_id:
            return {"success": False, "error": "ID manquant"}
        
        query = """
        MATCH (n {id: $id})
        SET n += $properties,
            n.updated_at = datetime()
        RETURN n
        """
        result = tx.run(query, {"id": node_id, "properties": properties})
        
        if result.single():
            return {"success": True}
        return {"success": False, "error": "Nœud non trouvé"}

    def _batch_delete_node(self, tx, data: Dict):
        """
        Supprime un nœud en batch
        """
        node_id = data.get("id")
        
        if not node_id:
            return {"success": False, "error": "ID manquant"}
        
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        result = tx.run(query, {"id": node_id})
        deleted = result.single().get('deleted', 0)
        
        if deleted > 0:
            return {"success": True}
        return {"success": False, "error": "Nœud non trouvé"}

    def import_batch_from_list(self, nodes: List[Dict], node_type: str) -> Dict:
        """
        Importe une liste de nœuds en batch
        """
        for node in nodes:
            self.add_to_batch("create_node", {
                "label": node_type,
                "properties": node
            })
        
        return self.flush()