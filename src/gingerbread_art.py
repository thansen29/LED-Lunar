"""Gingerbread man pixel art for a 32x32 LED panel (decisions 1-6, docs/decisions.md).

Words used here:
  layer  32 rows of 32 characters. Each character is a PALETTE key; "." is see-through.
  pose   one position of the waving arm, stored as an arm layer.
  frame  what the panel shows: BODY with one arm layer drawn on top.

Pure module: it never imports rgbmatrix, so tests and the preview run anywhere.
"""

from typing import Dict, Iterator, Sequence, Tuple

Layer = Tuple[str, ...]
RGB = Tuple[int, int, int]

SIZE = 32
CLEAR = "."

# Picked on a screen, not yet on the LEDs (decision 8).
PALETTE: Dict[str, RGB] = {
    "o": (140, 30, 20),    # outline
    "b": (205, 110, 40),   # cookie
    "w": (255, 240, 215),  # icing, eyes, smile
    "g": (20, 140, 50),    # bow tie
    "r": (230, 30, 30),    # buttons
}

# Everything except the arm on the viewer's right, which comes from a pose.
BODY: Layer = (
    ".............oooooo.............",  # 0
    "............obbbbbbo............",  # 1
    "...........obwwbbwwbo...........",  # 2
    "..........obwbbbbbbwbo..........",  # 3
    "..........obbbwbbwbbbo..........",  # 4
    "..........obbbwbbwbbbo..........",  # 5
    "..........obbbbbbbbbbo..........",  # 6
    "..........obbwbbbbwbbo..........",  # 7
    ".....oo....obbwwwwbbo...........",  # 8
    "....obwooo.obbbbbbbbo...........",  # 9
    "...obbbwbbobbggbbggo............",  # 10
    "...obbwbbbbbbggggggbo...........",  # 11
    "...obbbwbbbbbggbbggbbo..........",  # 12
    "....obwbbbbbbbbbbbbbbo..........",  # 13
    ".....oobbbbbbbbrrbbbbo..........",  # 14
    ".......oobbbbbbrrbbbbo..........",  # 15
    ".........obbbbbbbbbbbo..........",  # 16
    "..........obbbbbbbbbbo..........",  # 17
    "..........obbbbrrbbbbo..........",  # 18
    "..........obbbbrrbbbbo..........",  # 19
    "..........obbbbbbbbbbo..........",  # 20
    "..........obbbbbbbbbbo..........",  # 21
    ".........obbbbbrrbbbbbo.........",  # 22
    "........obbbbbbrrbbbbbbo........",  # 23
    ".......obbbbbbbbbbbbbbbbo.......",  # 24
    ".....oobbbbbbbboobbbbbbbboo.....",  # 25
    "....obwbwbbbbbo..obbbbbwbwbo....",  # 26
    "....obbwbwbwbo....obwbwbwbbo....",  # 27
    "....obbbbbwbo......obwbbbbbo....",  # 28
    "....obbbbbbbo......obbbbbbbo....",  # 29
    ".....oobbbbo........obbbboo.....",  # 30
    ".......oooo..........oooo.......",  # 31
)

_ARM_REST: Layer = (
    "................................",  # 0
    "................................",  # 1
    "................................",  # 2
    "................................",  # 3
    "................................",  # 4
    "................................",  # 5
    "................................",  # 6
    "................................",  # 7
    ".........................oo.....",  # 8
    "......................ooowbo....",  # 9
    "...................bbobbwbbbo...",  # 10
    "....................bbbbbwbbo...",  # 11
    ".....................bbbwbbbo...",  # 12
    ".....................bbbbwbo....",  # 13
    ".....................bbbboo.....",  # 14
    ".....................bboo.......",  # 15
    ".....................bo.........",  # 16
    "................................",  # 17
    "................................",  # 18
    "................................",  # 19
    "................................",  # 20
    "................................",  # 21
    "................................",  # 22
    "................................",  # 23
    "................................",  # 24
    "................................",  # 25
    "................................",  # 26
    "................................",  # 27
    "................................",  # 28
    "................................",  # 29
    "................................",  # 30
    "................................",  # 31
)

_ARM_HALF: Layer = (
    "................................",  # 0
    "................................",  # 1
    "................................",  # 2
    "................................",  # 3
    "................................",  # 4
    "................................",  # 5
    "................................",  # 6
    ".......................ooooo....",  # 7
    "......................obbwbbo...",  # 8
    ".....................obbwbbbo...",  # 9
    "...................bbbbbbwbbo...",  # 10
    "....................bbbbwbbbo...",  # 11
    ".....................bbbbwoo....",  # 12
    ".....................bbboo......",  # 13
    ".....................bbo........",  # 14
    ".....................bo.........",  # 15
    "................................",  # 16
    "................................",  # 17
    "................................",  # 18
    "................................",  # 19
    "................................",  # 20
    "................................",  # 21
    "................................",  # 22
    "................................",  # 23
    "................................",  # 24
    "................................",  # 25
    "................................",  # 26
    "................................",  # 27
    "................................",  # 28
    "................................",  # 29
    "................................",  # 30
    "................................",  # 31
)

