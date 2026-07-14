"""
Types personnalisés pour le projet
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Property:
    """Propriété d'un nœud ou relation"""
    name: str
    value: Any
    type: str = "string"  # string, number, boolean, datetime

@dataclass
class Node:
    """Représentation d'un nœud Neo4j"""
    id: str
    labels: List[str]
    properties: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Récupère une propriété"""
        return self.properties.get(name, default)
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Relationship:
    """Représentation d'une relation Neo4j"""
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Graph:
    """Représentation d'un graphe"""
    nodes: List[Node] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    
    def add_node(self, node: Node):
        """Ajoute un nœud"""
        self.nodes.append(node)
    
    def add_relationship(self, relationship: Relationship):
        """Ajoute une relation"""
        self.relationships.append(relationship)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Récupère un nœud"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_relationships(self, node_id: str) -> List[Relationship]:
        """Récupère les relations d'un nœud"""
        result = []
        for rel in self.relationships:
            if rel.source_id == node_id or rel.target_id == node_id:
                result.append(rel)
        return result
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "relationships": [r.to_dict() for r in self.relationships]
        }

# Type alias pour les données
DataDict = Dict[str, Any]
DataList = List[DataDict]
NodeDict = Dict[str, Any]
RelationshipDict = Dict[str, Any]