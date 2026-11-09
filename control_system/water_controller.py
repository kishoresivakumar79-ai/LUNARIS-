"""
LUNARIS Control System: Water Controller
Automates recycling throughput and water rationing conservation protocols.
"""

from typing import Dict, Any

class WaterController:
    def __init__(self, water_warning_l: float = 180.0, water_critical_l: float = 90.0):
        self.water_warning_l = water_warning_l
        self.water_critical_l = water_critical_l
        
    def evaluate(self, water_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        water_level = water_telemetry["water_level_l"]
        pump_fault = water_telemetry["wrs_pump_fault"]
        
        actions = []
        set_rationing = False
        set_wrs = True
        
        if water_level < self.water_critical_l:
            set_rationing = True
            actions.append("CRITICAL_WATER_SHORTAGE: Mandatory water rationing active (hygiene restricted to sponge baths).")
        elif water_level < self.water_warning_l or pump_fault:
            set_rationing = True
            actions.append("LOW_WATER_WARNING: Water conservation mode enabled.")
            
        return {
            "set_rationing": set_rationing,
            "set_wrs": set_wrs,
            "actions_taken": actions
        }

