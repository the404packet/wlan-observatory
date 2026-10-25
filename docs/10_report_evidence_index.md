# 10. Report Evidence Index and Traceability Matrix

This index maps every major academic claim, formula, algorithm, and experimental result to its concrete implementation, test fixture, data artifact, or literature reference.

---

## 1. Traceability Matrix

| Scientific Claim / System Feature | Implementation Source File | Function / Code Reference | Test File / Verification Method | Empirical Data or Model Reference |
| :--- | :--- | :--- | :--- | :--- |
| **802.11a/g/iface Section Ingestion** | `src/pipeline/manifest.py` | `_route()`, `build_manifests()` | `tests/test_manifest.py::test_routes_three_sections` | 1,496 CRAWDAD files in `dataset/` |
| **Integrity & SNR Identity Check** | `src/pipeline/validate.py` | `audit_section()`, lines 89–98 | `tests/test_manifest.py::test_channel_mismatch_flag` | Sampled 200 rows per file; `data/manifests/` |
| **Feature Extraction & Summaries** | `src/pipeline/features.py` | `extract_file_features()`, lines 17–100 | Verified via Parquet cache loading | 1,057,366 rows in `channel_summaries.parquet` |
| **Multi-Criteria Ranking Formula** | `src/analysis/metrics.py` | `calculate_rank_score()`, lines 7–71 | `tests/test_ranking.py` | Normalized anchors: SNR, Stability, Noise, Rate |
| **Ranking Baselines Comparison** | `src/pipeline/ranking.py` | `rank_channels_for_link()`, lines 80–90 | `tests/test_ranking.py` | Median SNR, Mean RSS, Lowest Noise baselines |
| **BEB Contention Doubling** | `src/simulation/backoff.py` | `double_cw_on_failure()`, lines 37–57 | `tests/test_backoff.py::test_beb_doubling` | IEEE 802.11 DCF standard ($CW_{\min}=15, CW_{\max}=1023$) |
| **Fixed Contention Window Policy** | `src/simulation/backoff.py` | `double_cw_on_failure()`, line 54 | `tests/test_backoff.py::test_fixed_window_stays_constant` | Contention window fixed at $CW_{\min}=15$ |
| **Slot Countdown & Freezing** | `src/simulation/engine.py` | `CsmaSimulator.run()`, lines 111–248 | `tests/test_sim_engine.py::test_timeline_integrity` | Discrete-event clock with $9\,\mu\text{s}$ slot step |
| **RTS/CTS 4-Way Overhead** | `src/simulation/rts_cts.py` | `calculate_transmission_durations()` | Executed in simulator runs | Standard OFDM framing durations |
| **Bianchi Analytical Equations** | `src/simulation/bianchi.py` | `solve_bianchi_tau()`, lines 9–50 | `tests/test_bianchi.py` | Giuseppe Bianchi (IEEE JSAC 2000) equations |
| **Bianchi vs Sim Verification** | `src/simulation/runner.py` | `run_experiment_replications()` | `report_evidence/05_actual_experimental_results.md` | $N \in [2, 25]$ station sweeps ($0.17\% - 1.35\%$ error) |
| **Provenance Taxonomy & Guardrails** | `src/common/provenance.py` | `tag()`, lines 49–71 | Loaded from `config/provenance.yaml` | Strictly enforces `MEASURED`, `DERIVED`, `ASSUMED`, `SIMULATED` |
| **Exportable Project Report** | `src/web/api/evidence.py` | `generate_full_report()`, lines 21–53 | Validated via `test_api_contracts.py` | Delivers structured JSON evidence payload |

---

## 2. Directory Structure of Evidence Package

All generated evidence files are housed in `D:\tracewise\report_evidence\`:
- `01_project_overview.md`: Executive summary, problem definition, objectives, and scope exclusions.
- `02_problem_statement_objectives.md`: Detailed technical motivation, semantic ambiguities, FRs, and NFRs.
- `03_architecture_and_implementation.md`: Mermaid architecture and sequence diagrams, technology stack justification, and component descriptions.
- `04_dataset_and_methodology.md`: In-depth breakdown of the CRAWDAD PAM'09 dataset, schema definitions, and audit results.
- `05_actual_experimental_results.md`: Complete numerical tables for Bianchi validation ($N=2 \dots 25$), Channel 48 vs 157 ranking evidence, and BEB vs Fixed CW performance.
- `06_analysis_and_inference.md`: Technical deductions, avalanche effect of retries, and stability penalty explanations.
- `07_testing_and_validation.md`: Pytest test suite breakdown, line coverage percentages, and audit gap analysis.
- `08_literature_review_and_references.md`: Annotated bibliography (Bianchi 2000, Subramanian et al. 2008 & 2009, Jain's fairness index).
- `09_limitations_and_future_work.md`: Threats to internal/external validity, driver sniffing limitations, and future work.
- `10_report_evidence_index.md`: Traceability matrix and file index.
- `project_report_evidence.md`: Single compiled master evidence package containing all sections in order.
