"""
Routeur WebSocket pour le chat en temps réel
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Endpoint WebSocket pour le chat"""
    await websocket.accept()
    logger.info("✅ WebSocket client connecté")
    
    try:
        # Envoyer un message de bienvenue
        await websocket.send_text(json.dumps({
            "type": "connected",
            "content": "✅ Connecté au serveur WebSocket"
        }))
        
        while True:
            # Recevoir les messages du client
            data = await websocket.receive_text()
            logger.info(f"📥 Message reçu: {data[:50]}...")
            
            # Répondre avec un echo (pour le test)
            await websocket.send_text(json.dumps({
                "type": "response",
                "content": f"📨 Message reçu: {data}"
            }))
            
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client déconnecté")
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}")