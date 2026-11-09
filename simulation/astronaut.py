"""
LUNARIS Simulation: Astronaut Crew Model
Simulates astronaut metabolism, activity profiles, oxygen/water/food consumption, and metabolic heat emissions.
"""

from typing import List, Dict, Any

class Astronaut:
    def __init__(self, name: str, role: str, base_metabolic_rate: float = 1.0):
        self.name = name
        self.role = role
        self.base_metabolic_rate = base_metabolic_rate
        self.activity_state = "RESEARCH"  # SLEEP, RESEARCH, EXERCISE, EVA
        self.heart_rate = 72
        self.stress_level = 0.15  # 0.0 to 1.0
        
    def set_activity(self, activity: str) -> None:
        valid_activities = ["SLEEP", "RESEARCH", "EXERCISE", "EVA"]
        if activity in valid_activities:
            self.activity_state = activity
            if activity == "SLEEP":
                self.heart_rate = 58
                self.stress_level = max(0.05, self.stress_level - 0.05)
            elif activity == "RESEARCH":
                self.heart_rate = 75
            elif activity == "EXERCISE":
                self.heart_rate = 135
                self.stress_level = max(0.1, self.stress_level - 0.02)
            elif activity == "EVA":
                self.heart_rate = 110
                self.stress_level = min(0.9, self.stress_level + 0.1)

class CrewManager:
    """
    Manages the lunar base astronaut complement and computes aggregated metabolic demands.
    NASA baseline standards:
    - O2 consumption: ~0.84 kg / person / day (nominal)
    - CO2 generation: ~1.00 kg / person / day
    - Drinking + Food water: ~4.0 L / person / day
    - Hygiene water: ~8.0 L / person / day
    - Food intake: ~1.5 - 2.0 kg / person / day
    - Metabolic heat: ~120 W / person nominal
    """
    def __init__(self, count: int = 4):
        self.astronauts: List[Astronaut] = []
        default_crew = [
            ("Commander Sarah Chen", "Commander"),
            ("Dr. Marcus Vance", "Flight Engineer & Systems"),
            ("Dr. Elena Rostova", "Life Support & Astrobiologist"),
            ("Taro Tanaka", "Geologist & EVA Specialist")
        ]
        for i in range(count):
            if i < len(default_crew):
                name, role = default_crew[i]
            else:
                name, role = f"Specialist-{i+1}", "Mission Specialist"
            self.astronauts.append(Astronaut(name, role))
            
    @property
    def crew_count(self) -> int:
        return len(self.astronauts)
        
    def calculate_crew_demand(self, hours: float = 1.0) -> Dict[str, float]:
        """
        Calculates aggregate resource consumption for the crew over given hours.
        """
        day_fraction = hours / 24.0
        total_o2_kg = 0.0
        total_water_l = 0.0
        total_food_kg = 0.0
        total_heat_w = 0.0
        total_co2_kg = 0.0
        
        for astro in self.astronauts:
            mult = 1.0
            if astro.activity_state == "SLEEP":
                mult = 0.75
            elif astro.activity_state == "EXERCISE":
                mult = 2.2
            elif astro.activity_state == "EVA":
                mult = 1.6
                
            # Base rates per day
            total_o2_kg += (0.84 * mult) * day_fraction
            total_co2_kg += (1.00 * mult) * day_fraction
            total_water_l += (12.0 * mult) * day_fraction  # Drinking + food prep + hygiene
            total_food_kg += (1.5 * mult) * day_fraction
            total_heat_w += (130.0 * mult)
            
        return {
            "crew_count": self.crew_count,
            "o2_demand_kg": round(total_o2_kg, 4),
            "co2_produced_kg": round(total_co2_kg, 4),
            "water_demand_l": round(total_water_l, 4),
            "food_demand_kg": round(total_food_kg, 4),
            "metabolic_heat_w": round(total_heat_w, 2)
        }
        
    def get_crew_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": a.name,
                "role": a.role,
                "activity": a.activity_state,
                "heart_rate": a.heart_rate,
                "stress_level": round(a.stress_level, 2)
            }
            for a in self.astronauts
        ]

