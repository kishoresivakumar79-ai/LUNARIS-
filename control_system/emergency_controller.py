"""
LUNARIS Control System: Emergency Detection & Management Controller
Classifies base health status into NORMAL, WARNING, CRITICAL, and triggers automated protocols.
"""

from typing import Dict, List, Any
from datetime import datetime

class EmergencyController:
    def __init__(self):
        self.active_emergencies: List[Dict[str, Any]] = []
        self.incident_history: List[Dict[str, Any]] = []
        
    def evaluate(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans all subsystem telemetry for safety violations.
        Returns:
            overall_status: NORMAL, WARNING, CRITICAL
            emergencies: list of active alarm objects
        """
        alarms = []
        
        # 1. Oxygen & Pressure checks
        o2_level = telemetry.get("oxygen_level", 100.0)
        pressure = telemetry.get("cabin_pressure", 101.3)
        leak_active = telemetry.get("oxygen_leakage", 0.0) > 0.1
        
        if pressure < 85.0 or (leak_active and pressure < 95.0):
            alarms.append({
                "id": "EMERG_CABIN_BREACH",
                "subsystem": "Atmosphere",
                "severity": "CRITICAL",
                "title": "Rapid Cabin Depressurization",
                "message": f"Cabin pressure critically low: {pressure:.1f} kPa. Airlock isolation recommended."
            })
        elif o2_level < 25.0:
            alarms.append({
                "id": "EMERG_O2_DEPLETION",
                "subsystem": "Oxygen",
                "severity": "CRITICAL",
                "title": "Oxygen Reserve Depletion",
                "message": f"Primary oxygen down to {o2_level:.1f} kg (< 25 kg minimum safe threshold)."
            })
        elif o2_level < 40.0:
            alarms.append({
                "id": "WARN_O2_LOW",
                "subsystem": "Oxygen",
                "severity": "WARNING",
                "title": "Oxygen Reserve Low",
                "message": f"Oxygen inventory at {o2_level:.1f} kg. Monitor OGA output."
            })
            
        # 2. Power & Battery checks
        battery_pct = telemetry.get("battery_pct", 65.0)
        if battery_pct < 15.0:
            alarms.append({
                "id": "EMERG_BATTERY_BLACKOUT",
                "subsystem": "Power",
                "severity": "CRITICAL",
                "title": "Critical Battery Depletion",
                "message": f"Battery at {battery_pct:.1f}%. Immediate load shedding Level 3 required."
            })
        elif battery_pct < 30.0:
            alarms.append({
                "id": "WARN_BATTERY_LOW",
                "subsystem": "Power",
                "severity": "WARNING",
                "title": "Low Battery Warning",
                "message": f"Battery at {battery_pct:.1f}%. Aux generator recommended."
            })
            
        # 3. Water checks
        water_level = telemetry.get("water_level", 500.0)
        if water_level < 80.0:
            alarms.append({
                "id": "EMERG_WATER_DEPLETION",
                "subsystem": "Water",
                "severity": "CRITICAL",
                "title": "Critical Water Depletion",
                "message": f"Fresh water level at {water_level:.1f} L. Engage emergency reserve."
            })
        elif water_level < 150.0:
            alarms.append({
                "id": "WARN_WATER_LOW",
                "subsystem": "Water",
                "severity": "WARNING",
                "title": "Water Inventory Low",
                "message": f"Fresh water at {water_level:.1f} L. Water rationing initiated."
            })
            
        # 4. Temperature checks
        temp_in = telemetry.get("temp_internal", 21.5)
        if temp_in < 14.0 or temp_in > 32.0:
            alarms.append({
                "id": "EMERG_TEMP_EXTREME",
                "subsystem": "Thermal",
                "severity": "CRITICAL",
                "title": "Cabin Thermal Excursion",
                "message": f"Cabin temp at dangerous level: {temp_in:.1f}°C."
            })
        elif temp_in < 18.0 or temp_in > 25.0:
            alarms.append({
                "id": "WARN_TEMP_OFF_NOMINAL",
                "subsystem": "Thermal",
                "severity": "WARNING",
                "title": "Thermal Deviation",
                "message": f"Cabin temp at {temp_in:.1f}°C, outside optimal 18-24°C comfort band."
            })
            
        # Overall status derivation
        has_critical = any(a["severity"] == "CRITICAL" for a in alarms)
        has_warning = any(a["severity"] == "WARNING" for a in alarms)
        
        if has_critical:
            overall_status = "CRITICAL"
        elif has_warning:
            overall_status = "WARNING"
        else:
            overall_status = "NORMAL"
            
        self.active_emergencies = alarms
        return {
            "overall_status": overall_status,
            "active_emergencies": alarms,
            "emergency_count": len(alarms)
        }

