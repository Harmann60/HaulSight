"""Haul-Cycle / Production-Impact Forecasting.

Estimates how current visibility conditions affect haul-cycle time and
operational productivity.

This is a FORECAST / ESTIMATE. The relationship (visibility -> cycle time) is
derived from a labeled synthetic dataset representing *plausible* mine
operation figures. Numbers are clearly labelled ESTIMATE / SIMULATION and are
not claimed to be actual mine production figures.

Model: simple linear/regression relationship cycle_time = f(visibility,
vehicle_count, shift). We implement a small hand-rolled linear least-squares
fit (numpy closed form) — appropriate and explainable here.
"""
from __future__ import annotations

import asyncio
import math
from datetime import datetime
from typing import Any

import numpy as np

from . import ai_state
from . import visibility_ai
from ..api.websocket import broadcast

_SHIFT_LATENESS = {"Day": 1.0, "Night": 1.12, "Gravel": 1.05}


def _synth_cycle_dataset(n: int = 300) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    vis = rng.uniform(20, 900, n)
    vcount = rng.integers(2, 9, n).astype(float)
    shift = rng.integers(0, 3, n)  # 0 Day, 1 Night, 2 Gravel
    # baseline cycle ~31 min at good visibility
    base = 31.0
    lateness = np.array([1.0, 1.12, 1.05])[shift]
    cycle = base * lateness + 60.0 * math.e * (1.0 / (vis + 60)) * 8 + vcount * 0.8
    cycle += rng.normal(0, 1.5, n)
    X = np.stack([vis, vcount, shift], axis=1)
    y = cycle
    return X, y


class LinearCycleForecaster:
    def __init__(self) -> None:
        self.coef: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # design matrix: [visibility, visibility^2, vehicle_count, shift_lateness, bias]
        lateness = np.array([1.0, 1.12, 1.05])[X[:, 2].astype(int)]
        inv_vis = 1.0 / (X[:, 0] + 60.0)
        A = np.stack([np.ones_like(y), inv_vis, X[:, 1], lateness], axis=1)
        self.coef, *_ = np.linalg.lstsq(A, y, rcond=None)

    def predict(self, X: np.ndarray) -> np.ndarray:
        lateness = np.array([1.0, 1.12, 1.05])[X[:, 2].astype(int)]
        inv_vis = 1.0 / (X[:, 0] + 60.0)
        A = np.stack([np.ones_like(X[:, 0]), inv_vis, X[:, 1], lateness], axis=1)
        return A @ self.coef


_model: LinearCycleForecaster | None = None


def _ensure_model() -> LinearCycleForecaster:
    global _model
    if _model is None:
        X, y = _synth_cycle_dataset(400)
        _model = LinearCycleForecaster()
        _model.fit(X, y)
    return _model


def _shift_label(now: datetime) -> str:
    h = now.hour
    if 6 <= h < 14:
        return "Day"
    if 14 <= h < 22:
        return "Gravel"
    return "Night"


async def update_forecast() -> dict[str, Any]:
    now = datetime.utcnow()
    visibility = await visibility_ai.get_visibility_for_alerts()
    vis_m = visibility.get("estimated_visibility_m", 1000.0)
    shift = _shift_label(now)
    # vehicle count from store
    from ..state import vehicle_store
    vehicles = await vehicle_store.get_all()
    equipped = sum(1 for v in vehicles if v.is_equipped)

    model = _ensure_model()
    base_vis = 900.0
    X_normal = np.array([[base_vis, equipped, {"Day": 0, "Night": 2, "Gravel": 1}[shift]]])
    X_pred = np.array([[vis_m, equipped, {"Day": 0, "Night": 2, "Gravel": 1}[shift]]])
    normal_cycle = float(model.predict(X_normal)[0])
    predicted_cycle = float(model.predict(X_pred)[0])
    increase_pct = (predicted_cycle - normal_cycle) / normal_cycle * 100
    # production impact roughly inverse of cycle time increase (capacity limited)
    production_impact_pct = -increase_pct * 0.6
    # confidence degrades when visibility is extreme and inputs are few
    conf = max(55.0, min(95.0, 92.0 - (vis_m < 80) * 10 - (equipped < 2) * 8))

    result = {
        "normal_cycle_min": round(normal_cycle, 1),
        "predicted_cycle_min": round(predicted_cycle, 1),
        "increase_pct": round(increase_pct, 1),
        "production_impact_pct": round(production_impact_pct, 1),
        "confidence": round(conf, 1),
        "inputs": {
            "visibility_m": round(vis_m, 1),
            "fog_severity": visibility.get("fog_severity"),
            "active_equipped_vehicles": equipped,
            "shift": shift,
        },
        "data_mode": "ESTIMATE",
        "disclaimer": "Forecast based on simulated operational data — estimate only, not actual mine production figures.",
        "updated_at": now.isoformat(),
    }
    await ai_state.set_production(result)
    try:
        await broadcast({"type": "production_forecast", "data": result})
    except Exception:
        pass
    return result


async def run_loop(tick: float = 5.0) -> None:
    while True:
        try:
            await update_forecast()
        except Exception as e:
            print(f"[production_forecast] Error: {e}")
        await asyncio.sleep(tick)
