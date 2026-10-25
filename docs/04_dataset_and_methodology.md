# 04. Dataset Description, Manifests, and Data Integrity

---

## 1. Dataset Origin and Citation

- **Dataset Collection:** CRAWDAD dataset `rice/mesh-heterogeneity` (Community Resource for Archiving Wireless Data at Dartmouth).
- **Original Research Reference:**
  > Anand Prabhu Subramanian, Milind Buddhikot, and Himanshu Gupta, “Understanding Channel and Interface Heterogeneity in Multi-Radio Multi-Channel Wireless Networks,” in *Proceedings of the 10th Passive and Active Measurement Conference (PAM 2009)*, Seoul, Korea, April 2009.
- **Physical Testbed Context:**
  - 802.11a/g mesh testbed comprising nodes equipped with Atheros-based wireless NICs.
  - Fixed transmission power: $15\,\text{dBm}$.
  - Baseline modulation schemes: 6.0 Mbps fixed in 802.11a, 11.0 Mbps fixed in 802.11g.

---

## 2. Directory Structure and Physical File Breakdown

The dataset directory (`D:\tracewise\dataset`) contains 1,497 total files (1,496 CSV data captures + 1 original README).

| Dataset Section | Band / Physical Scope | Structure / Filename Pattern | Expected Count | Observed Count | Empty Files | Manifest Integrity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`802_11a`** | 5 GHz (13 Orthogonal Channels: 36, 40, 44, 48, 52, 56, 60, 64, 149, 153, 157, 161, 165) | `802_11a/link-<L>-channel-<C>.csv` (78 links $\times$ 13 channels) | 1,014 | 1,014 | 0 | **100% VERIFIED** |
| **`802_11g`** | 2.4 GHz (3 Non-Overlapping Channels: 1, 6, 11) | `802_11g/link-<L>-channel-<C>.csv` (54 links $\times$ 3 channels) | 162 | 162 | 0 | **100% VERIFIED** |
| **`interface`** | Multi-Radio Diversity (Channel 64, 16 Interface Pairs: 0-0 through 3-3) | `interface/link-<L>-interface-<I>-<J>.csv` (20 links $\times$ 16 pairs) | 320 | 320 | 0 | **100% VERIFIED** |
| **Total** | -- | -- | **1,496** | **1,496** | **0** | **100% VERIFIED** |

*Verification Date & Environment:* Verified October 20, 2026 via Stage 0 Manifest Engine (`src/pipeline/manifest.py`), serialized into `data/manifests/*.manifest.json`.

---

## 3. Fixed 8-Column Schema and Field Semantics

Every trace file is a headerless, comma-separated values (CSV) log recorded directly at the receiver driver:

```csv
<MAC_TIMESTAMP>,<PACKET_TYPE>,<CHANNEL>,<SNR>,<RSS>,<NOISE>,<DATA_RATE>,<MAC_SEQ>
```

| Col | Field Name | Python Data Type | Documented Physical Unit | Provenance | Scientific Meaning & Constraints |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `timestamp` | `np.float64` | Microseconds ($\mu\text{s}$) | `MEASURED` | Local receiver MAC clock timestamp. Monotonically increasing across captures. (Sample median delta ~ $2.2\,\text{ms}$). |
| **2** | `packet_type` | `str` | Categorical | `MEASURED` | Frame classification. In this dataset, all recorded frames are broadcast probe/data packets. |
| **3** | `channel` | `np.int32` | Integer ID | `MEASURED` | IEEE 802.11 center channel frequency identifier. |
| **4** | `snr` | `np.float64` | Decibels ($\text{dB}$) | `DERIVED` | Signal-to-Noise Ratio. Verified by mathematical identity check $\text{SNR} = \text{RSS} - \text{Noise}$. |
| **5** | `rss` | `np.float64` | $\text{dBm}$ | `MEASURED` | Received Signal Strength measured at receiver antenna connector during frame preamble. |
| **6** | `noise` | `np.float64` | $\text{dBm}$ | `MEASURED` | Receiver background noise floor sampled immediately following packet reception (typically $-96$ to $-85\,\text{dBm}$). |
| **7** | `data_rate` | `np.float64` | $\text{Mbps}$ | `MEASURED` | Modulation and coding PHY transmission rate. 6.0 Mbps for 802.11a, 11.0 Mbps for 802.11g. |
| **8** | `seq` | `np.float64` | Modulo 4096 Counter | `MEASURED` | 12-bit IEEE 802.11 MAC sequence counter ($0 \dots 4095$). Jumps in counter sequence indicate candidate packet losses. |

---

## 4. Integrity Audits and Verification Results

The automated audit suite (`src/pipeline/validate.py`) executes seven verification checks across every routed file:

```json
{
  "802_11a": {
    "status": "VERIFIED",
    "file_count": 1014,
    "expected_count": 1014,
    "empty_files_count": 0,
    "checks": [
      {"name": "File count verification", "status": "PASS", "detail": "Observed 1014 of 1014 files."},
      {"name": "Empty files check", "status": "PASS", "detail": "All files non-empty."},
      {"name": "Schema & column count check", "status": "PASS", "detail": "All 8 columns present across sampled rows."},
      {"name": "Channel identifier alignment", "status": "PASS", "detail": "Channel field strictly matches filename."},
      {"name": "Timestamp monotonicity", "status": "PASS", "detail": "Timestamps strictly increasing."},
      {"name": "SNR mathematical identity check", "status": "PASS", "detail": "Verified SNR == RSS - Noise across samples."},
      {"name": "Sequence semantics audit", "status": "PASS", "detail": "Sequence counters present; wrap-aware detection required."}
    ]
  }
}
```

---

## 5. Preprocessing, Caching, and Aggregation

Because processing 1,496 raw files ($\approx 419\,\text{MB}$) would introduce excessive latency into dashboard requests, the pipeline compiles summary statistics into `data/processed/channel_summaries.parquet` and `channel_summaries.json`:
- **Total Processed Records:** 1,057,366 packets across 1,240 link-channel combinations.
- **Computed Summary Features:**
  - `snr_mean`, `snr_std`, `snr_median`
  - `rss_mean`, `rss_std`, `rss_median`
  - `noise_mean`, `noise_std`
  - `data_rate_mode`
  - `seq_gap_count` (Wrap-aware: $(\Delta \text{seq}) \pmod{4096} > 1$)
  - `seq_anomaly_ratio` ($\text{gaps} / (N - 1)$)
  - `duration_us` ($t_{\max} - t_{\min}$)

---

## 6. Scientific Caveats and Methodological Guardrails

1. **Passive Sniffing Capture Bias:** Every row represents a frame successfully received and decoded by the receiver. Frames lost due to severe destructive interference or low SNR never generate a driver interrupt and are therefore absent from the dataset.
2. **Sequence Gaps $\neq$ Conclusive Packet Loss:** In IEEE 802.11, sequence gaps can occur due to:
   - Operating system and driver buffer drops under high CPU load.
   - Channel switching delays during multi-channel measurement scans.
   - Broadcast probes dropped by the receiver PHY.
   Consequently, sequence discontinuities are formally classified as `DERIVED: candidate_sequence_gaps` rather than absolute packet loss rates.
3. **Trace Volume $\neq$ Medium Load:** The number of captured packets is a function of the sender's probe generation rate, not channel saturation. It must never be interpreted as channel utilization or airtime busy fraction.
