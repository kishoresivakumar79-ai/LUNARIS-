"""
LUNARIS API: Temperature & Thermal Control Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.services.simulation_service import SimulationService

router = APIRouter(prefix="/temperature", tags=["Thermal Management"])
sim = SimulationService()

class SetpointRequest(BaseModel):
    target_temp_c: float

@router.get("/status")
def get_temp_status() -> Dict[str, Any]:
    return {
        "temp_internal_c": sim.last_telemetry.get("temp_internal", 21.5),
        "temp_external_c": sim.last_telemetry.get("temp_external", -20.0),
        "target_temp_c": sim.temp.target_temp,
        "hvac_mode": sim.temp.hvac_mode,
        "hvac_power_kw": sim.temp.hvac_power_kw,
        "insulation_breach": sim.temp.insulation_breach,
        "heater_fault": sim.temp.heater_fault
    }

@router.post("/set-target")
def set_target(req: SetpointRequest):
    sim.temp.set_target_temperature(req.target_temp_c)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "new_target_temp_c": sim.temp.target_temp}

