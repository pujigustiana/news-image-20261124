# News-24 renderer — draws THE WORLD TODAY (Tuesday 24 November 2026)
# as a single 1024x1024 PNG with PIL only. Deterministic: no random,
# no timestamps, fixed fonts, fixed palette.
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FDIR = "/usr/share/fonts/truetype/noto"
def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SERIF_B = lambda s: F("NotoSerif-Bold.ttf", s)
SERIF_R = lambda s: F("NotoSerif-Regular.ttf", s)
SERIF_BLK = lambda s: F("NotoSerif-Black.ttf", s)
SERIF_I = lambda s: F("NotoSerif-Italic.ttf", s)
SANS_B = lambda s: F("NotoSans-Bold.ttf", s)
SANS_R = lambda s: F("NotoSans-Regular.ttf", s)
SANS_I = lambda s: F("NotoSans-Italic.ttf", s)

INK    = (18, 18, 18)
PAPER  = (255, 255, 255)
RED    = (178, 24, 24)
GRAY   = (90, 90, 90)
LGRAY  = (225, 225, 225)

REGIONS = {
    "EUROPE":      ((31, 119, 180), 9),
    "OCEANIA":     ((0, 150, 136), 7),
    "ASIA":        ((198, 40, 40), 6),
    "AMERICAS":    ((230, 126, 34), 5),
    "MIDDLE EAST": ((123, 90, 160), 1),
    "AFRICA":      ((160, 120, 40), 1),
    "WORLD":       ((110, 110, 110), 1),
}

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def tw(text, font):
    return d.textlength(text, font=font)

def wrap(text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(t, font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def spaced(draw, xy, text, font, fill, ls=2):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + ls
    return x

def center(y, text, font, fill, cx=512):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma")

def rule(y, x0=24, x1=1000, w=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)

# ---------------------------------------------------------------- masthead
d.line([(24, 12), (1000, 12)], fill=RED, width=4)
spaced(d, (24, 22), "THE WORLD IN ONE DAY", SANS_B(14), RED, ls=4)
d.text((1000, 22), "ONE PAGE  •  EVERY WIRE READ TO 04:00 UTC", font=SANS_B(11),
       fill=GRAY, anchor="ra")
center(44, "THE WORLD TODAY", SERIF_BLK(58), INK)
center(106, "Tuesday 24 November 2026", SERIF_B(25), INK)
rule(140, 24, 380, 1, LGRAY)
rule(140, 644, 1000, 1, LGRAY)

# red deck band: the three lead headlines
deck = ["NEPAL QUAKE  M5.3  ROCKS KOSHI",
        "STRIKE IN KHAN YOUNIS KILLS 3",
        "ASIAN MARKETS SURGE — NIKKEI +4.3%"]
d.rectangle([24, 150, 1000, 178], fill=RED)
for i, t in enumerate(deck):
    x0 = 24 + i * 325
    d.text((x0 + 14, 158), t, font=SANS_B(12), fill=(255, 255, 255))

# region chips with honest counts (30 stories: 9+7+6+5+1+1+1)
chips = [(name, col, n) for name, (col, n) in REGIONS.items()]
chips.append(("TOTAL", (18, 18, 18), 30))
widths = []
for name, col, n in chips:
    w_ = 16 + tw(name, SANS_B(12)) + 6 + tw(str(n), SANS_B(13)) + 16
    widths.append(w_)
gap = 8
total = sum(widths) + gap * (len(widths) - 1)
x = 512 - total // 2
y0 = 186
for (name, col, n), w_ in zip(chips, widths):
    d.rounded_rectangle([x, y0, x + w_, y0 + 26], radius=13, outline=col, width=2)
    d.ellipse([x + 9, y0 + 9, x + 19, y0 + 19], fill=col)
    d.text((x + 24, y0 + 5), name, font=SANS_B(12), fill=INK)
    d.text((x + 24 + tw(name, SANS_B(12)) + 6, y0 + 4), str(n),
           font=SANS_B(13), fill=col)
    x += w_ + gap

# ---------------------------------------------------------------- timeline
d.text((24, 220), "THE DAY IN UTC", font=SANS_B(11), fill=RED)
d.line([(150, 242), (1000, 242)], fill=LGRAY, width=2)
stops = [
    ("00:30", "Khan Younis\nstrike"),
    ("00:30", "Emmy\nawards"),
    ("01:00", "Trump appeal\ncourt opens way"),
    ("01:32", "Nepal\nquake"),
    ("03:00", "Markets surge\nSingapore replies"),
    ("07:52 KST", "Korea jets\nscramble"),
    ("14:00", "Chess game 1\nstarts"),
]
for i, (t, lab) in enumerate(stops):
    cx = 185 + i * 132
    d.ellipse([cx - 5, 237, cx + 5, 247], fill=RED)
    d.text((cx, 220), t, font=SANS_B(11), fill=INK, anchor="ma")
    d.text((cx, 252), lab, font=SANS_R(10), fill=GRAY, anchor="ma")

# ---------------------------------------------------------------- lead scenes
def sky_grad(box, top, bot):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        f = (yy - y0) / max(1, (y1 - y0))
        c = tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3))
        d.line([(x0, yy), (x1, yy)], fill=c)

