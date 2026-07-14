"""
Gestionnaire d'alertes pour le monitoring du système GNL
"""

import logging
import yaml
import json
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Gestionnaire d'alertes pour le système GNL
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialise le gestionnaire d'alertes
        
        Args:
            rules_path: Chemin du fichier de règles
        """
        self.rules_path = rules_path or "src/monitoring/alerts/rules.yaml"
        self.rules = []
        self._load_rules()
        self._alert_history = []
        self._handlers = {}
        self._lock = threading.Lock()
        self._running = False
        
        # Configurer les handlers
        self._setup_handlers()
        
        logger.info(f"✅ AlertManager initialisé ({len(self.rules)} règles)")
    
    def _load_rules(self):
        """Charge les règles d'alertes"""
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.rules = config.get('rules', [])
                logger.info(f"✅ {len(self.rules)} règles chargées")
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement règles: {e}")
            # Règles par défaut
            self.rules = [
                {
                    "name": "api_high_error_rate",
                    "description": "Taux d'erreur API élevé",
                    "condition": "api_errors_total / api_requests_total > 0.05",
                    "severity": "critical",
                    "action": "notify_slack",
                    "message": "Le taux d'erreur API est de {value:.2%}"
                }
            ]
    
    def _setup_handlers(self):
        """Configure les handlers d'alertes"""
        self._handlers = {
            'log': self._log_alert,
            'notify_slack': self._notify_slack,
            'notify_email': self._notify_email,
            'webhook': self._send_webhook
        }
    
    def _log_alert(self, alert: Dict):
        """Log l'alerte"""
        logger.warning(
            f"🔔 ALERTE [{alert.get('severity', 'info').upper()}] "
            f"{alert.get('name')}: {alert.get('message')}"
        )
    
    def _notify_slack(self, alert: Dict):
        """
        Envoie une notification Slack
        """
        try:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                logger.warning("⚠️ SLACK_WEBHOOK_URL non défini")
                return
            
            color_map = {
                'critical': 'danger',
                'warning': 'warning',
                'info': 'good'
            }
            
            payload = {
                "attachments": [{
                    "color": color_map.get(alert.get('severity'), 'warning'),
                    "title": f"🔔 {alert.get('name')}",
                    "text": alert.get('message', ''),
                    "fields": [
                        {"title": "Sévérité", "value": alert.get('severity', 'info'), "short": True},
                        {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                    ],
                    "footer": "GNL Knowledge Graph",
                    "ts": int(time.time())
                }]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Erreur Slack: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erreur notification Slack: {e}")
    
    def _notify_email(self, alert: Dict):
        """
        Envoie une notification par email
        """
        try:
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            recipient = os.getenv('ALERT_EMAIL_RECIPIENT')
            
            if not all([smtp_host, smtp_user, smtp_password, recipient]):
                logger.warning("⚠️ Configuration email incomplète")
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = f"[GNL] Alerte {alert.get('severity', 'info')}: {alert.get('name')}"
            
            body = f"""
            🔔 ALERTE GNL KNOWLEDGE GRAPH
            
            Nom: {alert.get('name')}
            Sévérité: {alert.get('severity', 'info')}
            Message: {alert.get('message', '')}
            Description: {alert.get('description', '')}
            Timestamp: {datetime.now().isoformat()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
            logger.info(f"✅ Email d'alerte envoyé à {recipient}")
            
        except Exception as e:
            logger.error(f"❌ Erreur email: {e}")
    
    def _send_webhook(self, alert: Dict):
        """
        Envoie une alerte via webhook
        """
        try:
            webhook_url = os.getenv('WEBHOOK_URL')
            if not webhook_url:
                return
            
            response = requests.post(
                webhook_url,
                json=alert,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Erreur webhook: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erreur webhook: {e}")
    
    def evaluate_condition(self, rule: Dict, metrics: Dict) -> bool:
        """
        Évalue une condition d'alerte
        """
        try:
            condition = rule.get('condition', '')
            # Sécuriser l'évaluation
            # Dans la vraie vie, utiliser un système plus robuste
            # Pour l'exemple, on simule
            return False
        except Exception:
            return False
    
    def check_metrics(self, metrics: Dict) -> List[Dict]:
        """
        Vérifie les métriques et génère des alertes
        """
        alerts = []
        
        for rule in self.rules:
            # Vérifier la condition (simulée)
            # Dans la vraie vie, évaluer la condition réelle
            # avec les métriques
            if self.evaluate_condition(rule, metrics):
                alert = {
                    'name': rule.get('name'),
                    'description': rule.get('description'),
                    'severity': rule.get('severity', 'info'),
                    'message': rule.get('message', ''),
                    'action': rule.get('action', 'log'),
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        return alerts
    
    def process_alerts(self, alerts: List[Dict]):
        """
        Traite les alertes générées
        """
        with self._lock:
            for alert in alerts:
                # Vérifier si l'alerte a déjà été envoyée récemment
                if not self._should_send_alert(alert):
                    continue
                
                # Ajouter à l'historique
                self._alert_history.append(alert)
                
                # Envoyer l'alerte
                handler = self._handlers.get(alert.get('action', 'log'))
                if handler:
                    handler(alert)
                else:
                    self._log_alert(alert)
                
                # Limiter l'historique
                if len(self._alert_history) > 1000:
                    self._alert_history = self._alert_history[-500:]
    
    def _should_send_alert(self, alert: Dict) -> bool:
        """
        Vérifie si l'alerte doit être envoyée
        """
        # Vérifier si le même type d'alerte a été envoyé récemment
        for last_alert in reversed(self._alert_history[-10:]):
            if last_alert.get('name') == alert.get('name'):
                # Déjà envoyée dans les 5 minutes
                last_time = datetime.fromisoformat(last_alert.get('timestamp', ''))
                if (datetime.now() - last_time).seconds < 300:
                    return False
        return True
    
    def start(self, check_interval: int = 60):
        """
        Démarre le monitoring des alertes
        """
        self._running = True
        logger.info(f"🚀 AlertManager démarré (intervalle: {check_interval}s)")
        
        # Dans la vraie vie, lancer un thread qui vérifie les métriques
        # Pour l'exemple, on simule
    
    def stop(self):
        """Arrête le monitoring"""
        self._running = False
        logger.info("⏹️ AlertManager arrêté")
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Récupère les alertes
        """
        alerts = self._alert_history[-limit:]
        
        if severity:
            alerts = [a for a in alerts if a.get('severity') == severity]
        
        return alerts
    
    def get_alert_stats(self) -> Dict:
        """
        Récupère les statistiques des alertes
        """
        stats = {
            'total': len(self._alert_history),
            'by_severity': {
                'critical': len([a for a in self._alert_history if a.get('severity') == 'critical']),
                'warning': len([a for a in self._alert_history if a.get('severity') == 'warning']),
                'info': len([a for a in self._alert_history if a.get('severity') == 'info'])
            }
        }
        return stats

if __name__ == "__main__":
    # Test du gestionnaire d'alertes
    manager = AlertManager()
    
    # Simuler des alertes
    test_alerts = [
        {
            'name': 'Test Alert',
            'severity': 'warning',
            'message': 'Test message',
            'action': 'log'
        }
    ]
    
    manager.process_alerts(test_alerts)
    print("Stats:", manager.get_alert_stats())