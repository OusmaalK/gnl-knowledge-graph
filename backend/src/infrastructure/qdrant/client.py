"""
Client Qdrant - Gestion de la base vectorielle
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from qdrant_client import QdrantClient as QdrantBase
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Payload,
    UpdateResult
)
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantClient:
    """
    Client Qdrant pour la gestion des vecteurs
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialise le client Qdrant
        
        Args:
            host: Hôte Qdrant
            port: Port Qdrant
        """
        self.host = host or os.getenv('QDRANT_HOST', 'localhost')
        self.port = port or int(os.getenv('QDRANT_PORT', 6333))
        self.api_key = os.getenv('QDRANT_API_KEY')
        self.client = None
        self._vector_size = 768  # Dimension par défaut (BGE-M3)
        logger.info(f"🔗 Qdrant : {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """
        Établit la connexion à Qdrant
        """
        try:
            self.client = QdrantBase(
                host=self.host,
                port=self.port,
                api_key=self.api_key if self.api_key else None
            )
            # Vérifier la connexion
            self.client.get_collections()
            logger.info("✅ Connecté à Qdrant")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Qdrant : {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("🔒 Connexion Qdrant fermée")
    
    def create_collection(self, collection_name: str, vector_size: Optional[int] = None) -> bool:
        """
        Crée une collection Qdrant
        
        Args:
            collection_name: Nom de la collection
            vector_size: Dimension des vecteurs
        """
        if not self.client:
            if not self.connect():
                return False
        
        size = vector_size or self._vector_size
        
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection créée : {collection_name} (size: {size})")
            return True
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"ℹ️ Collection existe déjà : {collection_name}")
                return True
            logger.error(f"❌ Erreur création collection {collection_name} : {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Supprime une collection
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"🗑️ Collection supprimée : {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur suppression collection {collection_name} : {e}")
            return False
    
    def index_points(self, collection_name: str, points: List[Dict]) -> bool:
        """
        Indexe des points dans une collection
        
        Args:
            collection_name: Nom de la collection
            points: Liste des points à indexer
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            qdrant_points = []
            for point in points:
                qdrant_points.append(
                    PointStruct(
                        id=point.get('id'),
                        vector=point.get('vector'),
                        payload=point.get('payload', {})
                    )
                )
            
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
            logger.info(f"✅ {len(points)} points indexés dans {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur indexation dans {collection_name} : {e}")
            return False
    
    def search(self, collection_name: str, query_vector: np.ndarray, limit: int = 10) -> List[Dict]:
        """
        Recherche des points similaires
        
        Args:
            collection_name: Nom de la collection
            query_vector: Vecteur de requête
            limit: Nombre de résultats
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist(),
                limit=limit
            )
            
            return [
                {
                    'id': hit.id,
                    'score': hit.score,
                    'payload': hit.payload
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"❌ Erreur recherche dans {collection_name} : {e}")
            return []
    
    def search_by_filter(self, collection_name: str, filter_conditions: Dict, limit: int = 10) -> List[Dict]:
        """
        Recherche avec filtres sur le payload
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            # Construire le filtre
            field_conditions = []
            for key, value in filter_conditions.items():
                field_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            
            results = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                filter=Filter(
                    must=field_conditions
                )
            )
            
            points = results[0]
            return [
                {
                    'id': point.id,
                    'payload': point.payload
                }
                for point in points
            ]
        except Exception as e:
            logger.error(f"❌ Erreur recherche filtrée dans {collection_name} : {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        Récupère les informations d'une collection
        """
        if not self.client:
            if not self.connect():
                return {}
        
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                'name': collection_name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status,
                'vector_size': info.config.params.vectors.size if info.config else self._vector_size
            }
        except Exception as e:
            logger.error(f"❌ Erreur info collection {collection_name} : {e}")
            return {}

    def health_check(self) -> Dict:
        """
        Vérifie l'état de Qdrant
        """
        try:
            if not self.client:
                if not self.connect():
                    return {"status": "unhealthy", "error": "Connection failed"}
            
            collections = self.client.get_collections()
            return {
                "status": "healthy",
                "host": self.host,
                "port": self.port,
                "collections": len(collections.collections) if collections else 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test du client
    client = QdrantClient()
    print("Health :", client.health_check())
    client.close()