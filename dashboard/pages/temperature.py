"""
LUNARIS Dashboard: Temperature & Thermal Management
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.graph_objects as go
from dashboard.components.ui_widgets import apply_custom_theme
from dashboard.components.sim_bridge import get_temperature_status, set_temperature_target

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_temperature_page():
    apply_custom_theme()
    st.markdown("## 🌡 Temperature & Thermal Management")
    st.markdown("Regulates pressurized habitat biosphere against extreme lunar diurnal temperatures (-130°C to +120°C) using PID active HVAC control.")
    
    temp_data = get_temperature_status()
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        t_img = IMAGE_DIR / "temperature_management.jpg"
        if t_img.exists():
            st.image(str(t_img), caption="Space Energy System & Lunar Thermal Insulation", use_container_width=True)
    with stat_col:
        c1, c2 = st.columns(2)
        c1.metric("Internal Cabin Temp", f"{temp_data.get('temp_internal_c', 21.5):.1f} °C", f"Setpoint: {temp_data.get('target_temp_c', 21.0):.1f} °C")
        c2.metric("External Lunar Temp", f"{temp_data.get('temp_external_c', -20.0):.1f} °C", "Vacuum / Surface")
        c3, c4 = st.columns(2)
        c3.metric("HVAC Operating Mode", temp_data.get('hvac_mode', 'IDLE'), f"Load: {temp_data.get('hvac_power_kw', 5.0):.1f} kW")
        c4.metric("Insulation Status", "BREACHED" if temp_data.get('insulation_breach') else "NOMINAL", "MLI Blankets")
    
    st.markdown("---")
    
    col_chart, col_controls = st.columns([1.5, 1])
    
    with col_chart:
        st.markdown("### 📊 Thermal Gradient Visualization")
        int_t = temp_data.get('temp_internal_c', 21.5)
        ext_t = temp_data.get('temp_external_c', -20.0)
        set_t = temp_data.get('target_temp_c', 21.0)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["External Lunar", "Internal Cabin", "Target Setpoint"],
            y=[ext_t, int_t, set_t],
            marker_color=["#3b82f6" if ext_t < 0 else "#ef4444", "#10b981", "#00e5ff"],
            text=[f"{ext_t:.1f} °C", f"{int_t:.1f} °C", f"{set_t:.1f} °C"],
            textposition='auto'
        ))
        fig.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.6)",
            plot_bgcolor="rgba(15, 23, 42, 0.6)",
            font=dict(color="#e2e8f0"),
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title="Temperature (°C)", gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_controls:
        st.markdown("### 🎛 PID Temperature Regulator")
        new_setpoint = st.slider("Target Cabin Setpoint (°C)", 16.0, 26.0, float(temp_data.get('target_temp_c', 21.0)), 0.5)
        if st.button("Apply Setpoint", use_container_width=True):
            set_temperature_target(new_setpoint)
            st.success(f"Setpoint updated to {new_setpoint} °C")
            st.rerun()
            
        st.markdown("""
        **PID Control Law:**
        $$u(t) = K_p e(t) + K_i \\int e(t)dt + K_d \\frac{de(t)}{dt}$$
        - $K_p = 3.0$ (Proportional gain)
        - $K_i = 0.2$ (Integral anti-windup)
        - $K_d = 1.5$ (Derivative thermal dampening)
        """)

if __name__ == "__main__":
    render_temperature_page()
