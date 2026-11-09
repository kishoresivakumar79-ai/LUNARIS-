"""
Unit Tests for Power Management System & Controller
"""

import pytest
from simulation.power_simulation import PowerSystem
from control_system.power_controller import PowerController

def test_power_generation():
    ps = PowerSystem(battery_capacity_kwh=500.0, initial_battery_kwh=300.0)
    # Zero irradiance (lunar night)
    gen_night = ps.calculate_generation(solar_irradiance=0.0, dust_factor=0.02)
    assert gen_night == 0.0
    
    # Peak solar irradiance (1361 W/m^2)
    gen_peak = ps.calculate_generation(solar_irradiance=1361.0, dust_factor=0.0)
    assert gen_peak > 100.0

def test_battery_bounds():
    ps = PowerSystem(battery_capacity_kwh=500.0, initial_battery_kwh=490.0)
    # Excessive surplus should clamp at capacity
    step_out = ps.step(
        hours=5.0, solar_irradiance=1361.0, dust_factor=0.0,
        oga_active=False, wrs_active=False, hvac_power_kw=5.0
    )
    assert step_out["battery_level_kwh"] <= 500.0
    
    # Complete deficit should clamp at 0
    ps_empty = PowerSystem(battery_capacity_kwh=500.0, initial_battery_kwh=10.0)
    step_empty = ps_empty.step(
        hours=10.0, solar_irradiance=0.0, dust_factor=0.0,
        oga_active=True, wrs_active=True, hvac_power_kw=35.0
    )
    assert step_empty["battery_level_kwh"] == 0.0

def test_load_shedding():
    ps = PowerSystem()
    full_cons = ps.calculate_consumption(oga_active=True, wrs_active=True, hvac_power_kw=10.0)["total_consumption_kw"]
    
    ps.set_load_shed(1)
    cons_shed1 = ps.calculate_consumption(oga_active=True, wrs_active=True, hvac_power_kw=10.0)["total_consumption_kw"]
    assert cons_shed1 < full_cons
    
    ps.set_load_shed(3)
    cons_shed3 = ps.calculate_consumption(oga_active=True, wrs_active=True, hvac_power_kw=10.0)["total_consumption_kw"]
    assert cons_shed3 < cons_shed1

def test_power_controller_decision():
    controller = PowerController(battery_critical_pct=25.0, battery_warning_pct=45.0)
    
    # Critical battery state should mandate level 3 shedding and backup power
    decision = controller.evaluate({
        "battery_pct": 18.0,
        "net_power_kw": -20.0,
        "load_shed_level": 0,
        "backup_active": False
    })
    assert decision["target_load_shed"] == 3
    assert decision["target_backup_generator"] is True

