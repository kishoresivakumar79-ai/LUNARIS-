"""
LUNARIS Dashboard: Oxygen Management System
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.components.ui_widgets import apply_custom_theme, render_prediction_chart
from dashboard.components.sim_bridge import (
    get_oxygen_status, set_oga, toggle_emergency_reserve, isolate_bulkhead, get_all_predictions
)

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_oxygen_page():
    apply_custom_theme()
    st.markdown("## 💨 Oxygen Management System")
    st.markdown("Monitors Oxygen Generation Assembly (OGA), respiration consumption, cabin pressure, and emergency cryogenic storage.")
    
    o = get_oxygen_status()
    all_preds = get_all_predictions()
    forecast = all_preds.get("oxygen_forecast_7d", [])
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        o_img = IMAGE_DIR / "oxygen_management.jpg"
        if o_img.exists():
            st.image(str(o_img), caption="Occupy Mars Lunar Atmospheric OGA System", use_container_width=True)
    with stat_col:
        c1, c2 = st.columns(2)
        c1.metric("Oxygen Reserve", f"{o.get('oxygen_level_kg', 100.0):.1f} kg", "Capacity: 200 kg")
        c2.metric("OGA Production", f"{o.get('production_rate_kg', 8.0):.1f} kg/d", "Electrolysis: ONLINE" if o.get('oga_active') else "OGA: OFFLINE")
        c3, c4 = st.columns(2)
        c3.metric("Respiration Cons.", f"{o.get('consumption_rate_kg', 6.0):.1f} kg/d", "4 Crew Members")
        c4.metric("Cabin Pressure", f"{o.get('cabin_pressure_kpa', 101.3):.1f} kPa", "Nominal: 101.3 kPa")
    
    st.markdown("---")
    
    left_col, right_col = st.columns([1.5, 1])
    
    with left_col:
        st.markdown("### 📈 7-Day Oxygen Trajectory Forecast")
        if forecast:
            fig = render_prediction_chart(forecast, "predicted_oxygen_kg", "confidence_lower_kg", "confidence_upper_kg", "AI Forecasted Oxygen Reserve (kg)", "Oxygen (kg)", "#10b981")
            st.plotly_chart(fig, use_container_width=True)
            
    with right_col:
        st.markdown("### 🛠 Life Support Controls")
        
        # OGA State Toggle
        oga_active = o.get("oga_active", True)
        if st.button(f"{'🛑 Deactivate' if oga_active else '⚡ Activate'} OGA Electrolyzer", use_container_width=True):
            set_oga(not oga_active)
            st.rerun()
            
        # Emergency Valve Toggle
        valve_open = o.get("emergency_valve_open", False)
        if st.button(f"{'🔒 Close' if valve_open else '🚨 Deploy'} Emergency Cryo-Reserve", use_container_width=True):
            toggle_emergency_reserve(not valve_open)
            st.rerun()
            
        # Bulkhead Isolation
        isolated = o.get("section_isolated", False)
        if st.button("🚪 Isolate Breach Bulkhead Doors", use_container_width=True):
            isolate_bulkhead()
            st.warning("Bulkhead sealed. Micro-puncture isolated.")
            st.rerun()
            
        st.markdown(f"**Emergency Tank:** {o.get('emergency_reserve_kg', 50.0):.1f} kg available")
        if isolated:
            st.info("🔒 Bulkhead isolation active.")

if __name__ == "__main__":
    render_oxygen_page()
