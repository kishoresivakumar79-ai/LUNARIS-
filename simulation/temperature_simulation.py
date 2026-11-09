r"""
LUNARIS Simulation: Temperature Management System
Simulates habitat internal thermodynamics under extreme external lunar temperature fluctuations (-130°C to +120°C).
Regulates internal cabin temperature using a tuned Proportional-Integral-Derivative (PID) controller.
Mathematical formulation:
    Thermal mass: C_th * (dT_in / dt) = Q_crew + Q_equip - U*A*(T_in - T_ext) + Q_hvac
    PID Controller: u(t) = K_p * e(t) + K_i * \int e(t)dt + K_d * (de(t)/dt)
"""

from typing import Dict, Any

class PIDController:
    def __init__(self, kp: float = 2.5, ki: float = 0.15, kd: float = 1.2, output_limits: tuple = (-40.0, 40.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min, self.output_max = output_limits
        
        self.integral = 0.0
        self.prev_error = 0.0
        
    def reset(self) -> None:
        self.integral = 0.0
        self.prev_error = 0.0
        
    def compute(self, setpoint: float, current_val: float, dt_hours: float) -> float:
        error = setpoint - current_val
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup clamp
        self.integral += error * dt_hours
        self.integral = max(-50.0, min(50.0, self.integral))
        i_term = self.ki * self.integral
        
        # Derivative term
        d_term = self.kd * ((error - self.prev_error) / max(0.001, dt_hours))
        self.prev_error = error
        
        output = p_term + i_term + d_term
        return max(self.output_min, min(self.output_max, output))

class TemperatureSystem:
    def __init__(self, initial_temp: float = 21.5, target_temp: float = 21.0):
        self.temp_internal = initial_temp
        self.target_temp = target_temp
        
        # Thermal physical constants
        self.thermal_capacity_kwh_c = 15.0  # Heat capacity of habitat pressurized atmosphere + interior bulk
        self.insulation_ua = 0.18           # Overall heat transfer coefficient U*A (kW/°C)
        
        # PID Controller
        self.pid = PIDController(kp=3.0, ki=0.2, kd=1.5, output_limits=(-35.0, 35.0))
        
        # Modes & Status
        self.hvac_mode = "IDLE"  # HEATING, COOLING, IDLE
        self.hvac_power_kw = 5.0  # Standby baseline
        
        # Fault injection
        self.insulation_breach = False
        self.heater_fault = False
        self.radiator_blocked = False
        
    def step(self, hours: float, temp_external: float, crew_heat_w: float, equipment_power_kw: float) -> Dict[str, Any]:
        """
        Executes one thermodynamic step of the habitat.
        """
        effective_ua = self.insulation_ua * (3.0 if self.insulation_breach else 1.0)
        
        # Internal passive heat gains
        q_internal_kw = (crew_heat_w / 1000.0) + (equipment_power_kw * 0.40)  # ~40% of electrical power degrades to heat
        
        # Heat exchange with lunar exterior through multilayer insulation
        q_loss_to_space_kw = effective_ua * (self.temp_internal - temp_external)
        
        # PID HVAC control response
        # Positive u means habitat needs warmth; Negative u means habitat needs heat rejection
        pid_demand = self.pid.compute(self.target_temp, self.temp_internal, hours)
        
        q_hvac_kw = pid_demand
        
        # Apply faults if any
        if self.heater_fault and q_hvac_kw > 0:
            q_hvac_kw = 0.0  # Heaters offline
        if self.radiator_blocked and q_hvac_kw < 0:
            q_hvac_kw = 0.0  # Cannot reject heat
            
        # Determine HVAC operating mode and electrical power draw
        if q_hvac_kw > 1.0:
            self.hvac_mode = "HEATING"
            self.hvac_power_kw = 3.0 + abs(q_hvac_kw) * 0.95
        elif q_hvac_kw < -1.0:
            self.hvac_mode = "COOLING"
            # Heat pumps with COP ~ 2.5
            self.hvac_power_kw = 3.0 + (abs(q_hvac_kw) / 2.5)
        else:
            self.hvac_mode = "IDLE"
            self.hvac_power_kw = 3.0
            
        # Net thermal energy delta
        net_q_kw = q_internal_kw - q_loss_to_space_kw + q_hvac_kw
        temp_delta = (net_q_kw * hours) / self.thermal_capacity_kwh_c
        
        self.temp_internal = round(self.temp_internal + temp_delta, 2)
        
        # Status classification
        if self.temp_internal < 18.0:
            thermal_status = "COLD_WARNING"
        elif self.temp_internal > 25.0:
            thermal_status = "HOT_WARNING"
        elif self.temp_internal > 30.0 or self.temp_internal < 14.0:
            thermal_status = "CRITICAL"
        else:
            thermal_status = "NOMINAL"
            
        return {
            "temp_internal": self.temp_internal,
            "temp_external": temp_external,
            "target_temp": self.target_temp,
            "hvac_mode": self.hvac_mode,
            "hvac_power_kw": round(self.hvac_power_kw, 2),
            "pid_demand_kw": round(pid_demand, 2),
            "thermal_status": thermal_status,
            "insulation_breach": self.insulation_breach,
            "heater_fault": self.heater_fault,
            "radiator_blocked": self.radiator_blocked
        }
        
    def set_target_temperature(self, target: float) -> None:
        self.target_temp = max(16.0, min(28.0, target))
        
    def inject_insulation_breach(self, active: bool = True) -> None:
        self.insulation_breach = active
        
    def inject_heater_fault(self, active: bool = True) -> None:
        self.heater_fault = active
        
    def clear_faults(self) -> None:
        self.insulation_breach = False
        self.heater_fault = False
        self.radiator_blocked = False
        self.pid.reset()
