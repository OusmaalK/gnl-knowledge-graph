"""
Router pour les agents IA
Version corrigée avec imports FastAPI
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import time
import re
from pydantic import BaseModel

from ..schemas.agents import (
    ChatRequest,
    ChatResponse,
    AgentRequest,
    AgentResponse,
    DiagnosticRequest,
    RouteRequest,
    RiskRequest,
    AgentType
)
from ..schemas.responses import SuccessResponse
from ...core.exceptions import GNLException
from ...agents import DiagnosticAgent, LogisticsAgent, MaintenanceAgent
from ...agents.agents.incident_agent import IncidentAgent

# ============================================================
# MODÈLES ADDITIONNELS
# ============================================================

class SimpleChatRequest(BaseModel):
    question: str
    agent_type: str = "diagnostic"
    conversation_id: Optional[str] = None
    incident_id: Optional[str] = None
    equipment_id: Optional[str] = None
    start_id: Optional[str] = None
    end_id: Optional[str] = None

router = APIRouter()

# ============================================================
# CHAT - VERSION SIMPLIFIÉE POUR LE FRONTEND
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Dialogue avec un agent IA
    """
    start_time = time.time()
    
    try:
        agent = None
        response = ""
        
        # Vérifier si la question contient des IDs
        incident_match = re.search(r'INC-\d{3,4}', request.question)
        equipment_match = re.search(r'PIPE-\d{3,4}|COMP-\d{3,4}|TERM-\d{3,4}', request.question)
        route_match = re.search(r'route.*?(\w+-\d+).*?(\w+-\d+)', request.question, re.IGNORECASE)
        
        if request.agent_type == "diagnostic" or request.agent_type == AgentType.DIAGNOSTIC:
            agent = DiagnosticAgent()
            if incident_match:
                response = agent.diagnose_incident(incident_match.group())
            elif equipment_match:
                response = f"🔍 Analyse de l'équipement {equipment_match.group()}\n\n"
                response += agent.analyze_pattern()
            else:
                response = agent.analyze_pattern()
                
        elif request.agent_type == "incident" or request.agent_type == AgentType.INCIDENT:
            agent = IncidentAgent()
            if incident_match:
                response = f"📋 Détails de l'incident {incident_match.group()}\n\n"
                # Récupérer les détails de l'incident
                response += await diagnose_incident(DiagnosticRequest(incident_id=incident_match.group()))
                response = response.result if hasattr(response, 'result') else str(response)
            else:
                response = agent.list_incidents(request.equipment_id)
            
        elif request.agent_type == "logistics" or request.agent_type == AgentType.LOGISTICS:
            agent = LogisticsAgent()
            if route_match:
                start_id = route_match.group(1)
                end_id = route_match.group(2)
                response = agent.find_best_route(start_id, end_id)
            elif request.start_id and request.end_id:
                response = agent.find_best_route(request.start_id, request.end_id)
            elif equipment_match:
                response = agent.analyze_impact(equipment_match.group())
            else:
                response = agent.general_analysis()
                
        elif request.agent_type == "maintenance" or request.agent_type == AgentType.MAINTENANCE:
            agent = MaintenanceAgent()
            if equipment_match:
                response = agent.analyze_risk(equipment_match.group())
            elif request.equipment_id:
                response = agent.analyze_risk(request.equipment_id)
            else:
                response = agent.general_analysis()
        
        else:
            # Agent par défaut
            agent = DiagnosticAgent()
            response = "🤖 Assistant GNL\n\n"
            response += "Je suis votre assistant pour le réseau de gaz naturel liquéfié.\n\n"
            response += "**Questions possibles :**\n"
            response += "- 🔍 Diagnostiquer un incident (ex: INC-001)\n"
            response += "- 🗺️ Trouver une route (ex: TERM-001 → CLIENT-001)\n"
            response += "- 📊 Analyser un risque (ex: PIPE-001)\n"
            response += "- 📋 Lister les incidents\n\n"
            response += "💡 **Astuce :** Précisez le type d'agent pour une réponse plus ciblée."
        
        execution_time = (time.time() - start_time) * 1000
        
        # Si la réponse est un objet, la convertir en chaîne
        if hasattr(response, 'result'):
            response = response.result
        elif not isinstance(response, str):
            response = str(response)
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type.value if hasattr(request.agent_type, 'value') else str(request.agent_type),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        # Retourner une erreur structurée
        return ChatResponse(
            response=f"❌ Erreur: {str(e)}\n\n💡 Assurez-vous que le backend est correctement configuré.",
            agent_type=request.agent_type.value if hasattr(request.agent_type, 'value') else str(request.agent_type),
            execution_time_ms=(time.time() - start_time) * 1000
        )
    finally:
        if agent:
            try:
                agent.close()
            except:
                pass

# ============================================================
# DIAGNOSTIC
# ============================================================

