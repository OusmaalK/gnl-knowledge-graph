"""
Module Qdrant pour la gestion de la base vectorielle
"""

from .client import QdrantClient
from .collections import COLLECTIONS, create_collections

__all__ = [
    'QdrantClient',
    'COLLECTIONS',
    'create_collections'
]