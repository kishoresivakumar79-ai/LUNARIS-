"""
LUNARIS AI Engine: Oxygen Requirements & Depletion Forecasting
Predicts future oxygen consumption, days of safe oxygen remaining, and shortage risks.
Uses Random Forest Regressor.
"""

import pickle
from pathlib import Path
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "oxygen_model.pkl"

class OxygenPredictor:
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
        
        # Features: [crew_count, avg_activity_level (1=rest, 2=work, 3=eva), leak_rate_kg_hr, oga_production_kg_day]
        crew = np.random.choice([2, 3, 4, 6], n_samples)
        activity = np.random.uniform(1.0, 2.5, n_samples)
        leak = np.random.exponential(scale=0.05, size=n_samples)
        oga_prod = np.random.uniform(0.0, 9.0, n_samples)
        
        # Daily net oxygen change (kg/day): Production - Consumption - Leak
        cons_kg = crew * 0.84 * activity
        leak_day = leak * 24.0
        net_delta = oga_prod - cons_kg - leak_day + np.random.normal(0, 0.2, n_samples)
        
        X = np.column_stack([crew, activity, leak, oga_prod])
        model = RandomForestRegressor(n_estimators=80, max_depth=6, random_state=42)
        model.fit(X, net_delta)
        
        self.model = model
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
            
    def forecast_7_days(
        self,
        current_day: float,
        current_o2_kg: float,
        crew_count: int = 4,
        activity_level: float = 1.3,
        active_leak_rate_kg_hr: float = 0.0,
        oga_active: bool = True
    ) -> List[Dict[str, Any]]:
        forecast = []
        sim_o2 = current_o2_kg
        oga_prod = 8.0 if oga_active else 0.0
        
        for d in range(1, 8):
            future_day = current_day + d
            x = np.array([[crew_count, activity_level, active_leak_rate_kg_hr, oga_prod]])
            net_delta_day = float(self.model.predict(x)[0])
            
            sim_o2 = max(0.0, sim_o2 + net_delta_day)
            daily_cons = crew_count * 0.84 * activity_level
            days_rem = round(sim_o2 / max(0.1, daily_cons), 1)
            
            status = "OPTIMAL"
            if sim_o2 < 25.0:
                status = "CRITICAL_SHORTAGE"
            elif sim_o2 < 45.0:
                status = "LOW_RESERVE"
                
            forecast.append({
                "day": round(future_day, 1),
                "day_offset": d,
                "predicted_oxygen_kg": round(sim_o2, 2),
                "net_change_kg_day": round(net_delta_day, 2),
                "predicted_days_remaining": days_rem,
                "status": status,
                "confidence_lower_kg": max(0.0, round(sim_o2 - (d * 0.8), 2)),
                "confidence_upper_kg": round(sim_o2 + (d * 0.8), 2)
            })
            
        return forecast

