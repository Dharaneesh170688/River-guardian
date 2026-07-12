import os
import json
import time
from datetime import datetime

class CirrascaleCloudIntegration:
    def __init__(self, logs_dir: str = None):
        # Default to a subfolder in the scratch project directory
        if not logs_dir:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.logs_dir = os.path.join(project_dir, "logs")
        else:
            self.logs_dir = logs_dir
            
        os.makedirs(self.logs_dir, exist_ok=True)
        self.incidents_path = os.path.join(self.logs_dir, "incidents.json")
        
    def log_incident(self, state: str, trust_score: float, explanation: str, telemetry: dict):
        """Logs incident report locally to logs/incidents.json and simulates upload."""
        incident = {
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "trust_score": trust_score,
            "explanation": explanation,
            "telemetry": telemetry
        }
        
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
            print(f"[Cirrascale] Local incident logged to {self.incidents_path}")
        except Exception as e:
            print(f"[Cirrascale] Failed to write local incident log: {e}")

        # Simulate cloud dispatch on borderline / high-alert states
        if state in ["SUSPICIOUS", "DISTRESS", "EMERGENCY"]:
            print(f"[Cirrascale] Dispatching telemetry snapshot to Cirrascale AI 100 Ultra endpoint...")
            # Simulate a 100ms API latency
            time.sleep(0.1)
            print(f"[Cirrascale] AI 100 Ultra: Processing metadata. Event ID: cs-{int(time.time())}")

    def generate_heatmap_stats(self) -> dict:
        """Processes the local incident logs and returns stats for analysis."""
        if not os.path.exists(self.incidents_path):
            return {
                "total_incidents": 0,
                "state_distribution": {"NORMAL": 0, "OBSERVE": 0, "SUSPICIOUS": 0, "DISTRESS": 0, "EMERGENCY": 0},
                "last_updated": datetime.now().isoformat()
            }
            
        try:
            with open(self.incidents_path, "r", encoding="utf-8") as f:
                incidents = json.load(f)
        except Exception:
            return {"error": "Could not read incident log file."}
            
        counts = {"NORMAL": 0, "OBSERVE": 0, "SUSPICIOUS": 0, "DISTRESS": 0, "EMERGENCY": 0}
        for inc in incidents:
            state = inc.get("state", "NORMAL")
            if state in counts:
                counts[state] += 1
                
        return {
            "total_incidents": len(incidents),
            "state_distribution": counts,
            "last_updated": datetime.now().isoformat()
        }
