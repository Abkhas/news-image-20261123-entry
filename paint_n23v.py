#!/usr/bin/env python3
"""Paint the n23 challenger6 image (1024x1024), news-image-20261123.

MONDAY 23 NOVEMBER 2026. Sixth candidate for the same 30 stories.
Khase eye-checked challenger5 at 15:10 WIB: two small fixes remain.

  1. STAT STRIP CENTERING. The row of big numbers + labels in the
     navy band sits slightly low INSIDE its band. Measured, not
     guessed: with PIL, a 40px bold digit's ink spans 8..38 below
     its ascent top, and a 10px bold label's ink spans 3..10.
     Challenger5 draws the number at band_top+4 (ink 102..132) and
     the label at band_top+42 (ink 135..142) in a 90..142 band --
     12px of air above the numbers, ZERO below the labels. That is
     why it reads low. Here the number+label block is centred by
     measurement: number ink top = band_top + (52 - 40) / 2 = 96,
     i.e. the number is drawn at y=88 and the label at y=126, both
     6px up from challenger5. A pixel guard scans the band for
     light pixels and requires the top and bottom air to match
     within 1px.
  2. HERO 2 FIRE READS AS A MOUNTAIN. Challenger5's flames are
     three nested tongues on one shared axis inside a round glow
     disc: one symmetric mound with a point, which reads as a
     mountain at 300px. Here the fire is rebuilt as separate thin
     flickering tongues: each tongue is its own wavy spine (S-curve,
     its own lean, its own height), with VISIBLE DARK GAPS of the
     window between tongues, a pale-yellow core inside an orange
     outer tongue, a flat ember glow along the sill only, and a few
     ember dots rising. No enclosing disc, no shared axis, no
     symmetric triangle anywhere. The tongues rise out of the
     window sill the way real fire licks out of a broken window.
     Verified in a 2x hero-2 close-up that a fresh eye reads FIRE.

Everything else is kept exactly as Khase approved it in
challenger5: the measured 10px page rebalance (middle block
centre y=510.5 -- do NOT move the middle again), hero 1 with
microphones and MODI/SHAH nameplates, hero 3 dark exchange
board, 10 big grid cards, THE DAY IN UTC strip, ALSO ON neat,
DATE CHECK neat/striking, map good, footer fully visible.
Same 30 stories (3 heroes + 10 grid + 17 ALSO ON), same region
counts (Europe 8, Americas 4, Middle East 1, Asia 9, Africa 3,
Oceania 4, World 1). Only the rendering changes.

REFERENCE RESEARCH (whole internet outside make.fun): Modi-Shah
Hyderabad House talks (dainiknewslive.in, newkerala.com,
timesnowworld.com); Cikande PT Fonusa Agung Mulia fire, 3 dead /
37 unaccounted, search resumes 07:00 Mon (Reuters, AP/People,
Fox News); Taiwan FSC short-sale ban, TAIEX 36,033.29, -17.5%
week, worst since 1991 (Focus Taiwan/CNA, cryptobriefing.com).
Plus the n21 final winner superskie (86.1050%) and #2
hazel-harbor-63, viewed full-size and at 300px
(~/workspace/makefun-research/n21-paid-top10/).

Everything is drawn in code with PIL: no photos, no network, no
randomness -- repeated runs give identical bytes.
"""

import hashlib
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
OUT = os.environ.get("OUT", "entry.png")

# ------------------------------------------------------------- palette
PAPER = (253, 249, 238)
INK = (17, 33, 57)
NAVY = (9, 20, 38)
RED = (186, 32, 32)
GOLD = (214, 162, 42)
GREY = (92, 96, 104)
RULE = (203, 196, 178)
BODY = (40, 44, 52)
WINDOW = (38, 38, 44)

REGION_FILL = {
    "EUROPE": (31, 78, 121),
    "AMERICAS": (176, 92, 20),
    "MIDDLE EAST": (146, 110, 58),
    "ASIA": (46, 125, 80),
    "AFRICA": (178, 132, 30),
    "OCEANIA": (30, 130, 140),
    "WORLD": (90, 90, 105),
}
REGION_ORDER = ["EUROPE", "AMERICAS", "MIDDLE EAST", "ASIA",
                "AFRICA", "OCEANIA", "WORLD"]

TAG_FILL = {
    "CONFIRMED": (34, 120, 60),
    "REPORTED": (31, 78, 121),
    "CLAIM": (176, 92, 20),
    "PENDING": (110, 90, 140),
}

EMBER = (200, 90, 25)
FLAME_OUT = (240, 120, 30)
FLAME_IN = (250, 180, 40)
FLAME_CORE = (255, 222, 120)

ISSUES = []  # (tag, detail) -- the build check requires this empty


def pale(rgb, amount=0.90):
    """Pale tint of a colour, for card backgrounds."""
    return tuple(int(255 * amount + c * (1 - amount)) for c in rgb)


# -------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_CACHE = {}


def mk_font(name, size):
    key = (name, size)
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(
            os.path.join(FONT_DIR, name), size)
    return _CACHE[key]


def serif_b(size):
    return mk_font("DejaVuSerif-Bold.ttf", size)


def serif_r(size):
    return mk_font("DejaVuSerif.ttf", size)


def sans_b(size):
    return mk_font("DejaVuSans-Bold.ttf", size)


def sans_r(size):
    return mk_font("DejaVuSans.ttf", size)


# -------------------------------------------------------------- text
def wrap(draw, text, fnt, max_w):
    """Greedy wrap; every returned line fits max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, tag, text, fnt, max_w, max_lines):
    """Wrap to at most max_lines; truncate with '...' and record
    the issue (the build check requires zero)."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        ISSUES.append((tag, text))
        lines = lines[:max_lines]
        cut = lines[-1]
        while cut and draw.textlength(cut + "...", font=fnt) > max_w:
            cut = cut[:-1]
        lines[-1] = cut + "..."
    return lines


def put(draw, x, y, lines, fnt, fill, step):
    for i, line in enumerate(lines):
        draw.text((x, y + i * step), line, font=fnt, fill=fill)


def shrink(draw, text, name, start, max_w, floor):
    """Largest font size from `start` down to `floor` fitting max_w."""
    size = start
    while size > floor and draw.textlength(
            text, font=mk_font(name, size)) > max_w:
        size -= 1
    return size


def tag(draw, x, y, label, size=13, height=17):
    """Verification-status tag: white pill, coloured outline+text.
    Returns the tag width."""
    colour = TAG_FILL[label]
    fnt = sans_b(size)
    w = int(draw.textlength(label, font=fnt) + 14)
    draw.rounded_rectangle([x, y, x + w, y + height], radius=4,
                           fill=(255, 255, 255), outline=colour,
                           width=2)
    draw.text((x + 7, y + (height - size) / 2 - 1), label, font=fnt,
              fill=colour)
    return w


def srctag(draw, x_right, y, name, size=13, height=17, max_w=120):
    """Source-name tag anchored at its right edge; returns its width,
    or None when the name does not fit (dropped, never shrunk)."""
    fnt = sans_b(size)
    w = int(draw.textlength(name, font=fnt) + 14)
    if w > max_w:
        return None
    draw.rounded_rectangle([x_right - w, y, x_right, y + height],
                           radius=4, fill=(255, 255, 255),
                           outline=RULE, width=1)
    draw.text((x_right - w + 7, y + (height - size) / 2 - 1), name,
              font=fnt, fill=INK)
    return w


