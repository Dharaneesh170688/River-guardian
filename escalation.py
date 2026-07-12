import os
import json
import time
from datetime import datetime

class CloudEscalationSystem:
    def __init__(self, logs_dir: str = None):
        if not logs_dir:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.logs_dir = os.path.join(project_dir, "logs")
        else:
            self.logs_dir = logs_dir
            
        os.makedirs(self.logs_dir, exist_ok=True)
        self.incidents_path = os.path.join(self.logs_dir, "incidents.json")
        
    def log_incident(self, state: str, trust_score: float, explanation: str, telemetry: dict) -> dict:
        """Logs incident report locally to logs/incidents.json and simulates second opinion."""
        import uuid
        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
        incident = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "trust_score": trust_score,
            "explanation": explanation,
            "telemetry": telemetry,
            "cloud_escalated": False,
            "second_opinion_verdict": None
        }
        
        # Determine if cloud escalation is triggered (borderline SUSPICIOUS, DISTRESS, or EMERGENCY)
        is_borderline = state in ["SUSPICIOUS", "DISTRESS"]
        is_emergency = state == "EMERGENCY"
        
        if is_borderline or is_emergency:
            incident["cloud_escalated"] = True
            print(f"[Cloud Escalation] Initiating Cloud AI 100 Ultra evaluation for state: {state}...")
            # Simulate a brief network / inference latency
            time.sleep(0.08)
            
            # AI 100 Ultra verdict generation
            if is_emergency:
                verdict = "CRITICAL_ALERT_CONFIRMED"
            elif state == "DISTRESS":
                verdict = "PROBABLE_INCIDENT_WARNING"
            else:
                verdict = "MONITORING_SUGGESTED"
                
            incident["second_opinion_verdict"] = verdict
            print(f"[Cloud Escalation] Qualcomm Cloud AI 100 Ultra Response: {verdict}")
            
        # Append locally
        incidents = []
        if os.path.exists(self.incidents_path):
            try:
                with open(self.incidents_path, "r", encoding="utf-8") as f:
                    incidents = json.load(f)
            except Exception:
                incidents = []
                
        incidents.append(incident)
        
        try:
            with open(self.incidents_path, "w", encoding="utf-8") as f:
                json.dump(incidents, f, indent=2)
            print(f"[Cloud Escalation] Incident logged locally at: {self.incidents_path}")
        except Exception as e:
            print(f"[Cloud Escalation] Failed to write incident logs: {e}")
            
        return incident

    def get_analytics(self) -> dict:
        """Processes the local incident logs and returns stats for the dashboard."""
        if not os.path.exists(self.incidents_path):
            return {
                "total_incidents": 0,
                "state_distribution": {"NORMAL": 0, "OBSERVE": 0, "SUSPICIOUS": 0, "DISTRESS": 0, "EMERGENCY": 0},
                "cloud_escalated_count": 0,
                "last_updated": datetime.now().isoformat()
            }
            
        try:
            with open(self.incidents_path, "r", encoding="utf-8") as f:
                incidents = json.load(f)
        except Exception:
            return {"error": "Could not read incident log file."}
            
        counts = {"NORMAL": 0, "OBSERVE": 0, "SUSPICIOUS": 0, "DISTRESS": 0, "EMERGENCY": 0}
        escalations = 0
        
        for inc in incidents:
            state = inc.get("state", "NORMAL")
            if state in counts:
                counts[state] += 1
            if inc.get("cloud_escalated", False):
                escalations += 1
                
        return {
            "total_incidents": len(incidents),
            "state_distribution": counts,
            "cloud_escalated_count": escalations,
            "last_updated": datetime.now().isoformat()
        }
