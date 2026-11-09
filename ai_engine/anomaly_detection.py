"""
LUNARIS AI Engine: Unsupervised Anomaly Detection
Uses Isolation Forest to detect abnormal operational telemetry, sensor drifts,
unexpected power surges, and micro-leaks before explicit safety boundaries are crossed.
"""

import pickle
from pathlib import Path
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import IsolationForest

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "anomaly_model.pkl"

class AnomalyDetector:
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
        n_samples = 2000
        
        # Nominal telemetry distribution:
        # [power_cons (60-120 kW), battery_pct (40-100%), oxygen_level (70-150 kg),
        #  cabin_pressure (99-102 kPa), water_level (350-700 L), temp_internal (20-23 °C)]
        power_cons = np.random.normal(85.0, 10.0, n_samples)
        battery_pct = np.random.uniform(45.0, 98.0, n_samples)
        oxygen_level = np.random.normal(105.0, 8.0, n_samples)
        cabin_pressure = np.random.normal(101.3, 0.4, n_samples)
        water_level = np.random.normal(520.0, 40.0, n_samples)
        temp_internal = np.random.normal(21.5, 0.8, n_samples)
        
        # Inject 4% subtle anomalies
        n_anom = int(n_samples * 0.04)
        power_cons[:n_anom] += np.random.uniform(35.0, 60.0, n_anom)
        cabin_pressure[:n_anom] -= np.random.uniform(5.0, 15.0, n_anom)
        temp_internal[:n_anom] += np.random.uniform(5.0, 10.0, n_anom)
        
        X = np.column_stack([power_cons, battery_pct, oxygen_level, cabin_pressure, water_level, temp_internal])
        model = IsolationForest(n_estimators=100, contamination=0.04, random_state=42)
        model.fit(X)
        
        self.model = model
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
            
    def evaluate_telemetry(self, t: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a single telemetry point.
        Returns is_anomaly (bool), anomaly_score (float, 0 to 1), and contributing factors.
        """
        features = np.array([[
            float(t.get("power_consumption", 85.0)),
            float(t.get("battery_pct", 75.0)),
            float(t.get("oxygen_level", 100.0)),
            float(t.get("cabin_pressure", 101.3)),
            float(t.get("water_level", 500.0)),
            float(t.get("temp_internal", 21.5))
        ]])
        
        # decision_function gives negative for anomalies, positive for inliers
        raw_score = float(self.model.decision_function(features)[0])
        pred = int(self.model.predict(features)[0])  # -1 for anomaly, 1 for normal
        
        # Normalize anomaly severity index: 0.0 (perfectly normal) to 1.0 (extreme anomaly)
        # raw_score typically ranges from -0.3 (extreme) to +0.25 (typical)
        anomaly_index = max(0.0, min(1.0, round(0.5 - (raw_score * 2.0), 3)))
        is_anomaly = (pred == -1) or (anomaly_index > 0.65)
        
        # Identify suspicious features
        suspects = []
        if float(t.get("cabin_pressure", 101.3)) < 98.0:
            suspects.append("Atmospheric pressure depressurization trend")
        if float(t.get("power_consumption", 85.0)) > 115.0:
            suspects.append("Power consumption above nominal envelope")
        if float(t.get("temp_internal", 21.5)) > 24.5 or float(t.get("temp_internal", 21.5)) < 18.5:
            suspects.append("Thermal excursion")
        if float(t.get("oxygen_leakage", 0.0)) > 0.2:
            suspects.append("Uncharacteristic oxygen flow loss")
            
        return {
            "is_anomaly": is_anomaly,
            "anomaly_index": anomaly_index,
            "raw_decision_score": round(raw_score, 4),
            "suspect_factors": suspects
        }

