"""
Constantes du projet
"""

__version__ = "1.0.0"
__author__ = "GNL Team"

# Types de nœuds
NODE_TYPES = {
    "FOURNISSEUR": "Fournisseur",
    "TERMINAL": "Terminal",
    "METHANIER": "Méthanier",
    "PIPELINE": "Pipeline",
    "CLIENT": "Client",
    "STOCKAGE": "Stockage",
    "COMPRESSEUR": "Compresseur",
    "COMMANDE": "Commande",
    "INCIDENT": "Incident",
    "MAINTENANCE": "Maintenance"
}

# Types de relations
RELATIONSHIP_TYPES = {
    "FOURNIT": "FOURNIT",
    "LIVRE_A": "LIVRE_A",
    "ALIMENTE": "ALIMENTE",
    "DESSERT": "DESSERT",
    "STOCKE": "STOCKE",
    "DEPEND_DE": "DEPEND_DE",
    "HISTORIQUE": "HISTORIQUE",
    "AFFECTE": "AFFECTE",
    "CAUSE": "CAUSE",
    "EXPLOITE_PAR": "EXPLOITE_PAR",
    "DEPART_DE": "DEPART_DE",
    "ARRIVE_A": "ARRIVE_A"
}

# Gravités des incidents
INCIDENT_SEVERITIES = {
    "CRITIQUE": "critique",
    "MAJEUR": "majeur",
    "MINEUR": "mineur"
}

# Statuts
STATUS = {
    "ACTIF": "actif",
    "INACTIF": "inactif",
    "MAINTENANCE": "maintenance",
    "HORS_SERVICE": "hors_service",
    "EN_CONSTRUCTION": "en_construction",
    "EN_TEST": "en_test"
}

# Limites par défaut
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

# Cache
CACHE_TTL = {
    "SHORT": 60,      # 1 minute
    "MEDIUM": 3600,   # 1 heure
    "LONG": 86400,    # 24 heures
    "VERY_LONG": 604800  # 7 jours
}