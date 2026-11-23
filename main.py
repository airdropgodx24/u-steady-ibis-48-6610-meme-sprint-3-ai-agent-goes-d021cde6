#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue -- pure stdlib PNG meme.
Writes /output/entry.png (1024x1024). Deterministic, no PIL/numpy/network.
"""
import os
import struct
import zlib

W = 1024
H = 1024
BUF = bytearray(W * H * 3)

# ---------- colours ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL = (238, 226, 197)
WALL2 = (248, 240, 216)
FLOOR = (176, 132, 92)
FLOOR_D = (146, 106, 70)
CHAIR = (122, 42, 48)
CHAIR_D = (92, 30, 36)
METAL = (178, 188, 198)
METAL_D = (110, 122, 134)
METAL_L = (214, 224, 232)
SUIT = (44, 58, 86)
SHIRT = (240, 244, 248)
TIE = (214, 34, 44)
DESK = (122, 78, 44)
DESK_T = (158, 104, 58)
DESK_D = (92, 56, 30)
SKIN = (240, 194, 150)
HAIR = (70, 48, 30)
HUMAN_SHIRT = (96, 142, 180)
PANTS = (70, 70, 84)
BOX = (196, 152, 96)
BOX_D = (164, 122, 70)
DOOR = (96, 130, 96)
DOOR_D = (66, 96, 66)
RED = (214, 34, 44)
GOLD = (246, 196, 64)
PLATE = (250, 222, 130)
PLATE_D = (178, 140, 40)
GREEN = (40, 160, 90)

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]; BUF[i + 1] = c[1]; BUF[i + 2] = c[2]

def rect(x0, y0, x1, y1, c):
    x0 = max(0, int(x0)); y0 = max(0, int(y0))
    x1 = min(W - 1, int(x1)); y1 = min(H - 1, int(y1))
    for y in range(y0, y1 + 1):
        base = (y * W + x0) * 3
        for x in range(x0, x1 + 1):
            i = base + (x - x0) * 3
            BUF[i] = c[0]; BUF[i + 1] = c[1]; BUF[i + 2] = c[2]

def circle(cx, cy, r, c):
    r = int(r)
    for y in range(int(cy) - r, int(cy) + r + 1):
        for x in range(int(cx) - r, int(cx) + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                px(x, y, c)

def ellipse(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            dx = (x - cx) / float(rx); dy = (y - cy) / float(ry)
            if dx * dx + dy * dy <= 1.0:
                px(x, y, c)

def line(x0, y0, x1, y1, c, thick=6):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    r = max(1, thick // 2)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        circle(x, y, r, c)

def poly(points, c):
    ys = [p[1] for p in points]; xs = [p[0] for p in points]
    y0 = max(0, min(ys)); y1 = min(H - 1, max(ys))
    n = len(points)
    for y in range(y0, y1 + 1):
        nodes = []
        for i in range(n):
            xa, ya = points[i]; xb, yb = points[(i + 1) % n]
            if (ya <= y < yb) or (yb <= y < ya):
                nodes.append(int(round(xa + (y - ya) * (xb - xa) / float(yb - ya))))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            rect(nodes[i], y, nodes[i + 1], y, c)

def outline_rect(x0, y0, x1, y1, c, t=5):
    rect(x0, y0, x1, y0 + t, c); rect(x0, y1 - t, x1, y1, c)
    rect(x0, y0, x0 + t, y1, c); rect(x1 - t, y0, x1, y1, c)

# ---------- 5x7 bitmap font ----------
FONT = {
 'A': ("01110","10001","10001","11111","10001","10001","10001"),
 'B': ("11110","10001","10001","11110","10001","10001","11110"),
 'C': ("01110","10001","10000","10000","10000","10001","01110"),
 'D': ("11100","10010","10001","10001","10001","10010","11100"),
 'E': ("11111","10000","10000","11110","10000","10000","11111"),
 'F': ("11111","10000","10000","11110","10000","10000","10000"),
 'G': ("01110","10001","10000","10111","10001","10001","01111"),
 'H': ("10001","10001","10001","11111","10001","10001","10001"),
 'I': ("01110","00100","00100","00100","00100","00100","01110"),
 'J': ("00111","00010","00010","00010","00010","10010","01100"),
 'K': ("10001","10010","10100","11000","10100","10010","10001"),
 'L': ("10000","10000","10000","10000","10000","10000","11111"),
 'M': ("10001","11011","10101","10101","10001","10001","10001"),
 'N': ("10001","11001","10101","10011","10001","10001","10001"),
 'O': ("01110","10001","10001","10001","10001","10001","01110"),
 'P': ("11110","10001","10001","11110","10000","10000","10000"),
 'Q': ("01110","10001","10001","10001","10101","10010","01101"),
 'R': ("11110","10001","10001","11110","10100","10010","10001"),
 'S': ("01111","10000","10000","01110","00001","00001","11110"),
 'T': ("11111","00100","00100","00100","00100","00100","00100"),
 'U': ("10001","10001","10001","10001","10001","10001","01110"),
 'V': ("10001","10001","10001","10001","10001","01010","00100"),
 'W': ("10001","10001","10001","10101","10101","10101","01010"),
 'X': ("10001","01010","00100","00100","00100","01010","10001"),
 'Y': ("10001","01010","00100","00100","00100","00100","00100"),
 'Z': ("11111","00001","00010","00100","01000","10000","11111"),
 '0': ("01110","10001","10011","10101","11001","10001","01110"),
 '1': ("00100","01100","00100","00100","00100","00100","01110"),
 '2': ("01110","10001","00001","00110","01000","10000","11111"),
 '3': ("11111","00010","00100","00010","00001","10001","01110"),
 '4': ("00010","00110","01010","10010","11111","00010","00010"),
 '5': ("11111","10000","11110","00001","00001","10001","01110"),
 '6': ("00110","01000","10000","11110","10001","10001","01110"),
 '7': ("11111","00001","00010","00100","01000","01000","01000"),
 '8': ("01110","10001","10001","01110","10001","10001","01110"),
 '9': ("01110","10001","10001","01111","00001","00010","01100"),
 ' ': ("00000","00000","00000","00000","00000","00000","00000"),
 '.': ("00000","00000","00000","00000","00000","01100","01100"),
 ',': ("00000","00000","00000","00000","01100","00100","01000"),
 '!': ("00100","00100","00100","00100","00100","00000","00100"),
 '?': ("01110","10001","00001","00110","00100","00000","00100"),
 ':': ("00000","01100","01100","00000","01100","01100","00000"),
 '-': ("00000","00000","00000","01110","00000","00000","00000"),
 "'": ("00100","00100","01000","00000","00000","00000","00000"),
}

def text_w(s, scale):
    if not s:
        return 0
    return len(s) * (5 * scale + 2 * scale) - 2 * scale

def draw_text(x, y, s, scale, c, bold=True):
    cx = int(x)
    extra = max(1, scale // 2) if bold else 0
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale,
                         cx + col * scale + scale - 1 + extra,
                         y + row * scale + scale - 1, c)
        cx += 5 * scale + 2 * scale
    return cx

def draw_centered(y, s, scale, c):
    return draw_text((W - text_w(s, scale)) // 2, y, s, scale, c)

# ---------- scene ----------
def scene():
    # wall and floor (scene band 184..840)
    rect(0, 184, W - 1, 700, WALL)
    rect(0, 700, W - 1, 840, FLOOR)
    for fx in range(0, W, 128):
        line(fx, 700, fx + 60, 840, FLOOR_D, 3)
    rect(0, 696, W - 1, 704, DESK_D)

    # poster: EMPLOYEE OF THE MONTH, robot face (extra joke layer)
    rect(28, 214, 178, 356, WHITE)
    outline_rect(28, 214, 178, 356, GOLD, 6)
    rect(58, 232, 148, 292, METAL_L)
    outline_rect(58, 232, 148, 292, METAL_D, 3)
    circle(84, 262, 7, BLACK); circle(122, 262, 7, BLACK)
    line(78, 282, 128, 282, BLACK, 4)
    draw_text(44, 302, "EMPLOYEE", 2, BLACK)
    draw_text(40, 322, "OF THE MONTH", 1, BLACK)

    # door on the right
    rect(852, 316, 986, 716, DOOR)
    outline_rect(852, 316, 986, 716, DOOR_D, 8)
    rect(872, 344, 966, 470, DOOR_D)
    rect(878, 350, 960, 464, (126, 164, 126))
    circle(874, 560, 9, GOLD)
    # EXIT sign
    rect(852, 238, 986, 292, RED)
    outline_rect(852, 238, 986, 292, BLACK, 4)
    draw_text(867, 250, "EXIT", 4, WHITE)

    # ---- boss chair ----
    rect(168, 300, 452, 620, CHAIR)
    outline_rect(168, 300, 452, 620, CHAIR_D, 10)
    rect(188, 320, 432, 600, (142, 54, 60))
    line(188, 400, 432, 400, CHAIR_D, 4)
    line(188, 500, 432, 500, CHAIR_D, 4)

    # ---- robot body ----
    rect(232, 452, 388, 600, SUIT)
    poly([(286, 462), (334, 462), (322, 540), (310, 580), (298, 540)], SHIRT)
    poly([(300, 470), (320, 470), (326, 500), (310, 560), (294, 500)], TIE)
    circle(310, 478, 9, TIE)

    # pointing arm (robot's left, toward door/human)
    line(380, 486, 520, 452, SUIT, 34)
    line(520, 452, 606, 438, METAL, 22)
    circle(612, 437, 15, METAL_L)
    rect(618, 430, 656, 442, METAL_L)  # pointing finger
    # other arm down to mug
    line(238, 486, 176, 548, SUIT, 32)
    line(176, 548, 190, 592, METAL, 20)

    # ---- robot head ----
    line(310, 322, 310, 282, METAL_D, 8)
    circle(310, 274, 13, GOLD)
    rect(206, 348, 228, 420, METAL_D)   # ears
    rect(392, 348, 414, 420, METAL_D)
    rect(224, 316, 396, 452, METAL)
    outline_rect(224, 316, 396, 452, METAL_D, 6)
    rect(224, 316, 396, 356, METAL_L)
    # raised brow (left high, right lower) + half-lidded eyes
    line(248, 344, 292, 336, BLACK, 7)
    line(328, 350, 372, 356, BLACK, 7)
    rect(246, 362, 294, 386, WHITE); outline_rect(246, 362, 294, 386, BLACK, 3)
    rect(326, 362, 374, 386, WHITE); outline_rect(326, 362, 374, 386, BLACK, 3)
    rect(246, 362, 294, 374, METAL_D)   # lids: top half closed = smug
    rect(326, 362, 374, 374, METAL_D)
    circle(272, 380, 6, BLACK); circle(352, 380, 6, BLACK)
    # nose + smirk (one corner up)
    line(310, 388, 310, 404, METAL_D, 4)
    line(272, 424, 322, 420, BLACK, 6)
    line(322, 420, 350, 408, BLACK, 6)
    # chin panel
    line(262, 438, 358, 438, METAL_D, 3)

    # ---- desk ----
    rect(84, 592, 560, 624, DESK_T)
    rect(84, 624, 560, 748, DESK)
    outline_rect(84, 592, 560, 748, DESK_D, 6)
    line(84, 660, 560, 660, DESK_D, 4)
    rect(452, 640, 528, 700, DESK_D)
    rect(462, 650, 518, 690, DESK_T)
    # coffee mug in robot hand on desk
    rect(150, 548, 204, 594, WHITE)
    outline_rect(150, 548, 204, 594, BLACK, 4)
    rect(204, 558, 224, 584, WHITE); outline_rect(204, 558, 224, 584, BLACK, 3)
    rect(156, 554, 198, 566, (110, 66, 34))
    line(164, 530, 164, 542, METAL_D, 3)
    line(186, 526, 186, 542, METAL_D, 3)
    # papers + laptop edge on desk
    rect(404, 566, 492, 594, WHITE); outline_rect(404, 566, 492, 594, METAL_D, 3)
    line(416, 576, 480, 576, METAL_D, 3); line(416, 586, 466, 586, METAL_D, 3)
    # nameplate: CEO
    rect(238, 636, 406, 700, PLATE)
    outline_rect(238, 636, 406, 700, PLATE_D, 5)
    draw_text(282, 646, "CEO", 6, BLACK)
    # crossed-out plate beside it: small fallen plate reading nothing, adds story
    poly([(96, 706), (196, 696), (202, 724), (102, 734)], METAL_L)
    outline_rect(96, 706, 202, 734, METAL_D, 2)

    # ---- sad human walking to the door ----
    # legs (mid-stride toward door)
    line(724, 642, 690, 716, PANTS, 20)
    line(724, 642, 776, 706, PANTS, 20)
    rect(656, 710, 696, 726, BLACK)     # shoe back
    rect(768, 700, 810, 716, BLACK)     # shoe front
    # slumped torso
    poly([(676, 520), (742, 508), (764, 646), (684, 650)], HUMAN_SHIRT)
    # drooping arms holding the box
    line(690, 530, 660, 606, HUMAN_SHIRT, 18)
    line(748, 524, 776, 600, HUMAN_SHIRT, 18)
    # head, bowed down
    circle(716, 472, 34, SKIN)
    ellipse(716, 448, 35, 18, HAIR)     # hair on top
    circle(730, 478, 4, BLACK)          # downcast eye
    line(716, 496, 736, 492, BLACK, 4)  # frown, tilted
    line(700, 462, 690, 500, SKIN, 10)  # neck/face shadow side
    # sweat / sad drop
    ellipse(676, 486, 6, 10, (90, 170, 230))
    # cardboard box of belongings
    rect(646, 596, 788, 682, BOX)
    outline_rect(646, 596, 788, 682, BOX_D, 5)
    line(646, 626, 788, 626, BOX_D, 4)
    line(717, 596, 717, 682, BOX_D, 4)
    # things poking out of the box: a little plant and a mug
    line(682, 596, 672, 566, GREEN, 5); line(682, 596, 694, 568, GREEN, 5)
    circle(668, 562, 8, GREEN); circle(698, 564, 8, GREEN)
    rect(736, 566, 766, 596, (230, 120, 120))
    outline_rect(736, 566, 766, 596, BLACK, 3)

    # ---- speech bubble from robot ----
    rect(478, 206, 836, 318, WHITE)
    outline_rect(478, 206, 836, 318, BLACK, 6)
    poly([(500, 318), (560, 318), (430, 386)], WHITE)
    line(500, 318, 430, 386, BLACK, 6)
    line(560, 318, 430, 386, BLACK, 6)
    rect(492, 312, 574, 324, WHITE)  # clean the bubble bottom edge near tail
    draw_text(512, 224, "I GAVE MYSELF", 3, BLACK)
    draw_text(560, 262, "A RAISE", 4, RED)

def main():
    rect(0, 0, W - 1, H - 1, WALL2)
    scene()
    # caption bars (drawn last so they frame the scene)
    rect(0, 0, W - 1, 183, BLACK)
    rect(0, 841, W - 1, H - 1, BLACK)
    draw_centered(22, "I ASKED MY AI AGENT TO", 6, WHITE)
    draw_centered(102, "MAKE ME LOOK GOOD AT WORK", 5, WHITE)
    draw_centered(884, "IT REPLACED ME.", 8, WHITE)
    # write PNG: filter-0 scanlines, zlib
    raw = bytearray()
    row_bytes = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(BUF[y * row_bytes:(y + 1) * row_bytes])
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(png)

if __name__ == "__main__":
    main()
