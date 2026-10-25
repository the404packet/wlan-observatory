"""Bianchi DCF 2000 Analytical Model for 802.11 Saturated CSMA/CA."""
from __future__ import annotations

import math
from typing import Any, Dict, Tuple
from scipy.optimize import fsolve


def solve_bianchi_tau(n_stations: int, cw_min: int = 15, cw_max: int = 1023, retry_limit: int = 7) -> Tuple[float, float]:
    """Solve the non-linear system of equations for Bianchi's conditional collision probability p and transmission probability tau.

    Equation 1: p = 1 - (1 - tau)**(n - 1)
    Equation 2: tau = 2*(1 - 2*p) / ((1 - 2*p)*(W + 1) + p*W*(1 - (2*p)**m)) where W = cw_min + 1, 2**m * W = cw_max + 1
    """
    if n_stations <= 1:
        # For a single station, collision probability is 0
        tau = 2.0 / (cw_min + 2.0)
        return 0.0, tau

    W = cw_min + 1
    m = int(round(math.log2((cw_max + 1) / W)))

    def equations(vars):
        p, tau = vars
        p = max(1e-7, min(1.0 - 1e-7, p))
        tau = max(1e-7, min(1.0 - 1e-7, tau))

        eq1 = p - (1.0 - (1.0 - tau) ** (n_stations - 1))

        if abs(1.0 - 2.0 * p) < 1e-5:
            # Limit as p -> 0.5
            denom = (W + 1.0) / 2.0 + (W / 2.0) * (2 ** (m - 1) if m > 0 else 0.5)
            eq2 = tau - (1.0 / denom)
        else:
            term1 = (1.0 - 2.0 * p) * (W + 1.0)
            term2 = p * W * (1.0 - (2.0 * p) ** m)
            denom = term1 + term2
            eq2 = tau - (2.0 * (1.0 - 2.0 * p) / denom)

        return [eq1, eq2]

    # Initial guess
    initial_p = 0.1
    initial_tau = 2.0 / (cw_min + 1.0)
    sol_p, sol_tau = fsolve(equations, [initial_p, initial_tau])

    p_val = float(max(0.0, min(1.0, sol_p)))
    tau_val = float(max(0.0, min(1.0, sol_tau)))
    return p_val, tau_val


def compute_bianchi_throughput(
    n_stations: int,
    cw_min: int = 15,
    cw_max: int = 1023,
    payload_bytes: int = 1000,
    data_rate_mbps: float = 6.0,
    slot_time_us: float = 9.0,
    sifs_us: float = 16.0,
    difs_us: float = 34.0,
    ack_bytes: int = 14,
    phy_header_us: float = 20.0,
    mac_header_bytes: int = 28,
    rts_cts: bool = False,
) -> Dict[str, float]:
    """Calculate normalized saturation throughput and collision probability using Bianchi 2000.

    Normalized throughput S = E[Payload transmitted in a slot] / E[Length of a slot]
    """
    p, tau = solve_bianchi_tau(n_stations, cw_min, cw_max)

    # Probability that at least one station transmits
    p_tr = 1.0 - (1.0 - tau) ** n_stations

    if p_tr <= 0:
        return {"collision_prob": 0.0, "normalized_throughput": 0.0, "throughput_mbps": 0.0, "tau": 0.0}

    # Probability that a transmission is successful conditioned on someone transmitting
    p_s = (n_stations * tau * ((1.0 - tau) ** (n_stations - 1))) / p_tr

    # Transmission durations in microseconds
    payload_bits = payload_bytes * 8.0
    mac_frame_bits = (payload_bytes + mac_header_bytes) * 8.0
    ack_bits = ack_bytes * 8.0

    t_data = phy_header_us + (mac_frame_bits / data_rate_mbps)
    t_ack = phy_header_us + (ack_bits / data_rate_mbps)

    if not rts_cts:
        t_succ = difs_us + t_data + sifs_us + t_ack
        t_coll = difs_us + t_data + sifs_us + t_ack  # In basic access, colliding stations hold channel for DATA
    else:
        rts_bits = 20.0 * 8.0
        cts_bits = 14.0 * 8.0
        t_rts = phy_header_us + (rts_bits / data_rate_mbps)
        t_cts = phy_header_us + (cts_bits / data_rate_mbps)
        t_succ = difs_us + t_rts + sifs_us + t_cts + sifs_us + t_data + sifs_us + t_ack
        t_coll = difs_us + t_rts + sifs_us + t_cts

    # Expected slot duration
    e_slot = (1.0 - p_tr) * slot_time_us + p_tr * p_s * t_succ + p_tr * (1.0 - p_s) * t_coll

    # Expected payload bits
    e_payload_bits = p_tr * p_s * payload_bits

    # Normalized throughput = E[payload transmission time] / E[slot duration]
    s_norm = (p_tr * p_s * (payload_bits / data_rate_mbps)) / e_slot
    throughput_mbps = (e_payload_bits / e_slot)

    return {
        "collision_prob": round(float(p), 4),
        "tau": round(float(tau), 4),
        "normalized_throughput": round(float(s_norm), 4),
        "throughput_mbps": round(float(throughput_mbps), 3),
        "p_tr": round(float(p_tr), 4),
        "p_s": round(float(p_s), 4),
    }
