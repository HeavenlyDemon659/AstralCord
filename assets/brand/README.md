# AstralCord brand assets

AstralCord's mark is a four-point "astral" star, shown white on a deep-violet disc with a faint
orbit ring in the full-colour icon. The masters live in `astralcord/art/`, and
`python3 astralcord/icons.py` regenerates every file below (and the packaged icons) from them.
The upstream Serein file names are kept because code and packaging refer to them.

- `serein.svg`: the full-colour AstralCord icon, the master vector source.
- `serein-flat.svg`: flat (non-gradient) variant for small or low-colour contexts.
- `serein-mark.svg`: solid white star silhouette, with the view box trimmed to its bounding box.
  `tools/generate-icons.py` rasterizes it into the shared icon atlas as `serein-mark`, and the
  interface tints it at draw time. The Linux tray recolours it to the panel theme.
- `serein-1024.png`: 1024×1024 RGBA preview render of the full-colour icon.
- `serein-tray.png`: 72×72 black-on-transparent render of the mark, used as the macOS menu bar
  template and as the Linux tray's pixel fallback.

The packaged platform icons built from the same artwork live in `packaging/`:
`windows/Serein.ico`, `windows/serein.png`, and `linux/hicolor/*/apps/astralcord*`.

Palette: `#1A1240` → `#4A2DB5` → `#8E63F7` disc gradient, with a white star.
