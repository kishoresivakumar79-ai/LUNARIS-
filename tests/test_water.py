"""
Unit Tests for Water Management System & Controller
"""

import pytest
from simulation.water_simulation import WaterSystem
from control_system.water_controller import WaterController

def test_water_balance():
    ws = WaterSystem(tank_capacity_l=1000.0, initial_water_l=500.0)
    ws.nominal_recycle_rate_l_day = 40.0
    ws.recycling_efficiency = 1.0
    ws.nominal_loss_l_day = 5.0
    
    # 24 hours: Recycled = 40 L, Used = 50 L, Loss = 5 L -> Net = -15 L
    out = ws.step(hours=24.0, crew_water_demand_l=40.0, oga_water_demand_l=10.0)
    assert pytest.approx(out["water_level_l"], 0.1) == 485.0

def test_water_rationing():
    ws = WaterSystem(initial_water_l=500.0)
    out_normal = ws.step(hours=24.0, crew_water_demand_l=48.0, oga_water_demand_l=0.0)
    
    ws_ration = WaterSystem(initial_water_l=500.0)
    ws_ration.set_rationing(True)
    out_ration = ws_ration.step(hours=24.0, crew_water_demand_l=48.0, oga_water_demand_l=0.0)
    
    # Under rationing, used water should be lower and remaining water higher
    assert out_ration["water_used_l"] < out_normal["water_used_l"]
    assert out_ration["water_level_l"] > out_normal["water_level_l"]

def test_water_pump_failure():
    ws = WaterSystem(initial_water_l=500.0)
    ws.inject_pump_failure(True)
    out = ws.step(hours=24.0, crew_water_demand_l=20.0, oga_water_demand_l=0.0)
    # Recycling should be heavily throttled
    assert out["water_recycled_l"] < 5.0

def test_water_controller_rules():
    controller = WaterController(water_warning_l=180.0, water_critical_l=90.0)
    
    # Warning water level triggers rationing
    eval_warn = controller.evaluate({
        "water_level_l": 150.0,
        "wrs_pump_fault": False
    })
    assert eval_warn["set_rationing"] is True