def scene_nepal(box):
    x0, y0, x1, y1 = box
    sky_grad(box, (58, 84, 120), (214, 226, 235))
    peaks = [(x0, y1), (x0 + 60, y0 + 42), (x0 + 110, y1 - 18),
             (x0 + 170, y0 + 22), (x0 + 230, y1 - 12),
             (x0 + 285, y0 + 48), (x1, y1)]
    d.polygon(peaks, fill=(148, 162, 178))
    d.polygon([(x0 + 60, y0 + 42), (x0 + 44, y0 + 58), (x0 + 78, y0 + 58)],
              fill=(250, 250, 250))
    d.polygon([(x0 + 170, y0 + 22), (x0 + 152, y0 + 40), (x0 + 190, y0 + 40)],
              fill=(250, 250, 250))
    d.polygon([(x0, y1), (x0, y1 - 26), (x1, y1 - 20), (x1, y1)], fill=(96, 104, 90))
    crack = [(x0 + 40, y1 - 8), (x0 + 70, y1 - 16), (x0 + 95, y1 - 6),
             (x0 + 130, y1 - 18), (x0 + 160, y1 - 8), (x0 + 200, y1 - 16),
             (x0 + 240, y1 - 6), (x0 + 280, y1 - 14)]
    d.line(crack, fill=(30, 28, 26), width=3)
    d.rectangle([x0 + 210, y1 - 46, x0 + 236, y1 - 20], fill=(70, 60, 52))
    d.polygon([(x0 + 206, y1 - 46), (x0 + 223, y1 - 56), (x0 + 240, y1 - 46)],
              fill=(120, 40, 32))
    d.rectangle([x0 + 250, y1 - 40, x0 + 272, y1 - 20], fill=(88, 76, 64))
    for (dx, dy, r) in [(90, 66, 5), (120, 74, 7), (150, 62, 4), (180, 78, 6)]:
        d.ellipse([x0 + dx - r, y0 + dy - r, x0 + dx + r, y0 + dy + r],
                  fill=(226, 220, 208))

