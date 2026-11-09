"""
LUNARIS Digital Twin: State Manager
Maintains in-memory ring buffers, state snapshots, and scenario branching ("what-if" models).
"""

from typing import Dict, Any, List, Optional
from collections import deque
import copy

class StateManager:
    def __init__(self, max_buffer_size: int = 500):
        self.history: deque = deque(maxlen=max_buffer_size)
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        
    def record_state(self, state_dict: Dict[str, Any]) -> None:
        self.history.append(copy.deepcopy(state_dict))
        
    def get_latest_state(self) -> Optional[Dict[str, Any]]:
        return self.history[-1] if self.history else None
        
    def get_history(self, count: int = 50) -> List[Dict[str, Any]]:
        return list(self.history)[-count:]
        
    def create_snapshot(self, label: str) -> None:
        if self.history:
            self.snapshots[label] = copy.deepcopy(self.history[-1])
            
    def get_snapshot(self, label: str) -> Optional[Dict[str, Any]]:
        return self.snapshots.get(label)
        
    def clear(self) -> None:
        self.history.clear()
        self.snapshots.clear()

