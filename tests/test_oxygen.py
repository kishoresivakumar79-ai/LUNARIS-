"""
Unit Tests for Oxygen Management System & Controller
"""

import pytest
from simulation.oxygen_simulation import OxygenSystem
from control_system.oxygen_controller import OxygenController

def test_oxygen_mass_balance():
    ox = OxygenSystem(tank_capacity_kg=200.0, initial_oxygen_kg=100.0)
    ox.nominal_leak_kg_day = 0.0
    ox.oga_active = True
    ox.oga_nominal_production_kg_day = 8.0
    
    # 24 hours step: production = 8 kg, consumption = 6 kg, net = +2 kg
    out = ox.step(hours=24.0, crew_o2_consumed_kg=6.0)
    assert pytest.approx(out["oxygen_level_kg"], 0.1) == 102.0

def test_oxygen_leak_and_depressurization():
    ox = OxygenSystem(initial_oxygen_kg=100.0)
    ox.inject_hull_puncture(leak_rate_kg_hr=2.0)
    
    out = ox.step(hours=2.0, crew_o2_consumed_kg=0.2)
    assert out["leak_active"] is True
    assert out["cabin_pressure_kpa"] < 101.3
    
    # Isolate bulkhead
    ox.isolate_breach_section()
    out2 = ox.step(hours=1.0, crew_o2_consumed_kg=0.1)
    assert out2["leak_active"] is False

def test_emergency_reserve_deployment():
    ox = OxygenSystem(initial_oxygen_kg=20.0)
    ox.deploy_emergency_reserve(True)
    out = ox.step(hours=2.0, crew_o2_consumed_kg=0.2)
    assert out["emergency_reserve_kg"] < 50.0
    assert out["oxygen_level_kg"] > 20.0

def test_oxygen_controller_rules():
    controller = OxygenController(o2_critical_kg=25.0, pressure_critical_kpa=90.0)
    
    # Low pressure should trigger bulkhead isolation & emergency valve
    eval_res = controller.evaluate({
        "oxygen_level_kg": 80.0,
        "cabin_pressure_kpa": 82.0,
        "leak_active": True
    })
    assert eval_res["isolate_section"] is True
    assert eval_res["deploy_emergency_reserve"] is True

