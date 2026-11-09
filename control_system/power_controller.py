"""
LUNARIS Control System: Power Controller
Automates load shedding, battery preservation, and backup generator dispatch.
"""

from typing import Dict, Any

class PowerController:
    def __init__(self, battery_critical_pct: float = 25.0, battery_warning_pct: float = 45.0):
        self.battery_critical_pct = battery_critical_pct
        self.battery_warning_pct = battery_warning_pct
        
    def evaluate(self, power_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates battery state of charge and power delta to adjust load shed level and auxiliary generator.
        """
        battery_pct = power_telemetry["battery_pct"]
        net_power = power_telemetry["net_power_kw"]
        current_shed = power_telemetry["load_shed_level"]
        backup_active = power_telemetry["backup_active"]
        
        actions = []
        target_shed = current_shed
        target_backup = backup_active
        
        # Power management rules
        if battery_pct <= self.battery_critical_pct:
            target_shed = 3  # Survival mode: life support only
            target_backup = True
            actions.append("CRITICAL_BATTERY: Initiated Level 3 Load Shedding and started Fuel Cell Generator.")
        elif battery_pct <= self.battery_warning_pct:
            if net_power < 0:
                target_shed = 2  # Urgent mode: shed labs and auxiliary
                target_backup = True
                actions.append("LOW_BATTERY_DEFICIT: Initiated Level 2 Load Shedding, auxiliary power online.")
            else:
                target_shed = 1  # Moderate conservation
        else:
            # Healthy battery
            if net_power >= 0:
                target_shed = 0  # Full normal
                target_backup = False
            elif battery_pct > 60.0:
                target_shed = 0
                target_backup = False
                
        return {
            "target_load_shed": target_shed,
            "target_backup_generator": target_backup,
            "actions_taken": actions
        }

