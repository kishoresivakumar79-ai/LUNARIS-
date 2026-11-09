"""
LUNARIS API: Water Management Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.services.simulation_service import SimulationService

router = APIRouter(prefix="/water", tags=["Water Management"])
sim = SimulationService()

class RationRequest(BaseModel):
    enable: bool

class WrsRequest(BaseModel):
    active: bool

@router.get("/status")
def get_water_status() -> Dict[str, Any]:
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

@router.post("/set-rationing")
def set_rationing(req: RationRequest):
    sim.water.set_rationing(req.enable)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "rationing_mode": sim.water.rationing_mode}

@router.post("/set-wrs")
def set_wrs(req: WrsRequest):
    sim.water.set_wrs(req.active)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "wrs_active": sim.water.wrs_active}

@router.get("/forecast-7-days")
def get_water_forecast():
    return sim.ai_water.forecast_7_days(
        current_day=sim.mission_day,
        current_water_l=sim.water.water_level_l,
        crew_count=sim.crew.crew_count,
        rationing_mode=sim.water.rationing_mode,
        wrs_efficiency=0.10 if sim.water.wrs_pump_fault else 0.90,
        pipe_leak_l_hr=sim.water.pipe_leak_rate_l_hr
    )

