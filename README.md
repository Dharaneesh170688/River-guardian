 RiverGuardian
⚠️ The Problem

Drowning is silent and fast. Most existing camera-based monitoring systems ask only one question: "Did the AI detect a drowning event?" They have no way to know if their own prediction can be trusted — rain, darkness, rising water, and device strain can all silently degrade a camera's confidence, leading to missed emergencies or false alarms. Wrong triggers waste rescue response; missed ones cost lives.

![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/f7460828e811d955f1ea0d5488eedcac7572e831/Screenshot_2026-07-12-12-48-17-95_0cf50405bf4e606ac561eec43039b08f.jpg)

Traditional systems trust a single confidence number. RiverGuardian cross-checks independent signals and explicitly discounts any of them if compromised:


Vision and environment agree on risk → fast, confident escalation
Only one signal flags risk → holds, waits for corroboration
A node reports degraded health (low light, rain, low battery, dropped connection) → the dashboard says so, out loud, and reweights the decision accordingly
Risk is trending up → the dashboard projects roughly how long until the next state, not just where things stand right now


EffectiveRisk = (0.50·PoseRisk + 0.20·WaterLevelRisk + 0.15·MovementRisk
                + 0.10·RainRisk + 0.05·LightRisk) × HealthFactor

![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/e7f965475237bc065d08b9222ec0066684cad171/Screenshot_2026-07-12-12-48-56-95_0cf50405bf4e606ac561eec43039b08f.jpg)


![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/e874641f26746d2fde1ac7cfb53e83b8fb244ce5/Screenshot_2026-07-12-12-49-06-41_0cf50405bf4e606ac561eec43039b08f.jpg)

Nothing here is a black box. Every emergency decision comes with a human-readable justification, generated live by GenieX:

textDecision: EMERGENCY
Trust Score: 100%

Reason:
✓ Phone and Arduino agree
✓ No movement detected for 12s
✓ Heavy rain detected by Arduino
✓ Water level rising
✓ Device health nominal

<!-- 📸 PASTE: Dashboard's live GenieX explanation panel -->

🚦 Mission State Machine

NORMAL → OBSERVE → SUSPICIOUS → DISTRESS → EMERGENCY

The system never jumps straight from detection to alarm — it escalates deliberately, with hysteresis, and every transition is logged with the reasoning behind it.

<!-- 📸 PASTE: Dashboard's state timeline / risk sparkline showing a full escalation sequence -->

🖥️ Two Dashboards, Two Audiences

![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/00890e71c083f75a7ce38e756191ba8a090a3941/WhatsApp%20Image%202026-07-12%20at%2010.46.26%20AM.jpeg)


![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/53e7b87ef4b252219cce943bc5dc2666fdce5611/WhatsApp%20Image%202026-07-12%20at%2010.46.55%20AM.jpeg)
DashboardAudienceFocusCommand Center (dashboard/app.py, port 8501)Judges / technical reviewFull telemetry, 3D pose visualization, trust-score breakdown, GenieX reasoningRescue Operations Center (dashboard/rescue_app.py, port 8502)Field first respondersLightweight, high-contrast, action-only view — live incident log, nothing else

This split matters for the user-experience story: a swimmer's life doesn't depend on a responder parsing a dense engineering dashboard under pressure — it depends on one clear instruction, fast.  
 Qualcomm Ecosystem Used

ToolRoleQualcomm AI HubCompiled and profiled the phone's pose model against real target hardwareLiteRT / ONNX Runtime + QNNRuns pose estimation on the Hexagon NPUArduino UNO QEnvironmental sensing, local sensor fusion, emergency hardware controlGenieXGenerates the plain-English reasoning shown on the dashboardSarvam AIMultilingual (English / Hindi / Tamil / Kannada) spoken emergency alert, with offline TTS fallbackQualcomm AI Cloud 100Incident logging, analytics, heatmaps      Quick Start

1. Android App

bashcd Android-App
./gradlew installDebug

Settings → enter AI PC's local IPv4 address → WebSocket port 9090 → Apply.

2. Arduino UNO Q

Open in Arduino App Lab, wire sensors per Arduino-UNOQ/README.md, press Run.