@router.post("/diagnostic", response_model=AgentResponse)
async def diagnose_incident(request: DiagnosticRequest):
    """
    Diagnostique un incident
    """
    try:
        agent = DiagnosticAgent()
        result = agent.diagnose_incident(request.incident_id)
        agent.close()
        
        return AgentResponse(
            result=result,
            success=True,
            message=f"Diagnostic de l'incident {request.incident_id} terminé"
        )
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors du diagnostic: {str(e)}",
            code="DIAGNOSTIC_ERROR",
            status_code=500
        )

@router.get("/diagnostic/patterns")
async def analyze_patterns():
    """
    Analyse les patterns d'incidents
    """
    try:
        agent = DiagnosticAgent()
        result = agent.analyze_pattern()
        agent.close()
        
        return {"patterns": result}
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de l'analyse des patterns: {str(e)}",
            code="PATTERN_ERROR",
            status_code=500
        )

# ============================================================
# ROUTES
# ============================================================

@router.post("/routes", response_model=AgentResponse)
async def find_route(request: RouteRequest):
    """
    Trouve une route entre deux nœuds
    """
    try:
        agent = LogisticsAgent()
        result = agent.find_best_route(request.start_id, request.end_id)
        agent.close()
        
        return AgentResponse(
            result=result,
            success=True,
            message=f"Route trouvée entre {request.start_id} et {request.end_id}"
        )
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la recherche de route: {str(e)}",
            code="ROUTE_ERROR",
            status_code=500
        )

@router.post("/routes/alternative")
async def find_alternative_route(request: RouteRequest):
    """
    Trouve une route alternative
    """
    try:
        agent = LogisticsAgent()
        if request.exclude_id:
            result = agent.find_alternative_route(
                request.start_id, 
                request.end_id, 
                request.exclude_id
            )
        else:
            result = agent.find_best_route(request.start_id, request.end_id)
        agent.close()
        
        return {
            "route": result,
            "start": request.start_id,
            "end": request.end_id,
            "excluded": request.exclude_id
        }
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la recherche de route alternative: {str(e)}",
            code="ROUTE_ERROR",
            status_code=500
        )

# ============================================================
# RISK
# ============================================================

@router.post("/risk", response_model=AgentResponse)
async def analyze_risk(request: RiskRequest):
    """
    Analyse le risque d'un équipement
    """
    try:
        agent = MaintenanceAgent()
        result = agent.analyze_risk(request.equipment_id)
        agent.close()
        
        return AgentResponse(
            result=result,
            success=True,
            message=f"Analyse de risque pour {request.equipment_id} terminée"
        )
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de l'analyse de risque: {str(e)}",
            code="RISK_ERROR",
            status_code=500
        )

@router.get("/risk/critical")
async def get_critical_equipment():
    """
    Récupère les équipements critiques
    """
    try:
        agent = MaintenanceAgent()
        result = agent.get_critical_equipment()
        agent.close()
        
        return {"critical_equipment": result}
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la récupération des équipements critiques: {str(e)}",
            code="CRITICAL_ERROR",
            status_code=500
        )

@router.post("/risk/maintenance")
async def plan_maintenance(request: RiskRequest):
    """
    Planifie la maintenance d'un équipement
    """
    try:
        agent = MaintenanceAgent()
        result = agent.plan_maintenance(request.equipment_id)
        agent.close()
        
        return {"maintenance_plan": result}
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la planification de maintenance: {str(e)}",
            code="MAINTENANCE_ERROR",
            status_code=500
        )

# ============================================================
# SUPPLY CHAIN
# ============================================================

@router.get("/supply-chain")
async def get_supply_chain():
    """
    Récupère la chaîne d'approvisionnement
    """
    try:
        agent = LogisticsAgent()
        result = agent.get_supply_chain()
        agent.close()
        
        return {"supply_chain": result}
    except Exception as e:
        raise GNLException(
            message=f"Erreur lors de la récupération de la chaîne d'approvisionnement: {str(e)}",
            code="SUPPLY_CHAIN_ERROR",
            status_code=500
        )

# ============================================================
# CHAT SIMPLIFIÉ POUR FRONTEND
# ============================================================

@router.post("/chat/simple")
async def simple_chat(request: SimpleChatRequest):
    """
    Version simplifiée du chat pour le frontend
    """
    start_time = time.time()
    
    try:
        # Convertir en ChatRequest
        chat_request = ChatRequest(
            question=request.question,
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            incident_id=request.incident_id,
            equipment_id=request.equipment_id,
            start_id=request.start_id,
            end_id=request.end_id
        )
        
        result = await chat_with_agent(chat_request)
        return result
        
    except Exception as e:
        return ChatResponse(
            response=f"❌ Erreur: {str(e)}",
            agent_type=request.agent_type,
            execution_time_ms=(time.time() - start_time) * 1000
        )