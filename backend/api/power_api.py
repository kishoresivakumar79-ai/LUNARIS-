"""
LUNARIS API: Power Management Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from backend.services.simulation_service import SimulationService

router = APIRouter(prefix="/power", tags=["Power Management"])
sim = SimulationService()

class LoadShedRequest(BaseModel):
    level: int  # 0, 1, 2, 3

class BackupGenRequest(BaseModel):
    enable: bool

@router.get("/status")
def get_power_status() -> Dict[str, Any]:
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

@router.post("/set-load-shed")
def set_load_shed(req: LoadShedRequest):
    if not (0 <= req.level <= 3):
        raise HTTPException(status_code=400, detail="Level must be 0, 1, 2, or 3")
    sim.power.set_load_shed(req.level)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "new_load_shed_level": sim.power.load_shed_level}

@router.post("/toggle-backup-generator")
def toggle_backup(req: BackupGenRequest):
    sim.power.toggle_backup_generator(req.enable)
    sim.step(hours=0.0, persist_db=True)
    return {"status": "success", "backup_generator_active": sim.power.backup_generator_active}

@router.get("/forecast-7-days")
def get_power_forecast():
    return sim.ai_power.forecast_7_days(
        current_day=sim.mission_day,
        current_battery_pct=sim.power.battery_pct,
        battery_capacity_kwh=sim.power.battery_capacity_kwh,
        crew_count=sim.crew.crew_count
    )

