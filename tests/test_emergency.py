"""
Unit Tests for Emergency Detection, Scenario Injections, and Decision Engine
"""

import pytest
from control_system.emergency_controller import EmergencyController
from backend.services.simulation_service import SimulationService

def test_emergency_classification():
    ec = EmergencyController()
    
    # 1. Normal State
    res_normal = ec.evaluate({
        "oxygen_level": 100.0,
        "cabin_pressure": 101.3,
        "battery_pct": 75.0,
        "water_level": 500.0,
        "temp_internal": 21.5
    })
    assert res_normal["overall_status"] == "NORMAL"
    assert res_normal["emergency_count"] == 0
    
    # 2. Warning State (Low battery)
    res_warn = ec.evaluate({
        "oxygen_level": 100.0,
        "cabin_pressure": 101.3,
        "battery_pct": 28.0,
        "water_level": 500.0,
        "temp_internal": 21.5
    })
    assert res_warn["overall_status"] == "WARNING"
    
    # 3. Critical State (Low oxygen & depressurization)
    res_crit = ec.evaluate({
        "oxygen_level": 18.0,
        "cabin_pressure": 80.0,
        "battery_pct": 60.0,
        "water_level": 500.0,
        "temp_internal": 21.5
    })
    assert res_crit["overall_status"] == "CRITICAL"

def test_simulation_service_scenarios():
    sim = SimulationService()
    sim.reset()
    
    # Inject Solar Failure
    res1 = sim.inject_scenario_fault("SOLAR_POWER_FAILURE")
    assert "SOLAR_POWER_FAILURE" in sim.active_faults
    assert sim.power.solar_failure_pct == 0.70
    
    # Resolve Solar Failure
    sim.resolve_fault("SOLAR_POWER_FAILURE")
    assert "SOLAR_POWER_FAILURE" not in sim.active_faults
    assert sim.power.solar_failure_pct == 0.0
    
    # Inject O2 Leak
    sim.inject_scenario_fault("OXYGEN_LEAKAGE")
    assert "OXYGEN_LEAKAGE" in sim.active_faults
    assert sim.oxygen.active_leak_rate_kg_hr > 0.0
    
    # Clean up
    sim.resolve_fault("OXYGEN_LEAKAGE")
    assert "OXYGEN_LEAKAGE" not in sim.active_faults

