# 08. Literature Review and Academic References

---

## 1. Primary Foundational Papers

### 1.1 Analytical Modeling of 802.11 DCF
- **Citation:** Giuseppe Bianchi, “Performance Analysis of the IEEE 802.11 Distributed Coordination Function,” *IEEE Journal on Selected Areas in Communications*, vol. 18, no. 3, pp. 535–547, March 2000.
- **Digital Object Identifier (DOI):** [10.1109/49.840210](https://doi.org/10.1109/49.840210)
- **Problem & Method:** Bianchi proposed a discrete-time, two-dimensional Markov chain to model the backoff stage $j \in [0, m]$ and backoff counter $k \in [0, W_j - 1]$ of a contending station under saturated queue conditions and constant conditional collision probability $p$.
- **Project Adoption:**  
  Our analytical validation module (`src/simulation/bianchi.py`) directly implements Bianchi's coupled non-linear equations for transmission probability $\tau$ and collision probability $p$, solving them numerically via `scipy.optimize.fsolve` to benchmark the CSMA/CA simulator.
- **Specific Equations Adopted:**
  $$p = 1 - (1 - \tau)^{n - 1}$$
  $$\tau = \frac{2(1 - 2p)}{(1 - 2p)(W + 1) + pW(1 - (2p)^m)}$$

---

### 1.2 Multi-Channel Mesh Heterogeneity & Trace Foundation
- **Citation:** Anand Prabhu Subramanian, Milind Buddhikot, and Himanshu Gupta, “Understanding Channel and Interface Heterogeneity in Multi-Radio Multi-Channel Wireless Networks,” in *Proceedings of the 10th Passive and Active Measurement Conference (PAM 2009)*, Seoul, Korea, Lecture Notes in Computer Science, vol. 5448, pp. 115–124, Springer, 2009.
- **Digital Object Identifier (DOI):** [10.1007/978-3-642-00975-4_12](https://doi.org/10.1007/978-3-642-00975-4_12)
- **Problem & Method:** The authors collected extensive physical-layer packet traces across 78 links in a 5 GHz testbed and 54 links in a 2.4 GHz testbed to investigate whether wireless channels and antenna interfaces exhibit homogeneous RF propagation. They demonstrated substantial link quality variations across frequency channels.
- **Project Adoption:**  
  This is the empirical dataset (`rice/mesh-heterogeneity`) ingested by our manifest and analysis pipeline (`src/pipeline/manifest.py`, `src/pipeline/features.py`). We utilize their raw traces to evaluate real-world SNR, noise floor, and variance across 13 orthogonal channels.

---

### 1.3 Channel Assignment and Interference Mitigation
- **Citation:** Anand Prabhu Subramanian, Himanshu Gupta, Samir R. Das, and Milind Buddhikot, “Minimum Interference Channel Assignment in Multi-Radio Wireless Mesh Networks,” *IEEE Transactions on Mobile Computing*, vol. 7, no. 12, pp. 1459–1473, Dec. 2008.
- **Digital Object Identifier (DOI):** [10.1109/TMC.2008.70](https://doi.org/10.1109/TMC.2008.70)
- **Problem & Method:** Formulated algorithmic channel assignment as an optimization problem minimizing total network interference while preserving multi-radio network topology.
- **Project Adoption:**  
  Serves as theoretical motivation for our channel ranking engine. While Subramanian et al. optimized global graph interference, our project focuses on local link-level explainable ranking incorporating empirical noise floors and stability.

---

## 2. Supporting Standards and Reference Works

1. **IEEE Standard for Information Technology:**
   - *IEEE Std 802.11-2020: Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications*, IEEE Computer Society, Feb. 2021.
   - *Relevant Sections:* Section 10.3 (DCF MAC architecture), Section 17 (OFDM PHY timing: SIFS $= 16\,\mu\text{s}$, DIFS $= 34\,\mu\text{s}$, slot $= 9\,\mu\text{s}$).

2. **Fairness Metric Definition:**
   - Rajendra K. Jain, Dah-Ming W. Chiu, and William R. Hawe, “A Quantitative Measure of Fairness and Discrimination for Resource Allocation in Shared Computer Systems,” *DEC Research Report TR-301*, Sept. 1984.
   - *Adopted In:* `src/analysis/stats.py::jains_fairness_index()`.
   $$J(x) = \frac{\left(\sum_{i=1}^n x_i\right)^2}{n \sum_{i=1}^n x_i^2}$$

3. **CRAWDAD Wireless Archive:**
   - David Kotz and Tristan Henderson, “CRAWDAD: A Community Resource for Archiving Wireless Data at Dartmouth,” *IEEE Pervasive Computing*, vol. 4, no. 4, pp. 12–14, 2005.
