"""Metric definitions and calculations for wireless analysis."""
from __future__ import annotations

from typing import Any, Dict, List


def calculate_rank_score(
    snr_mean: float,
    snr_stability: float,
    noise_mean: float,
    data_rate: float,
    weights: Dict[str, float],
    anchors: Dict[str, Dict[str, float]],
) -> Dict[str, Any]:
    """Explainable channel ranking score computation using normalized criteria.

    Parameters:
      snr_mean: Mean Signal-to-Noise Ratio (dB)
      snr_stability: 1.0 / (1.0 + snr_std)
      noise_mean: Mean Background Noise floor (dBm, typically -95 to -80 dBm)
      data_rate: Operating transmission rate (Mbps)
      weights: Dictionary of weights summing to 1.0
      anchors: Min and max bounds for normalization
    """
    # Normalize SNR [0, 1]
    snr_min = anchors["snr"]["min"]
    snr_max = anchors["snr"]["max"]
    norm_snr = np_clamp((snr_mean - snr_min) / (snr_max - snr_min + 1e-6), 0.0, 1.0)

    # Normalize Noise floor: lower (more negative) noise is BETTER
    noise_min = anchors["noise"]["min"]  # e.g. -100 (best)
    noise_max = anchors["noise"]["max"]  # e.g. -75 (worst)
    # inverting so that lower noise gives higher normalized score
    norm_noise = np_clamp((noise_max - noise_mean) / (noise_max - noise_min + 1e-6), 0.0, 1.0)

    # Stability is already in (0, 1]
    norm_stability = np_clamp(snr_stability, 0.0, 1.0)

    # Data rate normalized
    rate_min = anchors["data_rate"]["min"]
    rate_max = anchors["data_rate"]["max"]
    norm_rate = np_clamp((data_rate - rate_min) / (rate_max - rate_min + 1e-6), 0.0, 1.0)

    w_snr = weights.get("w_snr", 0.40)
    w_stability = weights.get("w_stability", 0.25)
    w_noise = weights.get("w_noise", 0.20)
    w_rate = weights.get("w_rate", 0.15)

    composite = (
        w_snr * norm_snr +
        w_stability * norm_stability +
        w_noise * norm_noise +
        w_rate * norm_rate
    )

    return {
        "score": round(float(composite * 100), 2),
        "breakdown": {
            "snr_contrib": round(float(w_snr * norm_snr * 100), 2),
            "stability_contrib": round(float(w_stability * norm_stability * 100), 2),
            "noise_contrib": round(float(w_noise * norm_noise * 100), 2),
            "rate_contrib": round(float(w_rate * norm_rate * 100), 2),
        },
        "normalized_features": {
            "norm_snr": round(float(norm_snr), 3),
            "norm_stability": round(float(norm_stability), 3),
            "norm_noise": round(float(norm_noise), 3),
            "norm_rate": round(float(norm_rate), 3),
        },
    }


def np_clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))
