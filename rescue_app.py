import streamlit as st
import requests
import datetime
import os
import math
import time
import pandas as pd

st.set_page_config(layout="wide", page_title="Rescue Dashboard - RiverGuardian X")

# Premium global CSS and fonts (Red/Dark base for rescue operations)
RESCUE_CSS = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
    :root {
        --bg-1: #0A0505;
        --bg-2: #140A0A;
        --card-bg: rgba(30, 15, 15, 0.75);
        --card-border: rgba(239, 68, 68, 0.25);
        --accent: #FF1744;
        --accent-blue: #00F0FF;
        --success: #00E676;
        --warning: #FFAB00;
        --danger: #FF1744;
        --card-radius: 20px;
    }
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    html, body, [data-testid="stAppViewContainer"], .main {
        background: radial-gradient(circle at top right, rgba(239, 68, 68, 0.12), transparent 45%), radial-gradient(circle at bottom left, rgba(0, 240, 255, 0.08), transparent 45%), var(--bg-1) !important;
        color: #E6EEF6 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="block-container"] {
        padding: 1.5rem 2rem 2rem !important;
    }
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: 24px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        color: #E6EEF6;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(239, 68, 68, 0.45);
    }
    .rescue-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 20px 28px;
        margin-bottom: 20px;
        background: rgba(20, 10, 10, 0.95);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: var(--card-radius);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
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
        background: linear-gradient(135deg, var(--accent), #B71C1C);
        color: white;
        font-weight: 900;
        font-size: 1.15rem;
        letter-spacing: -0.04em;
        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.35);
    }
    .brand-content { display: flex; flex-direction: column; gap: 2px; }
    .brand-title { margin: 0; font-size: 2.1rem; font-weight: 900; letter-spacing: -0.04em; color: #F8FAFC; font-family: 'Outfit', sans-serif; }
    .brand-subtitle { margin: 0; font-size: 0.85rem; color: #FCA5A5; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
    .brand-tagline { margin: 0; font-size: 0.8rem; color: #FCA5A5; opacity: 0.8; }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes scanline {
        0% { transform: translateY(-160px); }
        100% { transform: translateY(160px); }
    }
</style>"""

st.markdown(RESCUE_CSS, unsafe_allow_html=True)

RESCUE_TOPBAR_HTML = '''<div class="rescue-bar">
    <div class="brand">
        <div class="logo-badge">RO</div>
        <div class="brand-content">
            <div class="brand-title">Rescue Operations Center</div>
            <div class="brand-subtitle">RiverGuardian X • Rescue Client Dashboard</div>
            <div class="brand-tagline">Real-Time Drowning Alert & Dispatch Synchronization System</div>
        </div>
    </div>
    <div style="font-family:monospace; background:rgba(239, 68, 68, 0.15); border:1px solid rgba(239, 68, 68, 0.3); color:#FF1744; padding:8px 16px; border-radius:10px; font-weight:bold; letter-spacing:1px;">
        ROLE: DISPATCH COMMAND
    </div>
</div>'''

st.markdown(RESCUE_TOPBAR_HTML, unsafe_allow_html=True)

# API endpoint references
BASE_URL = os.environ.get("FUSION_API_URL", "http://localhost:9090")
if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]
API_STATUS = f"{BASE_URL}/api/status"
API_INCIDENTS = f"{BASE_URL}/api/incidents"

def make_camera_svg(state: str, movement: float, phone: float) -> str:
    """Draw a dynamic stick-figure pose skeleton based on state and confidence factors."""
    if phone < 0.05:
        return '''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><circle cx="110" cy="110" r="45" fill="none" stroke="rgba(239, 68, 68, 0.25)" stroke-width="2" stroke-dasharray="6,6" /><line x1="110" y1="30" x2="110" y2="190" stroke="rgba(239, 68, 68, 0.15)" stroke-width="1" /><line x1="30" y1="110" x2="190" y2="110" stroke="rgba(239, 68, 68, 0.15)" stroke-width="1" /><text x="110" y="114" font-family="monospace" font-size="10" fill="rgba(239, 68, 68, 0.5)" text-anchor="middle">WAITING FOR POSE...</text></svg>'''
    is_danger = state in ("DISTRESS", "EMERGENCY")
    t = time.time()
    offset_y = int(math.sin(t * 6) * 6) if is_danger else 0
    offset_x = int(math.cos(t * 4) * 5) if movement > 0.3 else 0
    if is_danger:
        svg = f'''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><defs><filter id="glow-danger"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect x="25" y="145" width="170" height="60" fill="rgba(255, 23, 68, 0.08)" rx="8" /><path d="M20,150 Q50,{142 + offset_y} 100,150 T180,150 T200,150" fill="none" stroke="#2979FF" stroke-width="3" opacity="0.8"/><path d="M10,165 Q60,{158 - offset_y} 110,165 T210,165" fill="none" stroke="#00F0FF" stroke-width="2" opacity="0.5"/><rect x="35" y="30" width="150" height="150" fill="none" stroke="#FF1744" stroke-width="2" stroke-dasharray="4,4" filter="url(#glow-danger)"/><text x="45" y="48" font-family="monospace" font-size="11" fill="#FF1744" font-weight="bold">WARNING: FL_DISTRESS</text><circle cx="{110 + offset_x}" cy="{105 + offset_y}" r="14" fill="none" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{119 + offset_y}" x2="{110 + offset_x}" y2="{145 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{124 + offset_y}" x2="{80 + offset_x}" y2="{75 - offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{80 + offset_x}" y1="{75 - offset_y}" x2="{65 + offset_x}" y2="{55 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{124 + offset_y}" x2="{140 - offset_x}" y2="{75 + offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{140 - offset_x}" y1="{75 + offset_y}" x2="{155 - offset_x}" y2="{55 - offset_y}" stroke="#FF1744" stroke-width="3" filter="url(#glow-danger)"/><line x1="{110 + offset_x}" y1="{145 + offset_y}" x2="{95 + offset_x}" y2="{175 + offset_y}" stroke="rgba(255, 23, 68, 0.4)" stroke-width="3"/><line x1="{110 + offset_x}" y1="{145 + offset_y}" x2="{125 + offset_x}" y2="{175 + offset_y}" stroke="rgba(255, 23, 68, 0.4)" stroke-width="3"/><circle cx="{110 + offset_x}" cy="{119 + offset_y}" r="4" fill="#FFFFFF" /><circle cx="{80 + offset_x}" cy="{75 - offset_y}" r="4" fill="#FFFFFF" /><circle cx="{140 - offset_x}" cy="{75 + offset_y}" r="4" fill="#FFFFFF" /></svg>'''
    else:
        svg = f'''<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg"><defs><filter id="glow-normal"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect x="55" y="25" width="110" height="170" fill="none" stroke="#00F0FF" stroke-width="2" stroke-dasharray="3,3" filter="url(#glow-normal)"/><text x="62" y="42" font-family="monospace" font-size="11" fill="#00F0FF" font-weight="bold">TARGET_STABLE</text><circle cx="{110 + offset_x}" cy="58" r="16" fill="none" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="74" x2="{110 + offset_x}" y2="128" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="83" x2="{85 + offset_x}" y2="108" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{85 + offset_x}" y1="108" x2="{75 + offset_x}" y2="138" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="83" x2="{135 - offset_x}" y2="108" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{135 - offset_x}" y1="108" x2="{145 - offset_x}" y2="138" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="128" x2="{95 + offset_x}" y2="188" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><line x1="{110 + offset_x}" y1="128" x2="{125 + offset_x}" y2="188" stroke="#00F0FF" stroke-width="3" filter="url(#glow-normal)"/><circle cx="{110 + offset_x}" cy="74" r="4" fill="#FFFFFF" /><circle cx="{85 + offset_x}" cy="108" r="4" fill="#FFFFFF" /><circle cx="{135 - offset_x}" cy="108" r="4" fill="#FFFFFF" /><circle cx="{110 + offset_x}" cy="128" r="4" fill="#FFFFFF" /></svg>'''
    return svg

def format_rescue_explanation(state: str, telemetry: dict, trust_score: float) -> str:
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
    facts_str = "<br>".join([f"✓ {f}" for f in facts])
    action = "Notify rescue team immediately. Prepare life raft deployment." if state in ("DISTRESS", "EMERGENCY") else "Monitor target state closely. No action needed."
    html = f"Decision:<br><strong>{decision}</strong><br><br>Reason:<br>{facts_str}<br><br>Trust Score:<br><strong>{int(trust_score * 100)}%</strong><br><br>Recommended Action:<br><strong>{action}</strong>"
    return html

# 2 Columns for Rescue Dashboard main view
col_view_left, col_view_right = st.columns([1.1, 1.3], gap="large")

with col_view_left:
    left_placeholder = st.empty()

with col_view_right:
    right_placeholder = st.empty()

bottom_timeline_placeholder = st.empty()

# Streamlit fragment to update rescue dashboard dynamically
@st.fragment(run_every=1)
def update_rescue_dashboard():
    try:
        res_status = requests.get(API_STATUS, timeout=1.0)
        res_incidents = requests.get(API_INCIDENTS, timeout=1.0)
        status_data = res_status.json() if res_status.status_code == 200 else {}
        incidents_data = res_incidents.json() if res_incidents.status_code == 200 else []
    except Exception:
        with right_placeholder.container():
            st.error(f"Cannot connect to Laptop 1 central server at {API_STATUS}.")
            st.warning("Please ensure the Fusion Engine backend is running on Laptop 1.")
        return

    # Extract Status and Telemetry
    telemetry = status_data.get("telemetry", {})
    mission_state = status_data.get("mission", "NORMAL")
    trust_score = status_data.get("trust_score", 0.0)
    incident_id = status_data.get("incident_id", "INC-INIT")
    last_timestamp = status_data.get("timestamp")
    
    # Check if there is active emergency
    decision_map = {"NORMAL": "SAFE", "OBSERVE": "WARNING", "SUSPICIOUS": "WARNING", "DISTRESS": "HIGH RISK", "EMERGENCY": "EMERGENCY"}
    decision = decision_map.get(mission_state, "SAFE")

    # Mapped values
    phone_val = telemetry.get("phone", 0.0)
    movement_val = telemetry.get("movement", 0.0)
    
    # Sync rescue status in session state
    if "rescue_status_map" not in st.session_state:
        st.session_state.rescue_status_map = {}
        
    current_rescue_status = st.session_state.rescue_status_map.get(incident_id, "STANDBY")

    # Format timestamp
    detection_time_str = "--"
    if last_timestamp:
        try:
            dt = datetime.datetime.fromisoformat(last_timestamp)
            detection_time_str = dt.strftime('%H:%M:%S')
        except Exception:
            detection_time_str = last_timestamp

    # Keep track of latest emergency snapshot (capture SVG when state rises to alert)
    if "latest_emergency_id" not in st.session_state:
        st.session_state.latest_emergency_id = None
        st.session_state.latest_snapshot_svg = None

    if decision in ("HIGH RISK", "EMERGENCY") and st.session_state.latest_emergency_id != incident_id:
        st.session_state.latest_emergency_id = incident_id
        st.session_state.latest_snapshot_svg = make_camera_svg(mission_state, movement_val, phone_val)

    # --- LEFT COLUMN: LIVE SKELETON FEED AND LATEST SNAPSHOT ---
    with left_placeholder.container():
        st.markdown(f"""<div class="glass-card" style="padding:20px; margin-bottom:20px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;"><div style="font-weight:800; font-size:1rem; color:#FFFFFF; display:flex; align-items:center; gap:8px;"><span style="color:#FF1744; font-size:1.2rem; animation: blink 1s infinite;">●</span> LIVE POSE TRACKING</div><div style="background:rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color:#FF1744; padding:3px 8px; border-radius:10px; font-size:0.7rem; font-weight:700;">RESCUE CLIENT</div></div><div style="position:relative; width:100%; height:260px; border-radius:14px; overflow:hidden; background:#0A0505; border:1px solid rgba(239,68,68,0.3); display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 30px rgba(0,0,0,0.85);"><div style="position:absolute; inset:0; background-image: linear-gradient(rgba(239,68,68,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(239,68,68,0.02) 1px, transparent 1px); background-size: 15px 15px; pointer-events:none; z-index:1;"></div><div style="position:absolute; inset:0; z-index:2; display:flex; align-items:center; justify-content:center; pointer-events:none;">{make_camera_svg(mission_state, movement_val, phone_val)}</div></div></div>""", unsafe_allow_html=True)
        snap_svg = st.session_state.latest_snapshot_svg if st.session_state.latest_snapshot_svg else make_camera_svg("NORMAL", 0.0, 0.0)
        st.markdown(f"""<div class="glass-card" style="padding:20px;"><div style="font-weight:800; font-size:0.9rem; color:#FFFFFF; margin-bottom:14px;">LATEST CAMERA SNAPSHOT (AT ALERT TIME)</div><div style="width:100%; height:200px; border-radius:14px; background:#120707; border:1px solid rgba(255,255,255,0.05); display:flex; align-items:center; justify-content:center;">{snap_svg}</div></div>""", unsafe_allow_html=True)

    # --- RIGHT COLUMN: EMERGENCY DETAILS & ACTION CONTROLS ---
    with right_placeholder.container():
        # Flashing Emergency Banner
        if decision == "EMERGENCY":
            banner_style = "border:1px solid #FF1744; background:rgba(255,23,68,0.22); color:#FF1744; text-shadow: 0 0 10px rgba(255,23,68,0.6); animation: blink 1.2s infinite;"
            banner_lbl = "🚨 EMERGENCY ACTIVE - DISPATCH LIFERAFTS"
        elif decision == "HIGH RISK":
            banner_style = "border:1px solid #FF8A80; background:rgba(255,138,128,0.15); color:#FF5252;"
            banner_lbl = "⚠️ HIGH RISK - PREPARE TEAM"
        elif decision == "WARNING":
            banner_style = "border:1px solid #FFAB00; background:rgba(255,171,0,0.15); color:#FFC400;"
            banner_lbl = "🔍 WARNING STATE - ACTIVE OBSERVATION"
        else:
            banner_style = "border:1px solid #00E676; background:rgba(0,230,118,0.08); color:#00E676;"
            banner_lbl = "✅ STATE: SAFE"

        st.markdown(f"""<div style="padding:14px 20px; border-radius:16px; text-align:center; font-family:'Outfit', sans-serif; margin-bottom:18px; font-weight:800; font-size:1.2rem; {banner_style}">{banner_lbl}</div>""", unsafe_allow_html=True)
        geniex_exp = format_rescue_explanation(mission_state, telemetry, trust_score)
        st.markdown(f"""<div class="glass-card" style="padding:22px; margin-bottom:20px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;"><div style="font-weight:800; font-size:0.95rem; color:#FFFFFF;">ACTIVE INCIDENT LOG</div><div style="font-family:monospace; color:#E6EEF6; font-weight:bold;">ID: {incident_id}</div></div><div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:16px;"><div style="background:rgba(255,255,255,0.01); padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);"><div style="font-size:0.68rem; color:#FCA5A5;">DETECTION TIME</div><strong style="color:#FFFFFF; font-size:0.88rem;">{detection_time_str}</strong></div><div style="background:rgba(255,255,255,0.01); padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03);"><div style="font-size:0.68rem; color:#FCA5A5;">ACTIVE STATUS</div><strong style="color:#FF1744; font-size:0.88rem;">{decision}</strong></div></div><div style="background:rgba(10,5,5,0.6); border:1px solid rgba(239,68,68,0.15); padding:16px; border-radius:12px; font-family:monospace; font-size:0.85rem; color:#FCA5A5; line-height:1.5;">{geniex_exp}</div></div>""", unsafe_allow_html=True)

        with st.container():
            st.markdown("""<div style="margin-bottom:-10px; font-weight:700; font-size:0.85rem; color:#FCA5A5; letter-spacing:0.5px;">UPDATE RESCUE STATUS</div>""", unsafe_allow_html=True)
            status_options = ["STANDBY", "DISPATCHED", "ON SITE", "RESCUE COMPLETED"]
            try:
                curr_idx = status_options.index(current_rescue_status)
            except Exception:
                curr_idx = 0
            selected_status = st.selectbox("Rescue Status Options", status_options, index=curr_idx, label_visibility="collapsed", key="rescue_status_selector")
            if selected_status != current_rescue_status:
                st.session_state.rescue_status_map[incident_id] = selected_status

    # --- BOTTOM SECTION: INCIDENT TIMELINE (ONLY ALERTS) ---
    with bottom_timeline_placeholder.container():
        st.markdown("""<div class="glass-card" style="padding:20px; margin-top:10px;"><div style="font-weight:800; font-size:0.9rem; color:#FFFFFF; margin-bottom:14px; text-transform:uppercase; letter-spacing:1px;">📜 RESCUE INCIDENT TIMELINE</div>""", unsafe_allow_html=True)
        alerts_list = [inc for inc in incidents_data if inc.get("state") in ("DISTRESS", "EMERGENCY", "SUSPICIOUS")]
        if alerts_list:
            log_rows = []
            for inc in alerts_list[-5:]:
                inc_id = inc.get("incident_id", "INC-XXXX")
                t_str = inc.get("timestamp", "")
                try:
                    time_lbl = datetime.datetime.fromisoformat(t_str).strftime("%H:%M:%S")
                except Exception:
                    time_lbl = t_str
                r_status = st.session_state.rescue_status_map.get(inc_id, "STANDBY")
                log_rows.append({
                    "Incident ID": inc_id,
                    "Time": time_lbl,
                    "Verdict": inc.get("state"),
                    "Risk Score": f"{int(inc.get('trust_score', 0.0) * 100)}%",
                    "Rescue Status": r_status,
                    "Explanation": inc.get("explanation", "")
                })
            html_table = """<table style="width:100%; border-collapse:collapse; font-size:0.75rem; text-align:left; color:#E6EEF6;"><thead><tr style="border-bottom:1px solid rgba(255,255,255,0.1); background:rgba(255,255,255,0.02);"><th style="padding:8px; font-weight:600; color:#8CA3AF;">Incident ID</th><th style="padding:8px; font-weight:600; color:#8CA3AF;">Time</th><th style="padding:8px; font-weight:600; color:#8CA3AF;">Verdict</th><th style="padding:8px; font-weight:600; color:#8CA3AF;">Risk Score</th><th style="padding:8px; font-weight:600; color:#8CA3AF;">Rescue Status</th><th style="padding:8px; font-weight:600; color:#8CA3AF;">Explanation</th></tr></thead><tbody>"""
            for row in log_rows:
                v = row["Verdict"]
                v_style = "color:#FF1744; font-weight:bold;" if v in ("EMERGENCY", "HIGH RISK") else "color:#FFAB00; font-weight:bold;"
                html_table += f"""<tr style="border-bottom:1px solid rgba(255,255,255,0.04);"><td style="padding:8px; font-family:monospace; color:#E6EEF6;">{row["Incident ID"]}</td><td style="padding:8px; color:#94A3B8;">{row["Time"]}</td><td style="padding:8px; {v_style}">{v}</td><td style="padding:8px; color:#00F0FF; font-weight:bold;">{row["Risk Score"]}</td><td style="padding:8px; color:#FFFFFF; font-weight:600;"><span style="background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:4px;">{row["Rescue Status"]}</span></td><td style="padding:8px; color:#8CA3AF; max-width:250px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{row["Explanation"]}</td></tr>"""
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#FCA5A5; font-size:0.85rem; padding:10px;'>No active alert incidents logged. State is nominal.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Run update loop
update_rescue_dashboard()