def scene_khan(box):
    x0, y0, x1, y1 = box
    sky_grad(box, (196, 120, 74), (238, 214, 182))
    for (dx, dy, r) in [(150, 26, 16), (168, 38, 20), (146, 52, 22),
                        (172, 66, 18), (150, 78, 14)]:
        d.ellipse([x0 + dx - r, y0 + dy - r, x0 + dx + r, y0 + dy + r],
                  fill=(120, 112, 104))
    d.rectangle([x0 + 10, y1 - 52, x0 + 60, y1], fill=(74, 66, 60))
    d.rectangle([x0 + 68, y1 - 66, x0 + 110, y1], fill=(88, 78, 70))
    d.rectangle([x0 + 118, y1 - 44, x0 + 170, y1], fill=(66, 60, 54))
    d.ellipse([x0 + 196, y1 - 74, x0 + 236, y1 - 40], fill=(96, 86, 76))
    d.rectangle([x0 + 196, y1 - 44, x0 + 236, y1], fill=(96, 86, 76))
    d.rectangle([x0 + 248, y1 - 84, x0 + 258, y1], fill=(80, 72, 64))
    d.polygon([(x0 + 244, y1 - 84), (x0 + 253, y1 - 96), (x0 + 262, y1 - 84)],
              fill=(80, 72, 64))
    d.rectangle([x0 + 268, y1 - 56, x0 + 312, y1], fill=(74, 66, 60))
    for (wx, wy) in [(26, 60), (44, 66), (84, 48), (96, 60), (132, 70),
                     (210, 58), (282, 62)]:
        d.rectangle([x0 + wx, y0 + wy, x0 + wx + 5, y0 + wy + 7],
                    fill=(240, 200, 110))
    d.polygon([(x0, y1), (x0 + 60, y1 - 16), (x0 + 130, y1 - 6),
               (x0 + 210, y1 - 18), (x0 + 290, y1 - 8), (x1, y1 - 12),
               (x1, y1)], fill=(52, 48, 44))

def scene_markets(box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 42, 32))
    base = y1 - 18
    bars = [(18, 22), (52, 30), (86, 20), (120, 34), (154, 26),
            (188, 38), (222, 30), (256, 42)]
    for bx, bh in bars:
        d.rectangle([x0 + bx, base - bh, x0 + bx + 18, base], fill=(46, 180, 110))
        d.line([(x0 + bx + 9, base - bh - 6), (x0 + bx + 9, base + 4)],
               fill=(46, 180, 110), width=2)
    d.line([(x0 + 10, base - 14), (x0 + 90, base - 26), (x0 + 170, base - 34),
            (x0 + 250, base - 42), (x0 + 296, base - 48)], fill=(255, 210, 80),
           width=3)
    d.polygon([(x0 + 284, base - 54), (x0 + 302, base - 48), (x0 + 286, base - 40)],
              fill=(255, 210, 80))
    d.text((x0 + 12, y0 + 6), "NIKKEI +4.3%   KOSPI +7.4%   TAIWAN +9%",
           font=SANS_B(13), fill=(255, 255, 255))
    d.rectangle([x0 + 284, y1 - 16, x0 + 296, y1], fill=(10, 26, 20))
    d.polygon([(x0 + 286, y1 - 16), (x0 + 290, y1 - 28), (x0 + 294, y1 - 16)],
              fill=(10, 26, 20))
    d.rectangle([x0 + 300, y1 - 12, x0 + 314, y1], fill=(10, 26, 20))

LEADS = [
    ("1", "NEPAL  •  KOSHI PROVINCE", "01:32 UTC", "CONFIRMED",
     "Quake shakes Nepal's Koshi hills",
     "A magnitude 5.3 tremor, 10 km deep, rattled eastern Nepal and was felt in India, Bhutan, Bangladesh and China. No casualties were reported.",
     "Reuters  •  EMSC  •  USGS", scene_nepal),
    ("2", "GAZA  •  KHAN YOUNIS", "00:30 UTC", "REPORTED",
     "Strike near police post kills three",
     "An air strike beside a police position left three people dead and five wounded, Reuters reported from Cairo.",
     "Reuters (Cairo)", scene_khan),
    ("3", "ASIA  •  MARKETS", "03:00 UTC", "CONFIRMED",
     "Asian shares surge as Tokyo leads",
     "The Nikkei climbed 4.3% to 58,871, the KOSPI jumped 7.4% and Taiwan rose 9% in a broad regional rally.",
     "Reuters  •  WSJ", scene_markets),
]

