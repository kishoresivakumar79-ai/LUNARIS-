"""
LUNARIS Simulation: Power Management System
Simulates solar generation, energy storage (Li-S battery banks), auxiliary fuel cell generation,
power distribution across base subsystems, and load shedding.
Mathematical formulation:
    P_next = min(P_capacity, max(0, P_current + P_generated + P_backup - P_consumed))
"""

from typing import Dict, Any, List

class PowerSystem:
    def __init__(self, battery_capacity_kwh: float = 500.0, initial_battery_kwh: float = 325.0):
        self.battery_capacity_kwh = battery_capacity_kwh
        self.battery_level_kwh = min(battery_capacity_kwh, initial_battery_kwh)
        self.solar_array_area_m2 = 600.0  # Dual 300 m2 high-efficiency multi-junction arrays
        self.solar_efficiency = 0.32       # 32% space-grade solar efficiency
        self.battery_efficiency = 0.95     # 95% round-trip coulombic efficiency
        
        # Subsystem powers (kW)
        self.base_avionics_kw = 25.0
        self.science_lab_kw = 15.0
        self.backup_generator_active = False
        self.backup_power_output_kw = 40.0
        
        # Load shedding levels:
        # 0 = Full Normal (All systems powered)
        # 1 = Conservation (Science & aux throttled)
        # 2 = Urgent (Non-essential lighting & rover recharging off)
        # 3 = Survival (Critical Life Support & minimal heating only)
        self.load_shed_level = 0
        
        # Fault tracking
        self.solar_failure_pct = 0.0  # 0.0 to 1.0 (e.g. 0.7 = 70% lost)
        self.battery_fault = False
        
    @property
    def battery_pct(self) -> float:
        return (self.battery_level_kwh / self.battery_capacity_kwh) * 100.0
        
    def calculate_generation(self, solar_irradiance: float, dust_factor: float) -> float:
        """
        Calculates total solar generation in kW.
        P_solar = (Area * Irradiance * Efficiency * (1 - dust) * (1 - fault)) / 1000
        """
        raw_power_kw = (self.solar_array_area_m2 * solar_irradiance * self.solar_efficiency * (1.0 - dust_factor)) / 1000.0
        effective_power_kw = raw_power_kw * (1.0 - self.solar_failure_pct)
        return max(0.0, round(effective_power_kw, 2))
        
    def calculate_consumption(self, oga_active: bool, wrs_active: bool, hvac_power_kw: float) -> Dict[str, float]:
        """
        Calculates total power consumption accounting for load shedding.
        """
        avionics = self.base_avionics_kw
        oga = 20.0 if oga_active else 0.0
        wrs = 15.0 if wrs_active else 0.0
        hvac = hvac_power_kw
        science = self.science_lab_kw
        
        if self.load_shed_level == 1:
            science *= 0.3
        elif self.load_shed_level == 2:
            science = 0.0
            avionics *= 0.8
            wrs *= 0.5
        elif self.load_shed_level >= 3:
            science = 0.0
            avionics *= 0.6
            wrs = 0.0
            oga = min(oga, 10.0)
            
        total_kw = avionics + oga + wrs + hvac + science
        return {
            "total_consumption_kw": round(total_kw, 2),
            "avionics_kw": round(avionics, 2),
            "oga_kw": round(oga, 2),
            "wrs_kw": round(wrs, 2),
            "hvac_kw": round(hvac, 2),
            "science_kw": round(science, 2),
            "load_shed_level": self.load_shed_level
        }
        
    def step(self, hours: float, solar_irradiance: float, dust_factor: float,
             oga_active: bool, wrs_active: bool, hvac_power_kw: float) -> Dict[str, Any]:
        """
        Executes one simulation step for the power grid.
        """
        p_gen = self.calculate_generation(solar_irradiance, dust_factor)
        cons_dict = self.calculate_consumption(oga_active, wrs_active, hvac_power_kw)
        p_cons = cons_dict["total_consumption_kw"]
        
        # Backup generator dispatch
        p_backup = 0.0
        if self.backup_generator_active:
            p_backup = self.backup_power_output_kw
            
        # Power delta
        net_power_kw = (p_gen + p_backup) - p_cons
        
        # Energy exchange with battery bank
        if net_power_kw > 0:
            # Charging battery with efficiency
            charge_energy = net_power_kw * hours * self.battery_efficiency
            self.battery_level_kwh = min(self.battery_capacity_kwh, self.battery_level_kwh + charge_energy)
        else:
            # Discharging battery to cover deficit
            deficit_energy = abs(net_power_kw) * hours
            self.battery_level_kwh = max(0.0, self.battery_level_kwh - deficit_energy)
            
        return {
            "power_generation_kw": p_gen,
            "power_consumption_kw": p_cons,
            "backup_power_kw": p_backup,
            "net_power_kw": round(net_power_kw, 2),
            "battery_level_kwh": round(self.battery_level_kwh, 2),
            "battery_pct": round(self.battery_pct, 2),
            "load_shed_level": self.load_shed_level,
            "backup_active": self.backup_generator_active,
            "solar_failure_pct": self.solar_failure_pct,
            "details": cons_dict
        }
        
    def set_load_shed(self, level: int) -> None:
        self.load_shed_level = max(0, min(3, level))
        
    def toggle_backup_generator(self, enable: bool) -> None:
        self.backup_generator_active = enable
        
    def inject_solar_failure(self, failure_pct: float) -> None:
        self.solar_failure_pct = max(0.0, min(1.0, failure_pct))
        
    def clear_faults(self) -> None:
        self.solar_failure_pct = 0.0
        self.battery_fault = False

