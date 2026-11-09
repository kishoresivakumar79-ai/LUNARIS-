# LUNARIS: Complete System Architecture
## Virtual Moon Base Management System (AI + Digital Twin + 3D Simulation)

---

### 1. Architectural Philosophy

LUNARIS is designed as an autonomous, closed-loop mission control and digital twin simulation for a long-duration lunar surface outpost (e.g., Shackleton Crater rim, Lunar South Pole).

The architecture adheres to strict engineering principles:
1. **Separation of Concerns:** Distinct boundaries between physical simulation equations, autonomous decision engines, machine learning predictive models, persistent database storage, and 3D visualization.
2. **Deterministic Safety Primacy:** Emergency mitigation and life-support survival overrides are governed by deterministic, verifiable safety rules. AI assists with trend forecasting, anomaly detection, and predictive maintenance rather than overriding vital safety thresholds unconstrained.
3. **Continuous Digital Twin Synchronization:** All physical and simulated sensor readings update a unified in-memory graph of digital twin assets, which feeds both the Three.js WebGL spatial environment and the Mission Control Streamlit telemetry dashboard.

---

### 2. Seven-Layer System Architecture

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

    subgraph L3["Layer 3: Data Collection & Persistence"]
        DB[("SQLite moon_base.db\n• telemetry_history\n• equipment_status\n• incidents_log\n• inventory")]
    end

    subgraph L4["Layer 4: AI Predictive Engine"]
        A_PWR["PowerPredictor (Gradient Boosting / Random Forest)"]
        A_O2["OxygenPredictor (Random Forest Regressor)"]
        A_H2O["WaterPredictor (Ridge Regression Shortage Predictor)"]
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

### 3. Subsystem Interconnection & Flow

#### Power Balance Flow
Solar arrays convert incident solar irradiance into DC electrical power. If solar generation exceeds base electrical load, surplus energy charges the 500 kWh lithium-sulfur battery bank. When generation falls during lunar dusk or in shadowed craters, the battery discharges. If battery state-of-charge drops below 25%, the **PowerController** automatically commands **Level 3 Load Shedding** (disabling science labs, rovers, and auxiliary circuits) and starts the 40 kW Hydrogen-Oxygen Fuel Cell Generator.

#### Atmospheric & Life Support Loop
The **CrewManager** calculates metabolic consumption for the 4 astronauts ($3.36\text{ kg O}_2/\text{day}$, $48\text{ L H}_2\text{O}/\text{day}$, $6\text{ kg Food}/\text{day}$). The **Oxygen Generation Assembly (OGA)** uses water from the **Water Recovery System (WRS)** for electrolysis ($2\text{H}_2\text{O} \to 2\text{H}_2 + \text{O}_2$), generating breathable oxygen while the WRS recovers wastewater with 90% closed-loop efficiency.

#### Thermal Regulation Loop
A tuned PID controller computes thermal deviation $e(t) = T_{\text{target}} - T_{\text{internal}}(t)$ every step. If the cabin is too cold during lunar night ($-130^\circ\text{C}$ exterior), electric heating coils are throttled proportionally. If the cabin overheats during lunar noon ($+120^\circ\text{C}$ exterior), heat rejection radiator loops pump excess thermal mass to space.

