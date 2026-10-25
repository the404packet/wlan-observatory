# 01. Project Overview and Executive Summary

**Project Title:** Trace-Driven Channel Quality Ranking and Validated CSMA/CA Backoff Simulation for IEEE 802.11: A Provenance-Aware Analysis Tool

---

## 1. Abstract (Verified Implementation Baseline)

Modern IEEE 802.11 wireless local area networks (WLANs) operate in increasingly dense and heterogeneous radio environments. Selecting an optimal radio channel requires balancing multiple physical-layer quality indicators, while understanding medium access control (MAC) performance under contention requires validated discrete-event modeling. 

This project implements **WLAN Observatory**, an integrated, provenance-aware web-based engineering workbench that bridges empirical trace analysis and discrete-event network simulation. The system ingests and audits 1,496 wireless trace files from the CRAWDAD PAM 2009 multi-channel dataset (encompassing over 1,057,000 processed packet records across 5 GHz 802.11a, 2.4 GHz 802.11g, and multi-antenna interface diversity measurements). 

The application implements two distinct analytical pipelines:
1. **Explainable Multi-Criteria Channel Ranking:** An empirical scoring engine that normalizes and weights Mean Signal-to-Noise Ratio (SNR), SNR stability ($1/(1+\sigma)$), background noise floor, and transmission rate modes across user-defined physical anchors, benchmarked against single-metric heuristics (median SNR, mean RSS, and lowest noise).
2. **Validated Discrete-Event CSMA/CA Simulator:** A MAC-layer DCF simulation engine modeling slot-by-slot countdown ($9\,\mu\text{s}$), medium freezing, Binary Exponential Backoff (BEB), fixed contention windows, optional RTS/CTS 4-way handshakes, and non-collision frame errors.

The simulation engine is formally validated against Giuseppe Bianchi's classic analytical Markov chain model (IEEE JSAC 2000) under saturated conditions. Across station densities from $N=2$ to $N=10$, the simulator matches Bianchi's theoretical throughput within $0.17\%$ to $1.35\%$ relative error. 

Crucially, to preserve scientific integrity, every variable, chart, and exportable report enforces strict provenance classification: `MEASURED` (raw physical traces), `DERIVED` (computed statistics), `ASSUMED` (user configurations and theoretical assumptions), and `SIMULATED` (discrete-event outputs).

---

## 2. Background and Motivation

### 2.1 The Multi-Channel Wi-Fi Landscape
IEEE 802.11 networks partition the radio spectrum into distinct frequency channels (e.g., channels 36–165 in 5 GHz, channels 1–11 in 2.4 GHz). In real indoor deployments, channel quality varies significantly across frequencies even between the exact same transmitter-receiver antenna pair due to:
- Multi-path reflections and frequency-selective fading.
- Hardware diversity and non-flat antenna frequency responses.
- External non-Wi-Fi radio frequency (RF) interference and varying noise floors.

### 2.2 Shortcomings of Conventional Channel Selection
Most commercial access points (APs) rely on simplistic channel selection heuristics:
- **Least Congested Channel Search (LCCS):** Counting detected SSIDs or beacons, ignoring physical signal stability and noise.
- **Pure Signal Strength (RSS/RSSI):** Optimizing purely for signal amplitude, ignoring that high ambient noise can degrade SNR, or that unstable channels cause erratic modulation rate adaptations.

### 2.3 The Disconnect Between Physical Measurement and MAC Modeling
In wireless research, empirical trace collection and MAC protocol simulation are frequently conducted in silos:
- Empirical measurements capture raw physical metrics (RSS, SNR, noise) but lack ground truth for collision events, carrier sensing airtime, and multi-station queue states.
- Network simulators (e.g., ns-3) model complex MAC state machines but frequently assume idealized, homogeneous channel conditions.

This project creates a unified analytical tool where empirical trace quality is systematically evaluated and contrasted against an exact, validated discrete-event CSMA/CA simulator.

---

## 3. Exact Problem Statement

