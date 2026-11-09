"""
LUNARIS Simulation: Equipment Subsystem Simulation
Tracks component wear, thermal cycle degradation, operating hours, and fault states.
"""

from typing import Dict, List, Any
import random

class EquipmentManager:
    def __init__(self):
        self.components = {
            "SOLAR_A": {
                "name": "Solar Array Alpha",
                "subsystem": "Power",
                "health_pct": 98.5,
                "operating_hours": 420.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.02
            },
            "SOLAR_B": {
                "name": "Solar Array Beta",
                "subsystem": "Power",
                "health_pct": 97.8,
                "operating_hours": 420.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.03
            },
            "BATTERY_MAIN": {
                "name": "Lithium-Sulfur Battery Bank",
                "subsystem": "Power",
                "health_pct": 96.0,
                "operating_hours": 720.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.04
            },
            "BACKUP_GEN": {
                "name": "Hydrogen Fuel Cell Auxiliary",
                "subsystem": "Power",
                "health_pct": 100.0,
                "operating_hours": 48.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.01
            },
            "OGA_SYS": {
                "name": "Oxygen Generation Assembly",
                "subsystem": "LifeSupport",
                "health_pct": 94.2,
                "operating_hours": 580.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.05
            },
            "WRS_SYS": {
                "name": "Water Recovery System",
                "subsystem": "LifeSupport",
                "health_pct": 93.0,
                "operating_hours": 610.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.06
            },
            "ATCS_HVAC": {
                "name": "Active Thermal Control System",
                "subsystem": "Thermal",
                "health_pct": 95.5,
                "operating_hours": 720.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.03
            },
            "HAB_SEAL": {
                "name": "Habitat Pressure Hull Seal",
                "subsystem": "Structure",
                "health_pct": 99.1,
                "operating_hours": 720.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.01
            },
            "COMMS_ARRAY": {
                "name": "High-Gain Earth Dish",
                "subsystem": "Comms",
                "health_pct": 99.5,
                "operating_hours": 720.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.01
            },
            "ROVER_ALPHA": {
                "name": "Lunar Surface Rover 1",
                "subsystem": "Robotics",
                "health_pct": 92.0,
                "operating_hours": 150.0,
                "status": "OPTIMAL",
                "fault": None,
                "failure_probability": 0.08
            }
        }
        
    def step(self, hours: float, temp_internal: float, temp_external: float) -> None:
        """
        Applies continuous micro-wear and calculates failure probability based on operational stresses.
        """
        temp_gradient = abs(temp_internal - temp_external)
        
        for cid, comp in self.components.items():
            comp["operating_hours"] += hours
            
            # Slow wear and tear
            base_wear = (0.002 * hours)
            if cid in ["SOLAR_A", "SOLAR_B"]:
                # Thermal cycling stress from day/night transitions
                cycle_stress = (temp_gradient / 200.0) * 0.003 * hours
                comp["health_pct"] = max(5.0, comp["health_pct"] - base_wear - cycle_stress)
            elif cid in ["OGA_SYS", "WRS_SYS"]:
                # High pressure pumping wear
                comp["health_pct"] = max(5.0, comp["health_pct"] - base_wear * 1.5)
            else:
                comp["health_pct"] = max(5.0, comp["health_pct"] - base_wear)
                
            # If a fault is active, health drops and status is degraded or critical
            if comp["fault"]:
                comp["health_pct"] = max(10.0, min(50.0, comp["health_pct"]))
                comp["status"] = "CRITICAL" if comp["health_pct"] < 30.0 else "DEGRADED"
                comp["failure_probability"] = min(0.95, comp["failure_probability"] + 0.3)
            else:
                if comp["health_pct"] > 85.0:
                    comp["status"] = "OPTIMAL"
                elif comp["health_pct"] > 50.0:
                    comp["status"] = "DEGRADED"
                else:
                    comp["status"] = "CRITICAL"
                # Wear-based baseline failure probability
                comp["failure_probability"] = round(min(0.85, (100.0 - comp["health_pct"]) / 100.0 * 0.25), 3)
                
            comp["health_pct"] = round(comp["health_pct"], 2)
            
    def get_base_health_pct(self) -> float:
        """Calculates global base health score (0-100%)"""
        if not self.components:
            return 100.0
        return round(sum(c["health_pct"] for c in self.components.values()) / len(self.components), 1)
        
    def inject_fault(self, component_id: str, fault_description: str) -> bool:
        if component_id in self.components:
            self.components[component_id]["fault"] = fault_description
            self.components[component_id]["status"] = "CRITICAL"
            self.components[component_id]["health_pct"] = min(35.0, self.components[component_id]["health_pct"])
            self.components[component_id]["failure_probability"] = 0.85
            return True
        return False
        
    def repair_component(self, component_id: str) -> bool:
        if component_id in self.components:
            self.components[component_id]["fault"] = None
            self.components[component_id]["status"] = "OPTIMAL"
            self.components[component_id]["health_pct"] = 98.0
            self.components[component_id]["failure_probability"] = 0.02
            return True
        return False
        
    def get_all_components(self) -> List[Dict[str, Any]]:
        result = []
        for cid, comp in self.components.items():
            result.append({
                "component_id": cid,
                "name": comp["name"],
                "subsystem": comp["subsystem"],
                "status": comp["status"],
                "health_pct": comp["health_pct"],
                "operating_hours": round(comp["operating_hours"], 1),
                "failure_probability": comp["failure_probability"],
                "fault": comp["fault"]
            })
        return result

