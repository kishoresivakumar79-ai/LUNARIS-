"""
LUNARIS Simulation: Lunar Environment Model
Simulates the harsh lunar surface conditions including solar cycle, external temperature extremes,
solar irradiance, cosmic radiation, and micrometeorite risks.
"""

import math
from typing import Dict, Any

class LunarEnvironment:
    """
    Simulates external physical conditions at the Lunar Base site (e.g., Shackleton Crater rim / South Pole).
    The lunar synodic day is ~29.53 Earth days (708.7 hours).
    Near lunar south pole, elevated rims have extended sun visibility periods ("peaks of eternal light"),
    punctuated by brief shadow occultations.
    """
    
    SOLAR_CONSTANT = 1361.0  # W/m^2 solar constant in cislunar space
    LUNAR_DAY_HOURS = 708.7  # Full lunar rotation period in Earth hours
    
    def __init__(self, latitude_deg: float = -89.9, elevation_factor: float = 0.95):
        self.latitude_deg = latitude_deg
        self.elevation_factor = elevation_factor
        self.dust_accumulation: float = 0.02  # 2% initial dust cover on solar panels
        self.solar_flare_active: bool = False
        self.micrometeorite_risk: str = "LOW"  # LOW, MODERATE, HIGH
        self.cosmic_radiation_mSv_hr: float = 0.06  # Deep space background radiation
        
    def calculate_conditions(self, mission_day: float) -> Dict[str, Any]:
        """
        Calculate environmental parameters for a given mission day (float, e.g. 1.5).
        """
        # Solar phase angle in radians over the lunar synodic month (29.53 days)
        lunar_phase = (mission_day % 29.53) / 29.53 * 2.0 * math.pi
        
        # Sun elevation angle relative to local horizon at polar plateau
        # Polar sun grazes the horizon between -1.5 deg and +1.5 deg, plus topography boost
        solar_elevation_deg = math.sin(lunar_phase) * 1.5 + (self.elevation_factor * 2.0)
        
        # Solar irradiance (W/m^2)
        if solar_elevation_deg > 0:
            irradiance_factor = math.sin(math.radians(max(0.5, solar_elevation_deg)))
            # Account for high-efficiency polar direct line-of-sight
            irradiance_factor = min(1.0, irradiance_factor * 35.0)  # Polar rim refraction/direct exposure
            solar_irradiance = self.SOLAR_CONSTANT * irradiance_factor
        else:
            solar_irradiance = 0.0
            
        # External surface temperature (Kelvin / Celsius)
        # Moon day: up to +120 C; Moon night: down to -130 C (permanently shadowed craters -240 C)
        if solar_irradiance > 50.0:
            sun_intensity = solar_irradiance / self.SOLAR_CONSTANT
            temp_external = -20.0 + (sun_intensity * 140.0)  # -20 C to +120 C
        else:
            temp_external = -130.0  # Deep lunar night
            
        # Dust accumulation increases very slowly over time (lunar electrostatic regolith)
        self.dust_accumulation = min(0.35, 0.02 + (mission_day * 0.001))
        
        # Space weather variation
        radiation = self.cosmic_radiation_mSv_hr
        if self.solar_flare_active:
            radiation *= 15.0
            
        return {
            "mission_day": mission_day,
            "solar_elevation_deg": round(solar_elevation_deg, 2),
            "solar_irradiance": round(solar_irradiance, 2),
            "temp_external": round(temp_external, 2),
            "dust_factor": round(self.dust_accumulation, 4),
            "radiation_mSv_hr": round(radiation, 3),
            "solar_flare": self.solar_flare_active,
            "micrometeorite_risk": self.micrometeorite_risk
        }
        
    def trigger_solar_flare(self, active: bool = True) -> None:
        self.solar_flare_active = active
        
    def clean_solar_arrays(self) -> None:
        """Electrostatic dust mitigation or EVA wiper maintenance"""
        self.dust_accumulation = 0.01