In IEEE 802.11 wireless networks, physical channel selection is frequently driven by single-metric heuristics (such as peak RSS or beacon count) that fail to account for the interplay between signal strength, receiver noise floor, and channel temporal stability. Furthermore, empirical trace captures cannot directly measure MAC-layer collisions or carrier-busy airtime without specialized hardware monitors. 

Consequently, researchers and students face a dual challenge:
1. Formulating an explainable, multi-criteria channel-ranking methodology grounded in real empirical trace data without making unverified claims about real-world throughput improvements.
2. Building and analytically validating a discrete-event CSMA/CA MAC simulator against theoretical foundations (Bianchi's 2000 model) while rigorously tracking data provenance (`MEASURED`, `DERIVED`, `ASSUMED`, `SIMULATED`) to prevent unscientific conflation between observed trace telemetry and simulated MAC dynamics.

---

## 4. Research Questions and Project Objectives

### 4.1 Research Questions (RQs)
- **RQ1 (Empirical Multi-Criteria Ranking):** How does multi-criteria channel quality ranking (combining SNR, temporal variance, noise floor, and transmission rate) alter channel selection compared to traditional single-metric heuristics (e.g., maximum median SNR or maximum RSS)?
- **RQ2 (MAC Backoff Performance & Validation):** To what degree of precision does a Python discrete-event CSMA/CA DCF engine match Bianchi's analytical saturation throughput and collision probability under standard IEEE 802.11 physical parameters?
- **RQ3 (Contention Strategy Trade-offs):** What are the measurable performance trade-offs between Binary Exponential Backoff (BEB) and Fixed Contention Windows under increasing station densities ($N \in [2, 25]$) regarding aggregate throughput, collision rate, access delay, and Jain's fairness index?
- **RQ4 (Provenance Guardrails):** How can a scientific analysis tool systematically enforce data provenance classification to prevent unsupported claims regarding channel utilization and packet loss in empirical traces?

### 4.2 Project Objectives
1. **Pipeline & Ingestion:** Ingest, route, validate, and cache 1,496 trace files from the CRAWDAD PAM 2009 dataset across `802_11a`, `802_11g`, and `interface` sections.
2. **Channel Ranking Engine:** Develop an explainable ranking algorithm that normalizes physical metrics across physical anchors and compares composite scores against empirical baselines.
3. **CSMA/CA Simulation Workbench:** Implement an event-driven DCF simulator supporting slot decrements, medium freezing, BEB, Fixed CW, RTS/CTS, and non-collision frame error rates.
4. **Analytical Validation Suite:** Numerically solve Bianchi's coupled non-linear equations for $\tau$ and $p$ and execute matching simulation replications to measure exact error percentages.
5. **Kibana-Inspired Interface:** Provide an interactive engineering dashboard featuring Plotly telemetry graphs, an HTML5 medium state animation canvas, an event timeline inspector, and exportable JSON evidence packages.

---

## 5. Scope Exclusions and Critical Scientific Disclaimers

To maintain strict scientific integrity, the following boundaries are formally established:

| Scope Item | Project Status | Scientific Justification |
| :--- | :--- | :--- |
| **Real-world throughput improvement** | **NOT CLAIMED** | The ranking engine ranks channels based on physical receiver quality; it does *not* deploy configurations to live APs. |
| **Sequence gaps as packet loss** | **DISCLAIMED** | Discontinuities in 12-bit sequence counters ($0 \dots 4095$) indicate *candidate* gaps, not confirmed physical loss, as receiver drops, driver buffer overflows, and retransmissions cannot be isolated. |
| **Trace frame count as channel utilization** | **DISCLAIMED** | Packet counts reflect snapshot sampling rates; they do *not* represent carrier-busy time or channel airtime utilization. |
| **Direct linkage between trace & simulator** | **EXCLUDED** | Trace data measures physical link quality; the simulator models CSMA/CA MAC contention. They are independent analytical modules housed in a common workbench. |
| **Physical RF propagation emulation** | **EXCLUDED** | The simulator assumes a single broadcast collision domain without hidden terminals or spatial fading. |
