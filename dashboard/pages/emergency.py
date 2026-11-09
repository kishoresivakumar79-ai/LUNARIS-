"""
LUNARIS Dashboard: Emergency Detection & Scenario Control
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from dashboard.components.ui_widgets import apply_custom_theme
from dashboard.components.sim_bridge import (
    get_emergency_status, inject_scenario, resolve_scenario, resolve_incident_entry
)

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_emergency_page():
    apply_custom_theme()
    st.markdown("## 🚨 Emergency Detection & Response Center")
    st.markdown("Simulate mission critical failure scenarios, observe automated closed-loop mitigation responses, and review incident timelines.")
    
    data = get_emergency_status()
    base_status = data.get("base_status", "NORMAL")
    active_faults = data.get("active_faults", [])
    recent_actions = data.get("recent_actions", [])
    incidents = data.get("incidents", [])
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        e_img = IMAGE_DIR / "emergency_management.jpg"
        if e_img.exists():
            st.image(str(e_img), caption="NASA Moon Base Emergency Response Protocols", use_container_width=True)
    with stat_col:
        st.markdown(f"### Current Base Operational State: `{base_status}`")
        if active_faults:
            st.error(f"**ACTIVE FAULTS:** {', '.join(active_faults)}")
        else:
            st.success("All systems operating inside certified safe envelopes.")
            
    st.markdown("---")
    
    # 1. Failure Scenario Injection Cards
    st.markdown("### 💥 Mission Failure Scenario Simulator")
    st.write("Inject simulated engineering emergencies to evaluate the autonomous decision engine and 3D visual twin alarms.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚡ Scenario 1: Solar Power Failure")
        st.caption("Solar generation drops by 70%. AI predicts battery blackout; power controller sheds non-essential loads and starts backup fuel cell.")
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("🚨 Inject Solar Blackout", use_container_width=True):
                inject_scenario("SOLAR_POWER_FAILURE")
                st.rerun()
        with c_b:
            if st.button("✅ Restore Solar Array", use_container_width=True):
                resolve_scenario("SOLAR_POWER_FAILURE")
                st.rerun()
                
        st.markdown("#### 💧 Scenario 3: Water Recycling Failure")
        st.caption("WRS distillation pump jams, dropping recycling efficiency to 10%. Controller activates mandatory water rationing.")
        c_e, c_f = st.columns(2)
        with c_e:
            if st.button("🚨 Jam WRS Recycler", use_container_width=True):
                inject_scenario("WATER_SHORTAGE")
                st.rerun()
        with c_f:
            if st.button("✅ Repair WRS Pump", use_container_width=True):
                resolve_scenario("WATER_SHORTAGE")
                st.rerun()
                
    with col2:
        st.markdown("#### 💨 Scenario 2: Hull Oxygen Puncture")
        st.caption("Micro-meteorite breach causes rapid cabin depressurization. Autonomous safety isolates bulkhead and deploys emergency reserve.")
        c_c, c_d = st.columns(2)
        with c_c:
            if st.button("🚨 Puncture Habitat Hull", use_container_width=True):
                inject_scenario("OXYGEN_LEAKAGE")
                st.rerun()
        with c_d:
            if st.button("✅ Seal Hull Breach", use_container_width=True):
                resolve_scenario("OXYGEN_LEAKAGE")
                st.rerun()
                
        st.markdown("#### 🌡 Scenario 4: Insulation Breach")
        st.caption("Thermal blanket failure causes severe heat transfer to lunar void. Cabin temperature plunges; PID controller maxes heating.")
        c_g, c_h = st.columns(2)
        with c_g:
            if st.button("🚨 Breach MLI Insulation", use_container_width=True):
                inject_scenario("TEMPERATURE_EMERGENCY")
                st.rerun()
        with c_h:
            if st.button("✅ Reapply Insulation", use_container_width=True):
                resolve_scenario("TEMPERATURE_EMERGENCY")
                st.rerun()

    st.markdown("---")
    
    # 2. Automated Safety Actions Audit Log
    st.markdown("### 🤖 Autonomous Decision & Control Action Log")
    if recent_actions:
        for act in reversed(recent_actions[-6:]):
            st.info(f"🛡 **Automated Response:** {act}")
    else:
        st.success("No automated emergency overrides active. Base operating in nominal regime.")
        
    st.markdown("---")
    
    # 3. Incident Timeline from Database
    st.markdown("### 📜 Mission Incident Timeline (Database Log)")
    if incidents:
        df_inc = pd.DataFrame(incidents)
        disp = df_inc[["id", "timestamp", "mission_day", "subsystem", "severity", "title", "action_taken"]]
        disp.columns = ["ID", "Timestamp", "Sol", "Subsystem", "Severity", "Incident Title", "Action Executed"]
        st.dataframe(disp, use_container_width=True, hide_index=True)
    else:
        st.write("No historical incidents recorded.")

if __name__ == "__main__":
    render_emergency_page()
