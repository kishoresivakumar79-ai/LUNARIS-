"""
LUNARIS Synthetic Dataset Generator
Generates realistic 30-day lunar mission datasets for power, oxygen, water, and temperature.
"""

import math
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

def generate_all_datasets():
    print("Generating synthetic 30-day lunar mission datasets...")
    np.random.seed(42)
    
    # 30 days at 1-hour resolution = 720 time steps
    n_hours = 720
    hours = np.arange(n_hours)
    mission_days = hours / 24.0 + 1.0  # Day 1.0 to 31.0
    
    # Lunar synodic cycle (29.53 days)
    lunar_phase = (mission_days % 29.53) / 29.53 * 2.0 * math.pi
    solar_elev = np.sin(lunar_phase) * 1.5 + 1.9
    irradiance = np.where(solar_elev > 0, 1361.0, 0.0)
    
    # --- 1. Power Dataset ---
    solar_gen_kw = np.clip((600.0 * irradiance * 0.32 * (1.0 - (mission_days * 0.001))) / 1000.0, 0, 140)
    # Add diurnal noise and equipment fluctuations
    base_cons_kw = 85.0 + np.sin(hours * 0.26) * 12.0 + np.random.normal(0, 3.0, n_hours)
    base_cons_kw = np.clip(base_cons_kw, 50, 130)
    
    # Battery simulation
    bat_kwh = np.zeros(n_hours)
    bat_pct = np.zeros(n_hours)
    curr_bat = 325.0
    cap = 500.0
    for i in range(n_hours):
        net = solar_gen_kw[i] - base_cons_kw[i]
        if net > 0:
            curr_bat = min(cap, curr_bat + (net * 0.95))
        else:
            curr_bat = max(0.0, curr_bat + net)
        bat_kwh[i] = curr_bat
        bat_pct[i] = (curr_bat / cap) * 100.0
        
    df_power = pd.DataFrame({
        "hour": hours,
        "mission_day": np.round(mission_days, 2),
        "solar_irradiance_wm2": np.round(irradiance, 1),
        "solar_generation_kw": np.round(solar_gen_kw, 2),
        "power_consumption_kw": np.round(base_cons_kw, 2),
        "battery_level_kwh": np.round(bat_kwh, 2),
        "battery_pct": np.round(bat_pct, 1)
    })
    df_power.to_csv(DATA_DIR / "simulated_power.csv", index=False)
    print(f"-> Saved {DATA_DIR / 'simulated_power.csv'} ({len(df_power)} rows)")
    
    # --- 2. Oxygen Dataset ---
    # 4 astronauts breathing ~3.36 kg/day (~0.14 kg/hr)
    crew_o2_hr = 0.14 + np.random.normal(0, 0.015, n_hours)
    oga_prod_hr = np.full(n_hours, 0.33)  # 8 kg/day
    o2_levels = np.zeros(n_hours)
    curr_o2 = 100.0
    leak_hr = np.full(n_hours, 0.002)  # Nominal
    # Simulate a brief micro-puncture event between hour 300 and 312
    leak_hr[300:312] = 0.45
    
    for i in range(n_hours):
        curr_o2 = max(0.0, min(200.0, curr_o2 + oga_prod_hr[i] - crew_o2_hr[i] - leak_hr[i]))
        o2_levels[i] = curr_o2
        
    pressure_kpa = 101.3 - (leak_hr * 12.0)
    pressure_kpa = np.clip(pressure_kpa, 92.0, 101.3)
    
    df_oxygen = pd.DataFrame({
        "hour": hours,
        "mission_day": np.round(mission_days, 2),
        "oxygen_level_kg": np.round(o2_levels, 2),
        "production_rate_kg_hr": np.round(oga_prod_hr, 3),
        "consumption_rate_kg_hr": np.round(crew_o2_hr, 3),
        "leakage_kg_hr": np.round(leak_hr, 4),
        "cabin_pressure_kpa": np.round(pressure_kpa, 2)
    })
    df_oxygen.to_csv(DATA_DIR / "simulated_oxygen.csv", index=False)
    print(f"-> Saved {DATA_DIR / 'simulated_oxygen.csv'} ({len(df_oxygen)} rows)")
    
    # --- 3. Water Dataset ---
    water_levels = np.zeros(n_hours)
    curr_w = 500.0
    crew_w_hr = (48.0 / 24.0) + np.random.normal(0, 0.15, n_hours)  # ~2.0 L/hr
    oga_w_hr = oga_prod_hr * 1.125
    recycled_hr = (45.0 / 24.0) * 0.90 + np.random.normal(0, 0.05, n_hours)
    loss_hr = np.full(n_hours, 5.0 / 24.0)
    
    # Simulate water pump slowdown between hour 450 and 475
    recycled_hr[450:475] *= 0.20
    
    for i in range(n_hours):
        curr_w = max(0.0, min(1000.0, curr_w + recycled_hr[i] - crew_w_hr[i] - oga_w_hr[i] - loss_hr[i]))
        water_levels[i] = curr_w
        
    df_water = pd.DataFrame({
        "hour": hours,
        "mission_day": np.round(mission_days, 2),
        "water_level_l": np.round(water_levels, 2),
        "water_recycled_l_hr": np.round(recycled_hr, 3),
        "water_used_l_hr": np.round(crew_w_hr + oga_w_hr, 3),
        "water_loss_l_hr": np.round(loss_hr, 3)
    })
    df_water.to_csv(DATA_DIR / "simulated_water.csv", index=False)
    print(f"-> Saved {DATA_DIR / 'simulated_water.csv'} ({len(df_water)} rows)")
    
    # --- 4. Temperature Dataset ---
    ext_temp = np.where(irradiance > 50, -20.0 + (irradiance / 1361.0 * 140.0), -130.0)
    int_temp = 21.5 + np.random.normal(0, 0.4, n_hours)
    # Simulate a minor HVAC anomaly between hour 550 and 565
    int_temp[550:565] = 16.8 + np.sin(np.arange(15) * 0.3)
    
    df_temp = pd.DataFrame({
        "hour": hours,
        "mission_day": np.round(mission_days, 2),
        "temp_internal_c": np.round(int_temp, 2),
        "temp_external_c": np.round(ext_temp, 1),
        "target_temp_c": np.full(n_hours, 21.0),
        "hvac_power_kw": np.round(5.0 + np.abs(int_temp - ext_temp) * 0.12, 2)
    })
    df_temp.to_csv(DATA_DIR / "simulated_temperature.csv", index=False)
    print(f"-> Saved {DATA_DIR / 'simulated_temperature.csv'} ({len(df_temp)} rows)")
    print("All datasets generated successfully!")

if __name__ == "__main__":
    generate_all_datasets()

