"""Generate the StatCat Suite logo.

    python make_avatar.py style statcat-suite-avatar.svg   # the logo
    python make_avatar.py block blocking.svg               # flat layout, no styling
    python make_avatar.py favicon favicon.svg              # the head alone, for the docs sites' favicon

Render the PNG avatar with resvg, which draws strokes and gradients correctly:

    uv run --with resvg-py python -c "import resvg_py; open('statcat-suite-avatar.png', 'wb').write(bytes(resvg_py.svg_to_bytes(svg_path='statcat-suite-avatar.svg', width=500, height=500)))"

Colours are Catppuccin (Mocha unless noted). The glasses echo the SDMX mark:
two overlapping diamonds with exchange arrows.
"""

import math
import sys

# Catppuccin (Mocha unless noted)
LAVENDER = "#b4befe"
LAVENDER_DARK = "#7287fd"  # Latte Lavender
LAVENDER_LIGHT = "#c9d0ff"
CRUST = "#11111b"
SURFACE0 = "#313244"
SURFACE1 = "#45475a"
SAPPHIRE = "#74c7ec"
SAPPHIRE_DARK = "#209fb5"  # Latte Sapphire
SKY = "#89dceb"
TEXT = "#cdd6f4"
WHITE = "#eff1f5"  # Latte Base
PINK = "#f5c2e7"
BOOKS = ["#fab387", "#f38ba8", "#f9e2af", "#a6e3a1", "#94e2d5"]

FAVICON = sys.argv[1] == "favicon"  # the head alone, on a rounded square
STYLE = sys.argv[1] in ("style", "favicon")

# Head: centre and scale, relative to the r=96 head the shapes were drawn at.
HX, HY, S = (178, 196, 1.25) if STYLE else (178, 194, 1.3125)


def h(x: float, y: float) -> str:
    """Map a point drawn relative to the head centre (r=96) into the canvas."""
    return f"{HX + x * S:.1f} {HY + y * S:.1f}"


def hpath(cmds: list[tuple[str, list[tuple[float, float]]]]) -> str:
    """Build a path from (command, points) pairs given in head-local coordinates."""
    return " ".join(c + " ".join(h(*pt) for pt in pts) for c, pts in cmds) + " Z"


def mirror(cmds: list[tuple[str, list[tuple[float, float]]]]) -> list[tuple[str, list[tuple[float, float]]]]:
    return [(c, [(-x, y) for x, y in pts]) for c, pts in cmds]


def tapered(segments: list[tuple[tuple[float, float], ...]], w0: float, w1: float) -> tuple[str, tuple[float, float]]:
    """Outline a cubic centreline whose width narrows from w0 to w1. Returns the path and the end point."""
    pts = []
    for p0, c1, c2, p3 in segments:
        for i in range(48):
            t = i / 48
            mt = 1 - t
            pts.append((
                mt**3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t**3 * p3[0],
                mt**3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t**3 * p3[1],
            ))
    pts.append(segments[-1][3])
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        frac = lengths[i] / lengths[-1]
        half = (w1 + (w0 - w1) * (1 - frac) ** 2) / 2
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    ring = left + right[::-1]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ring) + " Z", pts[-1]


def poly(*pts: tuple[float, float]) -> str:
    return "M" + " L".join(h(*p) for p in pts) + " Z"


out: list[str] = []
add = out.append
add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">')

if STYLE:
    add(f"""<defs>
  <radialGradient id="bg" cx="0.35" cy="0.32" r="0.85">
    <stop offset="0" stop-color="{LAVENDER_LIGHT}"/><stop offset="1" stop-color="{LAVENDER}"/>
  </radialGradient>
  <linearGradient id="lens" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{SKY}"/><stop offset="1" stop-color="{SAPPHIRE}"/>
  </linearGradient>
  <linearGradient id="fur" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{SURFACE0}"/><stop offset="0.45" stop-color="{CRUST}"/>
  </linearGradient>
</defs>""")
    add('<rect width="512" height="512" fill="url(#bg)"/>')
else:
    add(f'<rect width="512" height="512" fill="{LAVENDER}"/>')

