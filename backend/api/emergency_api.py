"""
LUNARIS API: Emergency & Scenario Injection Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.services.simulation_service import SimulationService
from database.database import get_incidents, resolve_incident

router = APIRouter(prefix="/emergency", tags=["Emergency Management"])
sim = SimulationService()

class ScenarioFaultRequest(BaseModel):
    scenario: str  # SOLAR_POWER_FAILURE, OXYGEN_LEAKAGE, WATER_SHORTAGE, TEMPERATURE_EMERGENCY

class IncidentResolveRequest(BaseModel):
    incident_id: int

@router.get("/status")
def get_emergency_status() -> Dict[str, Any]:
    return {
        "base_status": sim.last_telemetry.get("base_status", "NORMAL"),
        "active_faults": sim.active_faults,
        "recent_actions": sim.recent_actions,
        "anomaly": sim.latest_anomaly,
        "incidents": get_incidents(unresolved_only=True, limit=20)
    }

@router.post("/inject-scenario")
def inject_scenario(req: ScenarioFaultRequest):
    valid_scenarios = ["SOLAR_POWER_FAILURE", "OXYGEN_LEAKAGE", "WATER_SHORTAGE", "TEMPERATURE_EMERGENCY"]
    if req.scenario.upper() not in valid_scenarios:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Must be one of {valid_scenarios}")
    res = sim.inject_scenario_fault(req.scenario)
    return {"status": "success", "result": res}

@router.post("/resolve-scenario")
def resolve_scenario(req: ScenarioFaultRequest):
    res = sim.resolve_fault(req.scenario)
    return {"status": "success", "result": res}

@router.post("/resolve-incident")
def resolve_incident_endpoint(req: IncidentResolveRequest):
    resolve_incident(req.incident_id)
    return {"status": "success", "resolved_id": req.incident_id}

