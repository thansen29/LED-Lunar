#!/usr/bin/env python3
"""Write preview/gingerbread.html: the 32x32 panel as LED dots, still and waving.

Built from src/gingerbread_art.py, so it shows the same pixels the Pi draws (decisions 9, 11).
Usage: python3 scripts/preview_gingerbread.py [--png assets/gingerbread-preview.png]
  --png also writes a picture of the still and raised-hand frames, for the README.
"""
import argparse
import json
import os
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import gingerbread_art as art  # noqa: E402

OUT = os.path.join(ROOT, "preview", "gingerbread.html")

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gingerbread man, 32x32 LED preview</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; padding: 24px; background: #111; color: #ddd;
         font: 15px/1.5 system-ui, -apple-system, sans-serif; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  p { margin: 0 0 20px; color: #aaa; max-width: 60em; }
  .row { display: flex; flex-wrap: wrap; gap: 28px; align-items: flex-start; }
  figure { margin: 0; }
  figcaption { margin-top: 8px; font-family: ui-monospace, Menlo, monospace; font-size: 13px; color: #bbb; }
  canvas { display: block; background: #050505; border: 6px solid #222; border-radius: 6px; }
  canvas.large { width: min(448px, 86vw); height: auto; }
  canvas.small { width: 224px; height: auto; }
  button { margin-top: 8px; background: #2a2a2a; color: #eee; border: 1px solid #444;
           border-radius: 4px; padding: 4px 12px; font: inherit; cursor: pointer; }
  h2 { font-size: 16px; margin: 32px 0 10px; }
</style>
</head>
<body>
<h1>Gingerbread man on a 32x32 LED panel</h1>
<p>Generated from <code>src/gingerbread_art.py</code>, so these are the exact pixels the Pi draws.
Colours are screen colours: real LEDs at low brightness look different, so judge the shapes here
and the colours on the panel.</p>
<div class="row">
  <figure><canvas id="still" class="large"></canvas>
    <figcaption>--mode still</figcaption></figure>
  <figure><canvas id="wave" class="large"></canvas>
    <figcaption>--mode wave &middot; pose <span id="pose"></span></figcaption>
    <button id="pause" type="button">Pause</button></figure>
</div>
<h2>Arm poses</h2>
<div class="row" id="poses"></div>
<script>
const D = __DATA__;
const CELL = 14;
function draw(canvas, rows) {
  canvas.width = canvas.height = D.size * CELL;
  const g = canvas.getContext("2d");
  g.fillStyle = "#050505";
  g.fillRect(0, 0, canvas.width, canvas.height);
  for (let y = 0; y < D.size; y++) {
    for (let x = 0; x < D.size; x++) {
      const ch = rows[y][x];
      g.fillStyle = ch === "." ? "#1a1a1a" : D.palette[ch];
      g.beginPath();
      g.arc(x * CELL + CELL / 2, y * CELL + CELL / 2, CELL * 0.4, 0, 2 * Math.PI);
      g.fill();
    }
  }
}
draw(document.getElementById("still"), D.frames[D.still]);
const posesEl = document.getElementById("poses");
for (const [name, rows] of Object.entries(D.frames)) {
  const fig = document.createElement("figure");
  const c = document.createElement("canvas");
  c.className = "small";
  draw(c, rows);
  const cap = document.createElement("figcaption");
  cap.textContent = name;
  fig.append(c, cap);
  posesEl.append(fig);
}
const waveEl = document.getElementById("wave");
const poseEl = document.getElementById("pose");
let step = 0, timer = null;
function tick() {
  const [pose, seconds] = D.wave[step];
  draw(waveEl, D.frames[pose]);
  poseEl.textContent = pose + " (" + seconds + " s)";
  step = (step + 1) % D.wave.length;
  timer = setTimeout(tick, seconds * 1000);
}
document.getElementById("pause").addEventListener("click", (e) => {
  if (timer === null) { tick(); e.target.textContent = "Pause"; }
  else { clearTimeout(timer); timer = null; e.target.textContent = "Play"; }
});
tick();
</script>
</body>
</html>
"""


def build_html() -> str:
    data = {
        "size": art.SIZE,
        "palette": {k: "#%02x%02x%02x" % rgb for k, rgb in art.PALETTE.items()},
        "frames": {pose: list(art.frame(pose)) for pose in art.ARM_POSES},
        "still": art.STILL_POSE,
        "wave": [[pose, seconds] for pose, seconds in art.WAVE_STEPS],
    }
    return TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))


PNG_FRAMES = (art.STILL_POSE, "high")
CELL, PAD, GAP = 12, 16, 24
PAGE_RGB, PANEL_RGB, UNLIT_RGB = (17, 17, 17), (5, 5, 5), (26, 26, 26)


def _dot_coverage(cell: int) -> list:
    """Share of each pixel in a cell covered by the LED dot, from 4x4 samples (smooth edges)."""
    centre, radius, cov = cell / 2, cell * 0.4, []
    for py in range(cell):
        row = []
        for px in range(cell):
            hits = sum((px + (i + 0.5) / 4 - centre) ** 2 + (py + (j + 0.5) / 4 - centre) ** 2 <= radius ** 2
                       for i in range(4) for j in range(4))
            row.append(hits / 16)
        cov.append(row)
    return cov


def build_png(layers) -> bytes:
    """Draw layers side by side as LED dots and return PNG bytes. Standard library only."""
    side = art.SIZE * CELL
    width, height = PAD * 2 + side * len(layers) + GAP * (len(layers) - 1), PAD * 2 + side
    img = [bytearray(PAGE_RGB * width) for _ in range(height)]
    cov = _dot_coverage(CELL)
    for n, layer in enumerate(layers):
        ox = PAD + n * (side + GAP)
        for y, row in enumerate(layer):
            for x, ch in enumerate(row):
                dot = UNLIT_RGB if ch == art.CLEAR else art.PALETTE[ch]
                for py in range(CELL):
                    line = img[PAD + y * CELL + py]
                    for px in range(CELL):
                        a = cov[py][px]
                        i = (ox + x * CELL + px) * 3
                        line[i:i + 3] = bytes(round(d * a + p * (1 - a)) for d, p in zip(dot, PANEL_RGB))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    raw = b"".join(b"\x00" + bytes(line) for line in img)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--png", metavar="PATH", help="also write a PNG of the still and raised-hand frames")
    args = parser.parse_args()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build_html())
    print(OUT)
    if args.png:
        with open(args.png, "wb") as f:
            f.write(build_png([art.frame(pose) for pose in PNG_FRAMES]))
        print(args.png)


if __name__ == "__main__":
    main()
