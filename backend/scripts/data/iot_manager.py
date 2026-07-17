import subprocess
import os
import signal
import time
import sys

# Dossier où se trouve le script listener
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LISTENER_SCRIPT = os.path.join(BASE_DIR, 'iot_listener.py')

_process = None

def start_listener():
    """Démarre le processus iot_listener.py en arrière-plan."""
    global _process
    if is_running():
        return {"status": "already_running", "message": "L'écouteur est déjà actif."}
    
    try:
        # Lancer le script en arrière-plan (sans terminal)
        # 'start' est nécessaire sur Windows pour lancer un processus détaché
        _process = subprocess.Popen(
            [sys.executable, LISTENER_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return {"status": "started", "message": "Écouteur démarré avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur de démarrage: {e}"}

def stop_listener():
    """Arrête le processus iot_listener.py."""
    global _process
    if not is_running():
        return {"status": "not_running", "message": "L'écouteur n'est pas actif."}
    
    try:
        _process.terminate()
        _process.wait(timeout=5)
        _process = None
        return {"status": "stopped", "message": "Écouteur arrêté avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur d'arrêt: {e}"}

def get_status():
    """Retourne l'état actuel de l'écouteur."""
    return {"running": _process is not None and _process.poll() is None}

def is_running():
    return _process is not None and _process.poll() is None
