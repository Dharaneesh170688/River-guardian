import streamlit as st
import requests
import time
import pandas as pd
import random
import datetime
import os
import json
import math
import streamlit.components.v1 as components

# Use wide layout for a command-center feel
st.set_page_config(layout="wide", page_title="RiverGuardian AI")

# Premium global CSS and fonts (Blue base)
PREMIUM_CSS = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    :root {
        --bg-1: #070B14;
        --bg-2: #0B111E;
        --card-bg: rgba(13, 22, 38, 0.75);
        --card-strong: rgba(9, 15, 28, 0.9);
        --card-border: rgba(59, 130, 246, 0.2);
        --accent: #00F0FF;
        --accent-2: #3B82F6;
        --success: #00E676;
        --warning: #FFAB00;
        --danger: #FF1744;
        --blue: #2979FF;
        --card-radius: 20px;
    }
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    html, body, [data-testid="stAppViewContainer"], .main {
        background: radial-gradient(circle at top right, rgba(29, 78, 216, 0.12), transparent 45%), radial-gradient(circle at bottom left, rgba(0, 240, 255, 0.08), transparent 45%), var(--bg-1) !important;
        color: #E6EEF6 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="block-container"] {
        padding: 1.5rem 2rem 2rem !important;
    }
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.01);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.4);
    }
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: 24px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        color: #E6EEF6;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 20px 48px rgba(30, 64, 175, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.1);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(0, 240, 255, 0.25);
    }
    .meta-title {
        color: #8CA3AF;
        font-size: 0.65rem;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    .meta-value {
        font-size: 1.15rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 20px 28px;
        margin-bottom: 20px;
        background: rgba(10, 15, 30, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: var(--card-radius);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(20px);
    }
    .brand { display: flex; align-items: center; gap: 16px; }
    .logo-badge {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        color: white;
        font-weight: 900;
        font-size: 1.15rem;
        letter-spacing: -0.04em;
        box-shadow: 0 10px 25px rgba(0, 240, 255, 0.25);
    }
    .brand-content { display: flex; flex-direction: column; gap: 2px; }
    .brand-title { margin: 0; font-size: 2.1rem; font-weight: 900; letter-spacing: -0.04em; color: #F8FAFC; font-family: 'Outfit', sans-serif; }
    .brand-subtitle { margin: 0; font-size: 0.85rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
    .brand-tagline { margin: 0; font-size: 0.8rem; color: #64748B; }
    .top-meta { display: flex; gap: 12px; align-items: center; }
    .meta-chip {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 90px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 8px 12px;
        font-size: 0.72rem;
        color: #CBD5E1;
        text-align: center;
        transition: all 0.2s ease;
    }
    .meta-chip:hover {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.3);
    }
    .meta-chip strong { color: #F8FAFC; font-weight: 700; }
    .meta-icon {
        font-size: 0.85rem;
        margin-bottom: 2px;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes scanline {
        0% { transform: translateY(-160px); }
        100% { transform: translateY(160px); }
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 23, 68, 0.2); }
        50% { box-shadow: 0 0 25px rgba(255, 23, 68, 0.5); }
    }
</style>"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# Top Header Layout (strictly no blank lines inside string)
TOPBAR_HTML = '''<div class="top-bar">
    <div class="brand">
        <div class="logo-badge">RG</div>
        <div class="brand-content">
            <div class="brand-title">RiverGuardian AI</div>
            <div class="brand-subtitle">See • Verify • Protect</div>
            <div class="brand-tagline">Enterprise AI Water Command Center (Qualcomm Stack)</div>
        </div>
    </div>
    <div class="top-meta">
        <div class="meta-chip"><span class="meta-icon">⏱</span>Time<br><strong id="chip-time">--:--:--</strong></div>
        <div class="meta-chip"><span class="meta-icon">☁️</span>Weather<br><strong>Clear</strong></div>
        <div class="meta-chip"><span class="meta-icon">📍</span>GPS<br><strong>COM3 Active</strong></div>
        <div class="meta-chip"><span class="meta-icon">🔋</span>Battery<br><strong>98%</strong></div>
        <div class="meta-chip"><span class="meta-icon">🌐</span>Network<br><strong>Connected</strong></div>
        <div class="meta-chip"><span class="meta-icon">🤖</span>Edge AI<br><strong>Active</strong></div>
    </div>
</div>
<script>
    function updateTime() {
        var now = new Date();
        var timeStr = now.toTimeString().split(' ')[0];
        var el = document.getElementById('chip-time');
        if (el) el.innerText = timeStr;
    }
    setInterval(updateTime, 1000);
    updateTime();
</script>'''

st.markdown(TOPBAR_HTML, unsafe_allow_html=True)

# API / WebSocket endpoints
BASE_URL = os.environ.get("FUSION_API_URL", "http://localhost:9090")
if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]
API_STATUS = f"{BASE_URL}/api/status"
API_METRICS = f"{BASE_URL}/api/metrics"
API_STATS = f"{BASE_URL}/api/stats"
API_INCIDENTS = f"{BASE_URL}/api/incidents"
API_SETTINGS = f"{BASE_URL}/api/settings"
_scheme = 'wss' if BASE_URL.startswith('https') else 'ws'
_host = BASE_URL.split('://', 1)[-1]
WS_URL = f"{_scheme}://{_host}/ws"

def make_svg_gauge(score: float) -> str:
    """Return a small SVG gauge for a 0..1 trust score using a blue/cyan gradient."""
    try:
        s = float(score)
    except Exception:
        s = 0.0
    s = max(0.0, min(1.0, s))
    pct = int(s * 100)
    angle = -90 + (s * 180)
    svg = f'''<div style="display:flex;align-items:center;justify-content:center;"><svg width="180" height="100" viewBox="0 0 180 100" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="blueGaugeGrad" x1="0" x2="1" y1="0" y2="0"><stop offset="0%" stop-color="#2979FF" /><stop offset="50%" stop-color="#00F0FF" /><stop offset="85%" stop-color="#FFAB00" /><stop offset="100%" stop-color="#FF1744" /></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="2" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><path d="M15,90 A75,75 0 0,1 165,90" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12" stroke-linecap="round"/><path d="M15,90 A75,75 0 0,1 165,90" fill="none" stroke="url(#blueGaugeGrad)" stroke-width="12" stroke-linecap="round" stroke-dasharray="236" stroke-dashoffset="{236 - int(s * 236)}" filter="url(#glow)"/><g transform="translate(90,90)"><line x1="0" y1="0" x2="0" y2="-65" stroke="#FFFFFF" stroke-width="4" transform="rotate({angle})" stroke-linecap="round" filter="url(#glow)"/><circle cx="0" cy="0" r="8" fill="#0A1128" stroke="#00F0FF" stroke-width="3" /></g><text x="90" y="82" font-family="'Inter', sans-serif" font-weight="800" font-size="18" fill="#FFFFFF" text-anchor="middle">{pct}%</text></svg></div>'''
    return svg

def make_svg_sparkline(values) -> str:
    """Render a compact SVG sparkline from a list of numeric values with a glowing gradient fill."""
    vals = [float(v) if v is not None else 0.0 for v in values]
    if not vals:
        return '<div style="text-align:center;color:#9ca3af">—</div>'
    w, h = 180, 40
    mx, mn = max(vals), min(vals)
    rng = mx - mn if mx != mn else 1.0
    pts = []
    for i, v in enumerate(vals):
        x = (i / (len(vals) - 1)) * w if len(vals) > 1 else w / 2
        y = h - ((v - mn) / rng) * h
        pts.append(f"{x:.1f},{y:.1f}")
    poly = ' '.join(pts)
    fill_pts = [f"0,{h}"] + pts + [f"{w},{h}"]
    fill_poly = ' '.join(fill_pts)
    svg = f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#00F0FF" stop-opacity="0.25"/><stop offset="100%" stop-color="#00F0FF" stop-opacity="0"/></linearGradient></defs><polygon fill="url(#sparkGrad)" points="{fill_poly}"/><polyline fill="none" stroke="#00F0FF" stroke-width="2" points="{poly}" stroke-linejoin="round" stroke-linecap="round" /></svg>'''
    return f'<div style="padding:6px;background:transparent;display:flex;justify-content:center;">{svg}</div>'

def make_camera_svg(state: str, movement: float, phone: float) -> str:
    """Draw a dynamic stick-figure pose skeleton based on state and confidence factors."""
    if phone < 0.05:
        return '''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><circle cx="110" cy="110" r="45" fill="none" stroke="rgba(59, 130, 246, 0.25)" stroke-width="2" stroke-dasharray="6,6" /><line x1="110" y1="30" x2="110" y2="190" stroke="rgba(59, 130, 246, 0.15)" stroke-width="1" /><line x1="30" y1="110" x2="190" y2="110" stroke="rgba(59, 130, 246, 0.15)" stroke-width="1" /><text x="110" y="114" font-family="monospace" font-size="10" fill="rgba(59, 130, 246, 0.5)" text-anchor="middle">WAITING FOR POSE...</text></svg>'''
    is_danger = state in ("DISTRESS", "EMERGENCY")
    t = time.time()
    offset_y = int(math.sin(t * 6) * 6) if is_danger else 0
    offset_x = int(math.cos(t * 4) * 5) if movement > 0.3 else 0
    if is_danger:
        svg = f'''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><defs><filter id="glow-danger"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect x="25" y="145" width="170" height="60" fill="rgba(255, 23, 68, 0.08)" rx="8" /><path d="M20,150 Q50,{142 + offset_y} 100,150 T180,150 T200,150" fill="none" stroke="#2979FF" stroke-width="3" opacity="0.8"/><path d="M10,165 Q60,{158 - offset_y} 110,165 T210,165" fill="none" stroke="#00F0FF" stroke-width="2" opacity="0.5"/><rect x="35" y="30" width="150" height="150" fill="none" stroke="#FF1744" stroke-width="2" stroke-dasharray="4,4" filter="url(#glow-danger)"/><text x="45" y="48" font-family="monospace" font-size="11" fill="#FF1744" font-weight="bold">WARNING: FL_DISTRESS</text><circle cx="{110 + offset_x}" cy="{105 + offset_y}" r="14" fill="none" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{119 + offset_y}" x2="{110 + offset_x}" y2="{145 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{124 + offset_y}" x2="{80 + offset_x}" y2="{75 - offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{80 + offset_x}" y1="{75 - offset_y}" x2="{65 + offset_x}" y2="{55 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{124 + offset_y}" x2="{140 - offset_x}" y2="{75 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{140 - offset_x}" y1="{75 + offset_y}" x2="{155 - offset_x}" y2="{55 - offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{145 + offset_y}" x2="{95 + offset_x}" y2="{175 + offset_y}" stroke="rgba(255, 23, 68, 0.4)" stroke-width="3"/><line x1="{110 + offset_x}" y1="{145 + offset_y}" x2="{125 + offset_x}" y2="{175 + offset_y}" stroke="rgba(255, 23, 68, 0.4)" stroke-width="3"/><circle cx="{110 + offset_x}" cy="{119 + offset_y}" r="4" fill="#FFFFFF" /><circle cx="{80 + offset_x}" cy="{75 - offset_y}" r="4" fill="#FFFFFF" /><circle cx="{140 - offset_x}" cy="{75 + offset_y}" r="4" fill="#FFFFFF" /></svg>'''
    else:
        svg = f'''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><defs><filter id="glow-normal"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect x="55" y="25" width="110" height="170" fill="none" stroke="#00F0FF" stroke-width="2" stroke-dasharray="3,3" filter="url(#glow-normal)"/><text x="62" y="42" font-family="monospace" font-size="11" fill="#00F0FF" font-weight="bold">TARGET_STABLE</text><circle cx="{110 + offset_x}" cy="58" r="16" fill="none" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="74" x2="{110 + offset_x}" y2="128" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="83" x2="{85 + offset_x}" y2="108" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{85 + offset_x}" y1="108" x2="{75 + offset_x}" y2="138" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="83" x2="{135 - offset_x}" y2="108" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{135 - offset_x}" y1="108" x2="{145 - offset_x}" y2="138" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="128" x2="{95 + offset_x}" y2="188" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="128" x2="{125 + offset_x}" y2="188" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><circle cx="{110 + offset_x}" cy="74" r="4" fill="#FFFFFF" /><circle cx="{85 + offset_x}" cy="108" r="4" fill="#FFFFFF" /><circle cx="{135 - offset_x}" cy="108" r="4" fill="#FFFFFF" /><circle cx="{110 + offset_x}" cy="128" r="4" fill="#FFFFFF" /></svg>'''
    return svg

# Define Chart.js metrics panel (strictly no blank lines inside template)
CHARTS_HTML_TEMPLATE = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; background-color: #0D1626; font-family: sans-serif; color: #c9d1d9; overflow: hidden; }}
        #chart-container {{ width: 100%; height: 180px; padding: 5px 0; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 5px; }}
        .tab-btn {{ background-color: #172439; border: 1px solid rgba(59, 130, 246, 0.15); color: #8CA3AF; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 10px; font-weight: bold; transition: all 0.2s ease; }}
        .tab-btn.active {{ background-color: #3B82F6; color: #ffffff; border-color: #3B82F6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.4); }}
        .tab-btn:hover:not(.active) {{ background-color: #20314C; color: #ffffff; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('latency')">FUSION LATENCY</button>
        <button class="tab-btn" onclick="switchTab('resources')">CPU/RAM USAGE</button>
        <button class="tab-btn" onclick="switchTab('fps')">FPS THROUGHPUT</button>
    </div>
    <div id="chart-container">
        <canvas id="perfChart"></canvas>
    </div>
    <script>
        var currentTab = 'latency';
        var maxDataPoints = 30;
        var labels = [];
        var latencyData = [];
        var cpuData = [];
        var ramData = [];
        var fpsData = [];
        var ctx = document.getElementById('perfChart').getContext('2d');
        var chart = new Chart(ctx, {{
            type: 'line',
            data: {{ labels: labels, datasets: [] }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: true, labels: {{ color: '#c9d1d9', font: {{ size: 9 }} }} }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(59, 130, 246, 0.05)' }}, ticks: {{ color: '#8ca3af', font: {{ size: 8 }} }} }},
                    y: {{ grid: {{ color: 'rgba(59, 130, 246, 0.05)' }}, ticks: {{ color: '#8ca3af', font: {{ size: 8 }} }} }}
                }},
                animation: {{ duration: 0 }}
            }}
        }});
        function updateChartDataset() {{
            if (currentTab === 'latency') {{
                chart.data.datasets = [{{
                    label: 'Latency (ms)',
                    data: latencyData,
                    borderColor: '#00F0FF',
                    backgroundColor: 'rgba(0, 240, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 1
                }}];
            }} else if (currentTab === 'resources') {{
                chart.data.datasets = [
                    {{ label: 'CPU (%)', data: cpuData, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', borderWidth: 2, fill: false, tension: 0.3, pointRadius: 1 }},
                    {{ label: 'RAM (%)', data: ramData, borderColor: '#FFAB00', backgroundColor: 'rgba(255, 171, 0, 0.05)', borderWidth: 2, fill: false, tension: 0.3, pointRadius: 1 }}
                ];
            }} else if (currentTab === 'fps') {{
                chart.data.datasets = [{{
                    label: 'FPS Throughput',
                    data: fpsData,
                    borderColor: '#FF1744',
                    backgroundColor: 'rgba(255, 23, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 1
                }}];
            }}
            chart.update();
        }}
        window.switchTab = function(tabName) {{
            currentTab = tabName;
            var buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(function(btn) {{ btn.classList.remove('active'); }});
            event.currentTarget.classList.add('active');
            updateChartDataset();
        }};
        updateChartDataset();
        var wsUrl = "{WS_URL}";
        var ws;
        function connect() {{
            ws = new WebSocket(wsUrl);
            ws.onmessage = function(event) {{
                try {{
                    var payload = JSON.parse(event.data);
                    if (payload.type === 'state_update' && payload.metrics) {{
                        var m = payload.metrics;
                        var timeStr = new Date(m.timestamp).toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit', second:'2-digit'}});
                        labels.push(timeStr);
                        latencyData.push(m.latency_ms);
                        cpuData.push(m.cpu_percent);
                        ramData.push(m.ram_percent);
                        fpsData.push(m.fps);
                        if (labels.length > maxDataPoints) {{
                            labels.shift();
                            latencyData.shift();
                            cpuData.shift();
                            ramData.shift();
                            fpsData.shift();
                        }}
                        chart.update();
                    }}
                }} catch (e) {{
                    console.error("Error parsing metrics: ", e);
                }}
            }};
            ws.onclose = function() {{ setTimeout(connect, 2000); }};
        }}
        connect();
        fetch("{API_METRICS}")
            .then(response => response.json())
            .then(data => {{
                if (data && data.length > 0) {{
                    labels.length = 0;
                    latencyData.length = 0;
                    cpuData.length = 0;
                    ramData.length = 0;
                    fpsData.length = 0;
                    data.forEach(m => {{
                        var timeStr = new Date(m.timestamp).toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit', second:'2-digit'}});
                        labels.push(timeStr);
                        latencyData.push(m.latency_ms);
                        cpuData.push(m.cpu_percent);
                        ramData.push(m.ram_percent);
                        fpsData.push(m.fps);
                    }});
                    while (labels.length > maxDataPoints) {{
                        labels.shift();
                        latencyData.shift();
                        cpuData.shift();
                        ramData.shift();
                        fpsData.shift();
                    }}
                    chart.update();
                }}
            }})
            .catch(err => console.error("Error fetching metrics history: ", err));
    </script>
</body>
</html>"""

# Helper function to normalize telemetry mappings (avoids breaking scenario mock runs)
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

# Format GenieX explanations strictly to match bulleted checklist layout without breaking page
def format_geniex_explanation(state: str, telemetry: dict, trust_score: float) -> str:
    decision_map = {"NORMAL": "SAFE", "OBSERVE": "WARNING", "SUSPICIOUS": "WARNING", "DISTRESS": "HIGH RISK", "EMERGENCY": "EMERGENCY"}
    decision = decision_map.get(state, "SAFE")
    phone_val = telemetry.get("phone", 0.0)
    water_val = telemetry.get("water", 0.0)
    movement_val = telemetry.get("movement", 0.0)
    rain_val = telemetry.get("rain", False)
    head_underwater = telemetry.get("head_underwater", False)
    is_underwater = False
    if isinstance(head_underwater, bool): is_underwater = head_underwater
    elif isinstance(head_underwater, (int, float)): is_underwater = head_underwater > 0.5
    elif isinstance(head_underwater, str): is_underwater = head_underwater.lower() in ("true", "1", "yes")
    facts = []
    if is_underwater: facts.append("Head underwater")
    else: facts.append("Head above water")
    if movement_val < 0.3: facts.append("Low movement")
    else: facts.append("Active movement")
    if water_val > 0.6: facts.append("Water level rising")
    else: facts.append("Water level stable")
    is_rain = False
    if isinstance(rain_val, bool): is_rain = rain_val
    elif isinstance(rain_val, (int, float)): is_rain = rain_val > 0.1
    elif isinstance(rain_val, str): is_rain = rain_val.lower() in ("true", "1", "yes", "on")
    if is_rain: facts.append("Rain detected")
    else: facts.append("No rain")
    if phone_val > 0.8: facts.append("Vision confidence high")
    elif phone_val > 0.4: facts.append("Vision confidence medium")
    else: facts.append("Vision confidence low")
    facts_str = "<br>".join([f"✓ {f}" for f in facts])
    score_pct = int(trust_score * 100)
    html = f"Decision:<br><strong>{decision}</strong><br><br>Reason:<br>{facts_str}<br><br>Trust Score:<br><strong>{score_pct}%</strong>"
    return html

# Layout Definitions (3 columns, 1 bottom spanning row)
col_left, col_center, col_right = st.columns([1.3, 1.3, 1.1], gap="medium")

with col_left:
    left_placeholder = st.empty()

with col_center:
    center_placeholder = st.empty()

with col_right:
    right_placeholder = st.empty()

bottom_placeholder = st.empty()

# Streamlit fragment to update dashboard dynamically
@st.fragment(run_every=1)
def update_dashboard_data():
    try:
        res_status = requests.get(API_STATUS, timeout=1.0)
        res_metrics = requests.get(API_METRICS, timeout=1.0)
        res_stats = requests.get(API_STATS, timeout=1.0)
        status_data = res_status.json() if res_status.status_code == 200 else {}
        metrics_history_data = res_metrics.json() if res_metrics.status_code == 200 else []
        stats_data = res_stats.json() if res_stats.status_code == 200 else {}
    except Exception as e:
        with center_placeholder.container():
            st.error(f"Cannot connect to Fusion Engine at {API_STATUS}.")
            st.warning("Please verify that the FastAPI backend server is running on port 8000.")
            st.info("Start the FastAPI server: `uvicorn fusion.main:app --port 8000 --reload` in your terminal.")
            st.info("Start the telemetry mock client: `python mock_client.py` in your terminal.")
        return

    # Extract Status and Telemetry
    telemetry = status_data.get("telemetry", {})
    # Normalize telemetry values for UI rendering
    telemetry = normalize_telemetry(telemetry)
    mission_state = status_data.get("mission", "NORMAL")
    trust_score = status_data.get("trust_score", 0.0)
    last_timestamp = status_data.get("timestamp")
    has_telemetry = bool(telemetry)

    # Initialize session states
    if "risk_history" not in st.session_state:
        st.session_state.risk_history = [0.0] * 60
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "English"

    # Append to risk progression
    st.session_state.risk_history.append(trust_score)
    if len(st.session_state.risk_history) > 60:
        st.session_state.risk_history.pop(0)

    # Telemetry mapped values
    light_val = telemetry.get("light", 0.0)
    water_val = telemetry.get("water", 0.0)
    rain_val = telemetry.get("rain", False)
    temp_val = telemetry.get("temp")
    humidity_val = telemetry.get("humidity")
    phone_val = telemetry.get("phone", 0.0)
    movement_val = telemetry.get("movement", 0.0)
    head_underwater_val = telemetry.get("head_underwater", False)
    person_count_val = telemetry.get("person_count", 0)

    # Connection status mapping
    telemetry_connection = "Disconnected"
    last_updated_str = "--"
    if last_timestamp:
        try:
            last_dt = datetime.datetime.fromisoformat(last_timestamp)
            last_updated_str = last_dt.strftime('%H:%M:%S')
            if (datetime.datetime.now() - last_dt).total_seconds() <= 5:
                telemetry_connection = "Live"
        except Exception:
            last_updated_str = last_timestamp
            telemetry_connection = "Disconnected"

    def fmt_num(value, fmt):
        return fmt.format(value) if isinstance(value, (int, float)) else "--"

    water_text = fmt_num(water_val, "{:.2f} m")
    flow_text = fmt_num(movement_val, "{:.2f} m/s")
    temp_text = fmt_num(temp_val, "{:.1f}°C")
    humidity_text = fmt_num(humidity_val, "{:.1f}%")
    light_text = fmt_num(light_val, "{:.1f}")
    
    underwater_text = "Yes" if head_underwater_val else "No"
    rain_text = "--"
    if rain_val is not None and rain_val != "":
        rain_str = str(rain_val).strip().lower()
        if rain_str in ("1", "true", "yes", "on"): rain_text = "Yes"
        elif rain_str in ("0", "false", "no", "off"): rain_text = "No"
        else: rain_text = str(rain_val)

    sensor_text = telemetry.get("device_status", "--")
    sensor_text = sensor_text.capitalize() if isinstance(sensor_text, str) else str(sensor_text)

    # Stats for Left column
    cam_fps = stats_data.get('camera_fps', '29') if isinstance(stats_data, dict) else '29'
    cam_latency = stats_data.get('camera_latency_ms', '23') if isinstance(stats_data, dict) else '23'

    # --- COLUMN 1: LEFT PANEL (Camera & Phone AI) ---
    with left_placeholder.container():
        st.markdown(f"""<div class="glass-card" style="padding: 20px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;"><div style="font-weight:800; font-size:1rem; color:#FFFFFF; display:flex; align-items:center; gap:8px;"><span style="color:#00F0FF; font-size:1.2rem; animation: blink 1s infinite;">●</span> PHONE AI MONITOR</div><div style="background:rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.2); color:#00F0FF; padding:3px 8px; border-radius:10px; font-size:0.7rem; font-weight:700; letter-spacing:0.5px;">SNAPDRAGON NPU</div></div><div style="position:relative; width:100%; height:320px; border-radius:14px; overflow:hidden; background:#040812; border:1px solid rgba(59, 130, 246, 0.25); display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 40px rgba(0,0,0,0.85);"><div style="position:absolute; top:0; left:0; width:100%; height:2px; background:rgba(0, 240, 255, 0.5); box-shadow:0 0 8px rgba(0, 240, 255, 0.7); animation: scanline 5s linear infinite; pointer-events:none; z-index:2;"></div><div style="position:absolute; inset:0; background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px); background-size: 15px 15px; pointer-events:none; z-index:1;"></div><div style="position:absolute; inset:0; z-index:2; display:flex; align-items:center; justify-content:center; pointer-events:none;">{make_camera_svg(mission_state, movement_val, phone_val)}</div><div style="position:absolute; bottom:12px; left:12px; z-index:3; background:rgba(10, 15, 30, 0.85); border:1px solid rgba(255,255,255,0.1); padding:8px 12px; border-radius:8px; font-family: monospace; font-size:0.75rem; color:#8CA3AF; line-height:1.4;"><div style="color:#00F0FF; font-weight:bold;">ISO 800 | F/1.8 | 1/60s</div><div>STATE: <span style="color:#E6EEF6;">{mission_state}</span></div><div>POSE: <span style="color:#E6EEF6;">{("DROWNING GESTURE" if mission_state in ("DISTRESS", "EMERGENCY") else "VERTICAL" if phone_val > 0.4 else "NO TARGET")}</span></div></div><div style="position:absolute; top:12px; right:12px; z-index:3; background:rgba(0, 240, 255, 0.1); border: 1px solid #00F0FF; padding:4px 8px; border-radius:6px; font-family: monospace; font-size:0.7rem; color:#00F0FF; font-weight:bold; letter-spacing:1px; animation: blink 1.2s infinite;">LIVE</div></div><div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; margin-top:14px;"><div class="metric-card"><div class="meta-title">POSE CONFIDENCE</div><div class="meta-value" style="color:#00F0FF;">{int(phone_val * 100)}%</div></div><div class="metric-card"><div class="meta-title">MOVEMENT</div><div class="meta-value" style="color:#00F0FF;">{flow_text}</div></div><div class="metric-card"><div class="meta-title">HEAD UNDERWATER</div><div class="meta-value" style="color:#00F0FF;">{underwater_text}</div></div><div class="metric-card"><div class="meta-title">PERSON COUNT</div><div class="meta-value" style="color:#00F0FF;">{person_count_val}</div></div><div class="metric-card" style="grid-column: span 2;"><div class="meta-title">AI THROUGHPUT</div><div class="meta-value" style="color:#00F0FF;">{cam_fps} FPS | {cam_latency} ms</div></div></div></div>""", unsafe_allow_html=True)

    # --- COLUMN 2: CENTER PANEL (Decision & Fusion) ---
    with center_placeholder.container():
        decision_map = {"NORMAL": "SAFE", "OBSERVE": "WARNING", "SUSPICIOUS": "WARNING", "DISTRESS": "HIGH RISK", "EMERGENCY": "EMERGENCY"}
        decision = decision_map.get(mission_state, "SAFE")
        if decision == "EMERGENCY":
            banner_style = "border:1px solid #FF1744; background:rgba(255,23,68,0.18); color:#FF1744; text-shadow: 0 0 10px rgba(255,23,68,0.5); animation: pulse-red 2s infinite;"
            badge_lbl = "🚨 EMERGENCY ACTIVE"
        elif decision == "HIGH RISK":
            banner_style = "border:1px solid #FF8A80; background:rgba(255,138,128,0.12); color:#FF5252;"
            badge_lbl = "⚠️ HIGH RISK ALERT"
        elif decision == "WARNING":
            banner_style = "border:1px solid #FFAB00; background:rgba(255,171,0,0.12); color:#FFC400;"
            badge_lbl = "🔍 WARNING STATE"
        else:
            banner_style = "border:1px solid #00F0FF; background:rgba(0,240,255,0.08); color:#00F0FF; text-shadow: 0 0 8px rgba(0,240,255,0.3);"
            badge_lbl = "✅ STATE: SAFE"

        if not has_telemetry:
            badge_lbl = "⏳ WAITING FOR TELEMETRY"
            banner_style = "border:1px solid rgba(255,255,255,0.15); background:rgba(255,255,255,0.05); color:#8CA3AF;"

        vision_conf_pct = int(status_data.get("vision_confidence", phone_val) * 100)
        sensor_conf_pct = int(status_data.get("sensor_confidence", 1.0) * 100)
        final_trust_pct = int(status_data.get("final_trust_score", 1.0 - trust_score) * 100)
        final_risk_pct = int(status_data.get("final_risk_score", trust_score) * 100)
        geniex_explanation = format_geniex_explanation(mission_state, telemetry, trust_score)

        st.markdown(f"""<div style="padding:14px 20px; border-radius:16px; text-align:center; font-family:'Outfit', sans-serif; margin-bottom:18px; font-weight:800; font-size:1.35rem; {banner_style}">{badge_lbl}</div><div class="glass-card" style="text-align:center; padding: 20px; margin-bottom: 18px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">FUSION ENGINE</div><div style="font-family:monospace; color:#8CA3AF; font-size:0.78rem;">RISK: {final_risk_pct}%</div></div><div style="margin:12px 0;">{make_svg_gauge(trust_score)}</div><div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:14px; text-align:left;"><div style="background:rgba(255,255,255,0.02); padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.65rem; color:#8CA3AF;">VISION CONF.</div><strong style="color:#00F0FF; font-size:0.85rem;">{vision_conf_pct}%</strong></div><div style="background:rgba(255,255,255,0.02); padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.65rem; color:#8CA3AF;">SENSOR CONF.</div><strong style="color:#00F0FF; font-size:0.85rem;">{sensor_conf_pct}%</strong></div><div style="background:rgba(255,255,255,0.02); padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.65rem; color:#8CA3AF;">TRUST SCORE</div><strong style="color:#00F0FF; font-size:0.85rem;">{final_trust_pct}%</strong></div><div style="background:rgba(255,255,255,0.02); padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.65rem; color:#8CA3AF;">RISK SCORE</div><strong style="color:#FF1744; font-size:0.85rem;">{final_risk_pct}%</strong></div></div></div><div class="glass-card" style="padding: 20px; margin-bottom: 18px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">DECISION ENGINE</div><div style="background:rgba(0, 240, 255, 0.1); border:1px solid #00F0FF; color:#00F0FF; padding:2px 8px; border-radius:8px; font-size:0.7rem; font-weight:700;">AI PC LOCAL</div></div><div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:0.8rem; color:#8CA3AF;">Current Status: <strong style="color:#FFFFFF;">{decision}</strong></span><span style="font-size:0.8rem; color:#8CA3AF;">Risk Score: <strong style="color:#FF1744;">{final_risk_pct}%</strong></span></div></div><div class="glass-card" style="padding: 20px; margin-bottom: 0px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">🧠 GENIEX EXPLAINABILITY</div><div style="background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.3); color:#60A5FA; padding:2px 8px; border-radius:8px; font-size:0.7rem; font-weight:700;">LOCAL LLM</div></div><div style="background: rgba(4, 8, 18, 0.6); border: 1px solid rgba(59, 130, 246, 0.15); padding:14px; border-radius:12px; font-family: monospace; font-size:0.85rem; color:#C9D1D9; line-height:1.6; min-height:86px; margin-bottom:12px;">{geniex_explanation}</div></div>""", unsafe_allow_html=True)
        
        # Reset State Machine Button
        if st.button("🔄 Reset State Machine", key="reset_state_btn", use_container_width=True):
            try:
                requests.post(f"{BASE_URL}/api/reset", timeout=1.0)
                st.success("State machine reset to NORMAL!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {e}")

    # --- COLUMN 3: RIGHT PANEL (Arduino Sensors) ---
    with right_placeholder.container():
        st.markdown(f"""<div class="glass-card" style="padding:20px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;"><div style="font-weight:800; font-size:1rem; color:#FFFFFF; display:flex; align-items:center; gap:8px;">ENVIRONMENT ARDUINO</div><div style="background:{'rgba(0, 230, 118, 0.15)' if telemetry_connection == 'Live' else 'rgba(255, 171, 0, 0.15)'}; border: 1px solid {'rgba(0, 230, 118, 0.3)' if telemetry_connection == 'Live' else 'rgba(255, 171, 0, 0.3)'}; color:{'#00E676' if telemetry_connection == 'Live' else '#FFAB00'}; padding:3px 8px; border-radius:10px; font-size:0.7rem; font-weight:700;">{telemetry_connection.upper()}</div></div><div style="display:flex; flex-direction:column; gap:10px;"><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">💧</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Water Level</div><div style="font-size:0.65rem; color:#64748B;">River Depth Sensor</div></div></div><div style="font-size:1.15rem; font-weight:800; color:#00F0FF;">{water_text}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">🌧️</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Rainfall</div><div style="font-size:0.65rem; color:#64748B;">Precipitation Rate</div></div></div><div style="font-size:1.15rem; font-weight:800; color:#00F0FF;">{rain_text}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">🌡️</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Temperature</div><div style="font-size:0.65rem; color:#64748B;">Ambient Air Temp</div></div></div><div style="font-size:1.15rem; font-weight:800; color:#00F0FF;">{temp_text}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">💦</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Humidity</div><div style="font-size:0.65rem; color:#64748B;">Air Moisture Context</div></div></div><div style="font-size:1.15rem; font-weight:800; color:#00F0FF;">{humidity_text}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">☀️</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Light Level (LDR)</div><div style="font-size:0.65rem; color:#64748B;">Ambient Brightness</div></div></div><div style="font-size:1.15rem; font-weight:800; color:#00F0FF;">{light_text}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:10px;"><div style="display:flex; align-items:center; gap:8px;"><span style="font-size:1.15rem;">⚙️</span><div><div style="font-size:0.78rem; color:#94A3B8; font-weight:600;">Device Status</div><div style="font-size:0.65rem; color:#64748B;">Hardware Status</div></div></div><div style="font-size:1.05rem; font-weight:800; color:{'#00E676' if sensor_text == 'Healthy' else '#FFAB00'};">{sensor_text}</div></div></div><div style="margin-top:14px; font-family:monospace; font-size:0.7rem; color:#64748B; text-align:center; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;">COM PORT: COM3 | ARDUINO UNO Q</div></div>""", unsafe_allow_html=True)

    # --- BOTTOM SECTION (Incident timeline, Cloud escalation, Sarvam Alerts, Sensor Health) ---
    with bottom_placeholder.container():
        col_bt1, col_bt2, col_bt3, col_bt4 = st.columns(4, gap="medium")
        
        # 1. Timeline Module
        with col_bt1:
            st.markdown("""<div class="glass-card" style="min-height:360px; padding:20px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px; display:flex; align-items:center; gap:8px;"><span>📜</span> RISK PROGRESSION</div>""", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:0.75rem; margin-bottom:8px; color:#8CA3AF;'>Final Risk Confidence (60s buffer)</div>", unsafe_allow_html=True)
            st.markdown(make_svg_sparkline(st.session_state.risk_history), unsafe_allow_html=True)
            total_inc = stats_data.get('total_incidents', 0) if isinstance(stats_data, dict) else 0
            st.markdown(f"""<div style="margin-top:20px; display:flex; flex-direction:column; gap:8px;"><div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; border:1px solid rgba(255,255,255,0.04);"><span style="font-size:0.75rem; color:#8CA3AF;">CURRENT RISK</span><strong style="color:#00F0FF;">{int(trust_score*100)}%</strong></div><div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; border:1px solid rgba(255,255,255,0.04);"><span style="font-size:0.75rem; color:#8CA3AF;">TOTAL EVENTS LOGGED</span><strong style="color:#FFFFFF;">{total_inc}</strong></div></div></div>""", unsafe_allow_html=True)

        # 2. Cloud Escalation Module
        with col_bt2:
            st.markdown("""<div class="glass-card" style="min-height:360px; padding:20px; overflow:hidden;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px; display:flex; align-items:center; gap:8px;"><span>☁️</span> CLOUD ESCALATION</div>""", unsafe_allow_html=True)
            cloud_sync = stats_data.get('cloud_synced', False) if isinstance(stats_data, dict) else False
            escalated_count = stats_data.get('cloud_escalated_count', 0) if isinstance(stats_data, dict) else 0
            st.markdown(f"""<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:0.78rem; color:#8CA3AF;">Cloud AI Sync Status</span><strong style="color:{'#00E676' if cloud_sync else '#8CA3AF'}; font-size:0.8rem;">{'SYNCED' if cloud_sync else 'INACTIVE'}</strong></div><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05);"><span style="font-size:0.78rem; color:#8CA3AF;">Escalated Incidents</span><strong style="color:#00F0FF; font-size:0.8rem;">{escalated_count}</strong></div>""", unsafe_allow_html=True)
            try:
                res_inc = requests.get(API_INCIDENTS, timeout=1.0)
                if res_inc.status_code == 200:
                    inc_list = res_inc.json()
                    if inc_list:
                        html_table = """<table style="width:100%; border-collapse:collapse; font-size:0.75rem; text-align:left; color:#E6EEF6;"><thead><tr style="border-bottom:1px solid rgba(255,255,255,0.1); background:rgba(255,255,255,0.02);"><th style="padding:4px; font-weight:600; color:#8CA3AF;">Time</th><th style="padding:4px; font-weight:600; color:#8CA3AF;">Verdict</th><th style="padding:4px; font-weight:600; color:#8CA3AF;">Risk Score</th></tr></thead><tbody>"""
                        for inc in inc_list[-2:]:
                            t_str = inc.get("timestamp", "")
                            try:
                                time_lbl = datetime.datetime.fromisoformat(t_str).strftime("%M:%S")
                            except Exception:
                                time_lbl = t_str
                            state = inc.get("state", "NORMAL")
                            s_style = "color:#FF1744; font-weight:bold;" if state in ("EMERGENCY", "HIGH RISK") else "color:#FFAB00; font-weight:bold;"
                            risk_pct = int(inc.get("trust_score", 0.0) * 100)
                            html_table += f"""<tr style="border-bottom:1px solid rgba(255,255,255,0.04);"><td style="padding:4px; color:#94A3B8;">{time_lbl}</td><td style="padding:4px; {s_style}">{state}</td><td style="padding:4px; color:#00F0FF; font-weight:bold;">{risk_pct}%</td></tr>"""
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
            except Exception:
                pass
            st.markdown("</div>", unsafe_allow_html=True)

        # 3. Sarvam Alerts Module
        with col_bt3:
            st.markdown("""<div class="glass-card" style="min-height:360px; padding:20px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px; display:flex; align-items:center; gap:8px;"><span>📢</span> SARVAM ALERTS</div>""", unsafe_allow_html=True)
            lang_options = ["English", "Hindi", "Tamil", "Kannada"]
            try:
                curr_idx = lang_options.index(st.session_state.selected_lang)
            except Exception:
                curr_idx = 0
            selected = st.selectbox("Alert Language", lang_options, index=curr_idx, key="lang_selector")
            if selected != st.session_state.selected_lang:
                st.session_state.selected_lang = selected
                try:
                    requests.post(API_SETTINGS, json={"language": selected.lower()}, timeout=1.0)
                except Exception:
                    pass
            st.markdown(f"""<div style="margin-top:14px; display:flex; flex-direction:column; gap:8px;"><div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; border:1px solid rgba(255,255,255,0.04);"><span style="font-size:0.75rem; color:#8CA3AF;">VOICE ALERT</span><strong style="color:#00F0FF;">ONLINE</strong></div><div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; border:1px solid rgba(255,255,255,0.04);"><span style="font-size:0.75rem; color:#8CA3AF;">SMS DISPATCH</span><strong style="color:#00F0FF;">READY</strong></div></div></div>""", unsafe_allow_html=True)

        # 4. Sensor Health & Metrics Chart
        with col_bt4:
            st.markdown("""<div class="glass-card" style="min-height:360px; padding:20px;"><div style="font-weight:700; color:#E6EEF6; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; display:flex; align-items:center; gap:8px;"><span>🔧</span> DIAGNOSTICS & PERF</div>""", unsafe_allow_html=True)
            components.html(CHARTS_HTML_TEMPLATE, height=216)
            cpu_pct = stats_data.get('cpu_percent', '12.5') if isinstance(stats_data, dict) else '12.5'
            ram_pct = stats_data.get('ram_percent', '45.0') if isinstance(stats_data, dict) else '45.0'
            st.markdown(f"""<div style="margin-top:10px; display:grid; grid-template-columns:1fr 1fr; gap:8px;"><div style="background:rgba(255,255,255,0.02); padding:6px; border-radius:8px; text-align:center; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.6rem; color:#8CA3AF;">CPU</div><strong style="color:#00F0FF; font-size:0.85rem;">{cpu_pct}%</strong></div><div style="background:rgba(255,255,255,0.02); padding:6px; border-radius:8px; text-align:center; border:1px solid rgba(255,255,255,0.04);"><div style="font-size:0.6rem; color:#8CA3AF;">RAM</div><strong style="color:#00F0FF; font-size:0.85rem;">{ram_pct}%</strong></div></div></div>""", unsafe_allow_html=True)

# Start dashboard update loop
update_dashboard_data()