ly = 280
for i, (num, loc, t, badge, head, body, src, scene) in enumerate(LEADS):
    x0 = 24 + i * 329
    x1 = x0 + 318
    d.rectangle([x0, ly, x1, ly + 216], outline=(200, 200, 200), width=1)
    scene((x0 + 1, ly + 1, x1 - 1, ly + 89))
    d.ellipse([x0 + 10, ly + 96, x0 + 30, ly + 116], fill=RED)
    d.text((x0 + 20, ly + 97), num, font=SANS_B(13), fill=(255, 255, 255),
           anchor="ma")
    d.text((x0 + 36, ly + 97), loc, font=SANS_B(11), fill=RED)
    d.text((x1 - 10, ly + 97), t, font=SANS_B(11), fill=INK, anchor="ra")
    hl = wrap(head, SERIF_B(17), 298)
    yy = ly + 120
    for ln in hl[:2]:
        d.text((x0 + 10, yy), ln, font=SERIF_B(17), fill=INK)
        yy += 20
    bl = wrap(body, SANS_R(11), 298)
    for ln in bl[:3]:
        d.text((x0 + 10, yy), ln, font=SANS_R(11), fill=(60, 60, 60))
        yy += 14
    d.text((x0 + 10, ly + 202), src, font=SANS_R(9), fill=GRAY)
    bw = tw(badge, SANS_B(9)) + 12
    d.rounded_rectangle([x1 - 10 - bw, ly + 200, x1 - 10, ly + 216],
                        radius=8, fill=(238, 238, 238))
    d.text((x1 - 10 - bw / 2, ly + 203), badge, font=SANS_B(9), fill=INK,
           anchor="ma")

# ---------------------------------------------------------------- mid stories
d.text((24, 504), "MORE OF THE DAY", font=SANS_B(12), fill=RED)
rule(522, 180, 1000, 1, LGRAY)

def thumb(box, kind, bg):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "court":
        for bx in (x0 + 5, x0 + 13, x0 + 21):
            d.rectangle([bx, y0 + 10, bx + 3, y1 - 6], fill=(255, 255, 255))
        d.rectangle([x0 + 3, y0 + 6, x1 - 3, y0 + 10], fill=(255, 255, 255))
        d.rectangle([x0 + 3, y1 - 6, x1 - 3, y1 - 3], fill=(255, 255, 255))
    elif kind == "chip":
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 255, 255))
        d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=bg)
        for px in (cx - 8, cx, cx + 8):
            d.line([(px, y0 + 2), (px, cy - 8)], fill=(255, 255, 255), width=2)
            d.line([(px, cy + 8), (px, y1 - 2)], fill=(255, 255, 255), width=2)
    elif kind == "bank":
        d.polygon([(x0 + 3, y0 + 12), (cx, y0 + 4), (x1 - 3, y0 + 12)],
                  fill=(255, 255, 255))
        for bx in (x0 + 6, x0 + 13, x0 + 20):
            d.rectangle([bx, y0 + 14, bx + 3, y1 - 5], fill=(255, 255, 255))
        d.rectangle([x0 + 3, y1 - 5, x1 - 3, y1 - 2], fill=(255, 255, 255))
    elif kind == "plane":
        d.polygon([(x0 + 4, cy + 2), (x1 - 4, cy - 6), (x1 - 8, cy + 2),
                   (x0 + 10, cy + 6)], fill=(255, 255, 255))
        d.polygon([(cx - 2, cy - 2), (cx + 4, cy - 12), (cx + 8, cy - 2)],
                  fill=(255, 255, 255))
    elif kind == "jets":
        d.polygon([(x0 + 3, cy), (x0 + 14, cy - 5), (x0 + 14, cy + 3)],
                  fill=(255, 255, 255))
        d.polygon([(x1 - 14, cy + 2), (x1 - 3, cy - 3), (x1 - 3, cy + 6)],
                  fill=(255, 210, 80))
        d.line([(x0 + 4, y1 - 4), (x1 - 4, y1 - 4)], fill=(255, 255, 255), width=2)
    elif kind == "parliament":
        d.rectangle([x0 + 5, y0 + 12, x1 - 5, y1 - 4], fill=(255, 255, 255))
        d.rectangle([x0 + 12, y0 + 18, x1 - 12, y1 - 8], fill=bg)
        d.line([(cx, y0 + 3), (cx, y0 + 12)], fill=(255, 210, 80), width=2)
        d.polygon([(cx, y0 + 3), (cx + 8, y0 + 6), (cx, y0 + 9)], fill=(255, 210, 80))
    elif kind == "chess":
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0:
                    d.rectangle([x0 + 3 + c * 6, y0 + 3 + r * 6,
                                 x0 + 8 + c * 6, y0 + 8 + r * 6],
                                fill=(255, 255, 255))
        d.rectangle([cx - 3, y0 + 6, cx + 5, y0 + 18], fill=(255, 210, 80))
    elif kind == "trophy":
        d.ellipse([cx - 8, y0 + 6, cx + 8, y0 + 18], fill=(255, 210, 80))
        d.rectangle([cx - 2, y0 + 18, cx + 2, y0 + 24], fill=(255, 210, 80))
        d.rectangle([cx - 6, y0 + 24, cx + 6, y1 - 4], fill=(255, 210, 80))
    elif kind == "museum":
        d.rectangle([x0 + 4, y0 + 18, x1 - 4, y1 - 4], fill=(255, 255, 255))
        d.pieslice([cx - 10, y0 + 2, cx + 10, y0 + 20], 180, 360,
                   fill=(255, 255, 255))
    elif kind == "bars":
        for bx in (x0 + 6, x0 + 13, x0 + 20):
            d.rectangle([bx, y0 + 4, bx + 3, y1 - 4], fill=(255, 255, 255))
        d.rectangle([x0 + 3, y0 + 4, x1 - 3, y0 + 7], fill=(255, 255, 255))
        d.rectangle([x0 + 3, y1 - 7, x1 - 3, y1 - 4], fill=(255, 255, 255))

