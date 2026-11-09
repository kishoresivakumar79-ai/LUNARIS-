"""
LUNARIS Simulation: Oxygen Management System
Simulates Oxygen Generation Assembly (OGA), crew metabolic breathing consumption,
cryogenic storage tanks, atmospheric pressure, and leak detection.
Mathematical formulation:
    O_next = O_current + O_produced - O_consumed - O_leaked
"""

from typing import Dict, Any

class OxygenSystem:
    def __init__(self, tank_capacity_kg: float = 200.0, initial_oxygen_kg: float = 100.0):
        self.tank_capacity_kg = tank_capacity_kg
        self.oxygen_level_kg = min(tank_capacity_kg, initial_oxygen_kg)
        self.emergency_reserve_kg = 50.0
        self.emergency_valve_open = False
        
        # Nominal OGA parameters
        self.oga_active = True
        self.oga_nominal_production_kg_day = 8.0  # 8 kg/day nominal capacity
        self.water_per_kg_o2 = 1.125               # Liters of water electrolyzed per kg O2
        
        # Habitat atmospheric envelope (approx 450 m^3 volume)
        self.cabin_pressure_kpa = 101.3            # Nominal Earth sea level (101.3 kPa)
        self.nominal_leak_kg_day = 0.05            # Normal microscopic airlock seal leakage
        
        # Fault injection
        self.active_leak_rate_kg_hr = 0.0          # Set during hull puncture / valve failure
        self.section_isolated = False               # Emergency bulkhead isolation
        self.oga_fault = False
        
    def step(self, hours: float, crew_o2_consumed_kg: float) -> Dict[str, Any]:
        """
        Executes one step of the oxygen balance simulation.
        """
        day_fraction = hours / 24.0
        
        # Oxygen Production from OGA
        if self.oga_active and not self.oga_fault:
            produced_kg = self.oga_nominal_production_kg_day * day_fraction
        else:
            produced_kg = 0.0
            
        # Consumption from crew
        consumed_kg = crew_o2_consumed_kg
        
        # Leakage
        leak_kg = (self.nominal_leak_kg_day * day_fraction)
        if self.active_leak_rate_kg_hr > 0.0 and not self.section_isolated:
            leak_kg += (self.active_leak_rate_kg_hr * hours)
            # Pressure drops with massive leak
            pressure_drop = (self.active_leak_rate_kg_hr * hours) * 4.2
            self.cabin_pressure_kpa = max(10.0, self.cabin_pressure_kpa - pressure_drop)
        else:
            # Gradually regulate pressure back to nominal if leakage stopped and OGA online
            if self.cabin_pressure_kpa < 101.3:
                self.cabin_pressure_kpa = min(101.3, self.cabin_pressure_kpa + (0.5 * hours))
                
        # Emergency reserve injection
        injected_reserve_kg = 0.0
        if self.emergency_valve_open and self.emergency_reserve_kg > 0.0:
            injected_reserve_kg = min(self.emergency_reserve_kg, 5.0 * hours)
            self.emergency_reserve_kg -= injected_reserve_kg
            self.oxygen_level_kg += injected_reserve_kg
            
        # Net balance
        self.oxygen_level_kg = max(0.0, min(self.tank_capacity_kg, self.oxygen_level_kg + produced_kg - consumed_kg - leak_kg))
        
        # Water consumed by OGA
        water_needed_liters = produced_kg * self.water_per_kg_o2
        
        # Safety margin
        o2_days_remaining = self.oxygen_level_kg / max(0.1, (consumed_kg / max(0.01, day_fraction))) if day_fraction > 0 else 0.0
        
        return {
            "oxygen_level_kg": round(self.oxygen_level_kg, 2),
            "oxygen_production_kg": round(produced_kg, 3),
            "oxygen_consumption_kg": round(consumed_kg, 3),
            "oxygen_leakage_kg": round(leak_kg, 3),
            "cabin_pressure_kpa": round(self.cabin_pressure_kpa, 2),
            "emergency_reserve_kg": round(self.emergency_reserve_kg, 2),
            "emergency_valve_open": self.emergency_valve_open,
            "oga_active": self.oga_active and not self.oga_fault,
            "water_consumed_liters": round(water_needed_liters, 2),
            "days_remaining": round(o2_days_remaining, 1),
            "section_isolated": self.section_isolated,
            "leak_active": (self.active_leak_rate_kg_hr > 0.0 and not self.section_isolated)
        }
        
    def inject_hull_puncture(self, leak_rate_kg_hr: float = 1.5) -> None:
        self.active_leak_rate_kg_hr = leak_rate_kg_hr
        self.section_isolated = False
        
    def isolate_breach_section(self) -> None:
        """Automatic or manual bulkhead seal closing"""
        self.section_isolated = True
        
    def deploy_emergency_reserve(self, open_valve: bool = True) -> None:
        self.emergency_valve_open = open_valve
        
    def set_oga(self, active: bool) -> None:
        self.oga_active = active
        
    def clear_faults(self) -> None:
        self.active_leak_rate_kg_hr = 0.0
        self.section_isolated = False
        self.oga_fault = False
        self.emergency_valve_open = False
        self.cabin_pressure_kpa = 101.3

