"""
Indexeur Qdrant pour les embeddings
Phase 3 - Stockage et recherche vectorielle
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import os
from dotenv import load_dotenv
import logging
import numpy as np
from typing import List, Dict, Any, Optional
import json

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QdrantIndexer:
    """
    Indexeur pour les embeddings vectoriels avec Qdrant
    """
    
    def __init__(self):
        self.host = os.getenv('QDRANT_HOST', 'localhost')
        self.port = int(os.getenv('QDRANT_PORT', 6333))
        self.api_key = os.getenv('QDRANT_API_KEY', '')
        self.client = None
        self.vector_size = 768  # Dimension des embeddings
        self.collection_name = "gnl_knowledge"
        logger.info(f"🔗 Qdrant : {self.host}:{self.port}")

    def connect(self):
        """Établit la connexion à Qdrant"""
        try:
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key if self.api_key else None
            )
            logger.info("✅ Connecté à Qdrant")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Qdrant : {e}")
            return False

    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            logger.info("🔒 Connexion Qdrant fermée")

    def create_collection(self, collection_name: Optional[str] = None):
        """
        Crée une collection Qdrant
        """
        name = collection_name or self.collection_name
        
        if not self.connect():
            return False
        
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection créée : {name}")
            return True
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"ℹ️ Collection existe déjà : {name}")
                return True
            logger.error(f"❌ Erreur création collection : {e}")
            return False
        finally:
            self.close()

    def index_documents(self, documents: List[Dict], embeddings: List[np.ndarray], 
                        collection_name: Optional[str] = None):
        """
        Indexe des documents avec leurs embeddings
        """
        name = collection_name or self.collection_name
        
        if not documents or not embeddings:
            logger.error("❌ Documents ou embeddings vides")
            return {"success": False, "error": "Données vides"}
        
        if len(documents) != len(embeddings):
            logger.error("❌ Nombre de documents et embeddings différent")
            return {"success": False, "error": "Dimensions mismatch"}
        
        if not self.connect():
            return {"success": False, "error": "Connexion impossible"}
        
        try:
            points = []
            for i, (doc, emb) in enumerate(zip(documents, embeddings)):
                points.append(
                    PointStruct(
                        id=i,
                        vector=emb.tolist() if isinstance(emb, np.ndarray) else emb,
                        payload={
                            "id": doc.get('id', f"doc_{i}"),
                            "content": doc.get('content', ''),
                            "metadata": doc.get('metadata', {}),
                            "source": doc.get('source', 'unknown')
                        }
                    )
                )
            
            self.client.upsert(
                collection_name=name,
                points=points
            )
            logger.info(f"✅ {len(points)} documents indexés dans Qdrant")
            return {"success": True, "count": len(points)}
        except Exception as e:
            logger.error(f"❌ Erreur indexation Qdrant : {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.close()

    def search(self, query_vector: np.ndarray, limit: int = 10, 
               collection_name: Optional[str] = None) -> List[Dict]:
        """
        Recherche les documents similaires
        """
        name = collection_name or self.collection_name
        
        if not self.connect():
            return []
        
        try:
            results = self.client.search(
                collection_name=name,
                query_vector=query_vector.tolist(),
                limit=limit
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                    "vector": hit.vector if hasattr(hit, 'vector') else None
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"❌ Erreur recherche Qdrant : {e}")
            return []
        finally:
            self.close()

    def search_by_payload(self, filter_field: str, filter_value: Any, 
                          limit: int = 10, collection_name: Optional[str] = None) -> List[Dict]:
        """
        Recherche par payload (filtrage)
        """
        name = collection_name or self.collection_name
        
        if not self.connect():
            return []
        
        try:
            results = self.client.scroll(
                collection_name=name,
                limit=limit,
                with_payload=True,
                filter=Filter(
                    must=[
                        FieldCondition(
                            key=f"metadata.{filter_field}",
                            match=MatchValue(value=filter_value)
                        )
                    ]
                )
            )
            
            points = results[0]
            return [
                {
                    "id": point.id,
                    "payload": point.payload,
                    "vector": point.vector if hasattr(point, 'vector') else None
                }
                for point in points
            ]
        except Exception as e:
            logger.error(f"❌ Erreur recherche par payload : {e}")
            return []
        finally:
            self.close()

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict:
        """
        Récupère les informations de la collection
        """
        name = collection_name or self.collection_name
        
        if not self.connect():
            return {"error": "Connexion impossible"}
        
        try:
            info = self.client.get_collection(collection_name=name)
            return {
                "name": name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"❌ Erreur info collection : {e}")
            return {"error": str(e)}
        finally:
            self.close()

    def delete_collection(self, collection_name: Optional[str] = None):
        """
        Supprime une collection
        """
        name = collection_name or self.collection_name
        
        if not self.connect():
            return {"success": False, "error": "Connexion impossible"}
        
        try:
            self.client.delete_collection(collection_name=name)
            logger.info(f"🗑️ Collection supprimée : {name}")
            return {"success": True}
        except Exception as e:
            logger.error(f"❌ Erreur suppression : {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.close()


# ============================================================
# GÉNÉRATION D'EMBEDDINGS SIMULÉS (pour test)
# ============================================================

def generate_mock_embeddings(texts: List[str], dimension: int = 768) -> List[np.ndarray]:
    """
    Génère des embeddings simulés (pour test)
    """
    np.random.seed(42)
    return [np.random.randn(dimension) for _ in texts]


if __name__ == "__main__":
    # Test de l'indexeur
    indexer = QdrantIndexer()
    indexer.create_collection()
    
    # Test d'indexation
    docs = [
        {"id": "doc1", "content": "Pipeline Nord-Sud incident", "source": "incidents"},
        {"id": "doc2", "content": "Maintenance du compresseur", "source": "maintenance"},
    ]
    embeddings = generate_mock_embeddings([d['content'] for d in docs])
    
    result = indexer.index_documents(docs, embeddings)
    print(result)