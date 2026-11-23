#!/usr/bin/env python3
"""Regenerate every AstralCord icon from the masters in tools/astralcord/art/.

    python3 tools/astralcord/icons.py      # needs rsvg-convert and Pillow

Writes the files Serein ships its own artwork in (upstream file names are kept where code or
packaging refers to them):

- packaging/linux/hicolor/*/apps/astralcord.png, scalable astralcord.svg and the
  astralcord-symbolic.svg tray icon
- packaging/windows/Serein.ico (exe + installer icon) and serein.png (window icon)
- assets/brand/serein*.svg/png: master, flat variant, white mark (tinted in the UI and the
  Linux tray), 72px black tray template, 1024px preview
- assets/icons/atlas.png: only the `serein-mark` cell is repainted; every other glyph is kept
- tools/generate-icons.py: the mark's checksum, so a full atlas rebuild still verifies
"""
import hashlib
import io
import pathlib
import re
import struct
import subprocess

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "tools/astralcord/art"
FULL = (ART / "astralcord.svg").read_text()
SMALL = (ART / "astralcord-small.svg").read_text()
# Bold four-point star from the small master: the mark, trimmed to its own bounding box.
STAR = re.search(r'<path d="([^"]+)" fill="#FFFFFF"/>', SMALL).group(1)

MARK = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="724" height="724" viewBox="150 150 724 724" fill="none">\n'
    "  <title>AstralCord mark</title>\n"
    "  <desc>AstralCord star mark, solid silhouette, trimmed to its own bounding box for the icon atlas.</desc>\n"
    f'<path id="astralcord-star" d="{STAR}" fill="#fff"/>\n'
    "</svg>\n"
)
SYMBOLIC = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" fill="none">\n'
    "  <title>AstralCord symbolic icon</title>\n"
    '  <style id="current-color-scheme" type="text/css">.ColorScheme-Text { color: #bebebe; }</style>\n'
    '  <g transform="translate(512 512) scale(1.15) translate(-512 -512)">\n'
    f'    <path d="{STAR}" fill="currentColor" class="ColorScheme-Text"/>\n'
    "  </g>\n"
    "</svg>\n"
)
FLAT = (FULL.replace('fill="url(#bg)"', 'fill="#4A2DB5"')
            .replace('<circle cx="512" cy="512" r="340" fill="url(#glow)"/>\n  ', "")
            .replace('fill="url(#star)"', 'fill="#FFFFFF"'))


def render(svg: str, size: int) -> Image.Image:
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size)],
                         input=svg.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def best(size: int) -> Image.Image:
    return render(SMALL if size <= 48 else FULL, size)


def write_ico(path: pathlib.Path, sizes) -> None:
    """ICO with PNG-compressed entries (Windows Vista and later, rc.exe and NSIS)."""
    blobs = []
    for size in sizes:
        buf = io.BytesIO()
        best(size).save(buf, format="PNG", optimize=True)
        blobs.append((size, buf.getvalue()))
    header = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    entries = data = b""
    for size, blob in blobs:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
        data += blob
    path.write_bytes(header + entries + data)


def main() -> None:
    hicolor = ROOT / "packaging/linux/hicolor"
    for size in (16, 22, 24, 32, 48, 64, 96, 128, 256, 512, 1024):
        best(size).save(hicolor / f"{size}x{size}/apps/astralcord.png", optimize=True)
    (hicolor / "scalable/apps/astralcord.svg").write_text(FULL)
    (hicolor / "scalable/apps/astralcord-symbolic.svg").write_text(SYMBOLIC)

    windows = ROOT / "packaging/windows"
    write_ico(windows / "Serein.ico", (16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256))
    best(256).save(windows / "serein.png", optimize=True)

    brand = ROOT / "assets/brand"
    (brand / "serein.svg").write_text(FULL)
    (brand / "serein-flat.svg").write_text(FLAT)
    (brand / "serein-mark.svg").write_text(MARK)
    render(FULL, 1024).save(brand / "serein-1024.png", optimize=True)
    render(MARK.replace('fill="#fff"', 'fill="#000"'), 72).save(brand / "serein-tray.png", optimize=True)

    # Repaint the mark's 64px cell in the UI icon atlas exactly where tools/generate-icons.py
    # would draw it (56px glyph, 4px padding), leaving every other glyph untouched.
    cell = next(int(line.split("\t")[1]) for line in (ROOT / "assets/icons/index.tsv").read_text().splitlines()
                if line.startswith("serein-mark\t"))
    atlas = Image.open(ROOT / "assets/icons/atlas.png").convert("RGBA")
    x, y = (cell % 8) * 64, (cell // 8) * 64
    atlas.paste((0, 0, 0, 0), (x, y, x + 64, y + 64))
    glyph = render(MARK, 56)
    atlas.alpha_composite(glyph, (x + 4, y + 4))
    atlas.save(ROOT / "assets/icons/atlas.png", optimize=True)

    generator = ROOT / "tools/generate-icons.py"
    digest = hashlib.sha256((brand / "serein-mark.svg").read_bytes()).hexdigest()
    text = re.sub(r'(\("serein-mark", BRAND_MARK, ")[0-9a-f]{64}("\))', rf"\g<1>{digest}\g<2>", generator.read_text())
    generator.write_text(text)
    print(f"icons written; atlas cell {cell} repainted; mark sha256 {digest[:12]}…")


if __name__ == "__main__":
    main()
