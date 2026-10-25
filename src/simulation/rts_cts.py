"""RTS/CTS 4-way handshake duration calculations."""
from __future__ import annotations


def calculate_transmission_durations(
    payload_bytes: int,
    data_rate_mbps: float = 6.0,
    slot_time_us: float = 9.0,
    sifs_us: float = 16.0,
    difs_us: float = 34.0,
    rts_cts: bool = False,
    ack_bytes: int = 14,
    phy_header_us: float = 20.0,
    mac_header_bytes: int = 28,
) -> dict:
    """Compute explicit timing durations in microseconds for successful and colliding transmissions."""
    mac_frame_bits = (payload_bytes + mac_header_bytes) * 8.0
    ack_bits = ack_bytes * 8.0

    t_data = phy_header_us + (mac_frame_bits / data_rate_mbps)
    t_ack = phy_header_us + (ack_bits / data_rate_mbps)

    if not rts_cts:
        t_succ = difs_us + t_data + sifs_us + t_ack
        t_coll = difs_us + t_data + sifs_us + t_ack
    else:
        rts_bits = 20.0 * 8.0
        cts_bits = 14.0 * 8.0
        t_rts = phy_header_us + (rts_bits / data_rate_mbps)
        t_cts = phy_header_us + (cts_bits / data_rate_mbps)
        t_succ = difs_us + t_rts + sifs_us + t_cts + sifs_us + t_data + sifs_us + t_ack
        t_coll = difs_us + t_rts + sifs_us + t_cts

    return {
        "t_succ_us": t_succ,
        "t_coll_us": t_coll,
        "t_data_us": t_data,
        "payload_bits": payload_bytes * 8.0,
        "slot_time_us": slot_time_us,
        "difs_us": difs_us,
        "sifs_us": sifs_us,
    }
