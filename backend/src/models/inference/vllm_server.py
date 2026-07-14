"""
Serveur vLLM pour l'inférence haute performance
"""

import logging
import os
import subprocess
import time
from typing import Dict, Any, Optional
import requests
import json
import threading

logger = logging.getLogger(__name__)

class VLLMServer:
    """
    Gestionnaire du serveur vLLM
    """
    
    def __init__(self, model_name: str = "llama3:70b", port: int = 8000):
        """
        Initialise le serveur vLLM
        
        Args:
            model_name: Nom du modèle
            port: Port du serveur
        """
        self.model_name = model_name
        self.port = port
        self.process = None
        self._is_running = False
        self._lock = threading.Lock()
        logger.info(f"🔄 vLLM Server - Modèle: {model_name}, Port: {port}")
    
    def start(self, gpu_memory_utilization: float = 0.8, tensor_parallel_size: int = 1) -> bool:
        """
        Démarre le serveur vLLM
        """
        with self._lock:
            if self._is_running:
                logger.warning("⚠️ Serveur déjà en cours")
                return True
            
            try:
                # Vérifier que vLLM est installé
                import vllm
                
                # Démarrer le serveur
                cmd = [
                    "python", "-m", "vllm.entrypoints.api_server",
                    "--model", self.model_name,
                    "--port", str(self.port),
                    "--gpu-memory-utilization", str(gpu_memory_utilization),
                    "--tensor-parallel-size", str(tensor_parallel_size),
                    "--max-num-seqs", "256",
                    "--disable-log-requests"
                ]
                
                logger.info(f"🚀 Démarrage de vLLM avec: {' '.join(cmd)}")
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Attendre que le serveur soit prêt
                time.sleep(10)
                self._is_running = True
                logger.info(f"✅ Serveur vLLM démarré (PID: {self.process.pid})")
                return True
                
            except ImportError:
                logger.warning("⚠️ vLLM non installé, installation...")
                subprocess.run(["pip", "install", "vllm"], check=True)
                return self.start(gpu_memory_utilization, tensor_parallel_size)
                
            except Exception as e:
                logger.error(f"❌ Erreur démarrage vLLM : {e}")
                return False
    
    def stop(self):
        """
        Arrête le serveur vLLM
        """
        with self._lock:
            if not self._is_running:
                logger.warning("⚠️ Serveur déjà arrêté")
                return
            
            if self.process:
                self.process.terminate()
                self.process.wait()
                self.process = None
                self._is_running = False
                logger.info("⏹️ Serveur vLLM arrêté")
    
    def is_running(self) -> bool:
        """
        Vérifie si le serveur est en cours
        """
        if self._is_running and self.process:
            return self.process.poll() is None
        return False
    
    def health_check(self) -> Dict:
        """
        Vérifie l'état du serveur
        """
        try:
            response = requests.get(f"http://localhost:{self.port}/health", timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "port": self.port,
                "model": self.model_name,
                "running": self.is_running()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "port": self.port,
                "error": str(e),
                "running": self.is_running()
            }
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Génère une réponse via le serveur vLLM
        """
        if not self.is_running():
            self.start()
        
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get('max_tokens', 2048),
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9),
                "stream": False
            }
            
            response = requests.post(
                f"http://localhost:{self.port}/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('text', '')
            else:
                logger.error(f"❌ Erreur API : {response.status_code}")
                return f"❌ Erreur : {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erreur génération vLLM : {e}")
            return f"❌ Erreur : {str(e)}"

if __name__ == "__main__":
    # Test du serveur vLLM
    server = VLLMServer()
    print("Health:", server.health_check())