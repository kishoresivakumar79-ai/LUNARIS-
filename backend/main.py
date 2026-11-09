"""
LUNARIS: Virtual Moon Base Management System
FastAPI Backend Server
Coordinates AI engines, physical simulation loops, Digital Twin synchronization,
WebSocket streaming, and 3D visualization.
"""

import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from database.database import init_db, get_recent_telemetry, get_incidents, get_inventory
from backend.services.simulation_service import SimulationService
from backend.services.digital_twin_service import DigitalTwinService

from backend.api.power_api import router as power_router
from backend.api.oxygen_api import router as oxygen_router
from backend.api.water_api import router as water_router
from backend.api.temperature_api import router as temp_router
from backend.api.emergency_api import router as emergency_router

app = FastAPI(
    title="LUNARIS Mission Control API",
    description="Virtual Moon Base Management System: AI + Digital Twin + 3D Simulation",
    version="1.0.0"
)

# Enable CORS for local dashboards and Three.js frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
init_db()
sim = SimulationService()
twin_service = DigitalTwinService()

# Mount Sub-Routers
app.include_router(power_router, prefix="/api")
app.include_router(oxygen_router, prefix="/api")
app.include_router(water_router, prefix="/api")
app.include_router(temp_router, prefix="/api")
app.include_router(emergency_router, prefix="/api")

# Static files for 3D visualization
FRONTEND_3D_DIR = Path(__file__).resolve().parent.parent / "frontend_3d"
if FRONTEND_3D_DIR.exists():
    app.mount("/3d", StaticFiles(directory=str(FRONTEND_3D_DIR), html=True), name="frontend_3d")

# Pydantic Schemas
class StepRequest(BaseModel):
    hours: float = 1.0

class StartRequest(BaseModel):
    speed_multiplier: float = 1.0

class ResetRequest(BaseModel):
    crew_count: int = 4
    battery_pct: float = 65.0
    o2_kg: float = 100.0
    water_l: float = 500.0
    food_kg: float = 120.0

@app.get("/")
def root():
    return {
        "system": "LUNARIS - Virtual Moon Base Management System",
        "status": "OPERATIONAL",
        "mission_day": round(sim.mission_day, 2),
        "docs_url": "/docs",
        "threejs_url": "/3d/"
    }

@app.get("/api/status")
def get_mission_status():
    return sim.get_full_status()

# Simulation controls
@app.post("/api/simulation/start")
def start_simulation(req: StartRequest):
    sim.start(speed_multiplier=req.speed_multiplier)
    return {"status": "started", "speed_multiplier": sim.speed_multiplier}

@app.post("/api/simulation/pause")
def pause_simulation():
    sim.pause()
    return {"status": "paused"}

@app.post("/api/simulation/step")
def step_simulation(req: StepRequest):
    composite = sim.step(hours=req.hours, persist_db=True)
    return {"status": "stepped", "hours": req.hours, "state": composite}

@app.post("/api/simulation/reset")
def reset_simulation(req: ResetRequest):
    sim.reset(
        crew_count=req.crew_count,
        initial_battery_pct=req.battery_pct,
        initial_o2_kg=req.o2_kg,
        initial_water_l=req.water_l,
        initial_food_kg=req.food_kg
    )
    return {"status": "reset", "mission_day": 1.0}

# Digital Twin Endpoints
@app.get("/api/digital-twin/state")
def get_digital_twin_state():
    return twin_service.get_state()

@app.get("/api/digital-twin/entities")
def get_digital_twin_entities():
    return twin_service.get_topology()

@app.get("/api/digital-twin/entity/{entity_id}")
def get_digital_twin_entity(entity_id: str):
    return twin_service.get_entity(entity_id)

# Consolidated AI Predictions
@app.get("/api/predictions/all")
def get_all_predictions():
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

# Database Endpoints
@app.get("/api/database/history")
def get_telemetry_history(limit: int = 100):
    return get_recent_telemetry(limit=limit)

@app.get("/api/database/incidents")
def get_incident_history(limit: int = 50, unresolved_only: bool = False):
    return get_incidents(unresolved_only=unresolved_only, limit=limit)

@app.get("/api/database/inventory")
def get_inventory_items():
    return get_inventory()

# WebSocket Real-Time Telemetry Streaming
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = {
                "mission_day": round(sim.mission_day, 2),
                "telemetry": sim.last_telemetry,
                "digital_twin": twin_service.get_state(),
                "base_status": sim.last_telemetry.get("base_status", "NORMAL"),
                "active_faults": sim.active_faults,
                "base_health_pct": sim.equipment.get_base_health_pct()
            }
            await websocket.send_json(payload)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

