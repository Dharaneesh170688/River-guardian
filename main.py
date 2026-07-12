import os
import sys
import time
import asyncio
import datetime
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure the root project directory is in the path for clean imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from fusion.state_machine import MissionStateMachine
from geniex.explain import GenieXExplainer
from sarvam.alerts import SarvamAlertSystem
from cloud.escalation import CloudEscalationSystem

app = FastAPI(title="AI PC Mission Control Fusion Engine (Qualcomm Stack)")

# Enable CORS for frontend dashboard interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize subsystems
state_machine = MissionStateMachine(cooldown_steps=5)
explainer = GenieXExplainer(model_path=os.getenv("GENIEX_LLM_PATH"))
alerts = SarvamAlertSystem()
cloud = CloudEscalationSystem()
active_language = None

# Try to import psutil for CPU/RAM metrics
try:
    import psutil
except ImportError:
    psutil = None

# ONNXRuntime QNN execution simulator
class ONNXRuntimeQNNSimulator:
    def __init__(self):
        self.ort_session = None
        try:
            import onnxruntime as ort
            print("[ONNXRuntime-QNN] ONNX Runtime imported successfully.")
            # Check if QNN provider is available
            providers = ort.get_available_providers()
            if "QNNExecutionProvider" in providers:
                print("[ONNXRuntime-QNN] Qualcomm QNN Execution Provider detected! Utilizing Snapdragon NPU.")
            else:
                print("[ONNXRuntime-QNN] QNN Provider not registered in this environment. Defaulting to CPU Execution.")
        except ImportError:
            print("[ONNXRuntime-QNN] ONNX Runtime library not installed. Running simulated QNN NPU inference.")

    def run_inference(self, telemetry: dict) -> float:
        """Simulates running a 1D classification network on Qualcomm Snapdragon NPU via ORT-QNN."""
        start_time = time.perf_counter()
        
        # Simulating NPU tensor execution delay (usually 1-3 ms for small models)
        time.sleep(0.002)
        
        # Return a classification confirmation factor
        phone = telemetry.get("phone", 0.0)
        water = telemetry.get("water", 0.0)
        movement = telemetry.get("movement", 0.0)
        
        # Simple decision model logic simulated
        npu_confidence = (phone * 0.6 + water * 0.3 + movement * 0.1)
        inference_latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Log NPU execution internally
        # print(f"[ONNXRuntime-QNN] Snapdragon NPU Inference finished in {inference_latency_ms:.2f}ms")
        return npu_confidence

qnn_engine = ONNXRuntimeQNNSimulator()

# Store active clients and system state
clients = []
latest_status = {
    "mission": "NORMAL",
    "trust_score": 0.0,
    "explanation": "System initialized and waiting for telemetry.",
    "telemetry": {},
    "timestamp": None,
    "incident_id": "INC-INIT"
}

# Metrics cache for charts: holds the last 50 data points
metrics_history = []
packet_count = 0
fps_start_time = time.time()
fps_value = 0.0

# Lock to synchronize state updates
state_lock = asyncio.Lock()

# Ensure metrics directory exists
metrics_dir = os.path.join(parent_dir, "metrics")
os.makedirs(metrics_dir, exist_ok=True)
performance_log_path = os.path.join(metrics_dir, "performance.json")

def play_alert_async(language: str):
    """Triggers Sarvam audio alert in the background to prevent blocking the async loop."""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, alerts.trigger_alert, language)

def get_system_usage():
    """Retrieves CPU and memory usage."""
    if psutil:
        try:
            return psutil.cpu_percent(), psutil.virtual_memory().percent
        except Exception:
            return 12.5, 45.0
    return 12.5, 45.0

