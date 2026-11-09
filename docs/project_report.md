# LUNARIS: Engineering Project Report & Mission Simulation Analysis

---

## 1. Executive Summary

**LUNARIS** (*Virtual Moon Base Management System*) is an integrated software platform combining multi-physics environmental simulation, deterministic autonomous safety control, predictive machine learning, and an interactive 3D WebGL Digital Twin. 

The software models a 4-astronaut human research outpost located at the rim of Shackleton Crater on the Moon's South Pole. The outpost must sustain human life and scientific exploration under extreme conditions: vacuum, severe temperature oscillations ($-130^\circ\text{C}$ to $+120^\circ\text{C}$), high-energy cosmic radiation, and a 1.28-second communication latency with Earth.

Rather than acting as a passive telemetry viewer, LUNARIS operates as an intelligent closed-loop mission control engine that forecasts future resource depletion, flags sensor anomalies, isolates physical hull failures, and automates emergency life-support reconfigurations.

---

## 2. Quantitative Baseline Parameters

| Subsystem Parameter | Nominal Baseline | Safety Threshold | Critical Threshold |
| :--- | :--- | :--- | :--- |
| **Crew Complement** | 4 Astronauts | 4 Astronauts | > 6 Astronauts |
| **Battery Storage** | 500 kWh capacity (65% initial: 325 kWh) | 45% (Load Shed Level 1) | < 25% (Load Shed Level 3 + Aux) |
| **Solar Generation** | Dual $300\text{ m}^2$ tracking arrays (120 kW peak) | > 60 kW | < 30 kW |
| **Oxygen Inventory** | 100 kg cryo-reserve (200 kg tank) | 45 kg | < 25 kg (Emergency Reserve Open) |
| **Cabin Pressure** | 101.3 kPa (1.0 atm sea level equivalent) | 98.0 kPa | < 90.0 kPa (Bulkhead Seal Active) |
| **Water Inventory** | 500 L clean reserve (1000 L tank) | 180 L (Water Conservation) | < 90 L (Strict Sponge Bath Rationing) |
| **WRS Recycling Rate** | 45 L/day (90% closed loop recovery) | 30 L/day | < 10 L/day (Distiller Pump Jam) |
| **Cabin Temperature** | $21.5^\circ\text{C}$ ($21.0^\circ\text{C}$ setpoint) | $< 18.0^\circ\text{C}$ or $> 25.0^\circ\text{C}$ | $< 14.0^\circ\text{C}$ or $> 30.0^\circ\text{C}$ |
| **Food Reserves** | 120 kg (30-day baseline + greenhouse) | 40 kg (10 days remaining) | < 20 kg (Resupply Urgent) |

---

## 3. Failure Scenario Validation & Automated Responses

### Scenario 1: Solar Power Failure
- **Injected Event:** Solar array generation drops by 70% due to an electrical inverter failure or shadow occultation.
- **AI Observation:** `PowerPredictor` detects a severe energy deficit of $-65\text{ kW}$ and forecasts complete battery blackout within 18 hours.
- **Autonomous Response:** `PowerController` triggers Level 3 Load Shedding (science labs offline, rover recharging suspended, cabin lighting dimmed) and starts the 40 kW Hydrogen Fuel Cell auxiliary generator.
- **Outcome:** Battery discharge rate stabilizes, preserving life-support and heating power for an additional 72 hours until array repair.

### Scenario 2: Hull Oxygen Puncture
- **Injected Event:** Simulated micrometeorite puncture in habitat outer shell, causing an air leak rate of $1.8\text{ kg/hr}$.
- **AI Observation:** `AnomalyDetector` flags pressure drop ($101.3 \to 94.2\text{ kPa}$) and uncharacteristic mass flow loss with an Anomaly Score of $0.825$.
- **Autonomous Response:** `OxygenController` commands automated electromagnetic bulkhead door closure to isolate the breached module and opens the emergency cryogenic reserve valve.
- **Outcome:** Cabin pressure recovers to $101.3\text{ kPa}$ in unbreached modules; oxygen loss is stopped.

### Scenario 3: Water Recycling Failure
- **Injected Event:** Water Recovery System (WRS) centrifuge pump jams, dropping recovery efficiency from 90% to 10%.
- **AI Observation:** `WaterPredictor` models the new burn curve and projects that clean water reserves will reach critical minimum (90 L) in 5.2 days.
- **Autonomous Response:** `WaterController` immediately activates mandatory water rationing mode, reducing non-potable consumption by 35% and prioritizing graywater filtration.
- **Outcome:** Depletion horizon extends past 14 days, providing adequate time for EVAs and pump impeller replacement.

### Scenario 4: MLI Thermal Insulation Breach
- **Injected Event:** Multi-layer insulation blanket tears on the sunward side, increasing conductive heat loss threefold during deep lunar night ($-130^\circ\text{C}$).
- **AI Observation:** Cabin temperature rapidly drops from $21.5^\circ\text{C}$ towards $16.0^\circ\text{C}$.
- **Autonomous Response:** Temperature PID controller raises heating demand to maximum $35\text{ kW}$; power management reallocates grid capacity to thermal coils.
- **Outcome:** Cabin temperature stabilizes at $19.2^\circ\text{C}$ inside safe physiological margins.

---

## 4. Key Engineering Differentiators

| Feature | Standard Telemetry Dashboards | LUNARIS Moon Base System |
| :--- | :--- | :--- |
| **Data Scope** | Static present-moment gauges | Present + 7-Day Predictive Horizon + Historical DB |
| **Intelligence** | Static colored alert thresholds | Machine Learning (Gradient Boosting, Random Forest, Ridge, Isolation Forest) |
| **Control Loop** | Read-only manual intervention | Closed-loop Autonomous Decision Engine with deterministic safety rules |
| **Digital Twin** | Flat 2D schematics or diagrams | Interactive Three.js WebGL 3D environment with raycasting & real-time telemetry HUD |
| **Scenario Testing** | Static synthetic sample rows | Dynamic fault injection engine with real-time recovery mechanisms |

---

## 5. Verification & Test Execution Summary

The test suite in `tests/` covers all mathematical conservation laws, controller decision trees, fault injection pipelines, and bounds checking:
- `test_power.py`: Validates solar irradiance generation, battery bounds clamping ($0 \le E \le 500\text{ kWh}$), and load shedding tiers.
- `test_oxygen.py`: Validates OGA mass balance, puncture depressurization, bulkhead isolation, and emergency reserve deployment.
- `test_water.py`: Validates closed-loop recycling, water rationing reduction, and pump failure response.
- `test_emergency.py`: Validates multi-level status classification (NORMAL, WARNING, CRITICAL), fault injection, and automated clearing.

**Result:** 14 of 14 unit tests passed with 100% success rate.

