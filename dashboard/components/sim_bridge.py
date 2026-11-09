"""
LUNARIS: Resilient Simulation Bridge
Transparently connects the Streamlit dashboard to the FastAPI backend when online,
and automatically falls back to in-process SimulationService when FastAPI is not running.
Prevents any ConnectionRefusedError [WinError 10061] crashes.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from backend.services.simulation_service import SimulationService
from database.database import get_recent_telemetry, get_incidents, get_inventory, resolve_incident

API_URL = "http://127.0.0.1:8000"

def get_sim_instance() -> SimulationService:
    return SimulationService()

def is_api_online() -> bool:
    try:
        r = requests.get(f"{API_URL}/api/status", timeout=0.4)
        return r.ok
    except Exception:
        return False

# Mission Status
def get_mission_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return get_sim_instance().get_full_status()

# Simulation Controls
def start_simulation(speed_multiplier: float = 1.0) -> None:
    try:
        r = requests.post(f"{API_URL}/api/simulation/start", json={"speed_multiplier": speed_multiplier}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    get_sim_instance().start(speed_multiplier=speed_multiplier)

def pause_simulation() -> None:
    try:
        r = requests.post(f"{API_URL}/api/simulation/pause", timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    get_sim_instance().pause()

def step_simulation(hours: float = 1.0) -> None:
    try:
        r = requests.post(f"{API_URL}/api/simulation/step", json={"hours": hours}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    get_sim_instance().step(hours=hours, persist_db=True)

def reset_simulation(crew_count: int = 4, battery_pct: float = 65.0, o2_kg: float = 100.0, water_l: float = 500.0, food_kg: float = 120.0) -> None:
    try:
        r = requests.post(f"{API_URL}/api/simulation/reset", json={
            "crew_count": crew_count, "battery_pct": battery_pct, "o2_kg": o2_kg, "water_l": water_l, "food_kg": food_kg
        }, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    get_sim_instance().reset(
        crew_count=crew_count,
        initial_battery_pct=battery_pct,
        initial_o2_kg=o2_kg,
        initial_water_l=water_l,
        initial_food_kg=food_kg
    )

# Power System
def get_power_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/power/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    return {
        "generation_kw": sim.last_telemetry.get("power_generation", 0.0),
        "consumption_kw": sim.last_telemetry.get("power_consumption", 0.0),
        "net_power_kw": sim.last_telemetry.get("net_power", 0.0),
        "battery_kwh": sim.last_telemetry.get("battery_level", 0.0),
        "battery_pct": sim.last_telemetry.get("battery_pct", 0.0),
        "backup_power_kw": sim.last_telemetry.get("backup_power", 0.0),
        "load_shed_level": sim.power.load_shed_level,
        "backup_active": sim.power.backup_generator_active,
        "solar_failure_pct": sim.power.solar_failure_pct
    }

def set_load_shed(level: int) -> None:
    try:
        r = requests.post(f"{API_URL}/api/power/set-load-shed", json={"level": level}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.power.set_load_shed(level)
    sim.step(hours=0.0, persist_db=True)

def toggle_backup_generator(enable: bool) -> None:
    try:
        r = requests.post(f"{API_URL}/api/power/toggle-backup-generator", json={"enable": enable}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.power.toggle_backup_generator(enable)
    sim.step(hours=0.0, persist_db=True)

# Oxygen System
def get_oxygen_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/oxygen/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    return {
        "oxygen_level_kg": sim.last_telemetry.get("oxygen_level", 0.0),
        "production_rate_kg": sim.last_telemetry.get("oxygen_production", 0.0),
        "consumption_rate_kg": sim.last_telemetry.get("oxygen_consumption", 0.0),
        "leakage_rate_kg": sim.last_telemetry.get("oxygen_leakage", 0.0),
        "cabin_pressure_kpa": sim.last_telemetry.get("cabin_pressure", 101.3),
        "emergency_reserve_kg": sim.oxygen.emergency_reserve_kg,
        "emergency_valve_open": sim.oxygen.emergency_valve_open,
        "oga_active": sim.oxygen.oga_active,
        "section_isolated": sim.oxygen.section_isolated
    }

def set_oga(active: bool) -> None:
    try:
        r = requests.post(f"{API_URL}/api/oxygen/set-oga", json={"active": active}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.oxygen.set_oga(active)
    sim.step(hours=0.0, persist_db=True)

def toggle_emergency_reserve(open_valve: bool) -> None:
    try:
        r = requests.post(f"{API_URL}/api/oxygen/toggle-emergency-reserve", json={"open_valve": open_valve}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.oxygen.deploy_emergency_reserve(open_valve)
    sim.step(hours=0.0, persist_db=True)

def isolate_bulkhead() -> None:
    try:
        r = requests.post(f"{API_URL}/api/oxygen/isolate-bulkhead", timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.oxygen.isolate_breach_section()
    sim.step(hours=0.0, persist_db=True)

# Water System
def get_water_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/water/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    return {
        "water_level_l": sim.last_telemetry.get("water_level", 0.0),
        "recycled_l": sim.last_telemetry.get("water_recycled", 0.0),
        "used_l": sim.last_telemetry.get("water_used", 0.0),
        "loss_l": sim.last_telemetry.get("water_loss", 0.0),
        "emergency_reserve_l": sim.water.emergency_reserve_l,
        "rationing_mode": sim.water.rationing_mode,
        "wrs_active": sim.water.wrs_active,
        "wrs_pump_fault": sim.water.wrs_pump_fault
    }

def set_rationing(enable: bool) -> None:
    try:
        r = requests.post(f"{API_URL}/api/water/set-rationing", json={"enable": enable}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.water.set_rationing(enable)
    sim.step(hours=0.0, persist_db=True)

def set_wrs(active: bool) -> None:
    try:
        r = requests.post(f"{API_URL}/api/water/set-wrs", json={"active": active}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.water.set_wrs(active)
    sim.step(hours=0.0, persist_db=True)

# Temperature System
def get_temperature_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/temperature/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    return {
        "temp_internal_c": sim.last_telemetry.get("temp_internal", 21.5),
        "temp_external_c": sim.last_telemetry.get("temp_external", -20.0),
        "target_temp_c": sim.temp.target_temp,
        "hvac_mode": sim.temp.hvac_mode,
        "hvac_power_kw": sim.temp.hvac_power_kw,
        "insulation_breach": sim.temp.insulation_breach,
        "heater_fault": sim.temp.heater_fault
    }

def set_temperature_target(target_c: float) -> None:
    try:
        r = requests.post(f"{API_URL}/api/temperature/set-target", json={"target_temp_c": target_c}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    sim = get_sim_instance()
    sim.temp.set_target_temperature(target_c)
    sim.step(hours=0.0, persist_db=True)

# Emergency System & Scenarios
def get_emergency_status() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/emergency/status", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    return {
        "base_status": sim.last_telemetry.get("base_status", "NORMAL"),
        "active_faults": sim.active_faults,
        "recent_actions": sim.recent_actions,
        "anomaly": sim.latest_anomaly,
        "incidents": get_incidents(unresolved_only=True, limit=20)
    }

def inject_scenario(scenario: str) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_URL}/api/emergency/inject-scenario", json={"scenario": scenario}, timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return get_sim_instance().inject_scenario_fault(scenario)

def resolve_scenario(scenario: str) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_URL}/api/emergency/resolve-scenario", json={"scenario": scenario}, timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return get_sim_instance().resolve_fault(scenario)

def resolve_incident_entry(incident_id: int) -> None:
    try:
        r = requests.post(f"{API_URL}/api/emergency/resolve-incident", json={"incident_id": incident_id}, timeout=0.6)
        if r.ok:
            return
    except Exception:
        pass
    resolve_incident(incident_id)

# AI Predictions
def get_all_predictions() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_URL}/api/predictions/all", timeout=1.0)
        if r.ok:
            return r.json()
    except Exception:
        pass
    sim = get_sim_instance()
    power_f = sim.ai_power.forecast_7_days(
        current_day=sim.mission_day,
        current_battery_pct=sim.power.battery_pct,
        battery_capacity_kwh=sim.power.battery_capacity_kwh,
        crew_count=sim.crew.crew_count
    )
    o2_f = sim.ai_oxygen.forecast_7_days(
        current_day=sim.mission_day,
        current_o2_kg=sim.oxygen.oxygen_level_kg,
        crew_count=sim.crew.crew_count,
        active_leak_rate_kg_hr=sim.oxygen.active_leak_rate_kg_hr if not sim.oxygen.section_isolated else 0.0,
        oga_active=sim.oxygen.oga_active
    )
    water_f = sim.ai_water.forecast_7_days(
        current_day=sim.mission_day,
        current_water_l=sim.water.water_level_l,
        crew_count=sim.crew.crew_count,
        rationing_mode=sim.water.rationing_mode,
        wrs_efficiency=0.10 if sim.water.wrs_pump_fault else 0.90,
        pipe_leak_l_hr=sim.water.pipe_leak_rate_l_hr
    )
    failure_f = sim.ai_failure.evaluate_all_equipment(
        sim.equipment.get_all_components(),
        thermal_stress=abs(sim.last_telemetry.get("temp_internal", 21.0) - sim.last_telemetry.get("temp_external", -20.0)) / 150.0
    )
    return {
        "mission_day": round(sim.mission_day, 2),
        "power_forecast_7d": power_f,
        "oxygen_forecast_7d": o2_f,
        "water_forecast_7d": water_f,
        "equipment_failure_risks": failure_f,
        "anomaly_analysis": sim.latest_anomaly
    }

# Inventory
def get_inventory_data() -> List[Dict[str, Any]]:
    try:
        r = requests.get(f"{API_URL}/api/database/inventory", timeout=0.6)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return get_inventory()

