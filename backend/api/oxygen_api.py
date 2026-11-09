"""
LUNARIS API: Oxygen Management Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.services.simulation_service import SimulationService

router = APIRouter(prefix="/oxygen", tags=["Oxygen Management"])
sim = SimulationService()

class OgaRequest(BaseModel):
    active: bool

class EmergencyReserveRequest(BaseModel):
    open_valve: bool

@router.get("/status")
def get_oxygen_status() -> Dict[str, Any]:
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

@router.post("/set-oga")
def set_oga(req: OgaRequest):
    sim.oxygen.set_oga(req.active)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "oga_active": sim.oxygen.oga_active}

@router.post("/toggle-emergency-reserve")
def toggle_reserve(req: EmergencyReserveRequest):
    sim.oxygen.deploy_emergency_reserve(req.open_valve)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "emergency_valve_open": sim.oxygen.emergency_valve_open}

@router.post("/isolate-bulkhead")
def isolate_bulkhead():
    sim.oxygen.isolate_breach_section()
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "section_isolated": True}

@router.get("/forecast-7-days")
def get_oxygen_forecast():
    return sim.ai_oxygen.forecast_7_days(
        current_day=sim.mission_day,
        current_o2_kg=sim.oxygen.oxygen_level_kg,
        crew_count=sim.crew.crew_count,
        active_leak_rate_kg_hr=sim.oxygen.active_leak_rate_kg_hr if not sim.oxygen.section_isolated else 0.0,
        oga_active=sim.oxygen.oga_active
    )

