"""
LUNARIS Database Manager
Handles SQLite persistent storage for telemetry, incident logs, equipment states, and mission inventories.
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "moon_base.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[Path] = None) -> None:
    target_path = db_path or DB_PATH
    with get_connection(target_path) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    seed_initial_data(target_path)

def seed_initial_data(db_path: Optional[Path] = None) -> None:
    target_path = db_path or DB_PATH
    with get_connection(target_path) as conn:
        cursor = conn.cursor()
        
        # Initial inventory
        cursor.execute("SELECT COUNT(*) FROM inventory")
        if cursor.fetchone()[0] == 0:
            default_items = [
                ("Food Rations", "Consumables", 120.0, "kg", 4.0, 20.0),
                ("Medical Packs", "Medical", 50.0, "units", 0.5, 10.0),
                ("Fuel Cell Reactants", "Energy", 200.0, "kg", 2.0, 30.0),
                ("Spare Filters (OGA/WRS)", "Spares", 24.0, "units", 0.1, 4.0),
                ("EVA Suit Batteries", "Hardware", 12.0, "units", 0.05, 2.0),
                ("Hydroponic Seeds", "Agriculture", 15.0, "kg", 0.02, 3.0),
                ("O2 Backup Canisters", "Emergency", 50.0, "kg", 0.0, 10.0),
                ("Water Emergency Bladder", "Emergency", 150.0, "L", 0.0, 30.0),
            ]
            cursor.executemany(
                """INSERT INTO inventory (item_name, category, quantity, unit, daily_burn_rate, critical_threshold)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                default_items
            )
            
        # Initial equipment status
        cursor.execute("SELECT COUNT(*) FROM equipment_status")
        if cursor.fetchone()[0] == 0:
            default_equipment = [
                ("SOLAR_A", "Solar Array Alpha", "Power", "OPTIMAL", 98.5, 420.0, 0.02),
                ("SOLAR_B", "Solar Array Beta", "Power", "OPTIMAL", 97.8, 420.0, 0.03),
                ("BATTERY_MAIN", "Lithium-Sulfur Battery Bank", "Power", "OPTIMAL", 96.0, 720.0, 0.04),
                ("BACKUP_GEN", "Hydrogen Fuel Cell Auxiliary", "Power", "OPTIMAL", 100.0, 48.0, 0.01),
                ("OGA_SYS", "Oxygen Generation Assembly", "LifeSupport", "OPTIMAL", 94.2, 580.0, 0.05),
                ("WRS_SYS", "Water Recovery System", "LifeSupport", "OPTIMAL", 93.0, 610.0, 0.06),
                ("ATCS_HVAC", "Active Thermal Control System", "Thermal", "OPTIMAL", 95.5, 720.0, 0.03),
                ("HAB_SEAL", "Habitat Pressure Hull Seal", "Structure", "OPTIMAL", 99.1, 720.0, 0.01),
                ("COMMS_ARRAY", "High-Gain Earth Dish", "Comms", "OPTIMAL", 99.5, 720.0, 0.01),
                ("ROVER_ALPHA", "Lunar Surface Rover 1", "Robotics", "OPTIMAL", 92.0, 150.0, 0.08)
            ]
            cursor.executemany(
                """INSERT INTO equipment_status (component_id, name, subsystem, status, health_pct, operating_hours, failure_probability)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                default_equipment
            )
            
        conn.commit()

def insert_telemetry(t: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        active_faults_str = json.dumps(t.get("active_faults", [])) if isinstance(t.get("active_faults"), list) else str(t.get("active_faults", ""))
        cursor.execute(
            """INSERT INTO telemetry_history (
                mission_day, solar_irradiance, power_generation, power_consumption,
                battery_level, battery_pct, backup_power, oxygen_level, oxygen_production,
                oxygen_consumption, oxygen_leakage, cabin_pressure, water_level,
                water_recycled, water_used, water_loss, temp_internal, temp_external,
                hvac_mode, hvac_power, food_level, base_status, active_faults
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                t.get("mission_day", 1.0),
                t.get("solar_irradiance", 1361.0),
                t.get("power_generation", 120.0),
                t.get("power_consumption", 90.0),
                t.get("battery_level", 325.0),
                t.get("battery_pct", 65.0),
                t.get("backup_power", 0.0),
                t.get("oxygen_level", 100.0),
                t.get("oxygen_production", 8.0),
                t.get("oxygen_consumption", 6.0),
                t.get("oxygen_leakage", 0.0),
                t.get("cabin_pressure", 101.3),
                t.get("water_level", 500.0),
                t.get("water_recycled", 40.0),
                t.get("water_used", 50.0),
                t.get("water_loss", 5.0),
                t.get("temp_internal", 21.5),
                t.get("temp_external", -20.0),
                t.get("hvac_mode", "IDLE"),
                t.get("hvac_power", 5.0),
                t.get("food_level", 120.0),
                t.get("base_status", "NORMAL"),
                active_faults_str
            )
        )
        conn.commit()
        return cursor.lastrowid

def get_recent_telemetry(limit: int = 100, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        # Return in chronological order
        return list(reversed(result))

def get_telemetry_range(start_day: float, end_day: float, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM telemetry_history WHERE mission_day >= ? AND mission_day <= ? ORDER BY mission_day ASC",
            (start_day, end_day)
        )
        return [dict(row) for row in cursor.fetchall()]

def upsert_equipment(equipment_list: List[Dict[str, Any]], db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for eq in equipment_list:
            cursor.execute(
                """INSERT INTO equipment_status (component_id, name, subsystem, status, health_pct, operating_hours, failure_probability, last_checked)
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(component_id) DO UPDATE SET
                   status=excluded.status,
                   health_pct=excluded.health_pct,
                   operating_hours=excluded.operating_hours,
                   failure_probability=excluded.failure_probability,
                   last_checked=CURRENT_TIMESTAMP""",
                (
                    eq["component_id"], eq["name"], eq["subsystem"],
                    eq["status"], eq["health_pct"], eq["operating_hours"],
                    eq.get("failure_probability", 0.01)
                )
            )
        conn.commit()

def get_equipment(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipment_status ORDER BY subsystem, component_id")
        return [dict(row) for row in cursor.fetchall()]

def log_incident(subsystem: str, severity: str, title: str, description: str, action_taken: str, mission_day: float = 1.0, db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO incidents_log (mission_day, subsystem, severity, title, description, action_taken, resolved)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (mission_day, subsystem, severity, title, description, action_taken)
        )
        conn.commit()
        return cursor.lastrowid

def get_incidents(unresolved_only: bool = False, limit: int = 50, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM incidents_log"
        params: List[Any] = []
        if unresolved_only:
            query += " WHERE resolved = 0"
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def resolve_incident(incident_id: int, db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE incidents_log SET resolved = 1 WHERE id = ?", (incident_id,))
        conn.commit()

def get_inventory(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY category, item_name")
        return [dict(row) for row in cursor.fetchall()]

def update_inventory(item_name: str, quantity: float, db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventory SET quantity = ?, last_updated = CURRENT_TIMESTAMP WHERE item_name = ?",
            (quantity, item_name)
        )
        conn.commit()

def reset_simulation_data(db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM telemetry_history")
        cursor.execute("DELETE FROM incidents_log")
        conn.commit()
    seed_initial_data(db_path)

