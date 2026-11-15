"""Tests for the pure gingerbread art module. Runs without LED hardware: sh scripts/test"""
import importlib.util
import json
import os
import py_compile
import struct
import sys
import unittest
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import gingerbread_art as art  # noqa: E402

HEAD_ROWS = range(0, 10)
FEATURES = "wgr"  # icing, bow tie, buttons


def blank():
    return [art.CLEAR * art.SIZE for _ in range(art.SIZE)]


class ArtTest(unittest.TestCase):
    def test_every_layer_is_valid(self):
        art.validate_layer("BODY", art.BODY)
        for name, layer in art.ARM_POSES.items():
            art.validate_layer(name, layer)

    def test_still_frame_is_mirror_symmetric(self):
        for y, row in enumerate(art.frame(art.STILL_POSE)):
            self.assertEqual(row, row[::-1], f"row {y} is not symmetric")

    def test_arm_never_draws_over_the_head(self):
        for name, layer in art.ARM_POSES.items():
            for y in HEAD_ROWS:
                for x in range(art.SIZE):
                    if art.BODY[y][x] != art.CLEAR:
                        self.assertEqual(layer[y][x], art.CLEAR, f"{name} covers head cell ({x}, {y})")

    def test_arm_never_covers_face_bow_buttons_or_icing(self):
        for name, layer in art.ARM_POSES.items():
            for y in range(art.SIZE):
                for x in range(art.SIZE):
                    if art.BODY[y][x] in FEATURES:
                        self.assertEqual(layer[y][x], art.CLEAR, f"{name} covers ({x}, {y})")

    def test_every_pose_frame_differs(self):
        frames = [art.frame(p) for p in art.ARM_POSES]
        self.assertEqual(len(set(frames)), len(frames))

    def test_wave_timing_is_the_tuned_value(self):
        # Decision 7. Change it deliberately, here and in the decision log together.
        self.assertEqual(art.WAVE_STEPS, (
            ("rest", 1.6), ("half", 0.45), ("high", 0.7),
            ("half", 0.45), ("high", 0.7), ("half", 0.45),
        ))


class ValidatorTest(unittest.TestCase):
    def test_rejects_wrong_row_count(self):
        with self.assertRaisesRegex(ValueError, "has 31 rows, needs 32"):
            art.validate_layer("x", blank()[:31])

    def test_rejects_short_row(self):
        layer = blank()
        layer[5] = layer[5][:-1]
        with self.assertRaisesRegex(ValueError, "row 5: has 31 characters"):
            art.validate_layer("x", layer)

    def test_rejects_unknown_colour_and_names_the_cell(self):
        layer = blank()
        layer[7] = layer[7][:3] + "z" + layer[7][4:]
        with self.assertRaisesRegex(ValueError, "row 7 column 3: 'z'"):
            art.validate_layer("x", layer)

    def test_wave_rejects_skipping_a_pose(self):
        with self.assertRaisesRegex(ValueError, "rest -> high"):
            art.validate_wave((("rest", 1.0), ("high", 1.0), ("half", 1.0)))

    def test_wave_rejects_skip_on_wrap_around(self):
        with self.assertRaisesRegex(ValueError, "high -> rest"):
            art.validate_wave((("rest", 1.0), ("half", 1.0), ("high", 1.0)))

    def test_wave_rejects_unknown_pose_zero_seconds_and_empty(self):
        with self.assertRaisesRegex(ValueError, "unknown pose 'wiggle'"):
            art.validate_wave((("rest", 1.0), ("wiggle", 1.0)))
        with self.assertRaisesRegex(ValueError, "must be more than 0"):
            art.validate_wave((("rest", 1.0), ("half", 0)))
        with self.assertRaisesRegex(ValueError, "no steps"):
            art.validate_wave(())

    def test_frame_rejects_unknown_pose(self):
        with self.assertRaisesRegex(ValueError, "unknown pose 'wiggle'"):
            art.frame("wiggle")


class DrawingTest(unittest.TestCase):
    def test_compose_lets_base_show_through(self):
        self.assertEqual(art.compose(("ab.",), ("..w",)), ("abw",))

    def test_pixels_skips_clear_cells_and_maps_palette(self):
        layer = art.frame(art.STILL_POSE)
        lit = list(art.pixels(layer))
        self.assertEqual(len(lit), sum(ch != art.CLEAR for row in layer for ch in row))
        self.assertIn((15, 14, art.PALETTE["r"]), lit)  # top button


class ScriptsTest(unittest.TestCase):
    def test_runner_compiles(self):
        # The runner needs rgbmatrix to run, so only its syntax is checked here.
        py_compile.compile(os.path.join(ROOT, "src", "gingerbread.py"), doraise=True)

    def load_preview(self):
        path = os.path.join(ROOT, "scripts", "preview_gingerbread.py")
        spec = importlib.util.spec_from_file_location("preview_gingerbread", path)
        preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        return preview

    def test_png_decodes_to_the_expected_size_and_colours(self):
        preview = self.load_preview()
        png = preview.build_png([art.frame(art.STILL_POSE)])
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", png[16:24])
        side = art.SIZE * preview.CELL + 2 * preview.PAD
        self.assertEqual((width, height), (side, side))
        idat_len = struct.unpack(">I", png[33:37])[0]
        raw = zlib.decompress(png[41:41 + idat_len])
        self.assertEqual(len(raw), height * (1 + width * 3))
        # centre of the top-left button's dot is pure button red
        x = preview.PAD + 15 * preview.CELL + preview.CELL // 2
        y = preview.PAD + 14 * preview.CELL + preview.CELL // 2
        i = y * (1 + width * 3) + 1 + x * 3
        self.assertEqual(tuple(raw[i:i + 3]), art.PALETTE["r"])

    def test_preview_embeds_every_frame_and_the_wave(self):
        html = self.load_preview().build_html()
        data = json.loads(html.split("const D = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(data["frames"], {p: list(art.frame(p)) for p in art.ARM_POSES})
        self.assertEqual(data["wave"], [list(s) for s in art.WAVE_STEPS])
        self.assertEqual(data["still"], art.STILL_POSE)


if __name__ == "__main__":
    unittest.main()
