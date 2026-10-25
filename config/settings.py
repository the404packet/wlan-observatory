"""Central configuration. Paths resolved from __file__ so `make` works from any CWD."""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field


BASE_DIR: Path = Path(__file__).resolve().parent.parent

DATA_RAW: Path = BASE_DIR / "data" / "raw"
DATA_INTERIM: Path = BASE_DIR / "data" / "interim"
DATA_PROCESSED: Path = BASE_DIR / "data" / "processed"
DATA_SIM_RUNS: Path = DATA_PROCESSED / "sim_runs"
DATA_MANIFESTS: Path = BASE_DIR / "data" / "manifests"

# Section names must match the top-level folders under DATA_RAW exactly.
SECTIONS: tuple[str, ...] = ("802_11a", "802_11g", "interface")

# Chunk size for CSV reads. Trade-off: memory vs throughput.
# 200_000 rows ~ a few MB in pandas per chunk; tune after profiling on the real dataset.
CHUNK_SIZE: int = 200_000

# Bump when manifest schema changes; forces re-hash on next build.
MANIFEST_VERSION: int = 1

# Timestamp units per section. "?" means UNVERIFIED.
# validate.py MUST refuse to compute any window-based feature while any value is "?".
# The CRAWDAD readme does not state the unit; samples are consistent with microseconds
# (~1.9 ms/frame on 802_11a), but this must be confirmed, not assumed.
TIMESTAMP_UNIT_PER_SECTION: dict[str, str] = {
    "802_11a": "?",       # likely "us" — confirm against PAM 2009 paper or CRAWDAD readme
    "802_11g": "?",       # likely "us"
    "interface": "?",     # likely "us"
}

# Expected file counts per section, from CRAWDAD readme:
#   (i)   802_11a: 78 links × 13 channels = 1014 files
#   (ii)  802_11g: 54 links × 3 channels  = 162 files
#   (iii) interface: 20 links × 16 iface-pairs = 320 files
EXPECTED_FILE_COUNTS: dict[str, int] = {
    "802_11a": 1014,
    "802_11g": 162,
    "interface": 320,
}

# The 8-column schema, in the exact order stated by the CRAWDAD readme:
#   <MAC_TIME_STAMP>,<PACKET_TYPE>,<CHANNEL>,<SNR>,<RSS>,<NOISE>,<DATA_RATE>,<MAC_SEQUENCE_NUMBERS>
EXPECTED_COLUMNS: tuple[str, ...] = (
    "timestamp", "packet_type", "channel", "snr",
    "rss", "noise", "data_rate", "seq",
)

# Number of rows read per file during Stage 0 manifest build (schema + integrity sample).
SAMPLE_ROWS: int = 200


def ensure_dirs() -> None:
    for p in (DATA_RAW, DATA_INTERIM, DATA_PROCESSED, DATA_SIM_RUNS, DATA_MANIFESTS):
        p.mkdir(parents=True, exist_ok=True)