MIDS = [
    ("4", "Appeals court clears way to erase Trump hush-money verdict",
     "01:00 UTC  •  AP  •  CONFIRMED", "court", (70, 90, 120)),
    ("5", "Nvidia faces FBI list, DOJ antitrust and SEC scrutiny",
     "01:30 UTC  •  Reuters  •  REPORTED", "chip", (30, 60, 90)),
    ("6", "Bank of Korea tipped to lift rates to 3.25% on Thursday",
     "01:30 UTC  •  Reuters  •  REPORTED", "bank", (40, 110, 70)),
    ("7", "Hasina to fly home on 16 December after exile in India",
     "02:45 UTC  •  Reuters  •  REPORTED", "plane", (150, 90, 40)),
    ("8", "Russian jets enter Korean zone; Seoul scrambles fighters",
     "07:52 KST  •  Reuters / Yonhap  •  CONFIRMED", "jets", (120, 60, 60)),
    ("9", "Singapore PM: Megaspeed inquiry goes on",
     "03:00 UTC  •  Reuters  •  OFFICIAL", "parliament", (170, 40, 40)),
    ("10", "World chess: youngest final ever starts today",
     "STARTS TODAY 14:00 UTC  •  FIDE  •  OFFICIAL", "chess", (60, 60, 60)),
    ("11", "Sky News wins International Emmy for Gaza film",
     "00:30 UTC  •  Sky News  •  REPORTED", "trophy", (150, 130, 30)),
    ("12", "London's new £437m museum opens to praise",
     "24 Nov  •  The Guardian  •  REPORTED", "museum", (90, 70, 110)),
    ("13", "Pastor Angel spends second night in custody",
     "00:30 UTC  •  NewsDay  •  REPORTED", "bars", (80, 80, 80)),
]

my = 524
for i, (num, head, meta, kind, bg) in enumerate(MIDS):
    col = i % 2
    row = i // 2
    x0 = 24 + col * 492
    yy = my + row * 34
    thumb((x0, yy, x0 + 30, yy + 30), kind, bg)
    d.text((x0 + 36, yy - 1), num + ".", font=SANS_B(12), fill=RED)
    hl = wrap(head, SERIF_B(12), 492 - 36 - 22)
    d.text((x0 + 58, yy - 1), hl[0], font=SERIF_B(12), fill=INK)
    if len(hl) > 1:
        d.text((x0 + 58, yy + 13), hl[1], font=SERIF_B(12), fill=INK)
        d.text((x0 + 58, yy + 26), meta, font=SANS_R(9), fill=GRAY)
    else:
        d.text((x0 + 58, yy + 13), meta, font=SANS_R(9), fill=GRAY)

