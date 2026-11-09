"""
LUNARIS: Virtual Moon Base Management System
Main Streamlit Mission Control Center
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.components.ui_widgets import apply_custom_theme
from dashboard.components.sim_bridge import is_api_online, get_mission_status

from dashboard.pages.overview import render_overview_page
from dashboard.pages.power import render_power_page
from dashboard.pages.oxygen import render_oxygen_page
from dashboard.pages.water import render_water_page
from dashboard.pages.temperature import render_temperature_page
from dashboard.pages.resources import render_resources_page
from dashboard.pages.ai_predictions import render_ai_predictions_page
from dashboard.pages.emergency import render_emergency_page

st.set_page_config(
    page_title="LUNARIS | Moon Base Mission Control",
    page_icon="🌕",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

# Sidebar Navigation & Telemetry Ticker
with st.sidebar:
    # Sidebar Logo / Identity
    id_img = IMAGE_DIR / "project_identity.jpg"
    if id_img.exists():
        st.image(str(id_img), use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #00e5ff; letter-spacing: 2px; margin: 0;">🌕 LUNARIS</h2>
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 2px 0 0 0;">Virtual Moon Base Management</p>
        </div>
        """, unsafe_allow_html=True)
        
    api_online = is_api_online()
    if api_online:
        st.success("🟢 FastAPI Backend Online")
    else:
        st.info("ℹ️ Running in Direct In-Process Mode (FastAPI optional)")
        
    nav_selection = st.radio(
        "Navigation Deck",
        [
            "🪐 Mission Overview",
            "⚡ Power Management",
            "💨 Oxygen Management",
            "💧 Water Management",
            "🌡 Temperature Management",
            "📦 Resource & Inventory",
            "🧠 AI Prediction Center",
            "🚨 Emergency & Scenarios"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # Telemetry HUD in sidebar
    status_data = get_mission_status()
    t = status_data.get("telemetry", {})
    mission_day = status_data.get("mission_day", 1.0)
    
    st.markdown(f"**Mission Clock:** Sol {mission_day:.2f} / 30.0")
    st.progress(min(1.0, mission_day / 30.0))
    
    st.markdown("##### 📡 Live Telemetry Ticker")
    st.markdown(f"""
    - **Battery:** `{t.get('battery_pct', 65.0):.1f}%`
    - **Oxygen:** `{t.get('oxygen_level', 100.0):.1f} kg`
    - **Cabin Press:** `{t.get('cabin_pressure', 101.3):.1f} kPa`
    - **Water:** `{t.get('water_level', 500.0):.1f} L`
    - **Cabin Temp:** `{t.get('temp_internal', 21.5):.1f} °C`
    - **Lunar Ext:** `{t.get('temp_external', -20.0):.1f} °C`
    """)
    
    st.markdown("---")
    st.caption("AI + Digital Twin + 3D Simulation\nDeep Space Systems Engineering")

# Route to selected page
if nav_selection == "🪐 Mission Overview":
    render_overview_page()
elif nav_selection == "⚡ Power Management":
    render_power_page()
elif nav_selection == "💨 Oxygen Management":
    render_oxygen_page()
elif nav_selection == "💧 Water Management":
    render_water_page()
elif nav_selection == "🌡 Temperature Management":
    render_temperature_page()
elif nav_selection == "📦 Resource & Inventory":
    render_resources_page()
elif nav_selection == "🧠 AI Prediction Center":
    render_ai_predictions_page()
elif nav_selection == "🚨 Emergency & Scenarios":
    render_emergency_page()
