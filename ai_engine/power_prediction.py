"""
LUNARIS AI Engine: Power Demand & Battery SoC Prediction
Forecasts future base electricity consumption and battery state-of-charge across 7-day mission horizon.
Uses Gradient Boosting / Random Forest regression models.
"""

import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "power_model.pkl"

class PowerPredictor:
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
        """Trains regression model on synthetic feature data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [solar_irradiance, temp_external, crew_count, load_shed_level, oga_active, wrs_active]
        irradiance = np.random.uniform(0.0, 1361.0, n_samples)
        temp_ext = np.where(irradiance > 50, np.random.uniform(-20, 120, n_samples), -130.0)
        crew = np.random.choice([2, 3, 4, 6], n_samples)
        shed = np.random.choice([0, 1, 2, 3], n_samples, p=[0.7, 0.15, 0.1, 0.05])
        oga = np.random.choice([0, 1], n_samples, p=[0.1, 0.9])
        wrs = np.random.choice([0, 1], n_samples, p=[0.1, 0.9])
        
        # Target: power consumption in kW
        target_kw = (
            25.0 + (crew * 2.0) + (oga * 20.0) + (wrs * 15.0) +
            np.abs(21.0 - temp_ext) * 0.15 - (shed * 18.0) +
            np.random.normal(0, 2.5, n_samples)
        )
        target_kw = np.clip(target_kw, 15.0, 140.0)
        
        X = np.column_stack([irradiance, temp_ext, crew, shed, oga, wrs])
        
        if HAS_XGB:
            model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
        else:
            model = HistGradientBoostingRegressor(max_iter=100, max_depth=5, random_state=42)
            
        model.fit(X, target_kw)
        self.model = model
        
        # Save model
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
            
    def predict_consumption(self, irradiance: float, temp_ext: float, crew_count: int, shed_level: int, oga_active: bool, wrs_active: bool) -> float:
        x = np.array([[irradiance, temp_ext, crew_count, shed_level, int(oga_active), int(wrs_active)]])
        pred = float(self.model.predict(x)[0])
        return max(15.0, round(pred, 2))
        
    def forecast_7_days(
        self,
        current_day: float,
        current_battery_pct: float,
        battery_capacity_kwh: float = 500.0,
        crew_count: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generates 7-day power trajectory with day-by-day confidence intervals.
        """
        forecast = []
        sim_bat_kwh = (current_battery_pct / 100.0) * battery_capacity_kwh
        
        for d in range(1, 8):
            future_day = current_day + d
            # Polar solar cycle approximation
            import math
            lunar_phase = (future_day % 29.53) / 29.53 * 2.0 * math.pi
            elevation = math.sin(lunar_phase) * 1.5 + 1.9
            irradiance = 1361.0 if elevation > 0 else 0.0
            temp_ext = 80.0 if irradiance > 0 else -120.0
            
            gen_kw = round((600.0 * irradiance * 0.32 * 0.95) / 1000.0, 1)
            pred_cons_kw = self.predict_consumption(irradiance, temp_ext, crew_count, 0, True, True)
            
            # Daily energy balance (24h)
            net_daily_kwh = (gen_kw - pred_cons_kw) * 24.0
            if net_daily_kwh > 0:
                sim_bat_kwh = min(battery_capacity_kwh, sim_bat_kwh + (net_daily_kwh * 0.95))
            else:
                sim_bat_kwh = max(0.0, sim_bat_kwh + net_daily_kwh)
                
            pred_bat_pct = round((sim_bat_kwh / battery_capacity_kwh) * 100.0, 1)
            
            forecast.append({
                "day": round(future_day, 1),
                "day_offset": d,
                "predicted_solar_kw": gen_kw,
                "predicted_consumption_kw": pred_cons_kw,
                "predicted_battery_pct": pred_bat_pct,
                "confidence_lower_pct": max(0.0, round(pred_bat_pct - (d * 1.5), 1)),
                "confidence_upper_pct": min(100.0, round(pred_bat_pct + (d * 1.5), 1))
            })
            
        return forecast

