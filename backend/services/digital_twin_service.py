"""
LUNARIS Backend: Digital Twin Service
Provides dedicated query and mutation endpoints for the virtual Moon base model.
"""

from typing import Dict, Any, List
from backend.services.simulation_service import SimulationService

class DigitalTwinService:
    def __init__(self):
        self.sim = SimulationService()
        
    def get_state(self) -> Dict[str, Any]:
        return self.sim.sync_service.get_digital_twin_state()
        
    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        state = self.get_state()
        entities = state.get("entities", {})
        return entities.get(entity_id, {"error": f"Entity {entity_id} not found"})
        
    def get_topology(self) -> List[Dict[str, Any]]:
        state = self.get_state()
        entities = state.get("entities", {})
        return list(entities.values())

