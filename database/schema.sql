-- LUNARIS Moon Base Relational Database Schema
-- SQLite3 Compatible

CREATE TABLE IF NOT EXISTS telemetry_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    mission_day REAL NOT NULL,
    solar_irradiance REAL NOT NULL,
    power_generation REAL NOT NULL,
    power_consumption REAL NOT NULL,
    battery_level REAL NOT NULL,
    battery_pct REAL NOT NULL,
    backup_power REAL NOT NULL,
    oxygen_level REAL NOT NULL,
    oxygen_production REAL NOT NULL,
    oxygen_consumption REAL NOT NULL,
    oxygen_leakage REAL NOT NULL,
    cabin_pressure REAL NOT NULL,
    water_level REAL NOT NULL,
    water_recycled REAL NOT NULL,
    water_used REAL NOT NULL,
    water_loss REAL NOT NULL,
    temp_internal REAL NOT NULL,
    temp_external REAL NOT NULL,
    hvac_mode TEXT NOT NULL,
    hvac_power REAL NOT NULL,
    food_level REAL NOT NULL,
    base_status TEXT NOT NULL,
    active_faults TEXT
);

CREATE TABLE IF NOT EXISTS equipment_status (
    component_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    subsystem TEXT NOT NULL,
    status TEXT NOT NULL,
    health_pct REAL NOT NULL,
    operating_hours REAL NOT NULL,
    failure_probability REAL NOT NULL,
    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    mission_day REAL NOT NULL,
    subsystem TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inventory (
    item_name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    daily_burn_rate REAL NOT NULL,
    critical_threshold REAL NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id TEXT PRIMARY KEY,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    astronauts_count INTEGER NOT NULL,
    duration_days REAL NOT NULL,
    status TEXT NOT NULL,
    outcome TEXT
);

-- Indexes for fast query telemetry
CREATE INDEX IF NOT EXISTS idx_telemetry_mission_day ON telemetry_history(mission_day);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents_log(severity);

