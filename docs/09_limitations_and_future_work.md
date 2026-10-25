# 09. Limitations, Threats to Validity, and Future Work

---

## 1. Threats to Internal Validity

1. **Passive Driver Capture Limitation:**  
   The CRAWDAD trace captures were collected at the wireless driver layer. Packets that experienced destructive collisions at the physical layer, preambles corrupted by noise, or frames failing CRC-32 checksums were discarded by the hardware PHY and never recorded. Consequently, empirical collision counts are entirely absent from the trace records.
2. **Ambiguity in Sequence Counter Semantics:**  
   While 12-bit MAC sequence numbers ($0 \dots 4095$) are present in the dataset, sequence gaps cannot be conclusively isolated as over-the-air packet loss. Operating system buffer overruns, channel switching pauses during multi-channel scanning, and hardware drop policies can all introduce discontinuities.
3. **Arbitrary Choice of Ranking Weights:**  
   The default weights ($w_{\text{snr}}=0.40, w_{\text{stability}}=0.25, w_{\text{noise}}=0.20, w_{\text{rate}}=0.15$) represent an intuitive heuristic. While supported by the sensitivity analysis tool, they do not stem from a formal multi-attribute utility theory (MAUT) optimization or user study.

---

## 2. Threats to External Validity

1. **Dataset Age and Modulation Relevance:**  
   The CRAWDAD traces were collected in 2009 under legacy IEEE 802.11a/g standards with fixed low-order modulation schemes (6.0 Mbps and 11.0 Mbps). While fundamental multi-path fading and noise floor dynamics remain physically identical today, modern 802.11ac/ax/be standards introduce wide channels (80/160/320 MHz), orthogonal frequency-division multiple access (OFDMA), MU-MIMO, and beamforming that are not captured in this dataset.
2. **Simplified Simulator RF Propagation:**  
   The CSMA/CA simulator implements a single broadcast collision domain:
   - All nodes are within mutual carrier sense range.
   - Hidden terminals and exposed terminals are not modeled.
   - Capture effect (where a receiver successfully decodes a stronger frame during a collision) is omitted.
3. **Decoupled System Architecture:**  
   The channel ranking engine and the CSMA/CA simulator reside within the same web application, but they operate as **independent analytical pipelines**. The simulator does not execute a real-time link adaptation policy based on the empirical ranking scores. Claiming that ranking "improves" simulator throughput would be a scientific fallacy.

---

## 3. Methodological Future Work

1. **Implementation of Block Bootstrapping:**  
   Implement moving-block bootstrap resampling to compute non-parametric confidence intervals for channel ranking scores that account for temporal auto-correlation in signal traces.
2. **Rank Correlation & Agreement Metrics:**  
   Integrate Kendall's $\tau$ rank correlation coefficient and Top-$k$ rank agreement algorithms to systematically quantify ranking stability across time-split holdout datasets.
3. **Multi-Rate Link Adaptation Simulation:**  
   Extend the CSMA/CA simulator with dynamic auto-rate fallback algorithms (e.g., Minstrel or SampleRate) to evaluate how channel stability affects rate hunting and MAC overhead.
4. **Integration of Modern Wi-Fi 6/7 Traces:**  
   Extend the Stage 0 manifest engine to support contemporary 802.11ax/be pcap files featuring multi-user transmissions and 6 GHz spectrum channels.
