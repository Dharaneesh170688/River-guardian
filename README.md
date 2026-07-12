 RiverGuardian
⚠️ The Problem

Drowning is silent and fast. Most existing camera-based monitoring systems ask only one question: "Did the AI detect a drowning event?" They have no way to know if their own prediction can be trusted — rain, darkness, rising water, and device strain can all silently degrade a camera's confidence, leading to missed emergencies or false alarms. Wrong triggers waste rescue response; missed ones cost lives.



RiverGuardian asks a second question: "Can the system trust its own judgment right now — and how soon might it need to act?"

Instead of one camera guessing, RiverGuardian runs two independent AI opinions — a phone's on-device pose model and the Arduino's own local sensor-fusion logic — cross-checked against real environmental data and live device-health monitoring, into a single explainable, trending risk score. Every decision is shown on screen in plain language, in real time, to both a technical command center and a field-responder dashboard. 
An Explainable, Multi-Device Edge AI Water Safety Platform

DeviceJobWhy it can't be dropped📱 Snapdragon Phone (Vision Node)Camera, HRPoseNet pose estimation, movement analysisOnly device with a camera + NPU for real-time vision🔌 Arduino UNO Q (Safety & Environment Node)Light / rain / water-level / temp-humidity sensing, device health, buzzer/RGB/relay controlPhysical sensing and deterministic hardware response the phone can't do💻 Snapdragon AI PC (Fusion Engine)Sensor fusion, risk analysis, mission state machine, live dashboardsWhere cross-verification and explainability actually happen☁ Qualcomm AI CloudIncident reports, analytics, heatmaps, data storageLong-term intelligence without blocking the real-time local loop

Data flow: Phone → pose metadata (WebSocket) → Fusion Engine. Arduino → sensor data (Serial/WebSocket) → Fusion Engine. Fusion Engine → emergency command → Arduino. Arduino/Fusion Engine → incident data → Qualcomm AI Cloud.

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

## Credits 🤗

- 🤓 Icons are from [flaticon.com](https://www.flaticon.com/) 
- 🖌️ Design inspired from [AnimeXStream](https://github.com/mukul500/AnimeXStream) 
- 💽 Data from [top250 API](https://github.com/theapache64/top250)
- 📄 Thanks [Foodium](https://github.com/patilshreyas/Foodium)

## TODO 🗒️

  - [x] Improve algorithms and code review 
  - [x] Add test cases
  - [ ] Integrate OMDB API to add search feature
  - [ ] Add favorites

## Author ✍️

- theapache64
