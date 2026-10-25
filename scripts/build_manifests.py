"""Shim so `python scripts/build_manifests.py` works without `-m src.pipeline.manifest`."""
from src.pipeline.manifest import _main

if __name__ == "__main__":
    _main()