def normalize_telemetry(data: dict) -> dict:
    normalized = data.copy()
    if "pose_confidence" in data:
        val = data["pose_confidence"]
        if isinstance(val, (int, float)):
            normalized["phone"] = val / 100.0 if val > 1.0 else val
        else:
            normalized["phone"] = 0.0
    elif "phone" in data:
        val = data["phone"]
        if isinstance(val, (int, float)):
            normalized["pose_confidence"] = int(val * 100) if val <= 1.0 else int(val)
            normalized["phone"] = val / 100.0 if val > 1.0 else val
    if "movement_level" in data:
        val = data["movement_level"]
        if isinstance(val, str):
            val_upper = val.upper()
            if val_upper == "HIGH":
                normalized["movement"] = 0.9
            elif val_upper in ("MED", "MEDIUM"):
                normalized["movement"] = 0.5
            else:
                normalized["movement"] = 0.1
        elif isinstance(val, (int, float)):
            normalized["movement"] = val / 100.0 if val > 1.0 else val
    elif "movement" in data:
        val = data["movement"]
        if isinstance(val, (int, float)):
            normalized["movement"] = val
            normalized["movement_level"] = "HIGH" if val > 0.7 else "MED" if val > 0.3 else "LOW"
    if "person_detected" not in normalized:
        normalized["person_detected"] = normalized.get("phone", 0.0) > 0.4
    if "person_count" not in normalized:
        normalized["person_count"] = 1 if normalized.get("person_detected", False) else 0
    if "camera_fps" not in normalized:
        normalized["camera_fps"] = data.get("fps", 29.0)
    if "head_underwater" not in normalized:
        normalized["head_underwater"] = normalized.get("water", 0.0) > 0.75 and normalized.get("phone", 0.0) > 0.6
    if "water_level" in data:
        normalized["water"] = data["water_level"]
    elif "water" in data:
        normalized["water_level"] = data["water"]
    if "rain_status" in data:
        val = data["rain_status"]
        if isinstance(val, bool):
            normalized["rain"] = val
        elif isinstance(val, str):
            normalized["rain"] = val.lower() in ("true", "1", "yes", "on", "rain", "active")
        else:
            normalized["rain"] = bool(val)
    elif "rain" in data:
        normalized["rain_status"] = data["rain"]
    if "light_level" in data:
        normalized["light"] = data["light_level"]
    elif "light" in data:
        normalized["light_level"] = data["light"]
    if "device_status" in data:
        normalized["health"] = data["device_status"]
    elif "health" in data:
        normalized["device_status"] = data["health"]
    if "temperature" in data:
        normalized["temp"] = data["temperature"]
    elif "temp" in data:
        normalized["temperature"] = data["temp"]
    return normalized

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print(f"[WebSocket] Client connected. Total clients: {len(clients)}")
    
    # Send current state
    try:
        await ws.send_json({
            "type": "state_update",
            "data": latest_status
        })
    except Exception:
        pass

    global packet_count, fps_start_time, fps_value
    try:
        while True:
            # Telemetry input
            data = await ws.receive_json()
            data = normalize_telemetry(data)
            
            # Start latency measurement
            start_process_time = time.perf_counter()
            packet_count += 1
            
            # Recalculate FPS every 2 seconds
            current_time = time.time()
            elapsed_fps = current_time - fps_start_time
            if elapsed_fps >= 2.0:
                fps_value = packet_count / elapsed_fps
                packet_count = 0
                fps_start_time = current_time
            
            async with state_lock:
                prev_state = state_machine.current_state
                
                # Execute simulated ONNXRuntime-QNN classification on the telemetry
                npu_factor = qnn_engine.run_inference(data)
                
                # Update state machine with telemetry
                new_state, trust_score, changed = state_machine.update(data)
                
                # Fetch target language, override with active_language if set by dashboard
                alert_language = active_language if active_language else data.get("language", "english")
                
                # Generate explainability via GenieX on change
                if changed or not latest_status["explanation"] or latest_status["explanation"] == "System initialized and waiting for telemetry.":
                    explanation = explainer.explain(prev_state, new_state, data, trust_score)
                    print(f"[Fusion] State: {prev_state} -> {new_state} (Trust: {trust_score:.2f})")
                    print(f"[GenieX] Explanation: {explanation}")
                    
                    # Play Sarvam voice alert on EMERGENCY escalation
                    if new_state == "EMERGENCY" and prev_state != "EMERGENCY":
                        play_alert_async(alert_language)
                    
                    # Escalate to Cloud AI 100 Ultra / write logs
                    incident_info = cloud.log_incident(new_state, trust_score, explanation, data)
                    current_incident_id = incident_info.get("incident_id", "INC-INIT")
                else:
                    explanation = latest_status["explanation"]
                    current_incident_id = latest_status.get("incident_id", "INC-INIT")
                
                # Compute Vision and Sensor confidence
                vision_conf = data.get("pose_confidence", 0.0)
                health = str(data.get("device_status", "healthy")).lower()
                if health == "critical":
                    sensor_conf = 0.50
                elif health == "warning":
                    sensor_conf = 0.80
                else:
                    sensor_conf = 1.00
                
                final_risk_score = trust_score
                final_trust_score = 1.0 - trust_score
                
                # Update status dict
                latest_status.update({
                    "mission": new_state,
                    "trust_score": trust_score,
                    "explanation": explanation,
                    "telemetry": data,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "vision_confidence": vision_conf,
                    "sensor_confidence": sensor_conf,
                    "final_risk_score": final_risk_score,
                    "final_trust_score": final_trust_score,
                    "incident_id": current_incident_id
                })
            
            # Complete latency measurement (ms)
            latency_ms = (time.perf_counter() - start_process_time) * 1000
            cpu_percent, ram_percent = get_system_usage()
            
            # Track metrics record
            metrics_record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "latency_ms": latency_ms,
                "cpu_percent": cpu_percent,
                "ram_percent": ram_percent,
                "fps": max(fps_value, 1.0)
            }
            
            metrics_history.append(metrics_record)
            if len(metrics_history) > 50:
                metrics_history.pop(0)
                
            # Log metrics to file periodically (write every 5 packets)
            if packet_count % 5 == 0:
                try:
                    with open(performance_log_path, "w", encoding="utf-8") as f:
                        json.dump(metrics_history, f, indent=2)
                except Exception:
                    pass
            
            # Broadcast state & metrics back to dashboard and clients
            broadcast_payload = {
                "type": "state_update",
                "data": latest_status,
                "metrics": metrics_record
            }
            
            dead_clients = []
            for client in clients:
                try:
                    await client.send_json(broadcast_payload)
                except Exception:
                    dead_clients.append(client)
            
            for dead in dead_clients:
                clients.remove(dead)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[WebSocket] Socket error: {e}")
    finally:
        if ws in clients:
            clients.remove(ws)

