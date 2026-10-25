# 05. Actual Experimental Results and Numerical Evidence

---

## 1. Verified Analytical Validation: Bianchi (2000) vs. Simulator

To formally validate the discrete-event CSMA/CA simulator, matched experiments were executed comparing Bianchi's analytical saturation model against the simulation engine across varying contending station densities ($N \in [2, 25]$).

### 1.1 Experimental Configuration (Identical for Model & Sim)
- **PHY/MAC Standard:** IEEE 802.11a defaults ($6.0\,\text{Mbps}$ PHY rate, $9\,\mu\text{s}$ slot time, $16\,\mu\text{s}$ SIFS, $34\,\mu\text{s}$ DIFS, $20\,\mu\text{s}$ preamble).
- **Contention Window:** $CW_{\min} = 15$, $CW_{\max} = 1023$, Backoff Policy: Binary Exponential Backoff (BEB).
- **Payload & Framing:** Payload $= 1000\,\text{bytes}$, MAC Header $= 28\,\text{bytes}$, ACK $= 14\,\text{bytes}$, Handshake: Basic Access (No RTS/CTS).
- **Channel Conditions:** Frame Error Prob $= 0.0$ (Ideal channel, matching Bianchi's assumptions).
- **Queue State:** Saturated (nodes continuously have packets ready).
- **Simulation Budget:** 3 Monte Carlo replications, 800 events per run.

### 1.2 Exact Measured Comparison Table

| Stations ($N$) | Bianchi Th ($\text{Mbps}$) `[DERIVED]` | Sim Th ($\text{Mbps}$) `[SIMULATED]` | Throughput Error ($\%$) | Bianchi Coll Prob ($p$) `[DERIVED]` | Sim Coll Prob ($p_{\text{sim}}$) `[SIMULATED]` | Collision Error ($\%$) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2** | 4.987 | 4.995 | **0.17%** | 10.46% | 9.78% | 6.50% | **VALIDATED** |
| **5** | 4.530 | 4.497 | **0.74%** | 27.15% | 27.59% | 1.62% | **VALIDATED** |
| **10** | 4.157 | 4.101 | **1.35%** | 38.44% | 39.49% | 2.73% | **VALIDATED** |
| **15** | 3.946 | 3.756 | **4.81%** | 44.23% | 48.67% | 10.04% | **VALIDATED** |
| **20** | 3.797 | 3.524 | **7.20%** | 48.09% | 54.99% | 14.35% | **ACCEPTABLE** |
| **25** | 3.681 | 3.231 | **12.22%** | 50.97% | 60.96% | 19.60% | **DIVERGENCE** |

*Provenance Classification:*
- Bianchi Analytical Predictions: `DERIVED` (from numerical solution of non-linear Markov chain equations).
- Simulation Outputs: `SIMULATED` (from discrete-event countdown engine).

---

## 2. Verified Empirical Channel Ranking: 802.11a Link 0

The multi-criteria ranking algorithm was executed on real CRAWDAD trace summaries for **802.11a Link 0** across all 13 orthogonal 5 GHz channels.

### 2.1 Configuration Parameters
- **Scoring Weights:** $w_{\text{snr}} = 0.40$, $w_{\text{stability}} = 0.25$, $w_{\text{noise}} = 0.20$, $w_{\text{rate}} = 0.15$ (`ASSUMED`).
- **Physical Anchors:** SNR $[5, 45]\,\text{dB}$, Noise $[-100, -75]\,\text{dBm}$, Rate $[6, 54]\,\text{Mbps}$ (`ASSUMED`).

### 2.2 Complete Channel Ranking Results Table

| Final Rank | Channel | Score (0–100) `[DERIVED]` | Mean SNR ($\text{dB}$) `[DERIVED]` | SNR StdDev ($\sigma$) `[DERIVED]` | Mean Noise ($\text{dBm}$) `[MEASURED]` | Median SNR Rank (Base 1) | Mean RSS Rank (Base 2) | Lowest Noise Rank (Base 3) | Key Analytical Factor |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1** | **Ch 48** | **55.05** | 26.24 | 0.47 | -96.00 | #2 | #2 | #1 | **Optimal:** Low noise (-96 dBm) + tight stability ($\sigma=0.47$) |
| **#2** | **Ch 44** | **51.75** | 23.82 | 0.55 | -96.00 | #4 | #4 | #2 | Clean noise floor, moderate SNR |
| **#3** | **Ch 157** | **51.21** | 28.01 | 1.05 | -95.01 | **#1** | **#1** | #6 | **Highest raw SNR & RSS**, but penalized for higher noise and higher variance ($\sigma=1.05$) |
| **#4** | **Ch 52** | **50.43** | 21.96 | 0.50 | -96.00 | #6 | #9 | #3 | Clean noise floor, lower signal power |
| **#5** | **Ch 60** | **49.99** | 23.57 | 0.71 | -96.00 | #5 | #5 | #4 | Moderate SNR and noise |
| **#6** | **Ch 36** | **49.55** | 21.88 | 0.50 | -95.00 | #7 | #7 | #7 | Mid-band balance |
| **#7** | **Ch 40** | **49.35** | 22.12 | 0.54 | -95.00 | #8 | #6 | #8 | Mid-band balance |
| **#8** | **Ch 64** | **48.63** | 21.40 | 0.54 | -95.00 | #9 | #8 | #9 | Lower SNR |
| **#9** | **Ch 149** | **47.10** | 24.47 | 1.15 | -95.00 | #3 | #3 | #10 | High SNR but degraded by high instability ($\sigma=1.15$) |
| **#10** | **Ch 56** | **45.95** | 19.33 | 0.60 | -95.00 | #10 | #10 | #11 | Weak signal level |
| **#11** | **Ch 161** | **43.85** | 17.61 | 0.64 | -95.00 | #11 | #12 | #12 | Low SNR |
| **#12** | **Ch 153** | **42.85** | 17.59 | 0.66 | -94.00 | #12 | #11 | #13 | Highest noise floor (-94 dBm) and low SNR |
| **#13** | **Ch 165** | **33.70** | 18.11 | 5.03 | -95.55 | #13 | #13 | #5 | **Severely Penalized:** Massive variance ($\sigma=5.03$) destroys stability score |

---

## 3. Contention Strategy Comparison: BEB vs. Fixed CW

Using the simulation runner (`src/simulation/runner.py`), Binary Exponential Backoff was benchmarked against a Fixed Contention Window alternative under identical conditions ($N=10\,\text{stations}$, $CW_{\min}=15$, $6.0\,\text{Mbps}$, $1000\,\text{B}$ payload, 800 events).

| Performance Metric | Binary Exponential Backoff (BEB) `[SIMULATED]` | Fixed Contention Window (CW=15) `[SIMULATED]` | Delta / Impact | Scientific Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Aggregate Throughput** | **4.101 Mbps** | **2.185 Mbps** | **-46.7%** | BEB doubles window on collision, reducing persistent simultaneous retransmissions. |
| **Collision Probability** | **39.49%** | **58.74%** | **+19.25%** | Without window expansion, colliding stations immediately re-collide in small [0, 15] window. |
| **Mean Access Delay** | **2.14 ms** | **4.82 ms** | **+125.2%** | Fixed CW suffers prolonged packet drops and repeated retry delays. |
| **Packet Drop Rate** | **0.82%** | **7.41%** | **+6.59%** | Severe drop surge under Fixed CW due to hitting 7-retry limit. |
| **Jain's Fairness Index** | **0.978** | **0.912** | **-0.066** | Fixed CW experiences severe short-term starvation for unlucky stations. |

---

## 4. Status of Missing or Unexecuted Experiments

To preserve scientific rigor, the following experimental items are explicitly declared:

| Experiment / Evaluation Item | Status | Detailed Explanation |
| :--- | :--- | :--- |
| **Block Bootstrapping Confidence Intervals** | **NOT IMPLEMENTED** | Block bootstrap resampling across temporal chunks does not exist in the codebase. Student-$t$ CI is implemented for summary aggregates, but not block-bootstrapped. |
| **Kendall's Tau & Top-$k$ Agreement** | **NOT IMPLEMENTED** | Formal non-parametric rank correlation metrics between composite ranks and baselines were planned but never implemented in `src/`. |
| **Ranking Regret Quantification** | **NOT IMPLEMENTED** | `src/pipeline/holdout.py` splits traces and computes train/test score drift, but does not compute true regret relative to an optimal oracle channel. |
| **Poisson Arrival Sweep over Multiple Rates** | **NOT RUN** | The engine supports Poisson traffic, but automated sweeps across arrival rates $\lambda \in [10, 1000]\,\text{pkts/s}$ were not stored as saved runs. |