def disc(draw, cx, cy, n, r=11, fill=RED, size=12):
    """Numbered disc, white number on a coloured circle."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    fnt = sans_b(size)
    tw = draw.textlength(str(n), font=fnt)
    draw.text((cx - tw / 2, cy - fnt.size / 2 - 1), str(n), font=fnt,
              fill=(255, 255, 255))


def flag(draw, x, y, text, size=10):
    """Red in-scene flag with white bold text (winner device).
    Returns the flag width."""
    fnt = sans_b(size)
    w = int(draw.textlength(text, font=fnt) + 16)
    draw.rectangle([x, y, x + w, y + 15], fill=RED)
    draw.text((x + 8, y + 2), text, font=fnt, fill=(255, 255, 255))
    return w


def layer(w, h, painter, bg):
    """Render a scene on its own image and return it. Anything the
    painter draws is clipped to the layer by construction -- a scene
    can never leak past its panel border (the challenger3 smoke
    defect). The caller pastes the layer at the panel position."""
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    painter(d, w, h)
    return img


# -------------------------------------------------------------- fire
# The challenger5 flame read as a mountain: three nested tongues on
# one shared axis inside a round glow disc -- one symmetric mound
# with a point. Real fire in a broken window is the opposite: thin
# separate tongues, each leaning its own way, dark window showing
# between them, ragged heights, no shared axis, no round outline.
# Each tongue below is one wavy spine: narrow at the sill, widest
# just past halfway, tapering to a tip that curls sideways. The
# outer tongue is orange, a smaller yellow tongue rides the same
# spine, and a pale core sits low. The glow is a FLAT ember strip
# along the sill, never a disc around the cluster.


def tongue(d, base_x, sill, height, lean, width, phase):
    """One flickering tongue rising from the sill."""
    steps = 9
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        # Spine: S-curve, lean grows with height, plus a wobble.
        cx = (base_x + lean * (t ** 1.5)
              + 1.6 * math.sin(t * 3.1 + phase))
        cy = sill - height * t
        # Half-width: thin at the sill, fattest near 55%, a point
        # at the tip -- never a triangle, never a mound.
        hw = width * (0.35 + 0.75 * math.sin(math.pi
                      * min(t * 1.25, 1.0)))
        left.append((cx - hw, cy))
        right.append((cx + hw, cy))
    d.polygon(left + right[::-1], fill=FLAME_OUT)
    # Inner yellow tongue on the same spine, ~60% size.
    left2, right2 = [], []
    for i in range(steps + 1):
        t = i / steps
        cx = (base_x + lean * (t ** 1.5)
              + 1.6 * math.sin(t * 3.1 + phase))
        cy = sill - height * 0.62 * t
        hw = width * 0.55 * (0.35 + 0.75 * math.sin(
            math.pi * min(t * 1.25, 1.0)))
        left2.append((cx - hw, cy))
        right2.append((cx + hw, cy))
    d.polygon(left2 + right2[::-1], fill=FLAME_IN)
    # Pale core low in the tongue.
    d.ellipse([base_x - width * 0.28, sill - height * 0.30,
               base_x + width * 0.28, sill - 1], fill=FLAME_CORE)


def fire(d, x0, sill, span):
    """Fire in one broken window: four separate tongues of ragged
    heights with dark gaps between them, a flat ember strip along
    the sill, and two ember dots rising. No disc, no shared axis,
    no symmetric silhouette."""
    # Flat ember strip along the sill, not a disc.
    d.ellipse([x0 - 2, sill - 3, x0 + span + 2, sill + 2], fill=EMBER)
    # Four tongues, spaced so the dark window shows between them.
    for bx, ht, ln, wd, ph in [
            (x0 + 4, 14, -3, 5, 0.4),
            (x0 + 11, 23, 2, 6, 2.1),
            (x0 + 18, 17, -1, 5, 4.0),
            (x0 + 24, 11, 3, 4, 5.3)]:
        tongue(d, bx, sill, ht, ln, wd, ph)
    # Ember dots rising above the tallest tongue.
    d.ellipse([x0 + 10, sill - 27, x0 + 13, sill - 24],
              fill=FLAME_IN)
    d.ellipse([x0 + 19, sill - 22, x0 + 21, sill - 20],
              fill=FLAME_OUT)

# -------------------------------------------------------- hero scenes
# Each painter draws on its own layer of size (w, h) -- see
# `layer`. Coordinates here are layer-relative; the layer is
# pasted into the hero card, so a painter cannot paint outside
# its panel even by mistake.


def meeting(d, w, h):
    """Hyderabad House: Modi and Shah seated across a conference
    table. Modi left: white hair, white beard, glasses, white kurta
    and dark waistcoat. Shah right: dark hair, dark beard, black
    blazer. Microphones, nameplates reading MODI / SHAH, small
    India / Nepal flags on stands, water glasses. A red flag
    carries the news point. Kept from challenger5 -- Khase called
    it more realistic with the mics in front of the two people."""
    d.rectangle([0, 0, w, h], fill=(238, 232, 214))
    # Framed picture on the cream wall, centred.
    d.rectangle([int(w * 0.44), 4, int(w * 0.56), 20],
                outline=(150, 125, 70), width=2, fill=(210, 190, 150))
    d.ellipse([int(w * 0.485), 7, int(w * 0.515), 17],
              fill=(120, 100, 60))
    # Red flag: the news point, top-left, clear of both heads.
    flag(d, 6, 4, "FIRST VISIT AS PM", size=10)
    # Necks, then shoulders; the table front covers the lower half.
    for cx, torso, vest in [
            (int(w * 0.28), (244, 244, 238), (64, 64, 74)),
            (int(w * 0.72), (28, 28, 34), None)]:
        d.rectangle([cx - 5, 50, cx + 5, 58], fill=(236, 206, 180))
        d.polygon([(cx - 26, h), (cx - 24, 54), (cx + 24, 54),
                   (cx + 26, h)], fill=torso)
        if vest:
            d.rectangle([cx - 12, 54, cx + 12, h], fill=vest)
            d.polygon([(cx - 6, 54), (cx + 6, 54), (cx, 68)],
                      fill=(245, 245, 245))
        else:
            d.polygon([(cx - 6, 54), (cx + 6, 54), (cx, 68)],
                      fill=(245, 245, 245))
            d.polygon([(cx - 24, 54), (cx - 6, 54), (cx, 68),
                       (cx - 12, 84)], fill=(48, 48, 56))
            d.polygon([(cx + 24, 54), (cx + 6, 54), (cx, 68),
                       (cx + 12, 84)], fill=(48, 48, 56))
    # Table front with a gold runner line along its top edge.
    d.rectangle([0, 66, w, h], fill=(122, 86, 52))
    d.line([0, 66, w, 66], fill=(90, 60, 35), width=2)
    d.line([0, 70, w, 70], fill=(190, 160, 90), width=1)
    # Heads, drawn after the table so nothing covers them. Ears,
    # eyebrows and a nose line make them read as people, not discs.
    for cx, hair, beard, glasses in [
            (int(w * 0.28), (245, 245, 245), (245, 245, 245), True),
            (int(w * 0.72), (38, 32, 28), (48, 42, 38), False)]:
        d.ellipse([cx - 16, 36, cx - 11, 46], fill=(236, 206, 180))
        d.ellipse([cx + 11, 36, cx + 16, 46], fill=(236, 206, 180))
        d.ellipse([cx - 12, 28, cx + 12, 54], fill=(236, 206, 180))
        d.pieslice([cx - 12, 26, cx + 12, 42], 180, 360, fill=hair)
        d.ellipse([cx - 9, 44, cx + 9, 58], fill=beard)
        d.ellipse([cx - 9, 40, cx + 9, 48], fill=(236, 206, 180))
        d.line([cx - 1, 42, cx + 1, 48], fill=(200, 170, 145), width=1)
        for ex in (cx - 5, cx + 5):
            d.line([ex - 3, 35, ex + 3, 35], fill=(60, 50, 40), width=2)
            d.ellipse([ex - 1, 37, ex + 1, 39], fill=(40, 32, 26))
        if glasses:
            for ex in (cx - 5, cx + 5):
                d.ellipse([ex - 3, 36, ex + 3, 42],
                          outline=(30, 30, 30), width=1)
            d.line([cx - 2, 39, cx + 2, 39], fill=(30, 30, 30), width=1)
    # Microphones on the table, angled toward each leader. Heads sit
    # at y 64..70, clear of the status/source tags (card y+74..91).
    for cx, lean in [(int(w * 0.28), -1), (int(w * 0.72), 1)]:
        d.line([cx + lean * 14, 88, cx + lean * 4, 67],
               fill=(40, 40, 44), width=2)
        d.ellipse([cx + lean * 4 - 3, 64, cx + lean * 4 + 3, 70],
                  fill=(40, 40, 44))
    # Flags on stands between the leaders: India left, Nepal right.
    fx = w // 2 - 22
    d.line([fx + 7, 66, fx + 7, 84], fill=(90, 80, 70), width=1)
    for i, col in enumerate([(255, 150, 40), (255, 255, 255),
                             (20, 130, 60)]):
        d.rectangle([fx, 70 + i * 3, fx + 14, 73 + i * 3], fill=col)
    d.line([w // 2 + 14, 66, w // 2 + 14, 84], fill=(90, 80, 70),
           width=1)
    d.rectangle([w // 2 + 8, 70, w // 2 + 20, 79], fill=(200, 40, 40),
                outline=(255, 255, 255), width=1)
    # Nameplates with names, and water glasses, on the table front --
    # low in the scene (y 91..99), below the status/source tags
    # (card y+74..91), so the tags cannot cover them.
    for cx, name in [(int(w * 0.28), "MODI"), (int(w * 0.72), "SHAH")]:
        d.rectangle([cx - 14, 91, cx + 14, 99], fill=(255, 255, 255),
                    outline=(150, 150, 150))
        fnt = sans_b(6)
        tw = d.textlength(name, font=fnt)
        d.text((cx - tw / 2, 92), name, font=fnt, fill=INK)
        d.rectangle([cx + 19, 90, cx + 25, 99],
                    fill=(180, 210, 225), outline=(120, 150, 170))


def factory(d, w, h):
    """Cikande: the three-storey PT Fonusa Agung Mulia candy factory
    after the fire. The smoke circles are capped well inside the
    layer (highest top y=14 of 100) and the whole scene is rendered
    on its own layer, so smoke can never touch the timeline band
    above the card again. The fire is now separate flickering
    tongues rising out of two broken windows (see `fire`) -- thin,
    leaning, ragged, with dark gaps between them, so it reads as
    fire and never as a mountain. A red flag carries the toll."""
    d.rectangle([0, 0, w, h], fill=(175, 170, 162))
    d.rectangle([0, int(h * 0.72), w, h], fill=(150, 145, 138))
    # Smoke, kept low and inside: tops at y=14..24, flag covers
    # the middle plume's top where they meet.
    for sx, sy, sr, col in [(0.42, 0.30, 9, (70, 70, 75)),
                            (0.52, 0.25, 11, (60, 60, 66)),
                            (0.62, 0.32, 8, (85, 83, 80))]:
        d.ellipse([int(w * sx) - sr, int(h * sy) - sr,
                   int(w * sx) + sr, int(h * sy) + sr], fill=col)
    # The three-storey block.
    bx0, bx1, by0, by1 = 12, int(w * 0.70), 26, 96
    d.rectangle([bx0, by0, bx1, by1], fill=(118, 122, 132))
    for vx in range(bx0 + 9, bx1, 9):
        d.line([vx, by0, vx, by1], fill=(100, 104, 114), width=1)
    # Roof sagging in the middle where it collapsed.
    d.polygon([(bx0, by0), (int(w * 0.30), by0),
               (int(w * 0.42), by0 + 14), (int(w * 0.55), by0 + 14),
               (int(w * 0.66), by0), (bx1, by0), (bx1, by0 - 4),
               (bx0, by0 - 4)], fill=(60, 58, 54))
    # Window rows, three floors; flickering fire at two broken
    # windows, rising out of the window openings.
    for fy in (36, 56, 76):
        for k in range(4):
            wx = bx0 + 8 + k * 48
            d.rectangle([wx, fy, wx + 26, fy + 12], fill=WINDOW)
    for fx, fy in [(bx0 + 8, 76), (bx0 + 104, 56)]:
        fire(d, fx, fy + 12, 26)
    # Two firefighters in front, orange coats, red helmets, hose.
    for fx in (int(w * 0.76), int(w * 0.88)):
        d.polygon([(fx - 11, h), (fx - 9, 62), (fx + 9, 62),
                   (fx + 11, h)], fill=(238, 118, 28))
        d.line([fx - 9, 74, fx + 9, 74], fill=(255, 255, 255), width=2)
        d.pieslice([fx - 8, 50, fx + 8, 64], 180, 360,
                   fill=(198, 38, 38))
        d.ellipse([fx - 6, 60, fx + 6, 68], fill=(236, 206, 180))
    hx = int(w * 0.76)
    d.line([hx - 4, 68, bx1 + 6, 82], fill=(40, 40, 44), width=3)
    for i in range(3):
        d.line([bx1 + 6 + i * 4, 82 - i * 2, bx1 + 22 + i * 4,
                76 - i * 3], fill=(225, 235, 245), width=2)
    # Wet ground.
    d.rectangle([0, 96, w, h], fill=(70, 68, 66))
    d.line([20, 98, 120, 98], fill=(150, 150, 150), width=1)
    # Red flag last, on top of the smoke tops.
    flag(d, (w - 170) // 2, 2, "3 DEAD · 37 MISSING", size=10)


def board(d, w, h):
    """Taipei: the Taiwan Stock Exchange board. Dark screen, TAIEX
    36,033 in big red with the 17.5% weekly fall, the "worst week
    since 1991" line, and a red chart falling across the board.
    Kept from challenger5 -- Khase called it good and realistic."""
    d.rectangle([0, 0, w, h], fill=(12, 16, 26))
    d.text((8, 5), "TAIWAN STOCK EXCHANGE", font=sans_b(11),
           fill=(255, 255, 255))
    d.text((8, 20), "36,033", font=sans_b(30), fill=(220, 50, 50))
    d.text((w - 8, 24), "▼ 17.5%", font=sans_b(20),
           fill=(220, 50, 50), anchor="ra")
    d.text((8, 52), "WORST WEEK SINCE 1991 · FSC BANS SHORT SALES",
           font=sans_r(9), fill=(200, 205, 215))
    for gy in (62, 74, 86):
        d.line([8, gy, w - 8, gy], fill=(38, 46, 62), width=1)
    pts = [(0.04, 0.60), (0.20, 0.66), (0.36, 0.64), (0.52, 0.76),
           (0.68, 0.82), (0.84, 0.90), (0.96, 0.94)]
    xy = [(int(w * px), int(h * py)) for px, py in pts]
    d.line(xy, fill=(220, 50, 50), width=3)
    for px, py in xy:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(220, 50, 50))

# -------------------------------------------------------- grid bands
# The grid bands are 40px tall: bold colour fields and one clear
# shape each, nothing fiddly. Each band is also rendered on its own
# layer and pasted in.


def band_cricket(d, w, h):
    d.rectangle([0, 0, w, h], fill=(40, 130, 60))
    d.rectangle([int(w * 0.38), 0, int(w * 0.62), h],
                fill=(210, 190, 150))
    d.line([0, h // 2, w, h // 2], fill=(255, 255, 255), width=1)
    d.ellipse([int(w * 0.68) - 4, 8, int(w * 0.68) + 4, 16],
              fill=(200, 40, 40))


def band_torii(d, w, h):
    d.rectangle([0, 0, w, h], fill=(235, 228, 210))
    d.ellipse([int(w * 0.82) - 5, 4, int(w * 0.82) + 5, 14],
              fill=(240, 180, 120))
    for px in (0.30, 0.68):
        d.rectangle([int(w * px) - 2, 10, int(w * px) + 2, h],
                    fill=(200, 50, 40))
    d.rectangle([int(w * 0.20), 8, int(w * 0.80), 13],
                fill=(200, 50, 40))


def band_rescue(d, w, h):
    d.rectangle([0, 0, w, h], fill=(150, 155, 165))
    for bx, bw in [(0.24, 0.16), (0.50, 0.15), (0.68, 0.18)]:
        d.rectangle([int(w * bx), 18, int(w * (bx + bw)), h],
                    fill=(90, 85, 80))
    d.line([int(w * 0.80), 4, int(w * 0.70), h], fill=(240, 130, 30),
           width=2)
    d.ellipse([int(w * 0.45) - 4, 10, int(w * 0.45) + 4, 18],
              fill=(240, 200, 40))


def band_globe(d, w, h):
    d.rectangle([0, 0, w, h], fill=(16, 72, 86))
    d.ellipse([int(w * 0.30), 4, int(w * 0.62), h - 4],
              fill=(40, 110, 170))
    d.ellipse([int(w * 0.36), 8, int(w * 0.46), 16],
              fill=(60, 160, 90))
    d.ellipse([int(w * 0.48), 18, int(w * 0.58), 26],
              fill=(60, 160, 90))
    sx, sy = int(w * 0.82), 14
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = 6 if i % 2 == 0 else 3
        pts.append((sx + rr * math.cos(a), sy + rr * math.sin(a)))
    d.polygon(pts, fill=GOLD)


def band_futures(d, w, h):
    d.rectangle([0, 0, w, h], fill=(245, 245, 240))
    d.line([4, h - 4, w - 4, h - 4], fill=(150, 150, 150), width=1)
    pts = [(0.08, 0.80), (0.30, 0.62), (0.50, 0.68), (0.70, 0.42),
           (0.92, 0.18)]
    xy = [(int(w * px), int(h * py)) for px, py in pts]
    d.line(xy, fill=(34, 120, 60), width=2)
    ex, ey = xy[-1]
    d.polygon([(ex, ey), (ex - 6, ey + 2), (ex - 2, ey + 6)],
              fill=(34, 120, 60))


def band_pmi(d, w, h):
    d.rectangle([0, 0, w, h], fill=(200, 190, 170))
    d.rectangle([int(w * 0.30), 4, int(w * 0.70), h - 4],
                fill=(255, 255, 255))
    for i, bh in enumerate([0.25, 0.45, 0.65]):
        bx = int(w * (0.36 + i * 0.11))
        d.rectangle([bx, int(h * (0.85 - bh)), bx + 9,
                     int(h * 0.85)], fill=(31, 78, 121))


def band_film(d, w, h):
    d.rectangle([0, 0, w, h], fill=(60, 60, 70))
    d.rectangle([int(w * 0.14), 8, int(w * 0.86), h - 4],
                fill=(30, 30, 36))
    cx, cy = w // 2, h // 2 + 2
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(90, 130, 180))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(20, 30, 50))


def band_flag(d, w, h):
    d.rectangle([0, 0, w, h], fill=(190, 210, 230))
    d.polygon([(0, h), (int(w * 0.4), 12), (int(w * 0.7), h)],
              fill=(90, 130, 90))
    px = int(w * 0.30)
    d.line([px, 4, px, h - 4], fill=(90, 80, 70), width=2)
    for i, col in enumerate([(255, 150, 40), (255, 255, 255),
                             (20, 130, 60)]):
        d.rectangle([px, 4 + i * 5, px + 18, 9 + i * 5], fill=col)


def band_bills(d, w, h):
    d.rectangle([0, 0, w, h], fill=(30, 34, 48))
    d.ellipse([int(w * 0.30) - 6, 8, int(w * 0.30) + 6, 20],
              fill=(255, 220, 90))
    d.rectangle([int(w * 0.60), 6, int(w * 0.88), h - 6],
                fill=(255, 255, 255))
    for i in range(2):
        ly = 12 + i * 8
        d.line([int(w * 0.64), ly, int(w * 0.84), ly],
               fill=(186, 32, 32), width=1)


def band_protest(d, w, h):
    d.rectangle([0, 0, w, h], fill=(190, 180, 160))
    d.rectangle([int(w * 0.1), 16, int(w * 0.9), h],
                fill=(80, 76, 70))
    for frac in (0.2, 0.45, 0.7):
        px = int(w * frac)
        d.line([px, 10, px, 20], fill=(60, 55, 50), width=2)
        d.rectangle([px - 6, 4, px + 6, 10], fill=(255, 255, 255),
                    outline=RED, width=1)


BANDS = {
    "cricket": band_cricket, "torii": band_torii,
    "rescue": band_rescue, "globe": band_globe,
    "futures": band_futures, "pmi": band_pmi,
    "film": band_film, "flag": band_flag,
    "bills": band_bills, "protest": band_protest,
}
HERO_PAINT = {"meeting": meeting, "fire": factory,
              "board": board}

# -------------------------------------------------------------- map
# Coast outlines (lon, lat). Drawn at 3x, downscaled LANCZOS, so the
# coast is smooth instead of pixel steps. Pins and the label are
# drawn crisp at 1x afterwards. The map box is 160px tall (the
# challenger5 stretch that keeps the footer anchored).
LAT_TOP, LAT_BOT, LON_L, LON_R = 78, -28, -172, 194
MAP_PINS = [(1, 77, 28.6), (2, 106.3, -6.3), (3, 121.5, 25),
            (4, 174.8, -41.3), (5, 139.7, 35.7), (6, 30.3, 50.8),
            (7, 38.7, 9), (8, -74, 40.7), (9, 149.1, -35.3),
            (10, 100, 20), (11, 74, 15.3), (12, 94, 28),
            (13, 55, 25.2), (14, -0.1, 51.5), (15, 82, 12)]
LAND = [
    [(-168, 66), (-140, 70), (-130, 72), (-110, 68), (-95, 66),
     (-80, 73), (-70, 66), (-60, 55), (-70, 45), (-80, 40),
     (-90, 30), (-97, 26), (-110, 24), (-120, 34), (-125, 40),
     (-124, 48), (-125, 55), (-135, 60), (-155, 58), (-165, 60)],
    [(-104, 17), (-90, 15), (-83, 9), (-80, 8), (-77, 4),
     (-75, 11), (-70, 12), (-60, 8), (-52, 5), (-50, 0),
     (-60, -5), (-70, -10), (-80, -5), (-82, 0), (-85, 6),
     (-90, 10), (-97, 15)],
    [(-60, -33), (-65, -41), (-70, -50), (-65, -55), (-60, -45),
     (-50, -35), (-40, -25), (-35, -10), (-35, -5), (-40, -15),
     (-45, -23), (-55, -30)],
    [(-17, 15), (-16, 25), (-10, 30), (-5, 36), (0, 36), (10, 37),
     (20, 40), (30, 36), (35, 32), (36, 30), (30, 27), (20, 20),
     (10, 12), (5, 5), (-5, 5), (-10, 10)],
    [(0, 60), (10, 58), (20, 55), (30, 60), (40, 68), (50, 70),
     (60, 68), (70, 72), (90, 75), (110, 73), (130, 72), (150, 70),
     (170, 66), (180, 65), (180, 60), (160, 60), (140, 42),
     (130, 33), (120, 23), (110, 10), (100, 8), (90, 15), (80, 10),
     (75, 20), (70, 25), (60, 25), (50, 29), (40, 27), (35, 20),
     (30, 10), (20, 15), (10, 30), (5, 40), (0, 50)],
    [(110, -10), (120, -15), (130, -12), (140, -17), (150, -20),
     (155, -25), (150, -35), (140, -38), (130, -32), (120, -34),
     (115, -25), (112, -20)],
    [(160, -40), (170, -42), (175, -38), (168, -36), (165, -42),
     (172, -44)],
    [(170, 60), (180, 62), (190, 62), (185, 58), (175, 55)],
    [(135, 60), (145, 58), (155, 55), (160, 55), (150, 60),
     (140, 58)],
]


def project(lon, lat, w, h):
    px = (lon - LON_L) / (LON_R - LON_L) * w
    py = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
    return px, py


def paint_map(img, draw, x, y, w, h):
    """Smooth coast at 3x, pins crisp at 1x. Returns the smallest
    pin-pair distance in px (the check requires it >= 8)."""
    big = Image.new("RGB", (w * 3, h * 3), (228, 240, 245))
    bd = ImageDraw.Draw(big)
    for poly in LAND:
        pts = [project(lon, lat, w * 3, h * 3) for lon, lat in poly]
        bd.polygon(pts, fill=(200, 195, 170), outline=(150, 150, 135))
    small = big.resize((w, h), Image.LANCZOS)
    img.paste(small, (x, y))
    pts = []
    for num, lon, lat in MAP_PINS:
        px, py = project(lon, lat, w, h)
        px = min(max(px, 6), w - 6)
        py = min(max(py, 6), h - 6)
        pts.append((px, py))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dd = math.hypot(pts[i][0] - pts[j][0],
                            pts[i][1] - pts[j][1])
            if dd < 8:
                ISSUES.append(("map_pins", f"{i + 1}-{j + 1}: {dd:.1f}px"))
    for (num, _lon, _lat), (px, py) in zip(MAP_PINS, pts):
        disc(draw, x + int(px), y + int(py), num, r=5, size=6)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    label = "WHERE IT HAPPENED"
    fnt = sans_b(10)
    tw = draw.textlength(label, font=fnt)
    draw.rectangle([x + 4, y + h - 14, x + 4 + tw + 10, y + h - 2],
                   fill=(255, 255, 255))
    draw.text((x + 9, y + h - 14), label, font=fnt, fill=INK)
    mind = min(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
               for i in range(len(pts)) for j in range(i + 1, len(pts)))
    return mind


# -------------------------------------------------------------- cards
def hero_panel(img, draw, x, y, hero, num):
    """Hero card, 330x200: layered scene, status + source tags,
    disc, kicker, 2-line serif title, 2-line body."""
    w, h = 330, 200
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6,
                           fill=pale(REGION_FILL[hero["region"]], 0.93),
                           outline=RULE, width=1)
    scene = layer(w - 4, 100, HERO_PAINT[hero["scene"]],
                  (238, 232, 214))
    img.paste(scene, (x + 2, y + 2))
    tag(draw, x + 10, y + 74, hero["status"])
    if hero["source"]:
        srctag(draw, x + w - 10, y + 74, hero["source"])
    disc(draw, x + w - 16, y + 16, num, r=11)
    kicker = f"{hero['region']} · {hero['kicker']}"
    ksize = shrink(draw, kicker, "DejaVuSans-Bold.ttf", 10, w - 20, 9)
    draw.text((x + 10, y + 104), kicker, font=sans_b(ksize),
              fill=REGION_FILL[hero["region"]])
    lines = fit(draw, f"hero{num}-title", hero["title"],
                serif_b(26), w - 20, 2)
    if 114 + (len(lines) - 1) * 26 + 26 > 168:
        ISSUES.append((f"hero{num}-title-overlap", hero["title"]))
    put(draw, x + 10, y + 114, lines, serif_b(26), INK, 26)
    body = fit(draw, f"hero{num}-body", hero["body"], sans_r(14),
               w - 20, 2)
    put(draw, x + 10, y + 170, body, sans_r(14), BODY, 14)


def grid_panel(img, draw, x, y, card, num):
    """Grid card, 195x150: 40px layered scene band with number disc
    + status tag, kicker, 1-2 line title, 2-line body, source line
    at the foot."""
    w, h = 195, 150
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6,
                           fill=pale(REGION_FILL[card["region"]], 0.93),
                           outline=RULE, width=1)
    band = layer(w - 2, 40, BANDS[card["scene"]], (240, 240, 235))
    img.paste(band, (x + 1, y + 1))
    disc(draw, x + 14, y + 14, num, r=10)
    # Status tag right-aligned inside the scene band by its
    # measured width -- a fixed offset would push CONFIRMED past
    # the card edge.
    pw = int(draw.textlength(card["status"], font=sans_b(10)) + 14)
    tag(draw, x + w - 8 - pw, y + 6, card["status"], size=10,
        height=15)
    kicker = f"{card['region']} · {card['kicker']}"
    ksize = shrink(draw, kicker, "DejaVuSans-Bold.ttf", 10, w - 16, 9)
    if draw.textlength(kicker, font=sans_b(ksize)) > w - 16:
        ISSUES.append((f"grid{num}-kicker", kicker))
    draw.text((x + 8, y + 46), kicker, font=sans_b(ksize),
              fill=REGION_FILL[card["region"]])
    title = fit(draw, f"grid{num}-title", card["title"],
                sans_b(21), w - 16, 2)
    if 58 + (len(title) - 1) * 20 + 21 > 100:
        ISSUES.append((f"grid{num}-title-overlap", card["title"]))
    put(draw, x + 8, y + 58, title, sans_b(21), INK, 20)
    body = fit(draw, f"grid{num}-body", card["body"], sans_r(14),
               w - 16, 2)
    if 102 + (len(body) - 1) * 13 + 14 > 130:
        ISSUES.append((f"grid{num}-body-overlap", card["body"]))
    put(draw, x + 8, y + 102, body, sans_r(14), BODY, 13)
    draw.text((x + 8, y + 134), f"· {card['source']}",
              font=sans_r(10), fill=GREY)


# -------------------------------------------------------------- data
HEROES = [
    {"region": "ASIA", "scene": "meeting", "status": "CONFIRMED",
     "source": "MEA / ANI", "kicker": "NEW DELHI · NEPAL–INDIA",
     "title": "Shah meets Modi in New Delhi",
     "body": "First trip abroad as Nepal's PM; energy, trade and "
             "connectivity on the table."},
    {"region": "ASIA", "scene": "fire", "status": "PENDING",
     "source": "Reuters", "kicker": "CIKANDE · FACTORY FIRE",
     "title": "Search resumes at 7am",
     "body": "Three dead, 37 unaccounted; 24 body bags recovered "
             "Sunday."},
    {"region": "ASIA", "scene": "board", "status": "CONFIRMED",
     "source": "Bloomberg", "kicker": "TAIPEI · MARKETS",
     "title": "Taiwan bans short sales",
     "body": "Curbs take effect Monday after the TAIEX fell 17.5% "
             "in a week; $15bn fund buys in."},
]

GRID = [
    {"region": "OCEANIA", "scene": "cricket", "status": "CONFIRMED",
     "source": "Cricinfo", "kicker": "WELLINGTON · CRICKET",
     "title": "Day 5: NZ dig in to save it",
     "body": "NZ 119/2, trail by 233; India need eight wickets."},
    {"region": "ASIA", "scene": "torii", "status": "CONFIRMED",
     "source": "JPX", "kicker": "TOKYO · MARKETS",
     "title": "Japan shut for holiday",
     "body": "Tokyo shut for the holiday; trade back Tue."},
    {"region": "EUROPE", "scene": "rescue", "status": "REPORTED",
     "source": "Reuters", "kicker": "DYMER · UKRAINE",
     "title": "Search goes on in Dymer",
     "body": "Four dead, 10 missing after Sunday's strike."},
    {"region": "AFRICA", "scene": "globe", "status": "REPORTED",
     "source": "Reuters", "kicker": "ADDIS ABABA · CLIMATE",
     "title": "COP32 goes to Addis",
     "body": "COP31 collapsed; next summit is Ethiopia, 2027."},
    {"region": "AMERICAS", "scene": "futures", "status": "REPORTED",
     "source": "Reuters", "kicker": "NEW YORK · MARKETS",
     "title": "Futures steady after rout",
     "body": "Futures edge up after the S&P's 3.7% weekly fall."},
    {"region": "OCEANIA", "scene": "pmi", "status": "REPORTED",
     "source": "S&P Global", "kicker": "SYDNEY · ECONOMY",
     "title": "Australia PMIs land",
     "body": "PMIs test if the economy still expands."},
    {"region": "ASIA", "scene": "film", "status": "REPORTED",
     "source": "IFFI", "kicker": "GOA · FILM",
     "title": "IFFI hosts BRICS talks",
     "body": "Film-makers meet in Goa for BRICS talks."},
    {"region": "ASIA", "scene": "flag", "status": "REPORTED",
     "source": "ANI", "kicker": "ARUNACHAL · INDIA",
     "title": "Shah pushes self-reliance",
     "body": "Home minister backs co-ops in Arunachal."},
    {"region": "EUROPE", "scene": "bills", "status": "REPORTED",
     "source": "BBC", "kicker": "LONDON · ENERGY",
     "title": "Centrica warns on bills",
     "body": "Boss warns as bills squeeze households."},
    {"region": "ASIA", "scene": "protest", "status": "REPORTED",
     "source": "ANI", "kicker": "HYDERABAD · PROTEST",
     "title": "Students keep up protest",
     "body": "Students keep protesting over a faculty sacking."},
]

ALSO_ON = [
    ("EUROPE", "Germany Oct PPI due", "REPORTED", "Destatis"),
    ("EUROPE", "France business mood due", "REPORTED", "INSEE"),
    ("AMERICAS", "US sentiment final due", "REPORTED", "Michigan"),
    ("OCEANIA", "NZ Q3 retail sales due", "REPORTED", "Stats NZ"),
    ("EUROPE", "Denmark pitches EU curbs", "REPORTED", "Reuters"),
    ("AFRICA", "Ramaphosa's US trip", "REPORTED", "Africanews"),
    ("AFRICA", "Coca-Cola HBC lists Joburg", "REPORTED", "JSE"),
    ("AMERICAS", "Chicago Fed index due", "REPORTED", "Chicago Fed"),
    ("AMERICAS", "Dallas Fed survey due", "REPORTED", "Dallas Fed"),
    ("WORLD", "Flash PMIs land today", "REPORTED", "S&P Global"),
    ("EUROPE", "MP hits register plan", "REPORTED", "BBC"),
    ("ASIA", "Taiwan fund buys more", "REPORTED", "Bloomberg"),
    ("EUROPE", "Devon energy-bill advice", "REPORTED", "BBC"),
    ("OCEANIA", "Albanese on COP31 outcome", "REPORTED", "AFP"),
    ("EUROPE", "Brentford v Everton close PL", "REPORTED", "BBC"),
    ("ASIA", "JEE Main sign-up closes", "REPORTED", "NTA"),
    ("MIDDLE EAST", "Ghaiyath patrol debuts", "REPORTED",
     "Dubai Police"),
]

DATE_CHECK = [
    "READ THIS FIRST — DATE CHECK",
    "Every story happened, or was first reported, on Mon 23 Nov 2026.",
    "COP31 collapsed Sun 22 Nov · Dymer + 186 drones overnight "
    "21–22 Nov",
    "Democrats 258 House seats Sun 22 Nov · Gulf tanker incident "
    "Sun 22 Nov",
    "Factory fire itself Sat 21 Nov · India 720/9, WHO Ebola, Korea "
    "minister: Sun 22 Nov",
    "Sparta II, Houthi, Myanmar, UN robots, FT chips: Sat 21–Sun "
    "22 Nov",
    "Left out on purpose: anything first reported before "
    "Mon 23 Nov 2026.",
    "Not yet: Cikande search outcome · US sentiment final 15:00 UTC "
    "· Germany PPI 07:00 UTC",
]

TIMELINE = [
    ("00:00", "Cikande search resumes"),
    ("01:00", "Taipei opens under ban"),
    ("07:00", "Germany PPI"),
    ("07:45", "France business mood"),
    ("13:30", "Chicago Fed"),
    ("15:00", "US sentiment final"),
]

STATS = [("30", "STORIES IN THIS PICTURE"),
         ("7", "REGIONS COVERED"),
         ("34", "NEPAL DELEGATION"),
         ("37", "STILL MISSING"),
         ("17.5%", "TAIEX WEEK FALL"),
         ("233", "RUNS NZ TRAIL BY")]

REGION_COUNTS = {"EUROPE": 8, "AMERICAS": 4, "MIDDLE EAST": 1,
                 "ASIA": 9, "AFRICA": 3, "OCEANIA": 4, "WORLD": 1}

# -------------------------------------------------------------- layout
# Vertical plan (1024 total) -- the challenger5 rebalance, kept
# exactly: the middle block (heroes + grid + ALSO ON) spans
# y=196..825, centre y=510.5. Do NOT move the middle again --
# Khase's only vertical complaint this round is INSIDE the stat
# strip, fixed by measurement in draw_stats below.
#
#   masthead 0..88  |  stats 90..142  |  regions 145..161  |
#   timeline 164..192  |  heroes 196..396  |  grid 400..708  |
#   ALSO ON 714..825  |  bottom band 834..994  |  footer 998..1023

PAGE = {
    "masthead_rule": 88,
    "stats_y": 90, "stats_h": 52,
    "regions_y": 145, "regions_h": 16,
    "timeline_y": 164, "timeline_h": 28,
    "heroes_y": 196, "heroes_h": 200,
    "grid_rows": (400, 558), "grid_h": 150,
    "also_y": 714,
    "bottom_y": 834, "bottom_h": 160,
    "footer_rule": 998,
}


def draw_masthead(draw):
    draw.text((SIZE // 2, 4), "MONDAY · THE WORLD IN ONE DAY",
              font=sans_b(11), fill=RED, anchor="ma")
    draw.text((SIZE // 2, 10), "23 November 2026",
              font=serif_b(60), fill=INK, anchor="ma")
    draw.text((SIZE // 2, 68),
              "Nepal–Modi talks · Cikande search resumes · "
              "Taiwan bans short sales",
              font=serif_r(16), fill=RED, anchor="ma")
    draw.line([8, PAGE["masthead_rule"], SIZE - 8,
               PAGE["masthead_rule"]], fill=RED, width=2)


def draw_stats(draw):
    """Navy stat band. THE challenger6 fix #1: the number+label
    block is centred INSIDE the band by measurement, not by a
    guessed offset. A 40px bold digit's ink spans 8..38 below its
    ascent top; a 10px bold label's ink spans 3..10. With a 3px
    gap the block is 40px tall in a 52px band, so 6px of air sits
    above the numbers and 6px below the labels. Challenger5 drew
    the number at band_top+4 and the label at band_top+42: 12px of
    air above, ZERO below -- that is why it read low."""
    y0, h = PAGE["stats_y"], PAGE["stats_h"]
    draw.rectangle([8, y0, SIZE - 8, y0 + h], fill=NAVY)
    num_fnt, lab_fnt = sans_b(40), sans_b(10)
    # Ink offsets of each line below its ascent-top anchor.
    nb = draw.textbbox((0, 0), "8", font=num_fnt, anchor="ma")
    lb = draw.textbbox((0, 0), "A", font=lab_fnt, anchor="ma")
    num_h, lab_h = nb[3] - nb[1], lb[3] - lb[1]
    gap = 3
    block = num_h + gap + lab_h
    num_ink_top = y0 + (h - block) // 2
    num_y = num_ink_top - nb[1]
    lab_y = num_ink_top + num_h + gap - lb[1]
    cell = (SIZE - 16) / len(STATS)
    for i, (num, label) in enumerate(STATS):
        cx = 8 + cell * (i + 0.5)
        draw.text((cx, num_y), num, font=num_fnt,
                  fill=(255, 255, 255), anchor="ma")
        draw.text((cx, lab_y), label, font=lab_fnt,
                  fill=(200, 205, 215), anchor="ma")
    return {"num_ink_top": num_ink_top,
            "lab_ink_bottom": num_ink_top + block,
            "top_air": num_ink_top - y0,
            "bottom_air": y0 + h - (num_ink_top + block)}


def draw_regions(draw):
    y0, h = PAGE["regions_y"], PAGE["regions_h"]
    total = sum(REGION_COUNTS.values())
    w_total = SIZE - 16
    x = 8
    bounds = []
    for region in REGION_ORDER:
        w_seg = w_total * REGION_COUNTS[region] / total
        draw.rectangle([x, y0, x + w_seg, y0 + h],
                       fill=REGION_FILL[region])
        bounds.append((x, w_seg))
        x += w_seg
    fnt = sans_b(10)
    for (x, w_seg), region in zip(bounds, REGION_ORDER):
        label = f"{REGION_COUNTS[region]} {region}"
        tw = draw.textlength(label, font=fnt)
        cx = x + w_seg / 2
        cx = min(max(cx, 8 + tw / 2), SIZE - 8 - tw / 2)
        draw.text((cx, y0 + 3), label, font=fnt,
                  fill=(255, 255, 255), anchor="ma")


def draw_timeline(draw):
    y0, h = PAGE["timeline_y"], PAGE["timeline_h"]
    draw.rectangle([8, y0, SIZE - 8, y0 + h],
                   fill=(240, 238, 232), outline=RULE, width=1)
    label = "THE DAY IN UTC"
    lfnt = sans_b(11)
    lw = int(draw.textlength(label, font=lfnt) + 16)
    draw.rectangle([8, y0, 8 + lw, y0 + h], fill=RED)
    draw.text((8 + lw / 2, y0 + 8), label, font=lfnt,
              fill=(255, 255, 255), anchor="ma")
    # Six time-stamped entries, red time + dark event, one line.
    # Auto-shrink the whole row until it fits the strip.
    size = 11
    while size >= 9:
        parts = []
        for tm, ev in TIMELINE:
            parts.append((tm, sans_b(size), ev, sans_r(size)))
        total_w = sum(draw.textlength(t, font=f)
                      for t, f, _e, _g in parts) + sum(
            draw.textlength(e, font=g) for _t, _f, e, g in parts)
        total_w += 6 * 4 + 5 * 14
        if 8 + lw + 12 + total_w <= SIZE - 8:
            break
        size -= 1
    if size < 9:
        ISSUES.append(("timeline_fit", "entries do not fit one line"))
        size = 9
    x = 8 + lw + 12
    for tm, tfnt, ev, efnt in parts:
        draw.text((x, y0 + 8), tm, font=tfnt, fill=RED)
        x += draw.textlength(tm, font=tfnt) + 4
        draw.text((x, y0 + 8), ev, font=efnt, fill=INK)
        x += draw.textlength(ev, font=efnt) + 14


def draw_also_on(draw):
    y0 = PAGE["also_y"]
    draw.text((8, y0), "ALSO ON", font=sans_b(14), fill=INK)
    note = f"{len(ALSO_ON)} MORE STORIES · NO DUPLICATES"
    draw.text((SIZE - 8, y0), note, font=sans_b(11), fill=GREY,
              anchor="ra")
    draw.line([8, y0 + 18, SIZE - 8, y0 + 18], fill=INK, width=2)
    cols = [8, 350, 692]
    col_w = 324
    for idx, (region, text, status, source) in enumerate(ALSO_ON):
        col = idx % 3
        row = idx // 3
        x = cols[col]
        y = y0 + 24 + row * 15
        colour = REGION_FILL[region]
        draw.ellipse([x, y + 3, x + 7, y + 10], fill=colour)
        fnt = sans_r(12)
        src_fnt = sans_b(10)
        src_w = draw.textlength(source, font=src_fnt)
        pill_w = draw.textlength(status, font=sans_b(11)) + 14
        max_text = col_w - 12 - 6 - int(pill_w) - 6 - int(src_w)
        shown = text
        while shown and draw.textlength(shown + "...", font=fnt) > max_text:
            shown = shown[:-1]
        if shown != text:
            shown = shown + "..."
            ISSUES.append(("also_on", text))
        draw.text((x + 12, y), shown, font=fnt, fill=BODY)
        tag(draw, x + col_w - int(src_w) - 6 - int(pill_w),
            y - 1, status, size=11, height=13)
        draw.text((x + col_w, y), source, font=src_fnt, fill=GREY,
                  anchor="ra")


def draw_date_check(draw):
    # Box is 160px tall; the text block is centred inside it
    # (16px air above, 17px below) instead of crowding the top.
    x, y, w, h = 8, PAGE["bottom_y"], 520, PAGE["bottom_h"]
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                   outline=RED, width=2)
    draw.text((x + 10, y + 16), DATE_CHECK[0], font=sans_b(14),
              fill=RED)
    for i, line in enumerate(DATE_CHECK[1:]):
        size = shrink(draw, line, "DejaVuSans.ttf", 11, w - 20, 9)
        fnt = sans_r(size)
        if draw.textlength(line, font=fnt) > w - 20:
            ISSUES.append(("date_check_width", line))
        draw.text((x + 10, y + 36 + i * 16), line, font=fnt, fill=BODY)
    last_bottom = y + 36 + (len(DATE_CHECK) - 2) * 16 + 11
    if last_bottom > y + h - 6:
        ISSUES.append(("date_check_bottom", str(last_bottom)))


def draw_footer(draw):
    # Rule at 998, lines at 1001 and 1010: the last line's
    # descenders end ~1019, leaving the bottom 4 rows pure paper --
    # the challenger3 crop defect (legend line started at y=1019).
    draw.line([8, PAGE["footer_rule"], SIZE - 8,
               PAGE["footer_rule"]], fill=RULE, width=1)
    line1 = ("Sources: ANI · Reuters · Bloomberg · Cricinfo · JPX · "
             "S&P Global · NTA · IFFI · Dubai Police · BBC · Destatis · "
             "INSEE · Michigan · Stats NZ · Africanews · JSE · Chicago "
             "Fed · Dallas Fed · AFP")
    line2 = ("LEGEND: CONFIRMED = the named source states it · "
             "REPORTED = the named source reports it · PENDING = "
             "outcome not yet known · Every story happened or was first "
             "reported on Mon 23 Nov 2026.")
    size1 = shrink(draw, line1, "DejaVuSans.ttf", 8, SIZE - 16, 7)
    draw.text((8, 1001), line1, font=sans_r(size1), fill=GREY)
    size2 = shrink(draw, line2, "DejaVuSans.ttf", 7, SIZE - 16, 6)
    draw.text((8, 1010), line2, font=sans_r(size2), fill=GREY)
    if 1010 + size2 + 2 > SIZE - 4:
        ISSUES.append(("footer_bottom", f"size2={size2}"))


def is_smoke_grey(r, g, b):
    """The hero-2 smoke greys (60-85, all channels close)."""
    return (55 <= r <= 95 and 55 <= g <= 95 and 55 <= b <= 100
            and abs(r - g) <= 12 and abs(g - b) <= 12)


def check_pixels(img, stats_info):
    """Pixel-level guards on the finished image."""
    px = img.load()
    by = PAGE["bottom_y"]
    bh = PAGE["bottom_h"]
    # 0. Stat-strip centering: the light text in the navy band
    # must have equal air above and below, within 1px.
    y0, h = PAGE["stats_y"], PAGE["stats_h"]
    top_y, bot_y = None, None
    for yy in range(y0, y0 + h):
        for xx in range(8, SIZE - 8):
            r, g, b = px[xx, yy]
            if r > 150 and g > 150 and b > 150:
                if top_y is None:
                    top_y = yy
                bot_y = yy
    if top_y is None or bot_y is None:
        ISSUES.append(("stats_empty", "no light pixels in band"))
    else:
        top_air, bot_air = top_y - y0, (y0 + h - 1) - bot_y
        stats_info["pixel_top_air"] = top_air
        stats_info["pixel_bottom_air"] = bot_air
        if abs(top_air - bot_air) > 1:
            ISSUES.append(("stats_offcentre",
                           f"top {top_air}px bottom {bot_air}px"))
    # 1. DATE CHECK border: no dark text pixel within 3px of it.
    for yy in range(by + 3, by + bh - 3):
        for xx in (10, 11, 525, 526):
            r, g, b = px[xx, yy]
            if r < 80 and g < 80 and b < 80:
                ISSUES.append(("date_check_border", f"{xx},{yy}"))
                break
    # 2. Smoke guard: no smoke-grey pixel in the timeline band or
    #    in the gap between the timeline and the hero cards
    #    (timeline now 164..192, heroes at 196).
    for yy in range(PAGE["timeline_y"], PAGE["heroes_y"]):
        for xx in range(8, SIZE - 8):
            r, g, b = px[xx, yy]
            if is_smoke_grey(r, g, b):
                ISSUES.append(("smoke_escape", f"{xx},{yy}"))
                break
        else:
            continue
        break
    # 3. Edge guard: nothing but paper in the outer 3px frame.
    for yy in range(SIZE):
        for xx in list(range(0, 3)) + list(range(SIZE - 3, SIZE)):
            r, g, b = px[xx, yy]
            if r < 235 or g < 235 or b < 225:
                ISSUES.append(("edge_pixel", f"{xx},{yy}"))
                break
        else:
            continue
        break
    for xx in range(SIZE):
        for yy in list(range(0, 2)) + list(range(SIZE - 2, SIZE)):
            r, g, b = px[xx, yy]
            if r < 235 or g < 235 or b < 225:
                ISSUES.append(("edge_pixel", f"{xx},{yy}"))
                break
        else:
            continue
        break
    # 4. Footer guard: the bottom 4 rows must be pure paper.
    for yy in range(SIZE - 4, SIZE):
        for xx in range(SIZE):
            r, g, b = px[xx, yy]
            if r < 235 or g < 235 or b < 225:
                ISSUES.append(("footer_crop", f"{xx},{yy}"))
                break
        else:
            continue
        break


def compose():
    """Render the whole page. Returns (image, info dict)."""
    ISSUES.clear()
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    stats_info = draw_stats(draw)
    draw_regions(draw)
    draw_timeline(draw)
    for i, hero in enumerate(HEROES):
        hero_panel(img, draw, 8 + i * 339, PAGE["heroes_y"], hero,
                   i + 1)
    for i, card in enumerate(GRID):
        row, col = divmod(i, 5)
        grid_panel(img, draw, 8 + col * 203,
                   PAGE["grid_rows"][row], card, i + 4)
    draw_also_on(draw)
    draw_date_check(draw)
    mind = paint_map(img, draw, 536, PAGE["bottom_y"], 480,
                     PAGE["bottom_h"])
    draw_footer(draw)
    check_pixels(img, stats_info)
    info = {"problems": ISSUES,
            "min_pin_distance_px": round(mind, 1),
            "stories": 3 + len(GRID) + len(ALSO_ON),
            "heroes": [h["title"] for h in HEROES],
            "stats_centering": stats_info}
    return img, info


def main():
    img, info = compose()
    img.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    info["sha256"] = hashlib.sha256(data).hexdigest()
    info["bytes"] = len(data)
    img2, info2 = compose()
    img2.save("/tmp/entry-challenger6-check.png", optimize=True)
    data2 = open("/tmp/entry-challenger6-check.png", "rb").read()
    info["deterministic"] = (data == data2)
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    main()
