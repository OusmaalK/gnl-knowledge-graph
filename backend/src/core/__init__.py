"""
Core du projet GNL Knowledge Graph
Configuration, constantes et exceptions
"""

from .config import settings
from .constants import __version__, __author__
from .exceptions import GNLException
from .types import Node, Relationship, Graph

__all__ = [
    'settings',
    '__version__',
    '__author__',
    'GNLException',
    'Node',
    'Relationship',
    'Graph'
]