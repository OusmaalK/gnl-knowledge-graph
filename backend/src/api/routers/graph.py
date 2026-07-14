"""
Router pour les opérations sur le graphe
Version corrigée avec imports FastAPI
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
import time

from ..schemas.graph import (
    NodeResponse,
    RelationshipResponse,
    GraphQueryRequest,
    GraphQueryResponse,
    NodeCreateRequest,
    RelationshipCreateRequest
)
from ..schemas.responses import PaginatedResponse
from ...core.exceptions import GNLException
from ...graph.operations.crud import GraphCRUD
from ...graph.operations.batch import BatchOperations
from ...core.config import settings

router = APIRouter()

# ============================================================
# QUERIES
# ============================================================

@router.post("/query", response_model=GraphQueryResponse)
async def execute_query(request: GraphQueryRequest):
    """
    Exécute une requête Cypher
    """
    try:
        crud = GraphCRUD()
        start_time = time.time()
        
        results = crud.execute_query(request.query, request.params)
        
        execution_time = (time.time() - start_time) * 1000
        
        return GraphQueryResponse(
            results=results[:request.limit],
            count=len(results),
            execution_time_ms=execution_time
        )
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la requête: {str(e)}",
            code="QUERY_ERROR",
            status_code=400
        )
    finally:
        crud.close()

@router.get("/nodes", response_model=PaginatedResponse[NodeResponse])
async def get_nodes(
    label: Optional[str] = Query(None, description="Filtrer par label"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Récupère les nœuds du graphe
    """
    try:
        crud = GraphCRUD()
        
        if label:
            nodes = crud.get_nodes_by_label(label, limit + offset)
        else:
            # Récupérer tous les nœuds
            query = "MATCH (n) RETURN n, labels(n) as labels LIMIT $limit"
            results = crud.execute_query(query, {"limit": limit + offset})
            nodes = [{"n": r.get('n'), "labels": r.get('labels')} for r in results]
        
        # Pagination
        paginated = nodes[offset:offset + limit]
        
        return PaginatedResponse(
            items=paginated,
            total=len(nodes),
            page=(offset // limit) + 1,
            per_page=limit,
            total_pages=(len(nodes) // limit) + (1 if len(nodes) % limit > 0 else 0)
        )
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la récupération des nœuds: {str(e)}",
            code="NODES_ERROR",
            status_code=400
        )
    finally:
        crud.close()

@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    """
    Récupère un nœud par son ID
    """
    try:
        crud = GraphCRUD()
        node = crud.get_node(node_id)
        
        if not node:
            raise HTTPException(status_code=404, detail=f"Nœud {node_id} non trouvé")
        
        return NodeResponse(
            id=node_id,
            labels=node.get('labels', []),
            properties=node.get('n', {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la récupération du nœud: {str(e)}",
            code="NODE_ERROR",
            status_code=400
        )
    finally:
        crud.close()

@router.get("/nodes/{node_id}/relationships")
async def get_node_relationships(
    node_id: str,
    direction: str = Query("BOTH", regex="^(BOTH|OUTGOING|INCOMING)$")
):
    """
    Récupère les relations d'un nœud
    """
    try:
        crud = GraphCRUD()
        relationships = crud.get_relationships(node_id, direction)
        return {"node_id": node_id, "relationships": relationships}
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la récupération des relations: {str(e)}",
            code="RELATIONSHIPS_ERROR",
            status_code=400
        )
    finally:
        crud.close()

# ============================================================
# CREATE
# ============================================================

@router.post("/nodes", response_model=NodeResponse)
async def create_node(request: NodeCreateRequest):
    """
    Crée un nouveau nœud
    """
    try:
        crud = GraphCRUD()
        result = crud.create_node(request.label, request.properties)
        
        if not result.get('success'):
            raise GNLException(
                message=result.get('error', "Erreur lors de la création"),
                code="CREATE_NODE_ERROR",
                status_code=400
            )
        
        node = result.get('data', {})
        return NodeResponse(
            id=node.get('n', {}).get('id'),
            labels=[request.label],
            properties=node.get('n', {})
        )
    except GNLException:
        raise
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la création du nœud: {str(e)}",
            code="CREATE_NODE_ERROR",
            status_code=400
        )
    finally:
        crud.close()

@router.post("/relationships", response_model=RelationshipResponse)
async def create_relationship(request: RelationshipCreateRequest):
    """
    Crée une nouvelle relation
    """
    try:
        crud = GraphCRUD()
        result = crud.create_relationship(
            request.type,
            request.source_id,
            request.target_id,
            request.properties
        )
        
        if not result.get('success'):
            raise GNLException(
                message=result.get('error', "Erreur lors de la création"),
                code="CREATE_RELATIONSHIP_ERROR",
                status_code=400
            )
        
        return RelationshipResponse(
            source=request.source_id,
            target=request.target_id,
            type=request.type,
            properties=request.properties
        )
    except GNLException:
        raise
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la création de la relation: {str(e)}",
            code="CREATE_RELATIONSHIP_ERROR",
            status_code=400
        )
    finally:
        crud.close()

# ============================================================
# DELETE
# ============================================================

@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """
    Supprime un nœud
    """
    try:
        crud = GraphCRUD()
        result = crud.delete_node(node_id)
        
        if not result.get('success'):
            raise GNLException(
                message=result.get('error', "Erreur lors de la suppression"),
                code="DELETE_NODE_ERROR",
                status_code=400
            )
        
        return {"success": True, "message": f"Nœud {node_id} supprimé"}
    except GNLException:
        raise
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la suppression du nœud: {str(e)}",
            code="DELETE_NODE_ERROR",
            status_code=400
        )
    finally:
        crud.close()