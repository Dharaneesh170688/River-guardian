import asyncio
import json
import websockets

# Connection URL
URI = "ws://localhost:9090/ws"

SCENARIO = [
    # State 1: NORMAL
    {
        "phone": 0.15, "water": 0.10, "movement": 0.12, "rain": False, "light": 0.05, "health": "healthy",
        "language": "english", "desc": "Normal baseline activity: Clear environment, device is healthy and stable."
    },
    {
        "phone": 0.20, "water": 0.15, "movement": 0.10, "rain": False, "light": 0.05, "health": "healthy",
        "language": "english", "desc": "Normal baseline activity: Minimal sensor readings registered."
    },
    
    # State 2: Escalation to OBSERVE
    {
        "phone": 0.45, "water": 0.30, "movement": 0.35, "rain": False, "light": 0.10, "health": "healthy",
        "language": "english", "desc": "Slight escalation: Phone activity increases, movement detected."
    },
    {
        "phone": 0.50, "water": 0.35, "movement": 0.40, "rain": False, "light": 0.12, "health": "healthy",
        "language": "english", "desc": "Escalation confirmed: Entering OBSERVE state."
    },
    
    # State 3: Escalation to SUSPICIOUS
    {
        "phone": 0.65, "water": 0.50, "movement": 0.50, "rain": True, "light": 0.25, "health": "warning",
        "language": "hindi", "desc": "Suspicious activity: Rain detected, warning status on health, language switched to Hindi."
    },
    {
        "phone": 0.70, "water": 0.55, "movement": 0.55, "rain": True, "light": 0.30, "health": "warning",
        "language": "hindi", "desc": "Suspicious activity confirmed: High humidity, warning flags active."
    },
    
    # State 4: Escalation to DISTRESS
    {
        "phone": 0.82, "water": 0.70, "movement": 0.70, "rain": True, "light": 0.50, "health": "warning",
        "language": "tamil", "desc": "Distress levels active: Water levels rising, language switched to Tamil."
    },
    {
        "phone": 0.85, "water": 0.75, "movement": 0.72, "rain": True, "light": 0.55, "health": "critical",
        "language": "tamil", "desc": "Distress levels confirmed: Device health has reached CRITICAL status."
    },
    
    # State 5: Escalation to EMERGENCY
    {
        "phone": 0.95, "water": 0.90, "movement": 0.90, "rain": True, "light": 0.75, "health": "critical",
        "language": "kannada", "desc": "Emergency state first reading: All sensors indicating severe risk, language is Kannada."
    },
    {
        "phone": 0.98, "water": 0.95, "movement": 0.95, "rain": True, "light": 0.80, "health": "critical",
        "language": "kannada", "desc": "Emergency state second reading: Triggers state transition and sounds Sarvam audio alert!"
    },
    
    # State 6: Cooldown and Recovery
    {
        "phone": 0.20, "water": 0.15, "movement": 0.10, "rain": False, "light": 0.10, "health": "healthy",
        "language": "english", "desc": "Recovery: Telemetry cleared, but state held in EMERGENCY due to cooldown (Step 1/5)."
    },
    {
        "phone": 0.18, "water": 0.12, "movement": 0.08, "rain": False, "light": 0.08, "health": "healthy",
        "language": "english", "desc": "Recovery: Sensors clean, state held in EMERGENCY (Step 2/5)."
    },
    {
        "phone": 0.15, "water": 0.10, "movement": 0.05, "rain": False, "light": 0.05, "health": "healthy",
        "language": "english", "desc": "Recovery: Sensors clean, state held in EMERGENCY (Step 3/5)."
    },
    {
        "phone": 0.10, "water": 0.08, "movement": 0.03, "rain": False, "light": 0.05, "health": "healthy",
        "language": "english", "desc": "Recovery: Sensors clean, state held in EMERGENCY (Step 4/5)."
    },
    {
        "phone": 0.10, "water": 0.05, "movement": 0.02, "rain": False, "light": 0.02, "health": "healthy",
        "language": "english", "desc": "Recovery: Cooldown completed (Step 5/5). Ready to de-escalate."
    },
    {
        "phone": 0.10, "water": 0.05, "movement": 0.02, "rain": False, "light": 0.02, "health": "healthy",
        "language": "english", "desc": "Recovery: Second reading under NORMAL threshold -> State returns to NORMAL."
    },
    {
        "phone": 0.10, "water": 0.05, "movement": 0.02, "rain": False, "light": 0.02, "health": "healthy",
        "language": "english", "desc": "Stable NORMAL state confirmed."
    }
]

async def run_simulator():
    print(f"Connecting to Fusion Engine WebSocket at {URI}...")
    try:
        async with websockets.connect(URI) as websocket:
            print("Connected successfully! Starting telemetry stream...")
            
            while True:
                for idx, step_data in enumerate(SCENARIO):
                    step = step_data.copy()
                    desc = step.pop("desc")
                    
                    print(f"\n[Step {idx+1}/{len(SCENARIO)}] {desc}")
                    print(f"Sending Telemetry: {json.dumps(step)}")
                    
                    await websocket.send(json.dumps(step))
                    
                    # Wait for server response
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        res_data = json.loads(response)
                        state_data = res_data.get("data", {})
                        metrics_data = res_data.get("metrics", {})
                        
                        print(f"Server Broadcast -> State: {state_data.get('mission')}, "
                              f"Trust: {state_data.get('trust_score'):.2f}")
                        print(f"Explanation: {state_data.get('explanation')}")
                        print(f"Performance -> Latency: {metrics_data.get('latency_ms', 0.0):.2f}ms, "
                              f"CPU: {metrics_data.get('cpu_percent', 0.0)}%, "
                              f"RAM: {metrics_data.get('ram_percent', 0.0)}%")
                    except asyncio.TimeoutError:
                        print("No broadcast response received (Timeout)")
                        
                    await asyncio.sleep(3.0)
                    
                print("\n=== Scenario complete, resetting server state and repeating in 5 seconds... ===")
                try:
                    import requests
                    requests.post("http://localhost:9090/api/reset", timeout=2)
                    print("Server state reset to NORMAL successfully.")
                except Exception as e:
                    print(f"Could not reset server state: {e}")
                    
                await asyncio.sleep(5.0)
                
    except Exception as e:
        print(f"WebSocket client error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
