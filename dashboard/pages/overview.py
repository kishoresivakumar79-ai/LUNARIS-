"""
LUNARIS Dashboard: Mission Overview Page
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.components.ui_widgets import apply_custom_theme, render_gauge_chart, render_3d_embedded_view
from dashboard.components.sim_bridge import (
    get_mission_status, start_simulation, pause_simulation,
    step_simulation, reset_simulation
)

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_overview_page():
    apply_custom_theme()
    
    # Safe fetch from sim_bridge (never crashes even if FastAPI is offline)
    data = get_mission_status()
    t = data.get("telemetry", {})
    mission_day = data.get("mission_day", 1.0)
    base_health = t.get("base_health_pct", 98.5)
    base_status = t.get("base_status", "NORMAL")
    active_faults = data.get("active_faults", [])
    
    # Header Banner
    status_class = f"status-{base_status.lower()}"
    st.markdown(f"""
    <div class="mission-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>LUNARIS Mission Control Center</h1>
                <p>Virtual Moon Base Management System • Shackleton Crater Station • Crew: 4 Astronauts</p>
            </div>
            <div>
                <span class="status-pill {status_class}">{base_status} OPERATIONAL</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulation Control Quickbar
    c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.5, 2.5])
    with c1:
        if st.button("▶ Start Mission", use_container_width=True):
            start_simulation(speed_multiplier=1.0)
            st.rerun()
    with c2:
        if st.button("⏸ Pause", use_container_width=True):
            pause_simulation()
            st.rerun()
    with c3:
        if st.button("⏭ Step (+1h)", use_container_width=True):
            step_simulation(hours=1.0)
            st.rerun()
    with c4:
        if st.button("🔄 Reset Mission", use_container_width=True):
            reset_simulation(crew_count=4, battery_pct=65.0, o2_kg=100.0, water_l=500.0, food_kg=120.0)
            st.rerun()
    with c5:
        sim_running = data.get("is_running", False)
        st.markdown(f"**Clock:** Sol {mission_day:.2f} | **Engine:** {'🟢 RUNNING' if sim_running else '🟡 PAUSED'}")

    st.markdown("---")
    
    # Visual Banner with Moon Base Images
    hero_col, info_col = st.columns([1.4, 1])
    with hero_col:
        hero_img = IMAGE_DIR / "hero_moonbase.jpg"
        if hero_img.exists():
            st.image(str(hero_img), caption="Virtual Moon Base Research Outpost (Shackleton Crater, Lunar South Pole)", use_container_width=True)
    with info_col:
        sys_img = IMAGE_DIR / "system_architecture.jpg"
        if sys_img.exists():
            st.image(str(sys_img), caption="Koatlus Digital Twin & Adaptive Sensing Architecture", use_container_width=True)
            
    st.markdown("---")
    
    # Top KPI Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Battery Charge", f"{t.get('battery_pct', 65.0):.1f}%", f"{t.get('net_power', 0.0):+.1f} kW net")
    m2.metric("Oxygen Reserve", f"{t.get('oxygen_level', 100.0):.1f} kg", f"{(t.get('oxygen_production', 8.0) - t.get('oxygen_consumption', 6.0)):+.1f} kg/d")
    m3.metric("Water Inventory", f"{t.get('water_level', 500.0):.1f} L", f"{t.get('water_recycled', 40.0):.1f} L/d recycled")
    m4.metric("Cabin Temp", f"{t.get('temp_internal', 21.5):.1f} °C", f"Ext: {t.get('temp_external', -20.0):.1f} °C")
    m5.metric("Base Integrity", f"{base_health:.1f}%", f"{len(active_faults)} active faults")
    
    # Alarms Alert Banner
    if active_faults:
        st.error(f"🚨 **ACTIVE CRITICAL FAULTS DETECTED:** {', '.join(active_faults)}. Autonomous safety protocols initiated.")
        
    st.markdown("### 🪐 Interactive 3D Digital Twin & Mission Operations")
    tab_3d, tab_gauges, tab_gallery, tab_video = st.tabs([
        "🌐 3D Moon Base Viewport", 
        "📊 Resource Gauges & Telemetry", 
        "🖼 Mission Design Concepts",
        "🎥 Mission Video Demo"
    ])
    
    with tab_3d:
        render_3d_embedded_view(telemetry=t, height=540)
        st.caption("WebGL Three.js Digital Twin. Click or drag to orbit. Click structures for component telemetry.")
        
    with tab_gauges:
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.plotly_chart(render_gauge_chart(t.get('battery_pct', 65.0), 0, 100, "Power Battery", "%", 40, 20), use_container_width=True)
        with g2:
            st.plotly_chart(render_gauge_chart(t.get('oxygen_level', 100.0), 0, 200, "Oxygen Reserve", "kg", 45, 25), use_container_width=True)
        with g3:
            st.plotly_chart(render_gauge_chart(t.get('water_level', 500.0), 0, 1000, "Water Storage", "L", 180, 90), use_container_width=True)
        with g4:
            st.plotly_chart(render_gauge_chart(t.get('cabin_pressure', 101.3), 70, 110, "Cabin Pressure", "kPa", 98, 90), use_container_width=True)
            
    with tab_gallery:
        gal_c1, gal_c2 = st.columns(2)
        with gal_c1:
            art_img = IMAGE_DIR / "artemis_basecamp.jpg"
            if art_img.exists():
                st.image(str(art_img), caption="Artemis Base Camp - 2030 Human Lunar Exploration", use_container_width=True)
            lun_img = IMAGE_DIR / "lunar_base_3d.jpg"
            if lun_img.exists():
                st.image(str(lun_img), caption="Lunar Base Alfa Modular Surface Habitation", use_container_width=True)
        with gal_c2:
            ui_img = IMAGE_DIR / "mission_control_ui.jpg"
            if ui_img.exists():
                st.image(str(ui_img), caption="JAOPS Aerospace Command Center Architecture", use_container_width=True)
            cmd_img = IMAGE_DIR / "command_cards.jpg"
            if cmd_img.exists():
                st.image(str(cmd_img), caption="Orbital Command Cards UI & Visual Cards", use_container_width=True)

    with tab_video:
        video_dir = PROJECT_ROOT / "dashboard" / "assets" / "Videos"
        video_file = video_dir / "LUNARIS .mp4"
        if not video_file.exists():
            video_file = video_dir / "LUNARIS.mp4"
            
        if video_file.exists():
            st.markdown("#### 🎬 LUNARIS Project Full System Walkthrough Video")
            st.caption("AI + Digital Twin + 3D Simulation Virtual Moon Base Management System")
            st.video(str(video_file))
        else:
            st.warning("Video file not found in dashboard/assets/Videos/")

if __name__ == "__main__":
    render_overview_page()
