"""
LUNARIS Simulation: Water Management System
Simulates Water Recovery System (WRS), graywater/urine distillation, hygiene/drinking consumption,
electrolysis feed for OGA, and emergency reserves.
Mathematical formulation:
    W_next = W_current + W_recycled - W_used - W_lost
"""

from typing import Dict, Any

class WaterSystem:
    def __init__(self, tank_capacity_l: float = 1000.0, initial_water_l: float = 500.0):
        self.tank_capacity_l = tank_capacity_l
        self.water_level_l = min(tank_capacity_l, initial_water_l)
        self.emergency_reserve_l = 150.0
        
        # WRS operational parameters
        self.wrs_active = True
        self.nominal_recycle_rate_l_day = 45.0  # Up to 60 L/day
        self.recycling_efficiency = 0.90         # 90% closed loop recycling
        self.nominal_loss_l_day = 5.0            # Nominal brine residue & filtration loss
        
        # Operational mode: NORMAL vs RATION
        self.rationing_mode = False
        
        # Fault injection
        self.wrs_pump_fault = False
        self.pipe_leak_rate_l_hr = 0.0
        
    def step(self, hours: float, crew_water_demand_l: float, oga_water_demand_l: float) -> Dict[str, Any]:
        """
        Executes one step of the water balance simulation.
        """
        day_fraction = hours / 24.0
        
        # Usage
        crew_used = crew_water_demand_l * (0.65 if self.rationing_mode else 1.0)
        total_used = crew_used + oga_water_demand_l
        
        # Recycling recovery
        if self.wrs_active and not self.wrs_pump_fault:
            recycled = self.nominal_recycle_rate_l_day * day_fraction * self.recycling_efficiency
        elif self.wrs_pump_fault:
            # Severely degraded when pump is jammed
            recycled = self.nominal_recycle_rate_l_day * day_fraction * 0.10
        else:
            recycled = 0.0
            
        # Losses and leaks
        loss = (self.nominal_loss_l_day * day_fraction) + (self.pipe_leak_rate_l_hr * hours)
        
        # New level
        self.water_level_l = max(0.0, min(self.tank_capacity_l, self.water_level_l + recycled - total_used - loss))
        
        # Days remaining projection
        daily_net_burn = max(1.0, (total_used - recycled + loss) / max(0.01, day_fraction)) if day_fraction > 0 else 1.0
        days_remaining = self.water_level_l / daily_net_burn
        
        return {
            "water_level_l": round(self.water_level_l, 2),
            "water_recycled_l": round(recycled, 3),
            "water_used_l": round(total_used, 3),
            "water_loss_l": round(loss, 3),
            "emergency_reserve_l": self.emergency_reserve_l,
            "wrs_active": self.wrs_active and not self.wrs_pump_fault,
            "rationing_mode": self.rationing_mode,
            "wrs_pump_fault": self.wrs_pump_fault,
            "pipe_leak_active": (self.pipe_leak_rate_l_hr > 0.0),
            "days_remaining": round(days_remaining, 1)
        }
        
    def set_rationing(self, enable: bool) -> None:
        self.rationing_mode = enable
        
    def set_wrs(self, active: bool) -> None:
        self.wrs_active = active
        
    def inject_pump_failure(self, fault: bool = True) -> None:
        self.wrs_pump_fault = fault
        
    def inject_pipe_leak(self, leak_l_hr: float = 2.0) -> None:
        self.pipe_leak_rate_l_hr = leak_l_hr
        
    def clear_faults(self) -> None:
        self.wrs_pump_fault = False
        self.pipe_leak_rate_l_hr = 0.0
        self.rationing_mode = False

