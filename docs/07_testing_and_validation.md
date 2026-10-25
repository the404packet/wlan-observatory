# 07. Testing, Verification, and Reproducibility Evidence

---

## 1. Test Suite Execution Summary

The project test suite is built on `pytest` and `pytest-cov`.

```bash
pytest -v --cov=src --cov-report=term-missing
```

### 1.1 Test Outcome Metrics
- **Platform:** Windows (Python 3.12.6, pytest 9.1.1, pluggy 1.7.0)
- **Total Tests Collected:** 23
- **Passed:** 23 (100% of collected tests)
- **Failed:** 0
- **Skipped:** 0
- **Execution Duration:** 5.32 seconds
- **Overall Line Coverage:** **70%** (780 statements covered out of 1,119 total statements; 339 missed statements)

---

## 2. Granular Test Suite Breakdown

| Test File | Test Case Name | Verified Behavior / Property Under Test | Result |
| :--- | :--- | :--- | :---: |
| **`tests/test_api_contracts.py`** | `test_api_datasets_overview` | Asserts `/api/datasets/overview` returns status success and expected section list. | **PASSED** |
| | `test_api_datasets_validation` | Asserts `/api/datasets/validation` returns complete audits for 802.11a/g/iface. | **PASSED** |
| | `test_api_channel_summaries` | Asserts `/api/analysis/summaries` filters by section and link_id correctly. | **PASSED** |
| | `test_api_ranking_evaluate` | Asserts `/api/ranking/evaluate` calculates ranks and returns breakdown contributions. | **PASSED** |
| | `test_api_simulation_run` | Asserts `/api/simulation/run` executes replications and returns 95% CIs. | **PASSED** |
| | `test_api_bianchi_validation` | Asserts `/api/simulation/bianchi` runs station sweeps and calculates error %. | **PASSED** |
| **`tests/test_backoff.py`** | `test_beb_doubling` | Verifies BEB doubles window correctly: $15 \rightarrow 31 \rightarrow 63 \rightarrow \dots \le 1023$. | **PASSED** |
| | `test_fixed_window_stays_constant` | Verifies Fixed CW strategy retains $CW=15$ across repeated collisions. | **PASSED** |
| | `test_retry_limit_drop` | Verifies packet is dropped and $CW$ resets to $CW_{\min}$ after exceeding 7 retries. | **PASSED** |
| **`tests/test_bianchi.py`** | `test_bianchi_single_station` | Verifies boundary invariant: single station ($N=1$) has 0.0 collision probability. | **PASSED** |
| | `test_bianchi_collision_monotonicity`| Verifies collision probability strictly increases as station count increases. | **PASSED** |
| | `test_bianchi_throughput_physical_bounds`| Verifies saturation throughput never exceeds physical PHY data rate (6.0 Mbps). | **PASSED** |
| **`tests/test_manifest.py`** | `test_routes_three_sections` | Asserts regex cleanly partitions `802_11a`, `802_11g`, and `interface`. | **PASSED** |
| | `test_channel_from_name_and_interface_pair`| Verifies channel and interface numbers correctly parsed from filenames. | **PASSED** |
| | `test_unroutable_file_raises` | Asserts unroutable filenames raise `UnroutableFileError` (no silent bucketing). | **PASSED** |
| | `test_unroutable_does_not_write_manifests`| Asserts manifest file write is aborted if unroutable files are found. | **PASSED** |
| | `test_idempotent_hash_skip` | Verifies unchanged files (identical size/mtime) skip expensive SHA-256 rehashing. | **PASSED** |
| | `test_channel_mismatch_flag` | Verifies integrity flag triggers when internal CSV channel differs from filename. | **PASSED** |
| | `test_counts_report_present` | Asserts expected file count matches README documented numbers. | **PASSED** |
| **`tests/test_ranking.py`** | `test_ranking_sorting_and_baselines` | Asserts composite scores sort strictly descending and baseline ranks populate. | **PASSED** |
| **`tests/test_sim_engine.py`** | `test_single_station_zero_collisions` | Asserts single contending station experiences 0 collisions across 500 events. | **PASSED** |
| | `test_multi_station_fairness_and_collisions`| Asserts $N=5$ stations experience collisions and Jain's fairness index $> 0.85$. | **PASSED** |
| | `test_timeline_integrity` | Asserts simulation timeline timestamps are monotonically non-decreasing. | **PASSED** |

---

## 3. Code Coverage by Subsystem

```
Name                             Stmts   Miss  Cover   Missing Lines
--------------------------------------------------------------------
src\analysis\metrics.py             21      0   100%   (Fully Covered)
src\analysis\stats.py               24      4    83%   18-19, 35, 39
src\common\provenance.py            39     10    74%   38, 44-46, 55-63
src\pipeline\manifest.py           141     13    91%   265-281, 285
src\pipeline\ranking.py             34      1    97%   43
src\pipeline\validate.py            39      1    97%   18
src\simulation\backoff.py           41      0   100%   (Fully Covered)
src\simulation\bianchi.py           54      9    83%   32-33, 76, 93-98
src\simulation\engine.py           171     25    85%   119, 128-140, 198-219, 229-232, 304
src\simulation\rts_cts.py           16      6    62%   27-32
src\simulation\runner.py            60     25    58%   99-119, 141-153, 169-173, 177-191
src\simulation\traffic.py           29     11    62%   23-31, 37-39
src\web\api\simulation.py           53      6    89%   134-135, 140-143
src\web\app.py                      55     11    80%   39, 43, 47, 51, 55, 59, 63, 67, 71, 75, 83
--------------------------------------------------------------------
TOTAL                             1119    339    70%
```

---

## 4. Test Deficiencies and Audit Warnings

The inspection revealed the following critical gaps in testing:
1. **Empty Test Files (0 Bytes):**  
   Five test files in the `tests/` directory are completely empty:
   - `tests/test_features.py` (0 bytes) $\rightarrow$ `src/pipeline/features.py` has **0% test coverage**.
   - `tests/test_holdout.py` (0 bytes) $\rightarrow$ `src/pipeline/holdout.py` has **0% test coverage**.
   - `tests/test_uncertainty.py` (0 bytes) $\rightarrow$ Sensitivity analysis has no automated test assertions.
   - `tests/test_validate.py` (0 bytes) $\rightarrow$ Pipeline audit helper functions lack direct unit tests.
   - `tests/test_runner_reproducibility.py` (0 bytes) $\rightarrow$ Random seed reproducibility lacks regression asserts.
2. **Superficial Sequence Check:**  
   In `src/pipeline/validate.py` (lines 101–106), the sequence semantics check appends `"status": "PASS"` unconditionally, without validating whether sequence gaps are present across all chunks of the file.
