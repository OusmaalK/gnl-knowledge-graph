"""
Configuration des collections Qdrant
"""

# Configuration des collections
COLLECTIONS = {
    # Embeddings des documents d'incidents
    'gnl_incidents_embeddings': {
        'description': 'Embeddings des rapports d\'incidents',
        'vector_size': 768,
    },
    
    # Embeddings des documents de maintenance
    'gnl_maintenance_embeddings': {
        'description': 'Embeddings des rapports de maintenance',
        'vector_size': 768,
    },
    
    # Embeddings des documents logistiques
    'gnl_logistics_embeddings': {
        'description': 'Embeddings des données logistiques',
        'vector_size': 768,
    },
    
    # Embeddings des documents réglementaires
    'gnl_regulatory_embeddings': {
        'description': 'Embeddings des documents réglementaires',
        'vector_size': 768,
    },
    
    # Embeddings des connaissances générales
    'gnl_knowledge': {
        'description': 'Embeddings des connaissances GNL',
        'vector_size': 768,
    }
}

def create_collections(client, collections: dict = None):
    """
    Crée toutes les collections configurées
    
    Args:
        client: Instance de QdrantClient
        collections: Configuration des collections
    """
    from .client import QdrantClient
    
    if not isinstance(client, QdrantClient):
        client = QdrantClient()
    
    collections_config = collections or COLLECTIONS
    
    for collection_name, config in collections_config.items():
        client.create_collection(
            collection_name=collection_name,
            vector_size=config.get('vector_size', 768)
        )
    
    client.close()

def get_collection_names() -> list:
    """
    Retourne la liste des noms de collections
    """
    return list(COLLECTIONS.keys())

def get_collection_config(collection_name: str) -> dict:
    """
    Retourne la configuration d'une collection
    """
    return COLLECTIONS.get(collection_name, {})

if __name__ == "__main__":
    from .client import QdrantClient
    
    client = QdrantClient()
    if client.connect():
        create_collections(client)
        print("✅ Collections créées avec succès")
        client.close()