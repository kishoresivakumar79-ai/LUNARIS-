"""
LUNARIS Digital Twin: Twin Engine
Maintains high-fidelity virtual representation of physical lunar base assets,
spatial topologies, and real-time operational states.
"""

from typing import Dict, Any, List
from datetime import datetime

class DigitalTwinEntity:
    def __init__(self, entity_id: str, name: str, entity_type: str, position: List[float]):
        self.entity_id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.position = position  # [x, y, z] in lunar base coordinates (meters)
        self.health_pct = 100.0
        self.state = "NOMINAL"    # NOMINAL, WARNING, CRITICAL, OFFLINE
        self.telemetry: Dict[str, Any] = {}
        self.last_updated = datetime.utcnow().isoformat()
        
    def update(self, health: float, state: str, telemetry: Dict[str, Any]) -> None:
        self.health_pct = health
        self.state = state
        self.telemetry = telemetry
        self.last_updated = datetime.utcnow().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "position": self.position,
            "health_pct": self.health_pct,
            "state": self.state,
            "telemetry": self.telemetry,
            "last_updated": self.last_updated
        }

class DigitalTwinEngine:
    def __init__(self):
        self.entities: Dict[str, DigitalTwinEntity] = {
            "HABITAT_CORE": DigitalTwinEntity("HABITAT_CORE", "Central Habitat Biosphere", "Habitat", [0.0, 0.0, 0.0]),
            "GREENHOUSE_DOME": DigitalTwinEntity("GREENHOUSE_DOME", "Hydroponic Greenhouse", "Agriculture", [28.0, 0.0, -12.0]),
            "SOLAR_ARRAY_A": DigitalTwinEntity("SOLAR_ARRAY_A", "Photovoltaic Array Alpha", "Energy", [-35.0, 0.0, 25.0]),
            "SOLAR_ARRAY_B": DigitalTwinEntity("SOLAR_ARRAY_B", "Photovoltaic Array Beta", "Energy", [-35.0, 0.0, -25.0]),
            "POWER_VAULT": DigitalTwinEntity("POWER_VAULT", "Subsurface Battery Bank & Fuel Cell", "Energy", [-18.0, 0.0, 0.0]),
            "OGA_CRYOTANK": DigitalTwinEntity("OGA_CRYOTANK", "Oxygen Generation & Storage Unit", "LifeSupport", [18.0, 0.0, 22.0]),
            "WRS_FACILITY": DigitalTwinEntity("WRS_FACILITY", "Water Reclamation & Filtration Plant", "LifeSupport", [20.0, 0.0, -24.0]),
            "COMMS_DISH": DigitalTwinEntity("COMMS_DISH", "High-Gain Lunar Earth Uplink", "Communications", [0.0, 15.0, 40.0]),
            "ROVER_ALPHA": DigitalTwinEntity("ROVER_ALPHA", "Autonomous Exploration Rover 1", "Robotics", [15.0, 0.0, 35.0])
        }
        
    def sync_from_telemetry(self, telemetry: Dict[str, Any], equipment: List[Dict[str, Any]]) -> None:
        """
        Updates each digital twin asset from the latest live telemetry and equipment reports.
        """
        eq_map = {eq["component_id"]: eq for eq in equipment}
        
        # 1. Habitat Core
        hab_state = "NOMINAL"
        if telemetry.get("cabin_pressure", 101.3) < 90.0 or telemetry.get("temp_internal", 21.0) < 16.0:
            hab_state = "CRITICAL"
        elif telemetry.get("temp_internal", 21.0) < 18.0 or telemetry.get("temp_internal", 21.0) > 25.0:
            hab_state = "WARNING"
        self.entities["HABITAT_CORE"].update(
            health=eq_map.get("HAB_SEAL", {}).get("health_pct", 99.0),
            state=hab_state,
            telemetry={
                "pressure_kpa": telemetry.get("cabin_pressure", 101.3),
                "temp_internal_c": telemetry.get("temp_internal", 21.5),
                "crew_count": 4,
                "hvac_mode": telemetry.get("hvac_mode", "IDLE")
            }
        )
        
        # 2. Solar Arrays
        sol_a_eq = eq_map.get("SOLAR_A", {})
        self.entities["SOLAR_ARRAY_A"].update(
            health=sol_a_eq.get("health_pct", 98.0),
            state="CRITICAL" if sol_a_eq.get("status") == "CRITICAL" else "NOMINAL",
            telemetry={
                "irradiance": telemetry.get("solar_irradiance", 1361.0),
                "output_kw": round(telemetry.get("power_generation", 120.0) * 0.5, 2)
            }
        )
        sol_b_eq = eq_map.get("SOLAR_B", {})
        self.entities["SOLAR_ARRAY_B"].update(
            health=sol_b_eq.get("health_pct", 97.0),
            state="CRITICAL" if sol_b_eq.get("status") == "CRITICAL" else "NOMINAL",
            telemetry={
                "irradiance": telemetry.get("solar_irradiance", 1361.0),
                "output_kw": round(telemetry.get("power_generation", 120.0) * 0.5, 2)
            }
        )
        
        # 3. Power Vault
        bat_eq = eq_map.get("BATTERY_MAIN", {})
        self.entities["POWER_VAULT"].update(
            health=bat_eq.get("health_pct", 96.0),
            state="CRITICAL" if telemetry.get("battery_pct", 65.0) < 20.0 else "NOMINAL",
            telemetry={
                "battery_pct": telemetry.get("battery_pct", 65.0),
                "battery_kwh": telemetry.get("battery_level", 325.0),
                "backup_active": telemetry.get("backup_power", 0.0) > 0
            }
        )
        
        # 4. OGA Plant
        oga_eq = eq_map.get("OGA_SYS", {})
        self.entities["OGA_CRYOTANK"].update(
            health=oga_eq.get("health_pct", 94.0),
            state="CRITICAL" if telemetry.get("oxygen_level", 100.0) < 25.0 else "NOMINAL",
            telemetry={
                "oxygen_kg": telemetry.get("oxygen_level", 100.0),
                "production_rate": telemetry.get("oxygen_production", 8.0),
                "leakage_kg": telemetry.get("oxygen_leakage", 0.0)
            }
        )
        
        # 5. WRS Facility
        wrs_eq = eq_map.get("WRS_SYS", {})
        self.entities["WRS_FACILITY"].update(
            health=wrs_eq.get("health_pct", 93.0),
            state="CRITICAL" if telemetry.get("water_level", 500.0) < 90.0 else "NOMINAL",
            telemetry={
                "water_liters": telemetry.get("water_level", 500.0),
                "recycled_liters": telemetry.get("water_recycled", 40.0)
            }
        )
        
        # 6. Greenhouse
        self.entities["GREENHOUSE_DOME"].update(
            health=97.5,
            state="NOMINAL",
            telemetry={"food_reserve_kg": telemetry.get("food_level", 120.0), "growth_cycle": "Optimal"}
        )
        
        # 7. Rover Position (simulated exploration arc)
        day = telemetry.get("mission_day", 1.0)
        import math
        rx = 25.0 + math.cos(day * 2.0) * 15.0
        rz = 30.0 + math.sin(day * 2.0) * 15.0
        rover_eq = eq_map.get("ROVER_ALPHA", {})
        self.entities["ROVER_ALPHA"].position = [round(rx, 2), 0.0, round(rz, 2)]
        self.entities["ROVER_ALPHA"].update(
            health=rover_eq.get("health_pct", 92.0),
            state=rover_eq.get("status", "OPTIMAL"),
            telemetry={"battery_pct": 88.0, "mode": "SURVEYING"}
        )
        
    def get_twin_snapshot(self) -> Dict[str, Any]:
        return {
            "entities": {eid: e.to_dict() for eid, e in self.entities.items()},
            "entity_count": len(self.entities),
            "timestamp": datetime.utcnow().isoformat()
        }

