"""
LUNARIS Control System: Oxygen Controller
Automates oxygen generation output, section isolation, and emergency reserve deployment.
"""

from typing import Dict, Any

class OxygenController:
    def __init__(self, o2_critical_kg: float = 25.0, pressure_critical_kpa: float = 90.0):
        self.o2_critical_kg = o2_critical_kg
        self.pressure_critical_kpa = pressure_critical_kpa
        
    def evaluate(self, o2_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        o2_level = o2_telemetry["oxygen_level_kg"]
        pressure = o2_telemetry["cabin_pressure_kpa"]
        leak_active = o2_telemetry["leak_active"]
        
        actions = []
        isolate_bulkhead = False
        deploy_emergency = False
        oga_active = True
        
        # Rapid depressurization / puncture
        if pressure < self.pressure_critical_kpa or leak_active:
            isolate_bulkhead = True
            deploy_emergency = True
            actions.append("RAPID_DEPRESSURIZATION: Automated bulkhead seal closed; emergency reserve valve opened.")
            
        # Low oxygen inventory
        if o2_level < self.o2_critical_kg:
            deploy_emergency = True
            oga_active = True
            actions.append("LOW_O2_INVENTORY: Emergency cryogenic reserve manifold opened.")
            
        return {
            "isolate_section": isolate_bulkhead,
            "deploy_emergency_reserve": deploy_emergency,
            "set_oga_active": oga_active,
            "actions_taken": actions
        }

