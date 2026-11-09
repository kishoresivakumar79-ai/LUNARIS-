"""
LUNARIS Simulation: Resource & Inventory Management System
Tracks food supplies, hydroponic greenhouse yields, medical stocks, fuel cell reactants, and spare parts.
Mathematical formulation:
    Days Remaining = Available Quantity / Daily Burn Rate  (T = Q / R)
"""

from typing import Dict, Any, List

class ResourceSystem:
    def __init__(self, initial_food_kg: float = 120.0, greenhouse_active: bool = True):
        self.food_level_kg = initial_food_kg
        self.greenhouse_active = greenhouse_active
        self.greenhouse_daily_yield_kg = 0.6  # Fresh hydroponic microgreens / vegetables
        
        self.fuel_cell_reactants_kg = 200.0   # H2/O2 for backup power
        self.medical_supplies_units = 50.0
        self.spare_filters = 24
        self.eva_batteries = 12
        
    def step(self, hours: float, crew_food_demand_kg: float, backup_power_active: bool) -> Dict[str, Any]:
        """
        Executes one step of inventory consumption and greenhouse replenishment.
        """
        day_fraction = hours / 24.0
        
        # Greenhouse yield
        fresh_yield = (self.greenhouse_daily_yield_kg * day_fraction) if self.greenhouse_active else 0.0
        
        # Net food balance
        self.food_level_kg = max(0.0, self.food_level_kg + fresh_yield - crew_food_demand_kg)
        
        # Fuel cell burn if backup generator is active (approx 1.5 kg reactant per hour at 40 kW)
        if backup_power_active:
            self.fuel_cell_reactants_kg = max(0.0, self.fuel_cell_reactants_kg - (1.5 * hours))
            
        # Daily burn rates
        daily_food_burn = max(0.1, (crew_food_demand_kg - fresh_yield) / max(0.01, day_fraction)) if day_fraction > 0 else 4.0
        food_days_remaining = self.food_level_kg / daily_food_burn if daily_food_burn > 0 else 999.0
        
        fuel_days_remaining = (self.fuel_cell_reactants_kg / 36.0) if backup_power_active else 999.0
        
        return {
            "food_level_kg": round(self.food_level_kg, 2),
            "greenhouse_active": self.greenhouse_active,
            "greenhouse_yield_kg": round(fresh_yield, 3),
            "food_days_remaining": round(food_days_remaining, 1),
            "fuel_cell_reactants_kg": round(self.fuel_cell_reactants_kg, 2),
            "fuel_days_remaining": round(fuel_days_remaining, 1),
            "medical_supplies_units": self.medical_supplies_units,
            "spare_filters": self.spare_filters,
            "resupply_recommended": (food_days_remaining < 15.0 or self.fuel_cell_reactants_kg < 40.0)
        }
        
    def resupply(self, food_kg: float = 100.0, fuel_kg: float = 150.0) -> None:
        """Simulate cargo lander resupply mission docking"""
        self.food_level_kg += food_kg
        self.fuel_cell_reactants_kg += fuel_kg
        self.medical_supplies_units += 20.0
        self.spare_filters += 10

