# WLAN Observatory: Trace-Driven Channel Quality Ranking and Validated CSMA/CA Backoff Simulation for IEEE 802.11

> **A Provenance-Aware Analysis Tool for Empirical Wireless Traces & Discrete-Event MAC Simulation**

---

## 📌 Overview

**WLAN Observatory** (Tracewise) is a research and pedagogical platform designed to bridge empirical trace analysis with theoretical MAC layer modeling in IEEE 802.11 networks. The tool combines:

1. **Trace-Driven Channel Analysis & Ranking:** Rigorous validation, feature extraction, and multi-metric ranking across 1,496 link traces from the CRAWDAD PAM 2009 dataset.
2. **Validated CSMA/CA DCF Simulator:** A discrete-event simulator supporting Binary Exponential Backoff (BEB), Contention Window adjustment, optional RTS/CTS, and an interactive real-time visual canvas.
3. **Bianchi Analytical Model Validation:** Automated mathematical comparison against Giuseppe Bianchi's classic 2000 Markov chain throughput formulation.
4. **Data Provenance:** Strict labeling across all outputs distinguishing `MEASURED`, `DERIVED`, `ASSUMED`, and `SIMULATED` metrics.

---

## 📸 Screenshots & UI Showcase

<!-- Placeholder sections for application screenshots -->

### 1. Telemetry Overview & Link Profiles
> *Interactive aggregate link distributions, SNR vs. delivery rates, and trace summaries.*
<img width="2880" height="1532" alt="image" src="https://github.com/user-attachments/assets/546d8ff6-24a0-48fb-993c-c7f3bda8c6b3" />


### 2. Trace Preprocessing & Dataset Validation
> *Manifest verification, checksum inspections, and microsecond timestamp audit.*
<img width="2880" height="1622" alt="image" src="https://github.com/user-attachments/assets/13308feb-1c37-4e95-a4f7-92ee6310b19f" />


### 3. Channel Quality Ranking & Uncertainty Estimation
> *Composite metric calculation, SNR/loss/interference weighting, and bootstrap ranking.*
<img width="2880" height="1594" alt="image" src="https://github.com/user-attachments/assets/3e23f04e-9d38-4d8b-83e1-0949d599a0c5" />


### 4. Interactive CSMA/CA Backoff Simulator
> *Per-slot DCF contention animation, station collision detection, CW backoff states, and throughput charts.*
<img width="2880" height="1606" alt="image" src="https://github.com/user-attachments/assets/0e418346-bd1e-4050-9c00-c11cd24eff96" />


### 5. Bianchi Model Analytical Validation
<img width="2880" height="1626" alt="image" src="https://github.com/user-attachments/assets/9a372ff1-79f2-489a-ba69-3a2bd832b903" />

---

## 🚀 Quickstart & Usage

### Prerequisites
- **Python:** 3.10 to 3.12
- **Operating System:** Windows, macOS, or Linux
- **Git**

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository
git clone https://github.com/your-username/tracewise.git
cd tracewise

# Create and activate virtual environment
# On Windows:
python -m venv .venv
.\.venv\Scripts\activate

# On Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Running Preprocessing & Dataset Manifests (Optional / Setup)
The CRAWDAD trace files reside in `dataset/` (or `data/raw/`). To compile the manifests and summary statistics:

```bash
# Set PYTHONPATH to project root
# Windows PowerShell:
$env:PYTHONPATH="."
python scripts/build_manifests.py
python scripts/compute_features.py

# Linux / macOS:
PYTHONPATH=. python scripts/build_manifests.py
PYTHONPATH=. python scripts/compute_features.py
```

### 4. Launching the Web Application

