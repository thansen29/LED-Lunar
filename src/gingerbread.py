#!/usr/bin/env python3
"""Show the gingerbread man on the LED matrix (decisions 1, 2, 5).

  sudo python3 src/gingerbread.py [--mode still|wave] <usual --led-* flags>
"""
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_ROOT)
from submodules.matrix.bindings.python.samples.samplebase import SampleBase  # noqa: E402

import gingerbread_art as art  # noqa: E402  (same folder as this script)


class Gingerbread(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Gingerbread, self).__init__(*args, **kwargs)
        self.parser.add_argument(
            "--mode", choices=("still", "wave"), default="still",
            help="still: hold the picture. wave: slowly wave one hand. Default: still")

    def run(self) -> None:
        if self.matrix.width < art.SIZE or self.matrix.height < art.SIZE:
            sys.exit(f"The art needs a {art.SIZE}x{art.SIZE} panel; this one is "
                     f"{self.matrix.width}x{self.matrix.height}. Check --led-rows and --led-cols.")
        canvas = self.matrix.CreateFrameCanvas()
        if self.args.mode == "still":
            self.show(canvas, art.frame(art.STILL_POSE))
            while True:  # the panel goes dark when this process exits
                time.sleep(60)
        frames = {pose: art.frame(pose) for pose in art.ARM_POSES}
        while True:
            for pose, seconds in art.WAVE_STEPS:
                canvas = self.show(canvas, frames[pose])
                time.sleep(seconds)

    def show(self, canvas, layer):
        """Draw a frame off-screen, swap it in, and return the canvas to draw on next."""
        canvas.Clear()
        for x, y, (r, g, b) in art.pixels(layer):
            canvas.SetPixel(x, y, r, g, b)
        return self.matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    GINGERBREAD = Gingerbread()
    if not GINGERBREAD.process():
        GINGERBREAD.print_help()
