"""
Router pour le chat avec LLM externe
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time
import logging

from ...agents.tools.llm_tools import LLMTools

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    agent_type: Optional[str] = "general"
    context: Optional[str] = ""

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    execution_time_ms: float
    provider: str

@router.post("/chat/advanced", response_model=ChatResponse)
async def advanced_chat(request: ChatRequest):
    """
    Chat avec LLM externe (Gemini, OpenAI, Ollama)
    """
    start_time = time.time()
    
    try:
        llm = LLMTools()
        response = llm.generate_response(request.question, request.context)
        
        execution_time = (time.time() - start_time) * 1000
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            execution_time_ms=execution_time,
            provider=llm.provider
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur chat avancé: {e}")
        raise HTTPException(status_code=500, detail=str(e))