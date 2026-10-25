import pathlib, re

pages_dir = pathlib.Path("templates/pages")
banner_pattern = re.compile(r'[ \t]*<div class="disclaimer-banner">.*?</div>\s*', re.DOTALL)

for f in sorted(pages_dir.glob("*.html")):
    text = f.read_text(encoding="utf-8")
    new_text = banner_pattern.sub("", text)
    if new_text != text:
        f.write_text(new_text, encoding="utf-8")
        print(f"Cleaned: {f.name}")
    else:
        print(f"No banner: {f.name}")
