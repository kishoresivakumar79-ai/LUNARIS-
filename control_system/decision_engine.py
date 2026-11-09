"""
LUNARIS Control System: Autonomous Decision Engine
Orchestrates autonomous safety responses across power, life support, and environmental systems.
Enforces deterministic safety rules and records automated responses.
"""

from typing import Dict, Any, List
from control_system.power_controller import PowerController
from control_system.oxygen_controller import OxygenController
from control_system.water_controller import WaterController
from control_system.emergency_controller import EmergencyController

class DecisionEngine:
    def __init__(self):
        self.power_controller = PowerController()
        self.oxygen_controller = OxygenController()
        self.water_controller = WaterController()
        self.emergency_controller = EmergencyController()
        
    def evaluate_and_control(
        self,
        telemetry: Dict[str, Any],
        power_sys: Any,
        o2_sys: Any,
        water_sys: Any,
        temp_sys: Any
    ) -> Dict[str, Any]:
        """
        Runs the closed-loop autonomous control cycle:
        1. Classifies emergency level (NORMAL, WARNING, CRITICAL)
        2. Evaluates subsystem controllers
        3. Applies control outputs directly to physical/simulated subsystem objects
        4. Compiles an audit log of automated actions
        """
        all_actions = []
        
        # 1. Emergency classification
        emerg_res = self.emergency_controller.evaluate(telemetry)
        overall_status = emerg_res["overall_status"]
        
        # 2. Power control
        power_eval = self.power_controller.evaluate({
            "battery_pct": telemetry.get("battery_pct", 65.0),
            "net_power_kw": telemetry.get("net_power", 0.0),
            "load_shed_level": power_sys.load_shed_level,
            "backup_active": power_sys.backup_generator_active
        })
        if power_eval["target_load_shed"] != power_sys.load_shed_level:
            power_sys.set_load_shed(power_eval["target_load_shed"])
        if power_eval["target_backup_generator"] != power_sys.backup_generator_active:
            power_sys.toggle_backup_generator(power_eval["target_backup_generator"])
        all_actions.extend(power_eval["actions_taken"])
        
        # 3. Oxygen control
        o2_eval = self.oxygen_controller.evaluate({
            "oxygen_level_kg": telemetry.get("oxygen_level", 100.0),
            "cabin_pressure_kpa": telemetry.get("cabin_pressure", 101.3),
            "leak_active": telemetry.get("oxygen_leakage", 0.0) > 0.1
        })
        if o2_eval["isolate_section"] and not o2_sys.section_isolated:
            o2_sys.isolate_breach_section()
        if o2_eval["deploy_emergency_reserve"] and not o2_sys.emergency_valve_open:
            o2_sys.deploy_emergency_reserve(True)
        if o2_eval["set_oga_active"] != o2_sys.oga_active:
            o2_sys.set_oga(o2_eval["set_oga_active"])
        all_actions.extend(o2_eval["actions_taken"])
        
        # 4. Water control
        water_eval = self.water_controller.evaluate({
            "water_level_l": telemetry.get("water_level", 500.0),
            "wrs_pump_fault": water_sys.wrs_pump_fault
        })
        if water_eval["set_rationing"] != water_sys.rationing_mode:
            water_sys.set_rationing(water_eval["set_rationing"])
        all_actions.extend(water_eval["actions_taken"])
        
        # 5. Temperature control
        temp_in = telemetry.get("temp_internal", 21.5)
        if temp_in < 18.0:
            temp_sys.set_target_temperature(22.5)  # Heat boost
        elif temp_in > 25.0:
            temp_sys.set_target_temperature(20.5)  # Cool down
            
        return {
            "overall_status": overall_status,
            "active_emergencies": emerg_res["active_emergencies"],
            "automated_actions": all_actions
        }

