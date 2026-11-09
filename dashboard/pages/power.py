"""
LUNARIS Dashboard: Power Management System
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px
from dashboard.components.ui_widgets import apply_custom_theme, render_prediction_chart
from dashboard.components.sim_bridge import (
    get_power_status, set_load_shed, toggle_backup_generator, get_all_predictions
)

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_power_page():
    apply_custom_theme()
    st.markdown("## ⚡ Power Management System")
    st.markdown("Monitors photovoltaic generation, Li-S battery reserves, auxiliary fuel cell generator, and automated load shedding.")
    
    p = get_power_status()
    all_preds = get_all_predictions()
    forecast = all_preds.get("power_forecast_7d", [])
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        p_img = IMAGE_DIR / "power_management.jpg"
        if p_img.exists():
            st.image(str(p_img), caption="Sandia Lunar Microgrid Architecture", use_container_width=True)
    with stat_col:
        c1, c2 = st.columns(2)
        c1.metric("Solar Generation", f"{p.get('generation_kw', 120.0):.1f} kW", "Dual 300m² Arrays")
        c2.metric("Total Consumption", f"{p.get('consumption_kw', 90.0):.1f} kW", f"Net: {p.get('net_power_kw', 30.0):+.1f} kW")
        c3, c4 = st.columns(2)
        c3.metric("Battery Storage", f"{p.get('battery_pct', 65.0):.1f}%", f"{p.get('battery_kwh', 325.0):.1f} / 500 kWh")
        c4.metric("Backup Fuel Cell", "ACTIVE" if p.get('backup_active') else "STANDBY", f"{p.get('backup_power_kw', 0.0):.1f} kW")
    
    st.markdown("---")
    
    left_col, right_col = st.columns([1.5, 1])
    
    with left_col:
        st.markdown("### 📈 7-Day Battery Charge Forecast")
        if forecast:
            fig = render_prediction_chart(forecast, "predicted_battery_pct", "confidence_lower_pct", "confidence_upper_pct", "AI Predicted Battery State-of-Charge (%)", "Battery (%)", "#00e5ff")
            st.plotly_chart(fig, use_container_width=True)
            
    with right_col:
        st.markdown("### ⚙ Power Grid Controls")
        curr_shed = p.get("load_shed_level", 0)
        new_shed = st.selectbox(
            "Load Shedding Priority Level",
            [0, 1, 2, 3],
            index=curr_shed,
            format_func=lambda x: [
                "Level 0: Full Normal (All systems active)",
                "Level 1: Conservation (Science 70% shed)",
                "Level 2: Urgent (Labs off, rover recharge off)",
                "Level 3: Survival (Life support & heat only)"
            ][x]
        )
        if new_shed != curr_shed:
            set_load_shed(new_shed)
            st.success(f"Load shedding set to Level {new_shed}")
            st.rerun()
            
        st.markdown("---")
        backup_state = p.get("backup_active", False)
        if st.button("🔌 Toggle 40 kW Fuel Cell Generator", use_container_width=True):
            toggle_backup_generator(not backup_state)
            st.rerun()
            
        if p.get("solar_failure_pct", 0) > 0:
            st.error(f"⚠️ Solar array failure active: {p.get('solar_failure_pct')*100:.0f}% generation reduction.")
            
    st.markdown("### 🔋 Subsystem Load Allocation")
    loads = {
        "Base Avionics & Comms": 25.0,
        "Oxygen Generation (OGA)": 20.0,
        "Water Recovery (WRS)": 15.0,
        "Thermal Control (HVAC)": 15.0,
        "Science Lab & Robotics": 15.0 if curr_shed < 2 else 0.0
    }
    pie_fig = px.pie(
        names=list(loads.keys()),
        values=list(loads.values()),
        color_discrete_sequence=["#00e5ff", "#00ff88", "#3b82f6", "#f59e0b", "#8b5cf6"],
        hole=0.45
    )
    pie_fig.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0.6)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font=dict(color="#e2e8f0"),
        height=280,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(pie_fig, use_container_width=True)

if __name__ == "__main__":
    render_power_page()
