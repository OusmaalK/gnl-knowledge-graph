"""
Outil de prédiction des risques - Version enrichie
Phase 3 - Prédiction et évaluation des risques
"""

from .base import BaseTool
from .graph_tools import GraphTools
from .llm_tools import LLMTools
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RiskPredictor(BaseTool):
    """
    Outil pour prédire et évaluer les risques
    """
    
    def __init__(self):
        super().__init__(name="RiskPredictor")
        self.graph_tools = GraphTools()
        self.llm_tools = LLMTools()
    
    def execute(self, equipment_id: Optional[str] = None, **kwargs) -> Dict:
        """
        Prédit le risque d'un équipement avec enrichissement
        """
        if not equipment_id:
            return {"error": "equipment_id est requis"}
        
        risk = self.graph_tools.get_risk_score(equipment_id)
        
        if not risk:
            return {"error": f"Équipement {equipment_id} non trouvé"}
        
        # Récupérer l'historique pour analyse supplémentaire
        history = self.graph_tools.get_incident_history(equipment_id)
        
        # Analyser les tendances
        trends = self._analyze_trends(history)
        
        # Construire le contexte pour le LLM
        context = f"""
📍 Équipement : {risk.get('equipment_name', equipment_id)}
📊 Score de risque : {risk.get('score', 0)}/100
⚠️ Niveau : {risk.get('niveau', 'FAIBLE')}
🚨 Incidents : {risk.get('incidents_count', 0)}
👥 Clients : {risk.get('clients_count', 0)}
📈 Tendance : {trends.get('trend', 'STABLE')}
"""

        # Enrichir avec le LLM
        question = f"""
Analyse le risque de cet équipement :

{context}

Fournis :
1. Une évaluation détaillée du risque
2. Les facteurs de risque identifiés
3. Une prédiction d'évolution
4. Un plan d'atténuation
"""
        
        enriched_analysis = self.llm_tools.generate_response(question, context)
        
        return {
            "equipment_id": risk.get('equipment_id'),
            "equipment_name": risk.get('equipment_name'),
            "score": risk.get('score', 0),
            "niveau": risk.get('niveau', 'FAIBLE'),
            "incidents_count": risk.get('incidents_count', 0),
            "clients_count": risk.get('clients_count', 0),
            "trends": trends,
            "predictions": self._get_predictions(risk, trends),
            "actions": self._get_actions(risk, trends),
            "analysis": enriched_analysis
        }
    
    def _analyze_trends(self, history: list) -> Dict:
        """
        Analyse les tendances des incidents
        """
        if not history:
            return {"trend": "STABLE", "frequency": 0}
        
        # Compter les incidents par mois
        months = {}
        for inc in history:
            date = inc.get('date', '')
            if date:
                month = date[:7]  # YYYY-MM
                months[month] = months.get(month, 0) + 1
        
        frequencies = list(months.values())
        avg = sum(frequencies) / len(frequencies) if frequencies else 0
        
        if avg > 2:
            trend = "HAUSSE"
        elif avg > 0:
            trend = "STABLE"
        else:
            trend = "BAISSE"
        
        return {
            "trend": trend,
            "frequency": avg,
            "months": months,
            "periods": len(months)
        }
    
    def _get_predictions(self, risk: Dict, trends: Dict) -> str:
        """
        Génère des prédictions
        """
        niveau = risk.get('niveau', 'FAIBLE')
        trend = trends.get('trend', 'STABLE')
        incidents = risk.get('incidents_count', 0)
        
        predictions = []
        
        if niveau == 'CRITIQUE' and trend == 'HAUSSE':
            predictions.append("🔴 Risque critique en augmentation - Action immédiate requise")
            predictions.append(f"📈 Probabilité d'incident supplémentaire : {min(incidents * 20, 80)}%")
        elif niveau == 'CRITIQUE':
            predictions.append("🔴 Risque critique - Surveillance renforcée")
            predictions.append(f"📊 Probabilité d'incident supplémentaire : {min(incidents * 10, 60)}%")
        elif niveau == 'ELEVE' and trend == 'HAUSSE':
            predictions.append("🟡 Risque élevé en augmentation - Plan d'action nécessaire")
            predictions.append(f"📈 Probabilité d'incident supplémentaire : {min(incidents * 15, 50)}%")
        elif niveau == 'ELEVE':
            predictions.append("🟡 Risque élevé - Surveillance recommandée")
            predictions.append(f"📊 Probabilité d'incident supplémentaire : {min(incidents * 10, 40)}%")
        else:
            predictions.append("✅ Risque faible - Surveillance standard")
            predictions.append(f"📊 Probabilité d'incident supplémentaire : {min(incidents * 5, 20)}%")
        
        return "\n".join(predictions)
    
    def _get_actions(self, risk: Dict, trends: Dict) -> str:
        """
        Génère des actions recommandées
        """
        niveau = risk.get('niveau', 'FAIBLE')
        trend = trends.get('trend', 'STABLE')
        incidents = risk.get('incidents_count', 0)
        
        actions = []
        
        if niveau == 'CRITIQUE':
            actions.append("🔴 ACTION IMMÉDIATE : Inspection complète")
            actions.append("🔴 ACTION URGENTE : Plan de réparation")
            actions.append("🔴 ACTION PRÉVENTIVE : Notification parties prenantes")
            actions.append(f"📋 Échéance : {min(incidents * 5, 30)} jours")
        elif niveau == 'ELEVE':
            actions.append("🟡 ACTION 30 JOURS : Inspection approfondie")
            actions.append("🟡 ACTION 60 JOURS : Plan de maintenance")
            actions.append(f"📋 Échéance : {min(incidents * 10, 60)} jours")
        else:
            actions.append("✅ ACTION 90 JOURS : Inspection standard")
            actions.append("✅ ACTION 180 JOURS : Maintenance préventive")
            actions.append(f"📋 Échéance : {90 + incidents * 15} jours")
        
        if trend == 'HAUSSE':
            actions.append("📈 Surveillance renforcée - Tendance à la hausse")
        elif trend == 'BAISSE':
            actions.append("📉 Tendance à la baisse - Maintenir les efforts")
        
        return "\n".join(actions)
    
    def get_description(self) -> str:
        """
        Retourne la description de l'outil
        """
        return """
⚠️ PRÉDICTION DES RISQUES

Cet outil évalue le risque d'un équipement et prédit les tendances.

Paramètres :
- equipment_id : ID de l'équipement

Résultats :
- Score de risque (0-100)
- Niveau de risque (FAIBLE/MODERE/ELEVE/CRITIQUE)
- Tendances des incidents
- Prédictions
- Actions recommandées
- Analyse enrichie
"""