"""
LUNARIS Dashboard: AI Prediction & Anomaly Center
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components.ui_widgets import apply_custom_theme, render_prediction_chart
from dashboard.components.sim_bridge import get_all_predictions

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_ai_predictions_page():
    apply_custom_theme()
    st.markdown("## 🧠 AI Prediction & Anomaly Center")
    st.markdown("Leverages Machine Learning models (Gradient Boosting, Random Forest, Ridge Regression, Isolation Forest) for predictive telemetry forecasting and risk diagnosis.")
    
    data = get_all_predictions()
    power_f = data.get("power_forecast_7d", [])
    o2_f = data.get("oxygen_forecast_7d", [])
    water_f = data.get("water_forecast_7d", [])
    anomaly_data = data.get("anomaly_analysis", {})
    eq_risks = data.get("equipment_failure_risks", [])
    
    # Visual illustrations row
    ai_col, dt_col = st.columns(2)
    with ai_col:
        ai_img = IMAGE_DIR / "ai_platform.jpg"
        if ai_img.exists():
            st.image(str(ai_img), caption="Aerospace Intelligence & Telemetry Predictive Platform", use_container_width=True)
    with dt_col:
        dt_img = IMAGE_DIR / "digital_twin.jpg"
        if dt_img.exists():
            st.image(str(dt_img), caption="PETRAN Digital Twin Predictive Maintenance Engine", use_container_width=True)
            
    st.markdown("---")
    
    # 1. Anomaly Detection Gauge & Suspects
    st.markdown("### 🔍 Unsupervised Anomaly Detection (Isolation Forest)")
    a_col1, a_col2 = st.columns([1, 2])
    with a_col1:
        anom_score = anomaly_data.get("anomaly_score", 0.05)
        is_anom = anomaly_data.get("is_anomaly", False)
        st.metric(
            "Anomaly Index",
            f"{anom_score:.3f}",
            "🚨 CRITICAL OUTLIER" if is_anom else "NOMINAL ENVELOPE",
            delta_color="inverse" if is_anom else "normal"
        )
    with a_col2:
        suspects = anomaly_data.get("suspect_factors", [])
        if suspects:
            st.error(f"**Anomalous Drivers Identified:**\n- " + "\n- ".join(suspects))
        else:
            st.success("All multivariate sensor channels (power, pressure, O2, water, temp) are inside nominal operational bounds.")
            
    st.markdown("---")
    
    # 2. 7-Day Forecast Multi-Tab
    st.markdown("### 📈 7-Day Predictive Horizon (Multi-Resource Forecasting)")
    t1, t2, t3 = st.tabs(["⚡ Power Demand & Battery", "💨 Oxygen Reserves", "💧 Water Reserves"])
    
    with t1:
        if power_f:
            st.plotly_chart(
                render_prediction_chart(power_f, "predicted_battery_pct", "confidence_lower_pct", "confidence_upper_pct", "7-Day Predicted Battery State-of-Charge (%)", "Battery (%)", "#00e5ff"),
                use_container_width=True
            )
    with t2:
        if o2_f:
            st.plotly_chart(
                render_prediction_chart(o2_f, "predicted_oxygen_kg", "confidence_lower_kg", "confidence_upper_kg", "7-Day Predicted Oxygen Reserve (kg)", "Oxygen (kg)", "#10b981"),
                use_container_width=True
            )
    with t3:
        if water_f:
            st.plotly_chart(
                render_prediction_chart(water_f, "predicted_water_l", "confidence_lower_l", "confidence_upper_l", "7-Day Predicted Water Reserve (Liters)", "Water (L)", "#3b82f6"),
                use_container_width=True
            )
            
    st.markdown("---")
    
    # 3. Equipment Failure Risk & Remaining Useful Life (RUL)
    st.markdown("### ⚙ Predictive Maintenance & Component Risk Ranking")
    if eq_risks:
        df_eq = pd.DataFrame(eq_risks)
        fig_bar = px.bar(
            df_eq,
            x="failure_probability",
            y="name",
            orientation='h',
            color="failure_probability",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            labels={"failure_probability": "Failure Probability (0.0 to 1.0)", "name": "Subsystem"},
            text_auto='.2f'
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.6)",
            plot_bgcolor="rgba(15, 23, 42, 0.6)",
            font=dict(color="#e2e8f0"),
            height=340,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Display Table with RUL
        disp_df = df_eq[["name", "subsystem", "health_pct", "operating_hours", "failure_probability", "estimated_rul_hours", "risk_status"]]
        disp_df.columns = ["Component", "Subsystem", "Health (%)", "Operating Hours", "Failure Prob", "Est. RUL (Hours)", "Risk Status"]
        st.dataframe(disp_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render_ai_predictions_page()