3. AI PC — Fusion Engine + Dashboards

bash# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r AI-PC/fusion/requirements.txt

# .env in AI-PC/ root
SARVAM_API_KEY=your_api_key_here

# Terminal 1 — Fusion Engine backend (WebSocket + REST, port 9090)
python AI-PC/fusion/main.py

# Terminal 2 — Command Center dashboard
streamlit run AI-PC/dashboard/app.py --server.port 8501

# Terminal 3 — Rescue Operations Center dashboard
streamlit run AI-PC/dashboard/rescue_app.py --server.port 8502

# Terminal 4 (optional) — Telemetry simulator, if phone/Arduino aren't connected
python AI-PC/mock_client.py

RiverGuardian asks a second question: "Can the system trust its own judgment right now — and how soon might it need to act?"

Instead of one camera guessing, RiverGuardian runs two independent AI opinions — a phone's on-device pose model and the Arduino's own local sensor-fusion logic — cross-checked against real environmental data and live device-health monitoring, into a single explainable, trending risk score. Every decision is shown on screen in plain language, in real time, to both a technical command center and a field-responder dashboard. 
An Explainable, Multi-Device Edge AI Water Safety Platform

DeviceJobWhy it can't be dropped📱 Snapdragon Phone (Vision Node)Camera, HRPoseNet pose estimation, movement analysisOnly device with a camera + NPU for real-time vision🔌 Arduino UNO Q (Safety & Environment Node)Light / rain / water-level / temp-humidity sensing, device health, buzzer/RGB/relay controlPhysical sensing and deterministic hardware response the phone can't do💻 Snapdragon AI PC (Fusion Engine)Sensor fusion, risk analysis, mission state machine, live dashboardsWhere cross-verification and explainability actually happen☁ Qualcomm AI CloudIncident reports, analytics, heatmaps, data storageLong-term intelligence without blocking the real-time local loop

Data flow: Phone → pose metadata (WebSocket) → Fusion Engine. Arduino → sensor data (Serial/WebSocket) → Fusion Engine. Fusion Engine → emergency command → Arduino. Arduino/Fusion Engine → incident data → Qualcomm AI Cloud.

![image alt](https://github.com/Dharaneesh170688/River-guardian/blob/4bfe762ac7c9129bfa50d18d521e2fbf2659046c/WhatsApp%20Image%202026-07-12%20at%201.19.18%20PM.jpeg)

See. Predict. Verify. Protect.
## Project Structure 📂

```
.
├── App.kt
├── data
│   ├── local
│   │   ├── AppDatabase.kt
│   │   ├── Converters.kt
│   │   ├── daos
│   │   │   └── MoviesDao.kt
│   │   └── entities
│   ├── remote
│   │   ├── ApiInterface.kt
│   │   └── Movie.kt
│   └── repositories
│       └── movies
│           └── MoviesRepo.kt
├── di
│   ├── components
│   │   └── AppComponent.kt
│   └── modules
│       ├── ActivitiesBuilderModule.kt
│       ├── AppModule.kt
│       ├── DatabaseModule.kt
│       ├── NetworkModule.kt
│       ├── RepoModule.kt
│       └── ViewModelModule.kt
├── models
│   └── FeedItem.kt
├── ui
│   ├── activities
│   │   ├── feed
│   │   │   ├── FeedActivity.kt
│   │   │   └── FeedViewModel.kt
│   │   ├── movie
│   │   │   ├── MovieActivity.kt
│   │   │   └── MovieViewModel.kt
│   │   ├── splash
│   │   │   ├── SplashActivity.kt
│   │   │   └── SplashViewModel.kt
│   └── adapters
│       ├── FeedAdapter.kt
│       └── MoviesAdapter.kt
└── utils
    ├── BindingAdapters.kt
    ├── NetworkBoundResource.kt
    ├── retrofit
    │   ├── FlowResourceCallAdapterFactory.kt
    │   └── FlowResourceCallAdapter.kt
    └── test
        ├── EspressoIdlingResource.kt
        └── OpenForTesting.kt

21 directories, 30 files
```

