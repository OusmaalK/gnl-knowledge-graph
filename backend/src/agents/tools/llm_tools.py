"""
Outils LLM pour les agents IA - Version Multi-provider (OpenAI / Groq / Ollama)
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LLMTools:
    """
    Outils pour l'intégration avec les LLM (OpenAI, Groq, Ollama)
    """
    
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'groq') # Par défaut groq
        self.model = os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')
        self.api_key = os.getenv('LLM_API_KEY', '')
        
        self._client = None
        
        # Initialisation selon le provider
        if self.provider == 'openai' and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
                logger.info(f"✅ OpenAI client initialisé avec {self.model}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur OpenAI: {e}")

        elif self.provider == 'groq' and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info(f"✅ Groq client initialisé avec {self.model}")
            except ImportError:
                logger.warning("⚠️ Groq non installé (pip install groq)")
            except Exception as e:
                logger.warning(f"⚠️ Erreur Groq: {e}")
                
        else:
            logger.info(f"🤖 Aucun client LLM connecté. Provider: {self.provider}")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Génère une réponse en utilisant le provider configuré
        """
        if self.provider in ['openai', 'groq'] and self._client:
            return self._generate_llm(prompt, context)
        else:
            return self._generate_fallback(prompt, context)
    
    def _generate_llm(self, prompt: str, context: str) -> str:
        """
        Appel unifié à l'API OpenAI ou Groq
        """
        try:
            if not self._client:
                return self._generate_fallback(prompt, context)
            
            system_prompt = f"""
Tu es un expert en transport de Gaz Naturel Liquéfié (GNL) et en réseaux de pipelines.

Voici les données du réseau GNL :
{context}

**Instructions :**
- Réponds en français
- Si la question concerne les données du réseau, utilise-les
- Si la question est générale sur le GNL, réponds avec tes connaissances
- Sois structuré et professionnel
- Utilise des émojis pour illustrer les points clés
- Si tu ne connais pas une information, dis-le honnêtement
"""
            
            # Appel générique (OpenAI et Groq ont la même signature de méthode)
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Erreur LLM ({self.provider}): {e}")
            return self._generate_fallback(prompt, context)
    
    def _generate_fallback(self, prompt: str, context: str) -> str:
        """
        Réponse de fallback
        """
        return f"""
📊 **ANALYSE DU RÉSEAU GNL (Mode Fallback)**

📋 **Votre question :** "{prompt}"

🔍 **Contexte disponible :**
{context if context else "Aucun contexte spécifique"}

💡 **Diagnostic :**
Le client LLM n'a pas pu être initialisé. Vérifiez votre fichier .env.

⚠️ *Cette réponse est générée en mode fallback.*
"""
    
    def enrich_with_context(self, question: str, graph_context: str) -> str:
        """
        Enrichit une question avec le contexte du graphe
        """
        prompt = f"""
Tu es un expert GNL. Utilise les données suivantes pour répondre à la question.

**Données du réseau :**
{graph_context}

**Question :** {question}

**Réponse :**
"""
        return self.generate_response(prompt, graph_context)