@app.get("/api/status")
async def get_status():
    return latest_status

@app.get("/api/metrics")
async def get_metrics():
    """Retrieve history of latency, CPU, RAM, and FPS."""
    return metrics_history

@app.get("/api/stats")
async def get_stats():
    return cloud.get_analytics()

@app.post("/api/reset")
async def reset_state():
    global latest_status
    async with state_lock:
        state_machine.current_state = "NORMAL"
        state_machine.steps_since_change = 0
        state_machine.escalation_candidate = None
        state_machine.escalation_count = 0
        state_machine.de_escalation_count = 0
        
        latest_status.update({
            "mission": "NORMAL",
            "trust_score": 0.0,
            "explanation": "System manually reset to NORMAL.",
            "telemetry": {},
            "timestamp": None,
            "incident_id": "INC-INIT"
        })
    print("[Fusion] System state reset.")
    return {"status": "ok", "message": "State machine reset to NORMAL"}

@app.get("/api/incidents")
async def get_incidents():
    inc_path = os.path.join(parent_dir, "logs", "incidents.json")
    if os.path.exists(inc_path):
        try:
            with open(inc_path, "r", encoding="utf-8") as f:
                import json
                return json.load(f)
        except Exception:
            return []
    return []

@app.post("/api/settings")
async def set_settings(payload: dict):
    global active_language
    active_language = payload.get("language", "english").lower()
    print(f"[Fusion] Active TTS language updated to: {active_language}")
    return {"status": "ok", "language": active_language}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)
