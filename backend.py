from fastapi import FastAPI, WebSocket
import json

app = FastAPI()

RISK_THRESHOLD = 0.5

@app.websocket("/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    print("[backend] WebSocket connected on /telemetry")
    try:
        while True:
            message = await websocket.receive_text()
            print("[backend] Raw telemetry received:", message)
            response_text = "ACK"
            try:
                payload = json.loads(message)
                risk_score = payload.get("risk_score")
                if risk_score is None and isinstance(payload.get("trust_score"), (int, float)):
                    risk_score = payload.get("trust_score")

                if isinstance(risk_score, (int, float)):
                    response_text = "A" if risk_score >= RISK_THRESHOLD else "N"
                    print(f"[backend] Parsed risk_score={risk_score}, reply={response_text}")
                else:
                    print("[backend] No numeric risk_score/trust_score found; replying ACK")
            except json.JSONDecodeError:
                print("[backend] Received non-JSON telemetry; replying ACK")

            await websocket.send_text(response_text)
    except Exception as e:
        print("[backend] WebSocket closed:", e)