body_start = len(out)

# Sea-serpent body: neck, one hump, then the tail runs under the books as their shelf.
BODY = ("M166 300 C150 372 52 372 62 438 C72 492 168 494 190 456 C204 432 236 430 252 450 "
        "C266 470 276 476 300 476 L466 476")
fur = "url(#fur)" if STYLE else CRUST
if STYLE:
    # Fins along the hump, swept back toward the tail: a convex leading edge,
    # a slightly concave trailing edge, and a base sunk into the body.
    # (base x, base y, height, sweep, half-width)
    for x, y, tip, sweep, half in ((186, 424, 20, 9, 12), (219, 410, 29, 12, 14), (251, 422, 18, 8, 11)):
        add(f'<path d="M{x - half} {y + 14} C{x - half} {y - tip * 0.4} {x + sweep - 6} {y - tip} {x + sweep} {y - tip} '
            f'Q{x + half * 0.4} {y - tip * 0.35} {x + half} {y + 14} Z" fill="{CRUST}" stroke="{CRUST}" stroke-width="3" stroke-linejoin="round"/>')
else:
    add(f'<path d="M204 440 L224 398 L246 440 Z" fill="{CRUST}" stroke="{CRUST}" stroke-width="10" stroke-linejoin="round"/>')
if STYLE:
    segs = [
        ((166, 290), (150, 372), (52, 372), (62, 438)),
        ((62, 438), (72, 492), (168, 494), (190, 456)),
        ((190, 456), (204, 432), (236, 430), (252, 450)),
        ((252, 450), (266, 470), (276, 476), (300, 476)),
        ((300, 476), (355, 476), (411, 476), (466, 476)),
        ((466, 476), (492, 476), (500, 456), (496, 430)),
        ((496, 430), (493, 408), (478, 398), (468, 410)),
    ]
    outline, end = tapered(segs, 118, 16)
    add(f'<path d="{outline}" fill="{fur}"/>')
    add(f'<circle cx="{end[0]}" cy="{end[1]}" r="8" fill="{CRUST}"/>')