# ---------------------------------------------------------------- also 14-30
d.text((24, 702), "ALSO TODAY  •  14–30", font=SANS_B(12), fill=RED)
rule(720, 230, 1000, 1, LGRAY)

ALSO = [
    ("14", "00:45 UTC", "Burnham urged to cool talk of Britain rejoining the EU", "BBC"),
    ("15", "01:31 UTC", "“No 10 North” in Manchester under closer watch", "BBC"),
    ("16", "01:53 UTC", "Severely ill spared repeat PIP assessments", "BBC"),
    ("17", "01:11 UTC", "Breeders sold sick puppies for £2,000 a pup", "BBC"),
    ("18", "01:03 UTC", "Autumn's coldest spell drags on: ice, hill snow, heavy rain", "BBC"),
    ("19", "24 Nov", "Green leader backs pro-NATO report, keeps nuclear arms", "The Guardian"),
    ("20", "24 Nov", "Faith in COP “misplaced”, says Macfarlane", "The Guardian"),
    ("21", "02:21 UTC", "Nvidia HQ split over Huang's return", "BBC"),
    ("22", "24 Nov", "Harrelson turned down Haymitch twice", "Variety"),
    ("23", "24 Nov", "Pacific Elders accuse Australia of climate betrayal", "PINA"),
    ("24", "24 Nov", "Kanton Island emptied at a day's notice", "PINA"),
    ("25", "24 Nov", "Origin star Hudson Young joins PNG Chiefs", "PINA"),
    ("26", "24 Nov", "Pacific bloc unites before key tuna talks", "PINA"),
    ("27", "24 Nov", "Solomons PM flies to Canberra to meet Albanese", "PINA"),
    ("28", "24 Nov", "Lamarre-Condon takes “long road” to witness box", "The Guardian"),
    ("29", "24 Nov", "UNSW launches world-first AI “megafire” simulator", "Medianet"),
    ("30", "01:01 UTC", "“I pay £250 a month for someone to run my life”", "BBC"),
]
ay = 722
for i, (num, t, head, src) in enumerate(ALSO):
    col = 0 if i < 9 else 1
    row = i if i < 9 else i - 9
    x0 = 24 + col * 492
    yy = ay + row * 14
    d.text((x0, yy), num + ".", font=SANS_B(11), fill=RED)
    d.text((x0 + 26, yy), t, font=SANS_B(10), fill=(150, 60, 60))
    tx = x0 + 26 + tw(t, SANS_B(10)) + 8
    d.text((tx, yy), head, font=SANS_R(11), fill=INK)
    d.text((x0 + 478, yy), src, font=SANS_I(9), fill=GRAY, anchor="ra")