_ARM_HIGH: Layer = (
    "................................",  # 0
    "................................",  # 1
    "................................",  # 2
    "................................",  # 3
    "................................",  # 4
    "........................oo......",  # 5
    "......................oowbo.....",  # 6
    "......................bwbbbo....",  # 7
    ".....................bbbwbbo....",  # 8
    ".....................bbwbbbo....",  # 9
    "...................bbbbbwbbo....",  # 10
    "....................bbbwbbo.....",  # 11
    ".....................bbbbo......",  # 12
    ".....................bbbo.......",  # 13
    ".....................boo........",  # 14
    "................................",  # 15
    "................................",  # 16
    "................................",  # 17
    "................................",  # 18
    "................................",  # 19
    "................................",  # 20
    "................................",  # 21
    "................................",  # 22
    "................................",  # 23
    "................................",  # 24
    "................................",  # 25
    "................................",  # 26
    "................................",  # 27
    "................................",  # 28
    "................................",  # 29
    "................................",  # 30
    "................................",  # 31
)

ARM_POSES: Dict[str, Layer] = {
    "rest": _ARM_REST,  # mirror of the left arm
    "half": _ARM_HALF,  # raised about 30 degrees
    "high": _ARM_HIGH,  # raised about 45 degrees, behind the head (decision 6)
}

STILL_POSE = "rest"

# One wave as (pose, seconds), repeated forever. Tuned by eye in the preview (decision 7).
WAVE_STEPS: Tuple[Tuple[str, float], ...] = (
    ("rest", 1.6),
    ("half", 0.45),
    ("high", 0.7),
    ("half", 0.45),
    ("high", 0.7),
    ("half", 0.45),
)


def validate_layer(name: str, layer: Sequence[str]) -> None:
    """Raise ValueError naming the first row or cell that is wrong."""
    if len(layer) != SIZE:
        raise ValueError(f"{name}: has {len(layer)} rows, needs {SIZE}")
    for y, row in enumerate(layer):
        if len(row) != SIZE:
            raise ValueError(f"{name} row {y}: has {len(row)} characters, needs {SIZE}")
        for x, ch in enumerate(row):
            if ch != CLEAR and ch not in PALETTE:
                raise ValueError(f"{name} row {y} column {x}: {ch!r} is not a PALETTE key")


def validate_wave(steps: Sequence[Tuple[str, float]]) -> None:
    """Raise ValueError unless the arm moves one pose at a time, wrap-around included."""
    if not steps:
        raise ValueError("wave has no steps")
    order = list(ARM_POSES)
    for i, (pose, seconds) in enumerate(steps):
        if pose not in ARM_POSES:
            raise ValueError(f"wave step {i}: unknown pose {pose!r}")
        if not seconds > 0:
            raise ValueError(f"wave step {i}: {seconds} seconds must be more than 0")
    for i, (pose, _) in enumerate(steps):
        nxt = steps[(i + 1) % len(steps)][0]
        if abs(order.index(pose) - order.index(nxt)) != 1:
            raise ValueError(f"wave step {i}: {pose} -> {nxt} must move to a neighbouring pose")


def compose(base: Sequence[str], top: Sequence[str]) -> Layer:
    """Draw top over base; "." in top lets base show through."""
    return tuple(
        "".join(b if t == CLEAR else t for b, t in zip(base_row, top_row))
        for base_row, top_row in zip(base, top)
    )


def frame(pose: str) -> Layer:
    if pose not in ARM_POSES:
        raise ValueError(f"unknown pose {pose!r}; known poses: {', '.join(ARM_POSES)}")
    return compose(BODY, ARM_POSES[pose])


def pixels(layer: Sequence[str]) -> Iterator[Tuple[int, int, RGB]]:
    """Yield (x, y, colour) for every lit cell."""
    for y, row in enumerate(layer):
        for x, ch in enumerate(row):
            if ch != CLEAR:
                yield x, y, PALETTE[ch]


# Refuse broken art at import, before anything reaches the panel.
validate_layer("BODY", BODY)
for _name, _layer in ARM_POSES.items():
    validate_layer(f"arm pose {_name!r}", _layer)
if STILL_POSE not in ARM_POSES:
    raise ValueError(f"STILL_POSE {STILL_POSE!r} is not an arm pose")
validate_wave(WAVE_STEPS)