```bash
# Start Flask development server
# Windows PowerShell:
$env:PYTHONPATH="."
python -m flask --app src.web.app run --debug --port 5000

# Linux / macOS:
PYTHONPATH=. python3 -m flask --app src.web.app run --debug --port 5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📖 Project Documentation & Research Evidence

A full, chapter-by-chapter documentation source package is available in the [`docs/`](docs/README.md) directory. It provides deep technical evidence and rigorous academic traceability for project defense, reports, and papers:

- **[docs/01_project_overview.md](docs/01_project_overview.md)** — Executive overview, motivation, and scope boundaries.
- **[docs/02_problem_statement_objectives.md](docs/02_problem_statement_objectives.md)** — MAC layer bottlenecks, formal FRs/NFRs, and problem statements.
- **[docs/03_architecture_and_implementation.md](docs/03_architecture_and_implementation.md)** — Architectural diagrams, pipeline design, and Flask API specifications.
- **[docs/04_dataset_and_methodology.md](docs/04_dataset_and_methodology.md)** — CRAWDAD PAM'09 802.11 trace specifications and audit procedures.
- **[docs/05_actual_experimental_results.md](docs/05_actual_experimental_results.md)** — Real numerical tables: Bianchi validation ($N=2 \dots 25$), channel ranking evidence, and backoff comparisons.
- **[docs/06_analysis_and_inference.md](docs/06_analysis_and_inference.md)** — Finite retry limit divergence analysis and stability penalty models.
- **[docs/07_testing_and_validation.md](docs/07_testing_and_validation.md)** — Complete test suite coverage, invariants, and quality assurance.
- **[docs/08_literature_review_and_references.md](docs/08_literature_review_and_references.md)** — Comprehensive academic literature review and bibliography.
- **[docs/09_limitations_and_future_work.md](docs/09_limitations_and_future_work.md)** — Analytical constraints, threats to validity, and research roadmap.
- **[docs/10_report_evidence_index.md](docs/10_report_evidence_index.md)** — Traceability matrix linking all equations and metrics directly to source files.
- **[docs/project_report_evidence.md](docs/project_report_evidence.md)** — Complete unabridged unified reference report.

---

## 🛠️ Dashboard Navigation & Core Workflows

1. **Overview (`/overview`):**
   - High-level telemetry of CRAWDAD 802.11a/g traces.
   - Global link SNR distribution, delivery ratios, and noise variance.
2. **Datasets & Validation (`/datasets`):**
   - Verify integrity of trace files across links and channels.
   - Audit timestamp formats, column boundaries, and missing-frame rates.
3. **Channel Analysis (`/channel-analysis`):**
   - Per-channel SNR, noise, and loss profiles.
   - Deep dive into individual sender-receiver link pairs.
4. **Channel Ranking (`/ranking-eval`):**
   - Rank 802.11 channels based on multi-criteria utility functions (throughput, loss rate, stability).
   - Evaluate baseline algorithms (Random, Greedy SNR, Load-Aware) with confidence intervals.
5. **CSMA/CA Simulator (`/simulator`):**
   - Set station count ($N=2 \dots 50$), contention window parameters ($CW_{min}, CW_{max}$), payload size, and RTS/CTS threshold.
   - Watch real-time packet transmissions, backoff countdowns, collisions, and queue drops.
   - Adjust animation speed (0.5× to 16×).
6. **Bianchi Validation (`/validation`):**
   - Compare simulator throughput against closed-form theoretical predictions across varying station densities.

---

## 🧪 Testing & Verification

Run the comprehensive unit and integration test suite (23 tests covering API contracts, backoff algorithms, Bianchi model, holdout tests, and uncertainty calculations):

```bash
# Run pytest with coverage report
pytest --cov=src -v
```

---

## 📚 Papers & Dataset Citations

If you use this software, trace processing pipeline, or simulation model in academic research, please cite the underlying dataset and analytical model:

### 1. CRAWDAD Trace Dataset (PAM 2009)
```bibtex
@inproceedings{crawdad_pam2009,
  author    = {Chambers, Christopher and Wright, Matthew and Banerjee, Suman},
  title     = {Measurement-based Characterization of a Collection of 802.11 Wireless Links},
  booktitle = {Passive and Active Network Measurement (PAM)},
  series    = {Lecture Notes in Computer Science},
  volume    = {5448},
  pages     = {249--258},
  year      = {2009},
  publisher = {Springer},
  doi       = {10.1007/978-3-642-00975-4_25}
}
```
*Dataset available via CRAWDAD:* [crawdad.org/wisc/wand](https://crawdad.org/)

### 2. Bianchi CSMA/CA Analytical Model (IEEE JSAC 2000)
```bibtex
@article{bianchi2000performance,
  author    = {Bianchi, Giuseppe},
  journal   = {IEEE Journal on Selected Areas in Communications},
  title     = {Performance Analysis of the IEEE 802.11 Distributed Coordination Function},
  year      = {2000},
  volume    = {18},
  number    = {3},
  pages     = {535--547},
  doi       = {10.1109/49.840210}
}
```

---

## 🛡️ Provenance Taxonomy

All data generated or viewed in this application is strictly labeled according to its scientific origin:

| Provenance Tag | Meaning | Example |
| :--- | :--- | :--- |
| <span style="background:#22c55e;color:#000;padding:2px 6px;border-radius:4px;font-weight:bold;">MEASURED</span> | Directly observed physical values from trace captures | RSS, Noise Floor, Timestamp |
| <span style="background:#3b82f6;color:#fff;padding:2px 6px;border-radius:4px;font-weight:bold;">DERIVED</span> | Numerically computed or aggregated from measured data | Frame Delivery Ratio (PDR), SNR, Airtime |
| <span style="background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-weight:bold;">ASSUMED</span> | Standard IEEE protocol defaults or scenario parameters | SIFS, DIFS, Slot Time, Payload Size |
| <span style="background:#ec4899;color:#fff;padding:2px 6px;border-radius:4px;font-weight:bold;">SIMULATED</span> | Output produced via discrete-event CSMA/CA simulation | Simulated Collision Rate, Throughput |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
