"""
LUNARIS Backend: Simulation Core Service
Orchestrates the entire multi-physics lunar base simulation, autonomous control loop,
AI inference, and digital twin state updates.
"""

import threading
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from simulation.environment import LunarEnvironment
from simulation.astronaut import CrewManager
from simulation.power_simulation import PowerSystem
from simulation.oxygen_simulation import OxygenSystem
from simulation.water_simulation import WaterSystem
from simulation.temperature_simulation import TemperatureSystem
from simulation.resource_simulation import ResourceSystem
from simulation.equipment_simulation import EquipmentManager

from control_system.decision_engine import DecisionEngine
from digital_twin.synchronization import SynchronizationService
from database.database import log_incident, reset_simulation_data

from ai_engine.power_prediction import PowerPredictor
from ai_engine.oxygen_prediction import OxygenPredictor
from ai_engine.water_prediction import WaterPredictor
from ai_engine.anomaly_detection import AnomalyDetector
from ai_engine.failure_prediction import FailurePredictor

class SimulationService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulationService, cls).__new__(cls)
                cls._instance._init_simulation()
            return cls._instance

    def _init_simulation(self):
        self.mission_day = 1.0
        self.step_hours = 1.0
        self.is_running = False
        self.speed_multiplier = 1.0
        
        # Subsystems
        self.env = LunarEnvironment()
        self.crew = CrewManager(count=4)
        self.power = PowerSystem(battery_capacity_kwh=500.0, initial_battery_kwh=325.0)
        self.oxygen = OxygenSystem(tank_capacity_kg=200.0, initial_oxygen_kg=100.0)
        self.water = WaterSystem(tank_capacity_l=1000.0, initial_water_l=500.0)
        self.temp = TemperatureSystem(initial_temp=21.5, target_temp=21.0)
        self.resources = ResourceSystem(initial_food_kg=120.0, greenhouse_active=True)
        self.equipment = EquipmentManager()
        
        # Control & Twin
        self.decision_engine = DecisionEngine()
        self.sync_service = SynchronizationService()
        
        # AI Engines
        self.ai_power = PowerPredictor()
        self.ai_oxygen = OxygenPredictor()
        self.ai_water = WaterPredictor()
        self.ai_anomaly = AnomalyDetector()
        self.ai_failure = FailurePredictor()
        
        # State tracking
        self.active_faults = []
        self.last_telemetry: Dict[str, Any] = {}
        self.recent_actions: List[str] = []
        self.latest_anomaly: Dict[str, Any] = {"is_anomaly": False, "anomaly_index": 0.05, "suspect_factors": []}
        
        # Background worker thread
        self._thread = None
        self._stop_event = threading.Event()
        
        # Initial step to populate baseline telemetry
        self.step(hours=0.0, persist_db=True)
        
    def start(self, speed_multiplier: float = 1.0) -> None:
        self.speed_multiplier = speed_multiplier
        if not self.is_running:
            self.is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            
    def pause(self) -> None:
        self.is_running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            
    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self.step(hours=self.step_hours, persist_db=True)
            sleep_duration = max(0.2, 1.0 / max(0.1, self.speed_multiplier))
            time.sleep(sleep_duration)
            
    def reset(self, crew_count: int = 4, initial_battery_pct: float = 65.0, initial_o2_kg: float = 100.0, initial_water_l: float = 500.0, initial_food_kg: float = 120.0) -> None:
        self.pause()
        reset_simulation_data()
        self.mission_day = 1.0
        self.active_faults.clear()
        self.recent_actions.clear()
        
        self.env = LunarEnvironment()
        self.crew = CrewManager(count=crew_count)
        self.power = PowerSystem(battery_capacity_kwh=500.0, initial_battery_kwh=(initial_battery_pct / 100.0) * 500.0)
        self.oxygen = OxygenSystem(tank_capacity_kg=200.0, initial_oxygen_kg=initial_o2_kg)
        self.water = WaterSystem(tank_capacity_l=1000.0, initial_water_l=initial_water_l)
        self.temp = TemperatureSystem(initial_temp=21.5, target_temp=21.0)
        self.resources = ResourceSystem(initial_food_kg=initial_food_kg, greenhouse_active=True)
        self.equipment = EquipmentManager()
        
        self.step(hours=0.0, persist_db=True)
        
    def step(self, hours: float = 1.0, persist_db: bool = True) -> Dict[str, Any]:
        """
        Advances the entire lunar base simulation by `hours` and performs closed-loop control.
        """
        if hours > 0:
            self.mission_day += (hours / 24.0)
            
        # 1. Environment conditions
        env_cond = self.env.calculate_conditions(self.mission_day)
        
        # 2. Crew demand
        crew_demand = self.crew.calculate_crew_demand(hours)
        
        # 3. Subsystem step executions
        # A. Temperature simulation
        temp_out = self.temp.step(
            hours=hours,
            temp_external=env_cond["temp_external"],
            crew_heat_w=crew_demand["metabolic_heat_w"],
            equipment_power_kw=self.power.base_avionics_kw
        )
        
        # B. Power simulation
        power_out = self.power.step(
            hours=hours,
            solar_irradiance=env_cond["solar_irradiance"],
            dust_factor=env_cond["dust_factor"],
            oga_active=self.oxygen.oga_active,
            wrs_active=self.water.wrs_active,
            hvac_power_kw=temp_out["hvac_power_kw"]
        )
        
        # C. Oxygen simulation
        o2_out = self.oxygen.step(
            hours=hours,
            crew_o2_consumed_kg=crew_demand["o2_demand_kg"]
        )
        
        # D. Water simulation
        water_out = self.water.step(
            hours=hours,
            crew_water_demand_l=crew_demand["water_demand_l"],
            oga_water_demand_l=o2_out["water_consumed_liters"]
        )
        
        # E. Resource inventory
        res_out = self.resources.step(
            hours=hours,
            crew_food_demand_kg=crew_demand["food_demand_kg"],
            backup_power_active=power_out["backup_active"]
        )
        
        # F. Equipment wear & tear
        self.equipment.step(
            hours=hours,
            temp_internal=temp_out["temp_internal"],
            temp_external=env_cond["temp_external"]
        )
        
        # Compile raw telemetry snapshot
        raw_telemetry = {
            "mission_day": round(self.mission_day, 2),
            "solar_irradiance": env_cond["solar_irradiance"],
            "temp_external": env_cond["temp_external"],
            "radiation_mSv_hr": env_cond["radiation_mSv_hr"],
            "power_generation": power_out["power_generation_kw"],
            "power_consumption": power_out["power_consumption_kw"],
            "battery_level": power_out["battery_level_kwh"],
            "battery_pct": power_out["battery_pct"],
            "backup_power": power_out["backup_power_kw"],
            "net_power": power_out["net_power_kw"],
            "oxygen_level": o2_out["oxygen_level_kg"],
            "oxygen_production": o2_out["oxygen_production_kg"],
            "oxygen_consumption": o2_out["oxygen_consumption_kg"],
            "oxygen_leakage": o2_out["oxygen_leakage_kg"],
            "cabin_pressure": o2_out["cabin_pressure_kpa"],
            "water_level": water_out["water_level_l"],
            "water_recycled": water_out["water_recycled_l"],
            "water_used": water_out["water_used_l"],
            "water_loss": water_out["water_loss_l"],
            "temp_internal": temp_out["temp_internal"],
            "target_temp": temp_out["target_temp"],
            "hvac_mode": temp_out["hvac_mode"],
            "hvac_power": temp_out["hvac_power_kw"],
            "food_level": res_out["food_level_kg"],
            "food_days_remaining": res_out["food_days_remaining"],
            "fuel_cell_reactants": res_out["fuel_cell_reactants_kg"],
            "active_faults": list(self.active_faults),
            "base_health_pct": self.equipment.get_base_health_pct()
        }
        
        # 4. Closed-loop autonomous control decision
        control_decision = self.decision_engine.evaluate_and_control(
            telemetry=raw_telemetry,
            power_sys=self.power,
            o2_sys=self.oxygen,
            water_sys=self.water,
            temp_sys=self.temp
        )
        
        raw_telemetry["base_status"] = control_decision["overall_status"]
        if control_decision["automated_actions"]:
            self.recent_actions.extend(control_decision["automated_actions"])
            self.recent_actions = self.recent_actions[-20:]  # Keep latest 20
            # Log critical incidents to DB
            for act in control_decision["automated_actions"]:
                log_incident(
                    subsystem="AutonomousControl",
                    severity="CRITICAL" if "CRITICAL" in act else "WARNING",
                    title="Automated Life-Support Mitigation",
                    description=act,
                    action_taken="System autonomous response executed",
                    mission_day=self.mission_day
                )
                
        # 5. AI Anomaly evaluation
        self.latest_anomaly = self.ai_anomaly.evaluate_telemetry(raw_telemetry)
        raw_telemetry["anomaly_detected"] = self.latest_anomaly["is_anomaly"]
        raw_telemetry["anomaly_score"] = self.latest_anomaly["anomaly_index"]
        
        self.last_telemetry = raw_telemetry
        
        # 6. Digital Twin synchronization
        composite = self.sync_service.synchronize(
            telemetry=raw_telemetry,
            equipment=self.equipment.get_all_components(),
            persist_db=persist_db
        )
        
        return composite
        
    def inject_scenario_fault(self, scenario: str) -> Dict[str, Any]:
        """
        Implements the 4 core simulation failure scenarios from the design specification:
        1. "SOLAR_POWER_FAILURE": Solar panel generation decreases by 70%.
        2. "OXYGEN_LEAKAGE": Habitat experiences simulated oxygen leak & pressure drop.
        3. "WATER_SHORTAGE": Water recycling unit becomes degraded.
        4. "TEMPERATURE_EMERGENCY": MLI insulation breach causes high heat loss.
        """
        scenario = scenario.upper()
        if scenario not in self.active_faults:
            self.active_faults.append(scenario)
            
        desc = ""
        if scenario == "SOLAR_POWER_FAILURE":
            self.power.inject_solar_failure(0.70)
            self.equipment.inject_fault("SOLAR_A", "Severe Photovoltaic Output Drop (70%)")
            desc = "Solar array output degraded by 70%. Battery reserve depletion imminent."
            log_incident("Power", "CRITICAL", "Solar Power Failure", desc, "Alert generated. Load shedding prepared.", self.mission_day)
            
        elif scenario == "OXYGEN_LEAKAGE":
            self.oxygen.inject_hull_puncture(leak_rate_kg_hr=1.8)
            self.equipment.inject_fault("HAB_SEAL", "Hull Seal Micro-Puncture Detected")
            desc = "Atmospheric breach detected. Cabin pressure and O2 falling."
            log_incident("Oxygen", "CRITICAL", "Airlock Hull Breach", desc, "Anomaly flagged. Emergency reserve primed.", self.mission_day)
            
        elif scenario == "WATER_SHORTAGE":
            self.water.inject_pump_failure(True)
            self.equipment.inject_fault("WRS_SYS", "Distillation Centrifuge Jam")
            desc = "WRS processor failure. Recycling efficiency dropped to 10%."
            log_incident("Water", "WARNING", "WRS Processor Degraded", desc, "Water conservation mode recommended.", self.mission_day)
            
        elif scenario == "TEMPERATURE_EMERGENCY":
            self.temp.inject_insulation_breach(True)
            self.equipment.inject_fault("ATCS_HVAC", "Thermal Insulation Breached")
            desc = "External insulation failure. Rapid conductive thermal loss to space."
            log_incident("Thermal", "CRITICAL", "Insulation Heat Loss Emergency", desc, "PID heaters maxed out.", self.mission_day)
            
        self.step(hours=0.0, persist_db=True)
        return {"scenario": scenario, "description": desc, "active_faults": self.active_faults}
        
    def resolve_fault(self, scenario: str) -> Dict[str, Any]:
        scenario = scenario.upper()
        if scenario in self.active_faults:
            self.active_faults.remove(scenario)
            
        if scenario == "SOLAR_POWER_FAILURE":
            self.power.clear_faults()
            self.equipment.repair_component("SOLAR_A")
        elif scenario == "OXYGEN_LEAKAGE":
            self.oxygen.clear_faults()
            self.equipment.repair_component("HAB_SEAL")
        elif scenario == "WATER_SHORTAGE":
            self.water.clear_faults()
            self.equipment.repair_component("WRS_SYS")
        elif scenario == "TEMPERATURE_EMERGENCY":
            self.temp.clear_faults()
            self.equipment.repair_component("ATCS_HVAC")
            
        self.step(hours=0.0, persist_db=True)
        return {"resolved": scenario, "active_faults": self.active_faults}

    def get_full_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "mission_day": round(self.mission_day, 2),
            "telemetry": self.last_telemetry,
            "crew": self.crew.get_crew_status(),
            "equipment": self.equipment.get_all_components(),
            "digital_twin": self.sync_service.get_digital_twin_state(),
            "active_faults": self.active_faults,
            "recent_actions": self.recent_actions,
            "anomaly": self.latest_anomaly
        }

