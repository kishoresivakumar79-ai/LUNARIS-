"""
LUNARIS Dashboard: Resource & Inventory Management
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from dashboard.components.ui_widgets import apply_custom_theme
from dashboard.components.sim_bridge import get_inventory_data, get_mission_status

IMAGE_DIR = PROJECT_ROOT / "dashboard" / "assets" / "images"

def render_resources_page():
    apply_custom_theme()
    st.markdown("## 📦 Resource & Inventory Management")
    st.markdown("Tracks consumables, daily burn rates, hydroponic greenhouse yields, and predicts resupply mission requirements.")
    
    items = get_inventory_data()
    status_data = get_mission_status()
    t = status_data.get("telemetry", {})
    
    # Image Illustration
    img_col, stat_col = st.columns([1, 2])
    with img_col:
        r_img = IMAGE_DIR / "resource_management.jpg"
        if r_img.exists():
            st.image(str(r_img), caption="Space Station Parts & Consumables Logistics Management", use_container_width=True)
    with stat_col:
        c1, c2, c3 = st.columns(3)
        c1.metric("Food Supplies", f"{t.get('food_level', 120.0):.1f} kg", f"{t.get('food_days_remaining', 30.0):.1f} Days Rem.")
        c2.metric("Fuel Reactants", f"{t.get('fuel_cell_reactants', 200.0):.1f} kg", "Aux Energy")
        c3.metric("Greenhouse", "+0.6 kg/day", "Hydroponics")
    
    st.markdown("---")
    
    st.markdown("### 📋 Mission Consumables & Spares Ledger")
    if items:
        df = pd.DataFrame(items)
        df["days_remaining"] = df.apply(
            lambda row: round(row["quantity"] / max(0.01, row["daily_burn_rate"]), 1) if row["daily_burn_rate"] > 0 else 999.0,
            axis=1
        )
        df["status"] = df.apply(
            lambda row: "🔴 CRITICAL" if row["quantity"] <= row["critical_threshold"] else ("🟡 LOW" if row["quantity"] <= row["critical_threshold"] * 1.5 else "🟢 OPTIMAL"),
            axis=1
        )
        display_df = df[["item_name", "category", "quantity", "unit", "daily_burn_rate", "days_remaining", "status"]]
        display_df.columns = ["Item", "Category", "Quantity", "Unit", "Burn Rate / Day", "Days Remaining", "Status"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Loading inventory database...")
        
    st.markdown("---")
    st.markdown("### 🚀 Artemis Cargo Lander Resupply Logistics")
    st.write("Formula: $$Days\\ Remaining = \\frac{Available\\ Quantity}{Daily\\ Consumption}$$")
    if st.button("📦 Simulate Resupply Cargo Lander Docking", use_container_width=True):
        st.success("Cargo Lander 'Artemis Logistics-4' docked successfully. Transferred +100 kg rations and +150 kg fuel reactants.")

if __name__ == "__main__":
    render_resources_page()
