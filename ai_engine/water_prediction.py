"""
LUNARIS AI Engine: Water Shortage & Demand Prediction
Forecasts water reserve levels, abnormal consumption patterns, and recycling deficits across 7 days.
Uses Linear Regression / Ridge Regression.
"""

import pickle
from pathlib import Path
import numpy as np
from typing import Dict, List, Any
from sklearn.linear_model import Ridge

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "water_model.pkl"

class WaterPredictor:
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
        n_samples = 1000
        
        # Features: [crew_count, rationing_mode (0 or 1), wrs_efficiency (0.0 to 1.0), pipe_leak_l_hr]
        crew = np.random.choice([2, 3, 4, 6], n_samples)
        rationing = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        wrs_eff = np.random.uniform(0.1, 0.95, n_samples)
        leak = np.random.exponential(scale=0.1, size=n_samples)
        
        # Net daily water balance (L/day): Recycled - Consumed - Loss - Leak
        crew_used = crew * 12.0 * np.where(rationing == 1, 0.65, 1.0)
        recycled = 45.0 * wrs_eff
        loss = 5.0 + (leak * 24.0)
        net_delta = recycled - crew_used - loss + np.random.normal(0, 1.0, n_samples)
        
        X = np.column_stack([crew, rationing, wrs_eff, leak])
        model = Ridge(alpha=1.0)
        model.fit(X, net_delta)
        
        self.model = model
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
            
    def forecast_7_days(
        self,
        current_day: float,
        current_water_l: float,
        crew_count: int = 4,
        rationing_mode: bool = False,
        wrs_efficiency: float = 0.90,
        pipe_leak_l_hr: float = 0.0
    ) -> List[Dict[str, Any]]:
        forecast = []
        sim_water = current_water_l
        
        for d in range(1, 8):
            future_day = current_day + d
            x = np.array([[crew_count, int(rationing_mode), wrs_efficiency, pipe_leak_l_hr]])
            daily_delta_l = float(self.model.predict(x)[0])
            
            sim_water = max(0.0, sim_water + daily_delta_l)
            
            status = "OPTIMAL"
            if sim_water < 90.0:
                status = "CRITICAL_SHORTAGE"
            elif sim_water < 180.0:
                status = "LOW_RESERVE"
                
            forecast.append({
                "day": round(future_day, 1),
                "day_offset": d,
                "predicted_water_l": round(sim_water, 2),
                "net_change_l_day": round(daily_delta_l, 2),
                "status": status,
                "confidence_lower_l": max(0.0, round(sim_water - (d * 4.0), 2)),
                "confidence_upper_l": round(sim_water + (d * 4.0), 2)
            })
            
        return forecast

