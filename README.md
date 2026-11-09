# 🌕 LUNARIS: Virtual Moon Base Management System
### AI + Digital Twin + 3D Simulation • Advanced Python Project

<p align="center">
  <img src="dashboard/assets/images/project_identity.jpg" width="45%" alt="LUNARIS Mission Identity" style="border-radius: 10px; margin-right: 10px;"/>
  <img src="dashboard/assets/images/hero_moonbase.jpg" width="45%" alt="Virtual Moon Base Overview" style="border-radius: 10px;"/>
</p>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24%2B-FF4B4B.svg)](https://streamlit.io/)
[![Three.js](https://img.shields.io/badge/Three.js-r128%2Fr160-black.svg)](https://threejs.org/)
[![Demo Video](https://img.shields.io/badge/Demo%20Video-LUNARIS.mp4-red.svg)](dashboard/assets/Videos/LUNARIS%20.mp4)
[![Tests Passing](https://img.shields.io/badge/Tests-14%2F14%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 1. Project Overview

**LUNARIS** is an advanced software simulation platform that models and intelligently manages a virtual human research base situated on the Moon (Shackleton Crater rim, Lunar South Pole).

Astronauts living in a lunar habitat face extreme environmental challenges:
- No breathable atmosphere or ambient pressure.
- Extreme temperature swings between **$-130^\circ\text{C}$** (lunar night) and **$+120^\circ\text{C}$** (lunar day).
- Zero naturally available liquid surface water.
- Strictly limited energy reserves and solar exposure cycles.
- Dangerous space radiation and micrometeorite threats.
- Communication latency with Earth ground stations.

LUNARIS addresses these challenges by continuously monitoring life-support resources, predicting future shortages using **Machine Learning**, automatically mitigating emergencies via a **closed-loop Decision Engine**, and synchronizing states in real-time with an **interactive 3D WebGL Digital Twin**.

---

## 🎥 2. Project Video Demonstration

Watch the complete operational video walkthrough of the **LUNARIS Virtual Moon Base Management System** below. It demonstrates the multi-physics simulation engine, real-time AI predictive models, automated closed-loop emergency mitigation, and the interactive 3D WebGL Digital Twin:

<div align="center">
  <video width="85%" controls poster="dashboard/assets/images/hero_moonbase.jpg" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.7); max-width: 900px;">
    <source src="dashboard/assets/Videos/LUNARIS%20.mp4" type="video/mp4">
    <source src="dashboard/assets/Videos/LUNARIS.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <br/><br/>
  <p>
    🎬 <b>Direct Video Link:</b> <a href="dashboard/assets/Videos/LUNARIS%20.mp4">▶ Play / Download LUNARIS Demo Video (LUNARIS .mp4)</a> &nbsp;|&nbsp; <a href="dashboard/assets/Videos/LUNARIS.mp4">Alternate Link (LUNARIS.mp4)</a>
  </p>
</div>

> [!TIP]
> **Integrated Mission Control Video Player:** You can also watch this video directly inside the Streamlit Mission Control Center under the **"🎥 Mission Video Demo"** tab (`streamlit run "d:\project folder\dashboard\app.py"`).

---

## 📸 3. Step-by-Step Visual Tour & Screenshots

Here is the complete step-by-step visual demonstration of the LUNARIS system, its subsystems, 3D Digital Twin, and mission control centers:

### Step 1: System Architecture & Adaptive Sensing
The system is constructed upon a 7-layer architecture connecting physical simulation dynamics, autonomous safety feedback loops, machine learning predictors, and real-time spatial digital twins.
<p align="center">
  <img src="dashboard/assets/images/system_architecture.jpg" width="85%" alt="System Architecture & Adaptive Sensing" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);"/>
</p>

---

### Step 2: 3D Moon Base & Digital Twin Design
An interactive 3D WebGL Three.js viewport renders the lunar terrain, geodesic habitat dome, dual photovoltaic tracking arrays, subsurface battery vault, oxygen cryo-tanks, water recovery plant, Earth communications dish, and an autonomous 6-wheeled rover.
<p align="center">
  <img src="dashboard/assets/images/lunar_base_3d.jpg" width="48%" alt="Lunar Base Alfa 3D Model" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/moonbase_3d_design.jpg" width="48%" alt="Artemis Moon Base Process" style="border-radius: 8px;"/>
</p>

---

### Step 3: Mission Control Center & Orbital Command UI
The primary mission dashboard provides real-time glassmorphism KPI telemetry gauges, crew health monitoring, active alarm banners, and simulation controls (Start, Pause, Step, Reset).
<p align="center">
  <img src="dashboard/assets/images/mission_control_ui.jpg" width="48%" alt="Mission Control UI" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/command_cards.jpg" width="48%" alt="Orbital Command Cards Design" style="border-radius: 8px;"/>
</p>

---

### Step 4: Module 1 – Power Management System (Solar Microgrid)
Monitors solar generation from dual $300\text{ m}^2$ photovoltaic arrays, tracks the 500 kWh lithium-sulfur battery state-of-charge, manages progressive load shedding (Levels 0 to 3), and dispatches the 40 kW auxiliary hydrogen fuel cell.
<p align="center">
  <img src="dashboard/assets/images/power_management.jpg" width="85%" alt="Power Management Microgrid" style="border-radius: 8px;"/>
</p>

---

### Step 5: Module 2 – Oxygen Generation & Atmospheric Control (OGA)
Calculates crew respiration consumption ($3.36\text{ kg O}_2/\text{day}$ for 4 astronauts), monitors Oxygen Generation Assembly (OGA) electrolysis ($8.0\text{ kg/day}$ capacity), tracks cryogenic reserves, and controls emergency bulkhead isolation during depressurization.
<p align="center">
  <img src="dashboard/assets/images/oxygen_management.jpg" width="48%" alt="Oxygen Management System" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/oxygen_production.jpg" width="48%" alt="Lunar Oxygen Extraction" style="border-radius: 8px;"/>
</p>

---

### Step 6: Module 3 – Water Management & Closed-Loop Recycling (WRS)
Simulates graywater and urine distillation via the Water Recovery System (WRS) at 90% recovery efficiency, tracks the 1000 L fresh water reservoir, and automates water rationing protocols during pump anomalies.
<p align="center">
  <img src="dashboard/assets/images/water_management.jpg" width="48%" alt="Water Management System" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/water_prediction_ai.jpg" width="48%" alt="AI Water Shortage Prediction" style="border-radius: 8px;"/>
</p>

---

### Step 7: Module 4 – Temperature & Active PID Thermal Regulation
Maintains habitat internal temperature at $21.0^\circ\text{C}$ despite external lunar extremes ($-130^\circ\text{C}$ to $+120^\circ\text{C}$) using multi-layer insulation (MLI) and an active PID HVAC controller commanding resistive heaters and fluid loop radiators.
<p align="center">
  <img src="dashboard/assets/images/temperature_management.jpg" width="85%" alt="Temperature Management System" style="border-radius: 8px;"/>
</p>

---

### Step 8: Module 5 – Resource & Parts Inventory Logistics
Tracks food rations, medical kits, fuel cell reactants, filters, and EVA suit batteries. Accounts for hydroponic greenhouse biomass yield ($+0.6\text{ kg/day}$) and computes depletion days remaining ($T = Q/R$).
<p align="center">
  <img src="dashboard/assets/images/resource_management.jpg" width="85%" alt="Resource & Parts Inventory" style="border-radius: 8px;"/>
</p>

---

### Step 9: Module 6 – Emergency Detection & Autonomous Control
Scans real-time telemetry to classify base operational health into `NORMAL`, `WARNING`, and `CRITICAL`. Features interactive scenario injection (Solar Failure, Oxygen Leak, Water Pump Jam, Insulation Breach) with automated closed-loop safety responses.
<p align="center">
  <img src="dashboard/assets/images/emergency_management.jpg" width="48%" alt="Emergency Detection System" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/autonomous_operations.jpg" width="48%" alt="Autonomous Operations & Control" style="border-radius: 8px;"/>
</p>

---

### Step 10: Artificial Intelligence & Predictive Maintenance Platform
Integrates 5 machine learning models: Gradient Boosting for power forecasting, Random Forest for oxygen depletion curves, Ridge Regression for 7-day water reserves, Isolation Forest for unsupervised outlier anomaly detection, and Random Forest Classifier for Remaining Useful Life (RUL) estimation.
<p align="center">
  <img src="dashboard/assets/images/ai_platform.jpg" width="48%" alt="Aerospace AI Platform" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/digital_twin.jpg" width="48%" alt="Digital Twin Platform" style="border-radius: 8px;"/>
</p>

---

### Step 11: 30-Day Simulated Lunar Mission Scenarios
Simulates realistic 30-day lunar surface missions modeled after NASA Artemis Base Camp and international lunar outpost architectures.
<p align="center">
  <img src="dashboard/assets/images/artemis_basecamp.jpg" width="48%" alt="Artemis Lunar Base Camp" style="border-radius: 8px;"/>
  <img src="dashboard/assets/images/nasa_moon_base.jpg" width="48%" alt="NASA Moon Base 2030" style="border-radius: 8px;"/>
</p>

---

## 🏛 4. Complete 7-Layer Architecture

```mermaid
flowchart TD
    subgraph L1["Layer 1: Virtual Lunar Environment"]
        ENV["LunarEnvironment (Solar Irradiance, Diurnal Temp -130°C to +120°C, Regolith Dust, Cosmic Radiation)"]
        CREW["CrewManager (4 Astronauts: Respiration, Water, Food, Metabolic Heat)"]
    end

    subgraph L2["Layer 2: Multi-Physics Simulation Engine"]
        PWR["PowerSystem (Solar Generation, 500 kWh Li-S Battery, Backup Fuel Cell)"]
        O2["OxygenSystem (OGA Electrolysis, Cryo Storage, Cabin Pressure, Hull Leakage)"]
        H2O["WaterSystem (WRS Reclamation, Hygiene, Drinking, Electrolysis Feed)"]
        THERM["TemperatureSystem (Thermal Mass, MLI Blankets, PID Active HVAC)"]
        RES["ResourceSystem (Food Rations, Greenhouse Hydroponics, Reactants)"]
        EQ["EquipmentManager (10 Subsystems, Wear & Tear, Health Index)"]
    end

    subgraph L3["Layer 3: Data Storage & History"]
        DB[("SQLite database/moon_base.db\n• telemetry_history\n• equipment_status\n• incidents_log\n• inventory")]
    end

    subgraph L4["Layer 4: AI Predictive Engine"]
        A_PWR["PowerPredictor (Gradient Boosting / Random Forest)"]
        A_O2["OxygenPredictor (Random Forest Regressor)"]
        A_H2O["WaterPredictor (Ridge Linear Regression)"]
        A_ANOM["AnomalyDetector (Isolation Forest Unsupervised Outlier Detection)"]
        A_FAIL["FailurePredictor (Random Forest Risk & Remaining Useful Life)"]
    end

    subgraph L5["Layer 5: Decision & Control Engine"]
        DEC["DecisionEngine (Central Arbiter)"]
        C_PWR["PowerController (Load Shedding 0-3, Backup Dispatch)"]
        C_O2["OxygenController (Bulkhead Seal, Cryo Reserve)"]
        C_H2O["WaterController (Water Rationing, WRS Loop)"]
        C_EMERG["EmergencyController (NORMAL, WARNING, CRITICAL)"]
    end

    subgraph L6["Layer 6: Digital Twin Engine"]
        TWIN["DigitalTwinEngine (Entity Graph: Habitat, Solar Arrays, Vault, OGA, WRS, Rover)"]
        STATE["StateManager (Snapshots & Rolling Buffers)"]
        SYNC["SynchronizationService (Bi-directional Telemetry Mapping)"]
    end

    subgraph L7["Layer 7: Visualization & Control Interfaces"]
        API["FastAPI REST & WebSocket Backend (:8000)"]
        DASH["Streamlit Mission Control Dashboard (:8501)"]
        WEB3D["Three.js WebGL Interactive 3D Digital Twin Viewport"]
    end

    L1 --> L2
    L2 --> L3
    L2 --> L4
    L2 --> L5
    L4 --> L5
    L5 -->|Actuation Commands| L2
    L2 --> L6
    L6 --> L7
    API <--> DASH
    API <--> WEB3D
```

---

## 📐 5. Mathematical Models

### 1. Power Balance
$$P_{\text{next}} = \min\left(P_{\text{cap}}, \max\left(0, P_{\text{current}} + \left[P_{\text{gen}}(t) + P_{\text{backup}}(t) - P_{\text{cons}}(t)\right] \cdot \Delta t \cdot \eta_{\text{batt}}\right)\right)$$

### 2. Oxygen Mass Balance & Pressure
$$O_{\text{next}} = \max\left(0, \min\left(O_{\text{cap}}, O_{\text{current}} + \left[O_{\text{prod}} - O_{\text{cons}} - O_{\text{leaked}}\right] \cdot \Delta t + O_{\text{emergency}}\right)\right)$$

### 3. Water Mass Balance
$$W_{\text{next}} = \max\left(0, \min\left(W_{\text{cap}}, W_{\text{current}} + \left[W_{\text{recycled}} - W_{\text{used}} - W_{\text{lost}}\right] \cdot \Delta t\right)\right)$$

### 4. Inventory Depletion Horizon
$$T_{\text{remaining}} = \frac{Q_{\text{available}}}{\dot{R}_{\text{burn}}}$$

### 5. PID Thermal Regulator
$$u(t) = K_p \, e(t) + K_i \int_0^t e(\tau)\,d\tau + K_d \, \frac{de(t)}{dt}$$
- $K_p = 3.0$, $K_i = 0.2$ (with anti-windup clamp), $K_d = 1.5$. Target setpoint: $21.0^\circ\text{C}$.

---

## 📁 6. Project Directory Structure

```
Virtual_Moon_Base_Management_System/
│
├── README.md                           <- Comprehensive project documentation
├── requirements.txt                    <- Python dependencies
├── .env.example                        <- Configuration template
│
├── backend/
│   ├── main.py                         <- FastAPI server, WebSockets, static hosting
│   ├── api/
│   │   ├── power_api.py                <- Power status, load shedding, forecasts
│   │   ├── oxygen_api.py               <- OGA, reserve valve, bulkhead isolation
│   │   ├── water_api.py                <- WRS, rationing controls
│   │   ├── temperature_api.py          <- PID thermal setpoint controls
│   │   └── emergency_api.py            <- Fault scenario injection & incident logs
│   └── services/
│       ├── simulation_service.py       <- Multi-physics simulation orchestrator
│       └── digital_twin_service.py     <- Digital twin entity query service
│
├── simulation/
│   ├── environment.py                  <- Lunar day/night, solar irradiance, radiation
│   ├── astronaut.py                    <- Crew metabolism, respiration, water, food
│   ├── power_simulation.py             <- Solar generation, 500 kWh battery, fuel cell
│   ├── oxygen_simulation.py            <- OGA electrolysis, cryo tanks, pressure
│   ├── water_simulation.py             <- WRS recycling, hygiene, electrolysis feed
│   ├── temperature_simulation.py       <- Thermal mass, MLI blankets, PID HVAC
│   ├── resource_simulation.py          <- Food rations, greenhouse yield, reactants
│   └── equipment_simulation.py         <- 10 subsystems wear & tear, health index
│
├── ai_engine/
│   ├── power_prediction.py             <- Gradient Boosting power demand model
│   ├── oxygen_prediction.py            <- Random Forest oxygen depletion model
│   ├── water_prediction.py             <- Ridge Regression water forecast model
│   ├── anomaly_detection.py            <- Isolation Forest unsupervised outlier model
│   └── failure_prediction.py           <- Random Forest failure risk & RUL model
│
├── digital_twin/
│   ├── twin_engine.py                  <- Entity graph (Habitat, Solar, Vault, OGA, WRS)
│   ├── state_manager.py                <- Rolling buffer & state snapshot engine
│   └── synchronization.py              <- Telemetry-to-Twin synchronization service
│
├── control_system/
│   ├── decision_engine.py              <- Central closed-loop autonomous arbiter
│   ├── power_controller.py             <- Automated load shedding & backup dispatch
│   ├── oxygen_controller.py            <- Bulkhead seal & emergency reserve deploy
│   ├── water_controller.py             <- Water conservation & rationing controller
│   └── emergency_controller.py         <- NORMAL/WARNING/CRITICAL classifier
│
├── dashboard/
│   ├── app.py                          <- Streamlit Mission Control app
│   ├── assets/
│   │   ├── images/                     <- 22 visual screenshots and concept illustrations
│   │   └── Videos/                     <- LUNARIS .mp4 full system walkthrough video
│   ├── pages/
│   │   ├── overview.py                 <- Sol clock, 3D viewport, video player, gauges
│   │   ├── power.py                    <- Solar vs consumption, load shedding
│   │   ├── oxygen.py                   <- OGA electrolyzer, pressure, emergency valve
│   │   ├── water.py                    <- Fresh water, WRS recycling, rationing
│   │   ├── temperature.py              <- Thermal gradient, PID setpoint control
│   │   ├── resources.py                <- Consumables ledger, cargo resupply
│   │   ├── ai_predictions.py           <- 7-day forecasts, anomaly gauge, risk table
│   │   └── emergency.py                <- 4 scenario injectors, automated action log
│   └── components/
│       ├── ui_widgets.py               <- Glassmorphism theme, Plotly charts, 3D iframe
│       └── sim_bridge.py               <- Resilient bridge (direct in-process + API)
│
├── frontend_3d/
│   ├── index.html                      <- Standalone 3D mission control HTML HUD
│   ├── package.json                    <- Three.js module configuration
│   └── src/
│       ├── main.js                     <- Three.js scene, camera, lights, render loop
│       ├── moon_base.js                <- Terrain, stars, Earth, battery vault, OGA/WRS
│       ├── habitat.js                  <- Geodesic habitat & greenhouse domes
│       ├── solar_panels.js             <- Dual photovoltaic arrays & tracking
│       ├── rover.js                    <- 6-wheel rover & patrol animation
│       └── api_connection.js           <- WebSocket & REST telemetry connector
│
├── database/
│   ├── database.py                     <- SQLite helper functions & seeding
│   ├── schema.sql                      <- Telemetry, equipment, incidents, inventory
│   └── moon_base.db                    <- Seeded SQLite database
│
├── data/
│   ├── generate_datasets.py            <- Synthetic 30-day mission dataset generator
│   ├── simulated_power.csv             <- 720 hours solar & battery telemetry
│   ├── simulated_oxygen.csv            <- 720 hours OGA, pressure, & leak telemetry
│   ├── simulated_water.csv             <- 720 hours WRS recycling telemetry
│   └── simulated_temperature.csv       <- 720 hours internal & external temperatures
│
├── models/
│   ├── power_model.pkl                 <- Trained power regression model
│   ├── oxygen_model.pkl                <- Trained oxygen regression model
│   ├── water_model.pkl                 <- Trained water regression model
│   ├── anomaly_model.pkl               <- Trained Isolation Forest model
│   └── failure_model.pkl               <- Trained failure classification model
│
├── tests/
│   ├── conftest.py                     <- Universal test path configuration
│   ├── test_power.py                   <- Power balance & load shedding tests
│   ├── test_oxygen.py                  <- OGA production & leak tests
│   ├── test_water.py                   <- WRS recycling & rationing tests
│   └── test_emergency.py               <- Emergency classification & scenario tests
│
└── docs/
    ├── architecture.md                 <- 7-layer architecture & data flow diagrams
    ├── algorithms.md                   <- Mathematical formulas & PID tuning
    └── project_report.md               <- 30-day mission report & scenario analysis
```

---

## ⚡ 7. Quickstart Guide

### 1. Launch the Streamlit Mission Control Dashboard
In your terminal, navigate to the project directory or run directly:
```cmd
streamlit run "d:\project folder\dashboard\app.py"
```
Open **`http://localhost:8501`** in your browser.
*(The dashboard runs in **Direct In-Process Mode** with zero crashes, even if FastAPI is not started!)*

### 2. Optional: Launch the FastAPI Backend & WebSockets
In a separate terminal:
```cmd
cd /d "d:\project folder"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **3D Digital Twin Viewport:** `http://127.0.0.1:8000/3d/`

### 3. Run the Automated Test Suite
```cmd
python -m pytest "d:\project folder\tests" -v
```
**Verification Result:** All 14 unit tests pass with 100% success rate:
```
test_emergency.py::test_emergency_classification PASSED                  [  7%]
test_emergency.py::test_simulation_service_scenarios PASSED              [ 14%]
test_oxygen.py::test_oxygen_mass_balance PASSED                          [ 21%]
test_oxygen.py::test_oxygen_leak_and_depressurization PASSED             [ 28%]
test_oxygen.py::test_emergency_reserve_deployment PASSED                 [ 35%]
test_oxygen.py::test_oxygen_controller_rules PASSED                      [ 42%]
test_power.py::test_power_generation PASSED                              [ 50%]
test_power.py::test_battery_bounds PASSED                                [ 57%]
test_power.py::test_load_shedding PASSED                                 [ 64%]
test_power.py::test_power_controller_decision PASSED                     [ 71%]
test_water.py::test_water_balance PASSED                                 [ 78%]
test_water.py::test_water_rationing PASSED                               [ 85%]
test_water.py::test_water_pump_failure PASSED                            [ 92%]
test_water.py::test_water_controller_rules PASSED                        [100%]
============================= 14 passed in 3.65s ==============================
```

---

## 📜 8. License
Distributed under the MIT License. Developed for advanced aerospace software simulation, AI systems engineering, and digital twin research.