# ---------------------------------------------------------------- world map
# Land: polygons (lon, lat) + ellipses (cx, cy, rx, ry). Rough but the
# continents must read at a glance.
POLYS = [
    # North America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-145, 60), (-140, 60),
     (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
     (-110, 24), (-105, 20), (-100, 18), (-97, 16), (-94, 17), (-90, 14),
     (-86, 12), (-83, 9), (-80, 8), (-79, 9), (-82, 10), (-85, 12),
     (-88, 14), (-90, 14), (-92, 15), (-95, 16), (-97, 18), (-97, 22),
     (-94, 18), (-90, 21), (-87, 21), (-86, 25), (-84, 30), (-81, 25),
     (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 44), (-65, 44),
     (-60, 46), (-55, 47), (-60, 52), (-64, 58), (-68, 58), (-72, 62),
     (-78, 62), (-82, 66), (-88, 66), (-92, 66), (-95, 69), (-105, 68),
     (-115, 69), (-125, 70), (-135, 69), (-145, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70),
     (-20, 74), (-25, 76), (-35, 77), (-45, 76), (-55, 74), (-60, 70)],
    # South America
    [(-79, 9), (-77, 7), (-75, 10), (-72, 12), (-64, 10), (-60, 8),
     (-54, 6), (-51, 4), (-50, 0), (-44, -3), (-35, -8), (-37, -13),
     (-40, -20), (-41, -23), (-48, -27), (-52, -32), (-58, -35), (-62, -39),
     (-65, -41), (-66, -45), (-68, -50), (-69, -52), (-71, -54), (-74, -53),
     (-73, -48), (-73, -42), (-72, -37), (-71, -30), (-70, -23), (-70, -18),
     (-75, -15), (-77, -12), (-80, -6), (-81, -3), (-80, 1), (-80, 6)],
    # Africa
    [(-17, 15), (-16, 20), (-12, 25), (-10, 30), (-6, 33), (-2, 35),
     (5, 37), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32),
     (30, 31), (32, 31), (34, 28), (35, 23), (37, 18), (39, 15),
     (41, 11), (43, 11), (46, 11), (51, 11), (51, 6), (48, 2),
     (44, -2), (41, -4), (40, -10), (39, -15), (36, -18), (33, -22),
     (32, -26), (28, -30), (25, -33), (20, -35), (17, -32), (15, -28),
     (13, -20), (12, -15), (13, -10), (9, -1), (9, 4), (-8, 5),
     (-13, 8), (-17, 12)],
]
ELLIPSES = [
    (13, 52, 20, 9),    # mainland Europe
    (16, 63, 9, 7),     # Scandinavia
    (-2, 54, 3.5, 4.5), # Britain
    (-4, 40, 6, 3.5),   # Iberia
    (13, 42, 4, 4),     # Italy
    (23, 39, 3, 3),     # Greece
    (95, 58, 50, 14),   # Siberia / Central Asia
    (115, 35, 20, 12),  # East Asia
    (78, 21, 8, 11),    # India
    (45, 24, 9, 8),     # Arabia
    (101, 13, 9, 8),    # SE Asia
    (139, 37, 4, 7),    # Japan
    (112, -3, 10, 3),   # Indonesia west
    (125, -4, 8, 3),    # Indonesia east
    (141, -5, 9, 4),    # New Guinea
    (134, -25, 13, 8),  # Australia
    (147, -42, 3, 2),   # Tasmania
    (172, -41, 3, 5),   # New Zealand
]

def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside

def on_land(lon, lat):
    for p in POLYS:
        if point_in_poly(lon, lat, p):
            return True
    for (cx, cy, rx, ry) in ELLIPSES:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1:
            return True
    return False

MX0, MY0, MX1, MY1 = 24, 864, 484, 992
LAT_TOP, LAT_BOT = 80.0, -50.0
def project(lon, lat):
    px = MX0 + (lon + 180.0) / 360.0 * (MX1 - MX0)
    py = MY0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MY1 - MY0)
    return px, py

d.text((24, 850), "WHERE IT HAPPENED — 30 STORIES, 30 PINS", font=SANS_B(11), fill=RED)
d.rectangle([MX0, MY0, MX1, MY1], fill=(238, 242, 246),
            outline=(200, 200, 200), width=1)
step = 8
lat = LAT_TOP
while lat > LAT_BOT:
    lon = -180.0
    while lon < 180.0:
        if on_land(lon, lat):
            px, py = project(lon, lat)
            d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(120, 130, 140))
        lon += 3.0
    lat -= 3.0

