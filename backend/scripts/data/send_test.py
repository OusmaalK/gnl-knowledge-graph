#!/usr/bin/env python3
"""
Client de test MQTT pour envoyer un message JSON propre
Path: backend/scripts/data/send_test.py
"""

import paho.mqtt.client as mqtt
import json
import time

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "gnl/PIPE-001/sensors"

# Le message JSON à envoyer
payload = {
    "temperature": 45.5,
    "pression": 12.3
}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connecté au broker MQTT ({MQTT_BROKER}:{MQTT_PORT})")
        # Envoyer le message une fois connecté
        message = json.dumps(payload)
        client.publish(MQTT_TOPIC, message)
        print(f"📤 Message envoyé sur {MQTT_TOPIC} : {message}")
        client.disconnect()
    else:
        print(f"❌ Échec de connexion MQTT. Code retour: {rc}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()