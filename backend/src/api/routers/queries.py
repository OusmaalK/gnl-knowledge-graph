"""
Router pour les requêtes d'analyse avancées
Version corrigée avec imports FastAPI
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from ...graph.queries.impact_analysis import ImpactAnalysis
from ...graph.queries.route_finder import RouteFinder
from ...graph.queries.risk_prediction import RiskPredictor
from ...graph.queries.historical_analysis import HistoricalAnalysis
from ...core.exceptions import GNLException

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================
# IMPACT ANALYSIS
# ============================================================

@router.get("/impact")
async def analyze_impact(
    equipment_id: str = Query(..., description="ID de l'équipement")
):
    """
    Analyse l'impact d'un équipement
    """
    try:
        analysis = ImpactAnalysis()
        analysis.connect()
        
        result = analysis.get_impacted_clients(equipment_id)
        
        analysis.close()
        return {"impact": result}
    except Exception as e:
        logger.error(f"Erreur analyse d'impact: {e}")
        raise GNLException(
            message=f"Erreur lors de l'analyse d'impact: {str(e)}",
            code="IMPACT_ERROR",
            status_code=500
        )

@router.get("/impact/chain")
async def get_impact_chain():
    """
    Récupère la chaîne d'impact complète
    """
    try:
        analysis = ImpactAnalysis()
        analysis.connect()
        
        result = analysis.get_full_chain()
        
        analysis.close()
        return {"chain": result}
    except Exception as e:
        logger.error(f"Erreur récupération chaîne d'impact: {e}")
        raise GNLException(
            message=f"Erreur lors de la récupération de la chaîne d'impact: {str(e)}",
            code="IMPACT_CHAIN_ERROR",
            status_code=500
        )

# ============================================================
# HISTORY
# ============================================================

@router.get("/history/incidents")
async def get_incident_history(
    equipment_id: Optional[str] = Query(None, description="ID de l'équipement"),
    start_date: Optional[str] = Query(None, description="Date de début (ISO)"),
    end_date: Optional[str] = Query(None, description="Date de fin (ISO)"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère l'historique des incidents
    """
    try:
        analysis = HistoricalAnalysis()
        analysis.connect()
        
        if start_date and end_date:
            incidents = analysis.get_incidents_by_date_range(start_date, end_date)
        elif equipment_id:
            incidents = analysis.get_nodes_by_type('Incident')
            # Filtrer par équipement (simplifié)
            filtered = []
            for inc in incidents:
                if 'equipment_id' in inc.get('n', {}) and inc['n']['equipment_id'] == equipment_id:
                    filtered.append(inc)
            incidents = filtered
        else:
            incidents = analysis.get_nodes_by_type('Incident')
        
        analysis.close()
        return {"incidents": incidents[:limit], "total": len(incidents)}
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        raise GNLException(
            message=f"Erreur lors de la récupération de l'historique: {str(e)}",
            code="HISTORY_ERROR",
            status_code=500
        )

@router.get("/history/statistics")
async def get_incident_statistics():
    """
    Récupère les statistiques des incidents
    """
    try:
        analysis = HistoricalAnalysis()
        analysis.connect()
        
        stats = analysis.get_full_historical_report()
        
        analysis.close()
        return stats
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        raise GNLException(
            message=f"Erreur lors de la récupération des statistiques: {str(e)}",
            code="STATISTICS_ERROR",
            status_code=500
        )

# ============================================================
# RISK PREDICTION
# ============================================================

@router.get("/risk/predict")
async def predict_risk(
    equipment_id: str = Query(..., description="ID de l'équipement")
):
    """
    Prédit le risque d'un équipement
    """
    try:
        predictor = RiskPredictor()
        predictor.connect()
        
        risk = predictor.get_risk_score(equipment_id)
        
        predictor.close()
        return {"risk": risk}
    except Exception as e:
        logger.error(f"Erreur prédiction de risque: {e}")
        raise GNLException(
            message=f"Erreur lors de la prédiction de risque: {str(e)}",
            code="RISK_PREDICTION_ERROR",
            status_code=500
        )

@router.get("/risk/alerts")
async def get_risk_alerts():
    """
    Récupère les alertes de risque
    """
    try:
        predictor = RiskPredictor()
        predictor.connect()
        
        alerts = predictor.get_predictive_alerts()
        
        predictor.close()
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Erreur récupération alertes: {e}")
        raise GNLException(
            message=f"Erreur lors de la récupération des alertes: {str(e)}",
            code="ALERTS_ERROR",
            status_code=500
        )

# ============================================================
# ROUTES
# ============================================================

@router.get("/routes")
async def find_route(
    start_id: str = Query(..., description="ID du nœud de départ"),
    end_id: str = Query(..., description="ID du nœud d'arrivée"),
    exclude_id: Optional[str] = Query(None, description="ID du nœud à exclure")
):
    """
    Trouve une route entre deux nœuds
    """
    try:
        finder = RouteFinder()
        finder.connect()
        
        if exclude_id:
            route = finder.find_alternative_route(start_id, end_id, exclude_id)
        else:
            route = finder.find_shortest_path(start_id, end_id)
        
        finder.close()
        return {"route": route}
    except Exception as e:
        logger.error(f"Erreur recherche de route: {e}")
        raise GNLException(
            message=f"Erreur lors de la recherche de route: {str(e)}",
            code="ROUTE_FINDER_ERROR",
            status_code=500
        )