PINS = [  # (number, lon, lat, region) — positions nudged where stories
    # cluster, so every numbered pin stays readable
    (1, 84, 28, "ASIA"), (2, 34.4, 31.3, "MIDDLE EAST"), (3, 140, 36, "ASIA"),
    (4, -78, 38, "AMERICAS"), (5, -119, 41, "AMERICAS"), (6, 119, 42, "ASIA"),
    (7, 90.4, 23.8, "ASIA"), (8, 131, 38, "ASIA"), (9, 103.8, 1.35, "ASIA"),
    (10, 6.1, 46.2, "EUROPE"), (11, -68, 44, "AMERICAS"), (12, -0.1, 51.5, "EUROPE"),
    (13, 31, -17.8, "AFRICA"), (14, -11, 57, "EUROPE"), (15, -11, 51, "EUROPE"),
    (16, 7, 59, "EUROPE"), (17, -6, 60, "EUROPE"), (18, 3, 60, "EUROPE"),
    (19, 12, 47, "EUROPE"), (20, -11, 48, "EUROPE"), (21, -127, 33, "AMERICAS"),
    (22, -114, 32, "AMERICAS"), (23, 172, -17.7, "OCEANIA"), (24, -171.7, -2.8, "OCEANIA"),
    (25, 147.1, -9.5, "OCEANIA"), (26, 171, -7, "OCEANIA"), (27, 160, -9.4, "OCEANIA"),
    (28, 155, -31, "OCEANIA"), (29, 144, -39, "OCEANIA"), (30, 16, 57, "WORLD"),
]
for num, lon, lat, reg in PINS:
    col = REGIONS[reg][0]
    px, py = project(lon, lat)
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=col,
              outline=(255, 255, 255), width=1)
    d.text((px, py - 1), str(num), font=SANS_B(8), fill=(255, 255, 255), anchor="ma")
d.text((24, 996), "07:52 KST Tue 24 Nov = 22:52 UTC Mon 23 Nov — dated by local day.",
       font=SANS_I(9), fill=GRAY)

# ---------------------------------------------------------------- numbers (right)
NX0, NX1 = 496, 1000
d.rectangle([NX0, 850, NX1, 926], outline=(200, 200, 200), width=1)
d.text((NX0 + 10, 856), "THE DAY IN NUMBERS", font=SANS_B(11), fill=RED)
STATS = [
    ("5.3", "Nepal quake magnitude", 16),
    ("3 killed, 5 wounded", "Khan Younis strike", 13),
    ("+7.4%", "KOSPI jump", 16),
    ("$2.5M", "World chess prize fund", 16),
    ("3.25%", "Bank of Korea rate expected", 16),
    ("£437M", "Museum of London cost", 16),
]
for i, (big, lab, sz) in enumerate(STATS):
    col = i % 3
    row = i // 3
    sx = NX0 + 10 + col * 168
    sy = 874 + row * 26
    d.text((sx, sy), big, font=SERIF_B(sz), fill=INK)
    d.text((sx, sy + 17), lab, font=SANS_R(8), fill=GRAY)

# ---------------------------------------------------------------- date check
d.rectangle([NX0, 932, NX1, 986], fill=RED)
dc1 = "Every story on this page happened or was first reported on Tuesday 24 November 2026. Wires read to 04:00 UTC."
for j, ln in enumerate(wrap(dc1, SANS_B(11), NX1 - NX0 - 20)):
    d.text((NX0 + 10, 938 + j * 13), ln, font=SANS_B(11), fill=(255, 255, 255))
dc2 = ("Left out — earlier days: Iran–Bahrain strike (21 Nov) • "
       "El Chapo Isidro (20–21 Nov) • Sparta II (21 Nov) • COP31 collapse (22 Nov) • "
       "India 720/9 (22 Nov) • US House 258 (22 Nov) • Nvidia probe / FBI hack / Lisbon march (20–22 Nov).")
for j, ln in enumerate(wrap(dc2, SANS_R(8), NX1 - NX0 - 20)):
    d.text((NX0 + 10, 964 + j * 10), ln, font=SANS_R(8), fill=(255, 235, 235))

# ---------------------------------------------------------------- footer
d.text((NX0, 990), "HOW SURE:", font=SANS_B(9), fill=RED)
foot = ("REPORTED = the day's wires or officials  •  OFFICIAL = government / institution statement  •  "
        "CLAIM = one side's account  •  ONGOING = still unfolding. "
        "Scenes are drawn illustrations, not photographs.")
for j, ln in enumerate(wrap(foot, SANS_R(9), NX1 - NX0)):
    d.text((NX0, 1000 + j * 11), ln, font=SANS_R(9), fill=GRAY)

img.save(OUT, format="PNG")
print("wrote", OUT, os.path.getsize(OUT), "bytes")
