"""
LUNARIS AI Engine: Predictive Maintenance & Subsystem Failure Risk
Estimates failure probabilities and Remaining Useful Life (RUL) across Moon base hardware.
Uses Random Forest Classification and degradation regression.
"""

import pickle
from pathlib import Path
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "failure_model.pkl"

class FailurePredictor:
    def __init__(self):
        self.model = None
        self._load_or_train_model()
        
    def _load_or_train_model(self) -> None:
        if MODEL_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                return
            except Exception:
                pass
        self._train_default_model()
        
    def _train_default_model(self) -> None:
        np.random.seed(42)
        n_samples = 1500
        
        # Features: [health_pct (0-100), operating_hours (0-2000), thermal_stress (0-1), load_factor (0-1)]
        health = np.random.uniform(10.0, 100.0, n_samples)
        hours = np.random.uniform(50.0, 1800.0, n_samples)
        thermal_stress = np.random.uniform(0.1, 1.0, n_samples)
        load_factor = np.random.uniform(0.4, 1.2, n_samples)
        
        # Failure label: 1 if component fails soon, 0 if healthy
        # Risk increases when health is low, hours are high, and stress is high
        risk_score = ((100.0 - health) * 0.015) + (hours / 1800.0 * 0.4) + (thermal_stress * 0.25) + (load_factor * 0.2)
        label = (risk_score > 0.85).astype(int)
        
        X = np.column_stack([health, hours, thermal_stress, load_factor])
        model = RandomForestClassifier(n_estimators=75, max_depth=5, random_state=42)
        model.fit(X, label)
        
        self.model = model
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
            
    def predict_component_risk(
        self,
        health_pct: float,
        operating_hours: float,
        thermal_stress: float = 0.4,
        load_factor: float = 0.8
    ) -> Dict[str, Any]:
        """
        Calculates failure risk probability (0.0 to 1.0) and estimated Remaining Useful Life (RUL) in hours.
        """
        x = np.array([[health_pct, operating_hours, thermal_stress, load_factor]])
        probs = self.model.predict_proba(x)[0]
        # Class 1 probability
        fail_prob = float(probs[1]) if len(probs) > 1 else (1.0 if health_pct < 40 else 0.05)
        
        # Remaining useful life estimation
        # Assuming nominal life of 2000 operating hours at 100% health
        remaining_hours = max(10.0, (health_pct / 100.0) * (2000.0 - (operating_hours % 2000.0)) * (1.0 - fail_prob * 0.8))
        
        status = "HEALTHY"
        if fail_prob > 0.70:
            status = "CRITICAL_RISK"
        elif fail_prob > 0.35:
            status = "MAINTENANCE_REQUIRED"
            
        return {
            "failure_probability": round(fail_prob, 3),
            "estimated_rul_hours": round(remaining_hours, 1),
            "risk_status": status
        }
        
    def evaluate_all_equipment(self, equipment_list: List[Dict[str, Any]], thermal_stress: float = 0.4) -> List[Dict[str, Any]]:
        results = []
        for eq in equipment_list:
            pred = self.predict_component_risk(
                health_pct=eq["health_pct"],
                operating_hours=eq["operating_hours"],
                thermal_stress=thermal_stress
            )
            item = dict(eq)
            item.update(pred)
            results.append(item)
        # Sort by failure probability descending
        results.sort(key=lambda x: x["failure_probability"], reverse=True)
        return results

