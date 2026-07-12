RiverGuardian — Demo Walkthrough (Single‑Page Printable)

Duration: 6 minutes
Audience: Hackathon judges / demo audience
Goal: Show end‑to‑end flow: telemetry → fusion → explainability → multilingual alert → dashboard

0:00 — Prep (Terminals)
- Action: Ensure three terminals: API, Dashboard, Simulator. Activate venv.
- Commands:
  - `cd C:\Users\qcwor\.gemini\antigravity-ide\scratch\AI-PC`
  - `. .venv\Scripts\Activate.ps1`
- Narration: "I'll start with the Fusion backend, the Streamlit dashboard, and a telemetry simulator that drives the demo."

0:20 — Start services
- Terminal A (API):
  - `cd fusion`
  - `python main.py`
- Terminal B (Dashboard):
  - `cd ..\dashboard`
  - `streamlit run app.py`
- Narration: "Starting the backend and dashboard now — these run locally and communicate over WebSocket/HTTP."

0:40 — Open Dashboard
- Action: Browser → http://localhost:8501
- Narration: "This is RiverGuardian — a real‑time river safety stack that detects hazards, explains why, and issues multilingual alerts."
- Visual cue: Point to header, status banner, trust gauge, telemetry cards.

1:00 — Start Telemetry Stream
- Action: Terminal C: run simulator
  - `python mock_client.py`
- Narration: "I'm now streaming live sensor + pose telemetry into the fusion engine. You will see the dashboard update in real time."

1:20 — Early Escalation (OBSERVE / SUSPICIOUS)
- Observe: sparkline, risk gauge rise, small explanation panel populates.
- Narration (exact): "Notice the risk gauge rising to OBSERVE; GenieX attributes this to increased phone activity and movement."
- Action: Read the explanation text visible in the dashboard.

2:00 — Language Switch & Multilingual Alert
- Context: Simulator sends `"language": "hindi"` then `tamil`/`kannada` later.
- Visual: Language banner updates; TTS (Sarvam) plays or text banner appears.
- Narration (exact): "The system automatically selects the alert language. Here it switches to Hindi and prepares the TTS payload. You should hear (or see) the alert in the target language."

2:40 — Emergency Trigger & Explainability
- Observe: EMERGENCY banner appears, GenieX explanation panel shows structured JSON.
- Narration (exact): "EMERGENCY triggered. GenieX explains: 'Detected irregular arm motion consistent with drowning gesture.'"
- Action (show JSON): `{"event_type":"drowning","confidence":0.95,"reason":"Detected irregular arm motion consistent with drowning gesture"}`

3:40 — Incident Logging & Downstream
- Action: Open Incidents card or run API call:
  - `Invoke-RestMethod http://localhost:8000/api/incidents`
- Narration: "An incident record was logged and can be forwarded to cloud escalation or SMS/voice via Sarvam."

4:10 — Predictive Validation
- Visual: Highlight pre‑incident sparkline showing rising trend.
- Narration (exact): "The predictive signal raises the trust score before the final incident, enabling earlier alerts and interventions."

4:40 — Reset & Recovery
- Action: Click `Reset State Machine` in the dashboard sidebar or call API:
  - `Invoke-RestMethod -Method POST http://localhost:8000/api/reset`
- Narration (exact): "I'll reset the system to demonstrate recovery and the cooldown behavior."

5:00 — Wrap‑up (Callouts)
- Script (exact): "Recap: RiverGuardian fuses vision and telemetry, explains decisions with GenieX, and issues multilingual Sarvam alerts — all in real time. Architecture runs locally, supports ONNX export for edge, and includes explainability and audit logs for verifiability."
- Action: Offer to show architecture slide or code locations: `fusion/main.py`, `geniex/explain.py`, `mock_client.py`.

Recording & Backup Tips
- Capture: Screenshots at baseline, rising risk, and EMERGENCY with GenieX output.
- Audio: If TTS not available, use the explanation banner and incident JSON for evidence.

Notes for judges
- Mention ONNXRuntime-QNN simulation: indicates edge readiness.
- Mention ARM64-friendly requirements file `requirements-arm64.txt` for reproducibility.

End of script — good luck!
