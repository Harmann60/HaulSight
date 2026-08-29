"""AI Radar Object Classification.

Classifies radar/mmWave detections into VEHICLE / ANIMAL / ROCK / UNKNOWN
using radar-derived features (range, relative speed, reflectivity, size,
persistence across frames).

SIMULATION MODE: the radar simulator emits synthetic feature vectors with a
*ground-truth* class label. The classifier is a hand-implemented
k-nearest-neighbours model (numpy only). Confidence is the fraction of the k
nearest training neighbours agreeing with the predicted class. Ground truth is
only used to train/evaluate the stored synthetic dataset; at runtime the
classifier sees features only (ground_truth is reported separately for demo
transparency).

Key product behaviour: a detection classified as a non-vehicle object (ROCK /
ANIMAL) with high confidence is a false positive and does NOT escalate into a
vehicle collision alert.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import numpy as np

from . import ai_state
from ..api.websocket import broadcast

CLASSES = ["VEHICLE", "ANIMAL", "ROCK", "UNKNOWN"]


def _synth_features(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Synthetic labeled radar dataset (SIMULATION)."""
    rng = np.random.default_rng(42)
    X = np.zeros((n, 5))
    y = np.zeros(n, dtype=int)
    for i in range(n):
        cls = rng.integers(0, 4)
        y[i] = cls
        if cls == 0:  # VEHICLE
            X[i] = [
                rng.uniform(20, 120), abs(rng.normal(6, 3)),
                rng.uniform(0.7, 1.0), rng.uniform(4, 7), rng.uniform(0.8, 1.0),
            ]
        elif cls == 1:  # ANIMAL
            X[i] = [
                rng.uniform(8, 45), abs(rng.normal(2, 1.5)),
                rng.uniform(0.2, 0.5), rng.uniform(0.3, 0.9), rng.uniform(0.05, 0.4),
            ]
        elif cls == 2:  # ROCK (static)
            X[i] = [
                rng.uniform(5, 60), 0.1 + abs(rng.normal(0, 0.2)),
                rng.uniform(0.5, 0.9), rng.uniform(1, 3), 1.0,
            ]
        else:  # UNKNOWN / noisy edge
            X[i] = [
                rng.uniform(5, 130), abs(rng.normal(4, 4)),
                rng.uniform(0.0, 1.0), rng.uniform(0.0, 8), rng.uniform(0.0, 1.0),
            ]
    return X, y


class RadarKNN:
    """k-Nearest-Neighbours classifier for radar objects (numpy only)."""

    def __init__(self, k: int = 9) -> None:
        self.k = k
        self.X_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None
        self.mean: np.ndarray | None = None
        self.std: np.ndarray | None = None
        self.feature_weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0) + 1e-9
        self.X_train = (X - self.mean) / self.std
        self.y_train = y
        # Emphasise discriminative features: relative speed, persistence, size
        self.feature_weights = np.array([1.0, 1.6, 1.2, 1.4, 1.6])

    def _proba(self, x: np.ndarray) -> np.ndarray:
        xnorm = (x - self.mean) / self.std
        diff = (self.X_train - xnorm) * self.feature_weights
        dist = np.linalg.norm(diff, axis=1)
        idx = np.argsort(dist)[: self.k]
        counts = np.bincount(self.y_train[idx], minlength=len(CLASSES)).astype(float)
        return counts / counts.sum()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        return np.stack([self._proba(x) for x in X])


_classifier: RadarKNN | None = None


def _ensure_classifier() -> RadarKNN:
    global _classifier
    if _classifier is None:
        X, y = _synth_features(800)
        _classifier = RadarKNN(k=9)
        _classifier.fit(X, y)
    return _classifier


def classify(features: dict[str, Any]) -> dict[str, Any]:
    clf = _ensure_classifier()
    X = np.array([[
        features.get("range_m", 30.0),
        features.get("relative_speed_mps", 0.0),
        features.get("reflectivity", 0.5),
        features.get("size", 1.0),
        features.get("persistence", 0.0),
    ]])
    probs = clf.predict_proba(X)[0]
    idx = int(np.argmax(probs))
    return {
        "object_class": CLASSES[idx],
        "confidence": round(float(probs[idx]) * 100, 1),
        "probabilities": {CLASSES[i]: round(float(probs[i]) * 100, 1) for i in range(len(CLASSES))},
    }


async def record_classification(features: dict[str, Any], ground_truth: str | None = None) -> dict[str, Any]:
    result = classify(features)
    result.update({
        "detection_id": str(uuid.uuid4())[:8],
        "features": features,
        "ground_truth": ground_truth,
        "data_mode": "SIMULATION",
        "is_false_positive": result["object_class"] in ("ROCK", "ANIMAL"),
        "timestamp": datetime.utcnow().isoformat(),
    })
    await ai_state.add_radar_classification(result)
    try:
        await broadcast({"type": "radar_ai", "data": result})
    except Exception:
        pass
    return result
