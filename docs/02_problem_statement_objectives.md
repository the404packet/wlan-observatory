# 02. Problem Statement, Motivation, and System Requirements

---

## 1. Problem Statement in Detail

### 1.1 Inadequacy of Single-Metric Channel Selection
In traditional IEEE 802.11 deployments, dynamic frequency selection and auto-channel algorithms frequently rely on simplistic measurements:
1. **Received Signal Strength (RSS):** Signal strength alone ignores receiver noise. A strong signal (e.g., $-65\,\text{dBm}$) in a noisy environment (e.g., $-75\,\text{dBm}$) yields an SNR of only $10\,\text{dB}$, which cannot sustain high-order modulation schemes (e.g., 54 Mbps 64-QAM).
2. **Channel Beacon Counting:** Counting neighboring access points ignores non-Wi-Fi RF emitters (microwave ovens, cordless devices, radar) and fails to evaluate multi-path fading characteristics.
3. **Ignoring Temporal Variance:** A channel with a high average SNR but severe standard deviation causes excessive MAC-layer rate adaptation oscillations, packet retries, and buffer jitter.

### 1.2 The Semantic Ambiguity in Empirical Wireless Traces
Public wireless datasets (such as CRAWDAD) provide extensive packet captures. However, standard trace logs contain only frames that were **successfully received and decoded** by the wireless network interface card (NIC). This creates fundamental observational limitations:
- **Collided frames** destroy preambles or headers, meaning they never appear in software traces.
- **Clear Channel Assessment (CCA) busy time** is not recorded in pcap/CSV dumps unless dedicated RF spectrum analyzers are deployed.
- **Sequence counter wraps:** The 12-bit MAC sequence number wraps every 4,096 packets. Gaps in sequences can result from frame loss, driver buffer drops, or capture filter artifacts.

Without rigorous provenance guardrails, students and researchers frequently make flawed assumptions—such as asserting that a 500-packet capture implies low channel load, or that sequence jumps prove real-world collision rates.

### 1.3 The Need for Formal MAC Simulation and Analytical Grounding
Understanding MAC protocol performance under dense contention requires simulation. However, custom academic simulators often suffer from unverified assumptions:
- Failing to properly freeze backoff counters while other transmissions occupy the medium.
- Incorrectly modeling interframe spacing (SIFS vs DIFS) or slot durations ($9\,\mu\text{s}$).
- Implementing arbitrary formulas rather than event-driven contention countdowns.

Grounding the simulator against Giuseppe Bianchi's classic analytical model (IEEE JSAC 2000) provides a formal mathematical reference point to guarantee that the discrete-event engine accurately reflects IEEE 802.11 Distributed Coordination Function (DCF) standards.

---

## 2. Functional Requirements (FR)

| Req ID | Requirement Description | Verification Evidence / Code Reference |
| :--- | :--- | :--- |
| **FR-01** | **Dataset Ingestion & Routing:** The system must scan, route, and parse 8-column headerless CSV files across `802_11a`, `802_11g`, and `interface` sections. | Verified via `src/pipeline/manifest.py` and `tests/test_manifest.py`. Routes 1,496 files. |
| **FR-02** | **Integrity Auditing:** The system must verify column schemas, file sizes, channel identifier alignment, and the invariant $\text{SNR} = \text{RSS} - \text{Noise}$. | Verified via `src/pipeline/validate.py::audit_section()`. |
| **FR-03** | **Summary Caching:** The system must precompute and serialize channel feature summaries to Parquet and JSON to eliminate runtime re-parsing bottlenecks. | Implemented via `src/pipeline/cache.py` (`channel_summaries.parquet` and `.json`). |
| **FR-04** | **Multi-Criteria Channel Ranking:** The system must compute normalized composite scores based on SNR, temporal stability ($1/(1+\sigma)$), noise floor, and transmission rate. | Implemented in `src/analysis/metrics.py::calculate_rank_score()` and `src/pipeline/ranking.py`. |
| **FR-05** | **Baseline Benchmarking:** The ranking engine must benchmark composite scores against single-metric heuristics (Median SNR, Mean RSS, Lowest Noise). | Verified via `tests/test_ranking.py`. |
| **FR-06** | **Discrete-Event DCF Simulation:** The simulator must model contending stations, $9\,\mu\text{s}$ slot decrements, medium freezing during busy states, collision resolution, and retry limits. | Verified via `src/simulation/engine.py` and `tests/test_sim_engine.py`. |
| **FR-07** | **Contention Strategy Support:** The simulator must support Binary Exponential Backoff (BEB) and Fixed Contention Windows. | Verified via `src/simulation/backoff.py` and `tests/test_backoff.py`. |
| **FR-08** | **Analytical Validation Engine:** The system must solve Bianchi's non-linear Markov chain equations for $\tau$ and $p$ and compute percentage error against simulated runs. | Verified via `src/simulation/bianchi.py` and `tests/test_bianchi.py`. |
| **FR-09** | **Provenance Classification:** The application must classify and label every metric as `MEASURED`, `DERIVED`, `ASSUMED`, or `SIMULATED`, raising errors on unregistered metrics. | Implemented via `config/provenance.yaml` and `src/common/provenance.py::tag()`. |
| **FR-10** | **Report Export:** The system must export a comprehensive JSON audit package containing dataset metrics, algorithms, simulation configurations, and disclaimers. | Implemented via `src/web/api/evidence.py::generate_full_report()`. |

---

## 3. Non-Functional Requirements (NFR)

| Req ID | Requirement Description | Implementation Evidence |
| :--- | :--- | :--- |
| **NFR-01** | **Performance & Latency:** Telemetry dashboards and ranking queries must respond in $<100\,\text{ms}$ by querying precomputed Parquet/JSON summaries. | Measured on `/api/analysis/summaries` and `/api/ranking/evaluate`. |
| **NFR-02** | **Mathematical Consistency:** The simulator must match Bianchi's analytical saturation throughput within $2.0\%$ relative error for station counts $N \le 10$. | Confirmed via validation runs ($0.17\%$ for $N=2$, $0.74\%$ for $N=5$, $1.35\%$ for $N=10$). |
| **NFR-03** | **Reproducibility:** Replications executed with identical random seeds must produce identical metric timelines and distributions. | Controlled via `random.Random(seed)` instances per station. |
| **NFR-04** | **Observational Integrity:** The user interface must never present simulated data under empirical headings or present unvalidated assumptions as empirical facts. | Guarded via badge styling (`prov-badge`) and YAML schema validation. |
