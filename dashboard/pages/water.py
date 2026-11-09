"""
LUNARIS Dashboard: Water Management System
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.components.ui_widgets import apply_custom_theme, render_prediction_chart
from dashboard.components.sim_bridge import (
    get_water_status, set_rationing, set_wrs, get_all_predictions
)

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_water_page():
    apply_custom_theme()
    st.markdown("## 💧 Water Management System")
    st.markdown("Monitors Water Recovery System (WRS), graywater/urine distillation, hygiene/drinking consumption, and closed-loop recycling.")
    
    w = get_water_status()
    all_preds = get_all_predictions()
    forecast = all_preds.get("water_forecast_7d", [])
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        w_img = IMAGE_DIR / "water_management.jpg"
        if w_img.exists():
            st.image(str(w_img), caption="ESA Closed-Loop ISS/Lunar Water Reclamation", use_container_width=True)
    with stat_col:
        c1, c2 = st.columns(2)
        c1.metric("Fresh Water Tank", f"{w.get('water_level_l', 500.0):.1f} L", "Capacity: 1000 L")
        c2.metric("WRS Recycled", f"{w.get('recycled_l', 40.0):.1f} L/d", "Distillation: 90% Eff")
        c3, c4 = st.columns(2)
        c3.metric("Daily Consumption", f"{w.get('used_l', 50.0):.1f} L/d", "Crew + OGA feed")
        c4.metric("Emergency Reserve", f"{w.get('emergency_reserve_l', 150.0):.1f} L", "Reserve Bladder")
    
    st.markdown("---")
    
    left_col, right_col = st.columns([1.5, 1])
    
    with left_col:
        st.markdown("### 📈 7-Day Water Reserve Forecast")
        if forecast:
            fig = render_prediction_chart(forecast, "predicted_water_l", "confidence_lower_l", "confidence_upper_l", "AI Forecasted Water Reserve (Liters)", "Water (L)", "#3b82f6")
            st.plotly_chart(fig, use_container_width=True)
            
    with right_col:
        st.markdown("### 🚰 Water Reclamation Controls")
        
        ration_mode = w.get("rationing_mode", False)
        if st.button(f"{'Disable' if ration_mode else 'Enable'} Water Rationing Conservation", use_container_width=True):
            set_rationing(not ration_mode)
            st.rerun()
            
        wrs_active = w.get("wrs_active", True)
        if st.button(f"{'Stop' if wrs_active else 'Restart'} WRS Processor", use_container_width=True):
            set_wrs(not wrs_active)
            st.rerun()
            
        if ration_mode:
            st.warning("⚠️ Water rationing mode active: crew hygiene allocated to sponge baths only.")
            
        if w.get("wrs_pump_fault"):
            st.error("🚨 WRS centrifuge pump fault: recovery efficiency down to 10%!")

if __name__ == "__main__":
    render_water_page()
