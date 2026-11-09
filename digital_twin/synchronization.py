"""
LUNARIS Digital Twin: Synchronization Service
Orchestrates seamless synchronization between the physical simulation engine,
the Digital Twin entity graph, database storage, and connected clients (WebSockets/REST).
"""

from typing import Dict, Any, List
from digital_twin.twin_engine import DigitalTwinEngine
from digital_twin.state_manager import StateManager
from database.database import insert_telemetry, upsert_equipment, log_incident

class SynchronizationService:
    def __init__(self):
        self.twin_engine = DigitalTwinEngine()
        self.state_manager = StateManager()
        self.last_sync_timestamp = None
        
    def synchronize(
        self,
        telemetry: Dict[str, Any],
        equipment: List[Dict[str, Any]],
        persist_db: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronizes simulation outputs into the Digital Twin model and optionally persists to SQLite.
        """
        # 1. Update twin entities
        self.twin_engine.sync_from_telemetry(telemetry, equipment)
        twin_snapshot = self.twin_engine.get_twin_snapshot()
        
        # 2. Package composite state
        composite_state = {
            "telemetry": telemetry,
            "equipment": equipment,
            "digital_twin": twin_snapshot
        }
        
        # 3. Store in in-memory state manager
        self.state_manager.record_state(composite_state)
        
        # 4. Optional database persistence
        if persist_db:
            try:
                insert_telemetry(telemetry)
                upsert_equipment(equipment)
            except Exception as e:
                # Keep running smoothly even if DB file is temporarily locked
                pass
                
        return composite_state
        
    def get_digital_twin_state(self) -> Dict[str, Any]:
        return self.twin_engine.get_twin_snapshot()