else:
    add(f'<path d="{BODY}" stroke="{fur}" stroke-width="50" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

# Books: heights trace a normal distribution; they stand on the tail.
x0, w, gap, base = 286, 36, 3, 470
MU = x0 + 2 * (w + gap) + w / 2  # centre of the middle book
SIGMA, PEAK = 50, 246


def gauss(x: float) -> float:
    return PEAK * math.exp(-((x - MU) ** 2) / (2 * SIGMA**2))


heights = [round(gauss(x0 + i * (w + gap) + w / 2)) for i in range(5)]
centres = []
for i, (ht, col) in enumerate(zip(heights, BOOKS)):
    x = x0 + i * (w + gap)
    y = base - ht
    centres.append((x + w / 2, y))
    if STYLE:
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{ht}" rx="5" fill="{col}"/>')
        add(f'<rect x="{x + w - 8}" y="{y}" width="8" height="{ht}" rx="4" fill="{CRUST}" opacity="0.12"/>')  # shade
        add(f'<rect x="{x + 7}" y="{y + 16}" width="{w - 14}" height="5" rx="2.5" fill="{CRUST}" opacity="0.3"/>')
        add(f'<rect x="{x + 7}" y="{y + 26}" width="{w - 14}" height="3" rx="1.5" fill="{CRUST}" opacity="0.3"/>')
    else:
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{ht}" rx="4" fill="{col}"/>')
        add(f'<path d="M{x} {y + 18} h{w} M{x} {base - 18} h{w}" stroke="{CRUST}" stroke-width="4" opacity="0.25"/>')
# fitted normal curve over the tops
peak = centres[2][1] - 14
curve = f"M{x0 - 6} {base - 6} C{x0 + 46} {base - 6} {x0 + 62} {peak} {centres[2][0]} {peak} C{centres[2][0] + 34} {peak} {x0 + 150} {base - 6} {x0 + 200} {base - 6}"
if STYLE:
    lift = 12  # the curve rides just above the book tops
    xs = [x0 - 24 + i * 2 for i in range(int((5 * (w + gap) + 46) / 2) + 1)]
    d = "M" + " L".join(f"{x:.1f} {base - 4 - gauss(x) * (PEAK + lift) / PEAK:.1f}" for x in xs)
    add(f'<path d="{d}" stroke="{CRUST}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    for cx, y in centres:
        add(f'<circle cx="{cx}" cy="{base - 4 - gauss(cx) * (PEAK + lift) / PEAK:.1f}" r="5.5" fill="{CRUST}"/>')
else:
    add(f'<path d="{curve}" stroke="{CRUST}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="1 10"/>')

body_end = len(out)

# Head
TILT = 8 if STYLE else 0  # leans toward the data
add(f'<g transform="rotate({TILT} {HX} {HY + 110})">')
if STYLE:
    right_half = [
        ("C", [(44, -84), (80, -66), (94, -34)]),
        ("C", [(102, -14), (104, 12), (100, 28)]),
        ("L", [(118, 36)]), ("L", [(102, 46)]), ("L", [(114, 60)]), ("L", [(94, 66)]),
        ("C", [(78, 92), (40, 102), (0, 102)]),
    ]
    left_half = [
        ("C", [(-40, 102), (-78, 92), (-94, 66)]),
        ("L", [(-114, 60)]), ("L", [(-102, 46)]), ("L", [(-118, 36)]), ("L", [(-100, 28)]),
        ("C", [(-104, 12), (-102, -14), (-94, -34)]),
        ("C", [(-80, -66), (-44, -84), (0, -84)]),
    ]
    ear = [("M", [(-90, -36)]), ("C", [(-104, -84), (-106, -122), (-98, -150)]), ("C", [(-72, -134), (-46, -108), (-26, -80)])]
    inner_ear = [("M", [(-82, -50)]), ("C", [(-92, -86), (-94, -112), (-90, -132)]), ("C", [(-72, -118), (-56, -100), (-42, -84)])]
    for shape in (ear, mirror(ear)):
        add(f'<path d="{hpath(shape)}" fill="{fur}" stroke="{CRUST}" stroke-width="8" stroke-linejoin="round"/>')
    for shape in (inner_ear, mirror(inner_ear)):
        add(f'<path d="{hpath(shape)}" fill="{PINK}" stroke="{PINK}" stroke-width="6" stroke-linejoin="round"/>')
    for sx in (-1, 1):  # fur in the ears
        add(f'<path d="M{h(sx * 78, -66)} L{h(sx * 84, -100)} M{h(sx * 66, -78)} L{h(sx * 72, -108)} M{h(sx * 54, -88)} L{h(sx * 60, -110)}" '
            f'stroke="#eba0ac" stroke-width="3.5" stroke-linecap="round"/>')
    add(f'<path d="{hpath([("M", [(0, -84)]), *right_half, *left_half])}" fill="{fur}" stroke="{CRUST}" stroke-width="8" stroke-linejoin="round"/>')
    add(f'<ellipse cx="{h(0, 68).split()[0]}" cy="{h(0, 68).split()[1]}" rx="{34 * S:.1f}" ry="{21 * S:.1f}" fill="{SURFACE0}" opacity="0.55"/>')
else:
    ears = [((-84, -46), (-88, -142), (-8, -86)), ((84, -46), (88, -142), (8, -86))]
    inner = [((-70, -62), (-72, -118), (-26, -84)), ((70, -62), (72, -118), (26, -84))]
    for e in ears:
        add(f'<path d="{poly(*e)}" fill="{CRUST}"/>')
    for e in inner:
        add(f'<path d="{poly(*e)}" fill="{PINK}"/>')
    add(f'<circle cx="{HX}" cy="{HY}" r="{96 * S:.1f}" fill="{CRUST}"/>')

# SDMX glasses: overlapping diamonds, exchange arrows for eyes
lens_fill = "url(#lens)" if STYLE else SAPPHIRE
for cx in (-34, 34):
    pts = ((cx, -46), (cx + 46, 0), (cx, 46), (cx - 46, 0))
    extra = f' stroke="{SAPPHIRE_DARK}" stroke-width="4" stroke-linejoin="round"' if STYLE else ""
    add(f'<path d="{poly(*pts)}" fill="{lens_fill}"{extra}/>')
add(f'<path d="{poly((0, -12), (12, 0), (0, 12), (-12, 0))}" fill="{SAPPHIRE_DARK}"/>')
if STYLE:
    # glare on each lens
    for cx in (-34, 34):
        add(f'<path d="M{h(cx - 26, -10)} L{h(cx - 10, -26)}" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity="0.55"/>')
arrow = f' fill="{WHITE}" stroke="{WHITE}" stroke-linecap="round" stroke-linejoin="round"'
add(f'<path d="M{h(-34 + 14.4, 14.4)} L{h(-34 - 9.6, -9.6)}"{arrow} stroke-width="{8.5 * S:.1f}"/>')
add(f'<path d="{poly((-34 - 21.6, -21.6), (-34 - 1.2, -18), (-34 - 18, -1.2))}"{arrow} stroke-width="{3.5 * S:.1f}"/>')
add(f'<path d="M{h(34 - 14.4, -14.4)} L{h(34 + 9.6, 9.6)}"{arrow} stroke-width="{8.5 * S:.1f}"/>')
add(f'<path d="{poly((34 + 21.6, 21.6), (34 + 18, 1.2), (34 + 1.2, 18))}"{arrow} stroke-width="{3.5 * S:.1f}"/>')

# Nose, mouth, whiskers
add(f'<path d="{poly((-10, 54), (10, 54), (0, 65))}" fill="{PINK}"' + (f' stroke="{PINK}" stroke-width="5" stroke-linejoin="round"' if STYLE else "") + "/>")
if STYLE:
    # a "w" mouth whose corners turn up into a smile
    add(f'<path d="M{h(0, 65)} q{-11 * S:.1f} {15 * S:.1f} {-22 * S:.1f} {4 * S:.1f} q{-3 * S:.1f} {-3 * S:.1f} {-4 * S:.1f} {-7 * S:.1f} '
        f'M{h(0, 65)} q{11 * S:.1f} {15 * S:.1f} {22 * S:.1f} {4 * S:.1f} q{3 * S:.1f} {-3 * S:.1f} {4 * S:.1f} {-7 * S:.1f}" '
        f'stroke="{TEXT}" stroke-width="{4.5 * S:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
else:
    add(f'<path d="M{h(0, 65)} q{-11 * S:.1f} {14 * S:.1f} {-22 * S:.1f} {5 * S:.1f} M{h(0, 65)} q{11 * S:.1f} {14 * S:.1f} {22 * S:.1f} {5 * S:.1f}" '
        f'stroke="{TEXT}" stroke-width="{5 * S:.1f}" fill="none" stroke-linecap="round"/>')
if STYLE:
    for sx in (-1, 1):
        for dy, ey in ((60, -10), (72, 6)):
            add(f'<path d="M{h(sx * 50, dy)} q{sx * 24 * S:.1f} {(ey - 4) * S:.1f} {sx * 50 * S:.1f} {ey * S:.1f}" stroke="{TEXT}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.85"/>')
else:
    add(f'<path d="M{h(-48, 60)} l{-46 * S:.1f} {-8 * S:.1f} M{h(-48, 72)} l{-44 * S:.1f} {7 * S:.1f} '
        f'M{h(48, 60)} l{46 * S:.1f} {-8 * S:.1f} M{h(48, 72)} l{44 * S:.1f} {7 * S:.1f}" stroke="{TEXT}" stroke-width="4" stroke-linecap="round"/>')

add("</g>")
add("</svg>")

if FAVICON:
    del out[body_start:body_end]
    FX, FY, FW = 10, -16, 362  # the tilted head spans x 37-346, y 0-330; 16 px of padding
    out[0] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{FX} {FY} {FW} {FW}" width="64" height="64">'
    i = out.index('<rect width="512" height="512" fill="url(#bg)"/>')
    out[i] = f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FW}" rx="72" fill="url(#bg)"/>'
open(sys.argv[2], "w").write("\n".join(out))
