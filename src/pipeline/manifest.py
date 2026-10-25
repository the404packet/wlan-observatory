"""Stage 0: build provenance-aware manifests for the CRAWDAD dataset.

For each CSV under data/raw/, this produces an entry with:
  - section, band, link_id, channel_from_name (or interface_pair)
  - sha256, size, mtime
  - schema sample (first SAMPLE_ROWS rows)
  - cheap integrity flags computed on that sample

Idempotent: unchanged files (same sha256) are not re-hashed.
Unroutable files raise UnroutableFileError — nothing is silently bucketed.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import settings

log = logging.getLogger(__name__)


class UnroutableFileError(RuntimeError):
    """Raised when a file does not match any of the three known filename patterns."""


# (regex, section, band) — matched against path relative to DATA_RAW
_ROUTES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"^802_11a/link-(?P<link>\d+)-channel-(?P<channel>\d+)\.csv$"),
     "802_11a", "5GHz"),
    (re.compile(r"^802_11g/link-(?P<link>\d+)-channel-(?P<channel>\d+)\.csv$"),
     "802_11g", "2.4GHz"),
    (re.compile(r"^interface/link-(?P<link>\d+)-interface-(?P<iface>\d+)-(?P<sub>\d+)\.csv$"),
     "interface", "unknown"),
]


@dataclass
class ManifestEntry:
    path: str                          # relative to DATA_RAW
    section: str
    band: str
    link_id: int
    channel_from_name: int | None      # None for interface files
    interface_pair: str | None         # "I-J" for interface files, else None
    size_bytes: int
    sha256: str
    mtime: str
    schema_sample: dict
    integrity_flags: dict


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _route(rel: str) -> tuple[str, str, dict]:
    for pat, section, band in _ROUTES:
        m = pat.match(rel)
        if m:
            return section, band, m.groupdict()
    raise UnroutableFileError(f"file does not match any known pattern: {rel}")


def _sample_schema(path: Path) -> tuple[pd.DataFrame, dict]:
    """Read only the first SAMPLE_ROWS rows to infer schema and integrity."""
    df = pd.read_csv(
        path,
        header=None,
        names=list(settings.EXPECTED_COLUMNS),
        nrows=settings.SAMPLE_ROWS,
        dtype=str,            # read as strings to inspect raw shape safely
        keep_default_na=False,
        na_values=[""],
        engine="c",
    )
    schema = {
        "n_rows_read": int(len(df)),
        "header_present": False,
        "delimiter": ",",
        "column_count": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes_inferred": {c: str(df[c].dtype) for c in df.columns},
    }
    return df, schema


def _integrity_flags(
    df: pd.DataFrame,
    section: str,
    channel_from_name: int | None,
) -> dict:
    flags: dict[str, bool | str] = {}

    # Column count + order
    flags["column_count_is_8"] = df.shape[1] == 8
    flags["column_order_matches_readme"] = list(df.columns) == list(settings.EXPECTED_COLUMNS)

    # Channel in data vs channel in filename (only for channel-patterned sections)
    if channel_from_name is not None and "channel" in df:
        chan_numeric = pd.to_numeric(df["channel"], errors="coerce")
        unique_channels = sorted(chan_numeric.dropna().unique().tolist())
        flags["channel_unique_in_sample"] = len(unique_channels) == 1
        flags["channel_field_matches_name"] = (
            len(unique_channels) == 1 and int(unique_channels[0]) == channel_from_name
        )
    else:
        # interface section: readme says channel 64 only; assert on the sample
        if "channel" in df:
            chan_numeric = pd.to_numeric(df["channel"], errors="coerce").dropna()
            flags["interface_channel_all_64"] = bool((chan_numeric == 64).all())

    # SNR == RSS − noise (arithmetic identity check on the sample)
    try:
        snr = pd.to_numeric(df["snr"], errors="coerce")
        rss = pd.to_numeric(df["rss"], errors="coerce")
        noise = pd.to_numeric(df["noise"], errors="coerce")
        diff = (rss - noise)
        flags["snr_equals_rss_minus_noise"] = bool((snr == diff).all())
    except Exception:  # pragma: no cover - defensive
        flags["snr_equals_rss_minus_noise"] = False

    # 12-bit seq wrap: record min/max of the sample; do not claim wrap from a sample
    try:
        seq = pd.to_numeric(df["seq"], errors="coerce").dropna()
        if len(seq):
            flags["seq_min_in_sample"] = int(seq.min())
            flags["seq_max_in_sample"] = int(seq.max())
            flags["seq_within_12bit_range"] = bool(seq.between(0, 4095).all())
    except Exception:  # pragma: no cover
        pass

    # Timestamps monotonic in the sample
    try:
        ts = pd.to_numeric(df["timestamp"], errors="coerce").dropna()
        if len(ts) >= 2:
            flags["timestamps_monotonic_in_sample"] = bool(ts.is_monotonic_increasing)
            deltas = ts.diff().dropna()
            flags["timestamp_median_delta"] = float(deltas.median()) if len(deltas) else 0.0
    except Exception:  # pragma: no cover
        pass

    return flags


def _load_existing(out_dir: Path, section: str) -> dict[str, dict]:
    """Load existing manifest entries for a section, keyed by relative path."""
    f = out_dir / f"{section}.manifest.json"
    if not f.exists():
        return {}
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {e["path"]: e for e in data.get("files", [])}


def _walk_raw(raw_dir: Path) -> Iterable[Path]:
    ignored = {"Readme", "README", "README.md", "FIELD_SEMANTICS.md", ".gitkeep"}
    for p in sorted(raw_dir.rglob("*")):
        if p.is_file() and p.name not in ignored:
            yield p


def build_manifests(raw_dir: Path, out_dir: Path) -> list[Path]:
    raw_dir = Path(raw_dir).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    existing: dict[str, dict[str, dict]] = {
        s: _load_existing(out_dir, s) for s in settings.SECTIONS
    }
    by_section: dict[str, list[ManifestEntry]] = {s: [] for s in settings.SECTIONS}
    hashes_computed = 0
    hashes_skipped = 0

    for path in _walk_raw(raw_dir):
        rel = path.relative_to(raw_dir).as_posix()
        try:
            section, band, groups = _route(rel)
        except UnroutableFileError:
            log.error("unroutable file, refusing to bucket silently: %s", rel)
            raise

        prev = existing.get(section, {}).get(rel)
        size = path.stat().st_size
        mtime = datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).isoformat()

        # Hash-skip: re-use prior sha256 when size+mtime match AND manifest version matches.
        if (
            prev is not None
            and prev.get("size_bytes") == size
            and prev.get("mtime") == mtime
            and prev.get("manifest_version") == settings.MANIFEST_VERSION
        ):
            sha = prev["sha256"]
            schema_sample = prev["schema_sample"]
            integrity_flags = prev["integrity_flags"]
            hashes_skipped += 1
            log.debug("hash-skip: %s", rel)
        else:
            sha = _sha256(path)
            hashes_computed += 1
            df, schema_sample = _sample_schema(path)
            channel_from_name = int(groups["channel"]) if "channel" in groups else None
            integrity_flags = _integrity_flags(df, section, channel_from_name)

        entry = ManifestEntry(
            path=rel,
            section=section,
            band=band,
            link_id=int(groups["link"]),
            channel_from_name=int(groups["channel"]) if "channel" in groups else None,
            interface_pair=(
                f"{groups['iface']}-{groups['sub']}" if "iface" in groups else None
            ),
            size_bytes=size,
            sha256=sha,
            mtime=mtime,
            schema_sample=schema_sample,
            integrity_flags=integrity_flags,
        )
        by_section[section].append(entry)

    written: list[Path] = []
    for section, entries in by_section.items():
        payload = {
            "manifest_version": settings.MANIFEST_VERSION,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "section": section,
            "expected_file_count": settings.EXPECTED_FILE_COUNTS.get(section),
            "observed_file_count": len(entries),
            "counts_match_expected": (
                len(entries) == settings.EXPECTED_FILE_COUNTS.get(section)
            ),
            "files": [
                {**asdict(e), "manifest_version": settings.MANIFEST_VERSION}
                for e in entries
            ],
        }
        out = out_dir / f"{section}.manifest.json"
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
        written.append(out)

    log.info(
        "manifests written: %s | hashes computed=%d skipped=%d",
        [w.name for w in written], hashes_computed, hashes_skipped,
    )
    return written


def _main() -> None:
    import argparse
    import logging.config

    import yaml

    parser = argparse.ArgumentParser(description="Build Stage-0 manifests for CRAWDAD dataset")
    parser.add_argument("--raw", default=str(settings.DATA_RAW))
    parser.add_argument("--out", default=str(settings.DATA_MANIFESTS))
    parser.add_argument("--log-config", default=str(settings.BASE_DIR / "config" / "logging.yaml"))
    args = parser.parse_args()

    # Ensure log dir exists before dictConfig tries to open the file handler
    (settings.BASE_DIR / "data" / "logs").mkdir(parents=True, exist_ok=True)
    with open(args.log_config, "r", encoding="utf-8") as fh:
        logging.config.dictConfig(yaml.safe_load(fh))

    build_manifests(Path(args.raw), Path(args.out))


if __name__ == "__main__":
    _main()