#!/usr/bin/env python3
"""
IoT Data Listener - Version Pro avec Génération d'Incidents Automatiques
Path: backend/scripts/data/iot_listener.py
Version: Ultra-robuste (Mode binaire pur)
"""

import paho.mqtt.client as mqtt
import json
import os
import requests
from datetime import datetime

# ========================================================
# CONFIGURATION
# ========================================================
DEFAULT_CONFIG = {
    "mqtt_broker": "localhost",
    "mqtt_port": 1883,
    "mqtt_topic": "gnl/+/sensors",
    "neo4j_label": "SensorData",
    "alert_threshold_temperature": 80,
    "alert_threshold_pression": 20
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, '../../data/raw/iot')
os.makedirs(SAVE_DIR, exist_ok=True)

# Variables globales
config = {}
incident_created_for = {}  # Pour éviter de créer plusieurs fois le même incident

# ========================================================
# FONCTIONS UTILITAIRES
# ========================================================

def get_filename():
    return f"sensors_{datetime.now().strftime('%Y-%m-%d')}.json"

def save_to_json(payload):
    filename = os.path.join(SAVE_DIR, get_filename())
    data = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = []
    data.append(payload)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return filename

def decode_payload_safely(raw_bytes):
    """
    Décode le payload binaire en nettoyant les octets illégaux.
    Cette fonction lit octet par octet et garde uniquement les caractères ASCII/UTF-8 valides.
    """
    if not raw_bytes:
        return ""
    
    # Filtrer pour ne garder que les caractères imprimables (ASCII) et UTF-8 étendus
    # Cela supprime automatiquement le BOM 0xFF, les null bytes, et autres parasites
    filtered_bytes = bytes([b for b in raw_bytes if 32 <= b <= 126 or b >= 128])
    
    try:
        # Essayer de décoder en UTF-8 en ignorant les erreurs résiduelles
        return filtered_bytes.decode('utf-8', errors='ignore').strip()
    except:
        return ""

def fetch_config_from_api():
    try:
        response = requests.get("http://localhost:8000/api/settings/iot", timeout=5)
        if response.status_code == 200:
            print("✅ Configuration chargée depuis Neo4j (via API)")
            return response.json()
    except:
        pass
    print("⚠️ Utilisation des valeurs par défaut.")
    return DEFAULT_CONFIG

def create_incident_in_neo4j(equipment_id, reason, value, threshold):
    """
    Envoie une requête au Backend pour créer un incident critique dans Neo4j.
    """
    incident_id = f"INC-IOT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    payload = {
        "id": incident_id,
        "description": f"Dépassement de seuil critique sur {equipment_id} : {reason} = {value} (Seuil: {threshold})",
        "gravite": "critique",
        "date": datetime.now().isoformat(),
        "cause": "Capteur IoT",
        "duree_min": 0,
        "equipment_id": equipment_id
    }
    
    try:
        # Envoyer au backend pour création dans Neo4j
        response = requests.post("http://localhost:8000/api/incidents/auto", json=payload, timeout=5)
        if response.status_code == 200:
            print(f"🚨 INCIDENT CRÉÉ AUTOMATIQUEMENT : {incident_id} pour {equipment_id}")
            return True
        else:
            print(f"❌ Erreur création incident (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erreur réseau création incident: {e}")
        return False

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connecté au broker MQTT ({config['mqtt_broker']}:{config['mqtt_port']})")
        client.subscribe(config['mqtt_topic'])
        print(f"📡 Abonné au topic : {config['mqtt_topic']}")
    else:
        print(f"❌ Échec de connexion MQTT. Code retour: {rc}")

def on_message(client, userdata, msg):
    """Se déclenche à chaque réception d'un message d'un capteur."""
    try:
        # ==========================================================
        # DÉCODAGE BINAIRE ULTRA-ROBUSTE
        # ==========================================================
        clean_payload = decode_payload_safely(msg.payload)
        # ==========================================================

        # Si le message est vide, on l'ignore
        if not clean_payload:
            return

        # Charger le JSON
        payload = json.loads(clean_payload)
        
        # Ajouter un timestamp et le topic source
        payload['timestamp'] = datetime.now().isoformat()
        payload['topic'] = msg.topic
        
        # Extraire l'ID de l'équipement du topic (ex: gnl/PIPE-001/sensors)
        parts = msg.topic.split('/')
        if len(parts) >= 2:
            payload['equipment_id'] = parts[1]
        
        # Sauvegarder dans le fichier JSON
        filename = save_to_json(payload)
        print(f"📥 Donnée reçue de {payload.get('equipment_id', 'Inconnu')} -> Sauvegardée dans {os.path.basename(filename)}")

        # --- VÉRIFICATION DES SEUILS ---
        equipment_id = payload.get('equipment_id')
        if not equipment_id:
            return

        # Température
        if 'temperature' in payload:
            temp = payload['temperature']
            if temp > config.get('alert_threshold_temperature', 80):
                create_incident_in_neo4j(equipment_id, "Température", temp, config['alert_threshold_temperature'])

        # Pression
        if 'pression' in payload:
            pression = payload['pression']
            if pression > config.get('alert_threshold_pression', 20):
                create_incident_in_neo4j(equipment_id, "Pression", pression, config['alert_threshold_pression'])

    except json.JSONDecodeError:
        print(f"⚠️ Message non-JSON reçu sur {msg.topic}")
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")

# ========================================================
# MAIN
# ========================================================

def main():
    global config
    print("🚀 Démarrage de l'écouteur IoT Dynamique...")
    config = fetch_config_from_api()
    print(f"📁 Données sauvegardées dans : {SAVE_DIR}")
    print(f"📋 Configuration : {config}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(config['mqtt_broker'], config['mqtt_port'], 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur.")
        client.disconnect()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")

if __name__ == "__main__":
    main()