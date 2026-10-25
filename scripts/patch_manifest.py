import pathlib

p = pathlib.Path("src/pipeline/manifest.py")
content = p.read_text(encoding="utf-8")

old_code = """def _walk_raw(raw_dir: Path) -> Iterable[Path]:
    for p in sorted(raw_dir.rglob("*")):
        if p.is_file():
            yield p"""

new_code = """def _walk_raw(raw_dir: Path) -> Iterable[Path]:
    ignored = {"Readme", "README", "README.md", "FIELD_SEMANTICS.md", ".gitkeep"}
    for p in sorted(raw_dir.rglob("*")):
        if p.is_file() and p.name not in ignored:
            yield p"""

if old_code in content:
    p.write_text(content.replace(old_code, new_code), encoding="utf-8")
    print("Successfully patched manifest.py")
else:
    print("Old code not found in manifest.py")
