"""Builds img/raid/sprites.png + img/raid/atlas.json for raid.html (MAIGA Raid).
Characters reuse the existing pixel art (meme/pxjp.png = Jean-Phil, bolt.png = Bolt).
Run: python3 tools/build_raid_sprites.py
"""
import json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'img', 'raid')

K = (10, 10, 20, 255)          # outline
STEEL = (201, 211, 224, 255)
STEEL2 = (138, 150, 168, 255)
STEEL3 = (92, 104, 124, 255)
BRASS = (224, 180, 58, 255)
BRASS2 = (168, 124, 30, 255)
CYAN = (56, 242, 255, 255)
CYAN2 = (20, 150, 190, 255)
RED = (214, 52, 70, 255)
WHITE = (247, 240, 223, 255)
SKIN = (243, 201, 165, 255)


def grid(rows, pal):
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal:
                im.putpixel((x, y), pal[ch])
    return im


def rect(im, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < im.width and 0 <= y < im.height:
                im.putpixel((x, y), c)


def px(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), c)


# ---------------------------------------------------------------- Jean-Phil the ice knight
JP = Image.open(os.path.join(ROOT, 'meme', 'pxjp.png')).convert('RGBA')
HEAD = JP.crop((0, 0, 26, 21))          # hair, face, moustache, chin


def helmet(head):
    h = head.copy()
    # steel cap over the top of the hair, visor raised, plume in brand cyan
    rows = [
        "......KKKKKKKKKKKKKK......",
        "....KKSSSSSSSSSSSSSSKK....",
        "...KSSWSSSSSSSSSSSSSSSK...",
        "..KSSWSSSSSSSSSSSSSSSSSK..",
        "..KSSSSSSSSSSSSSSSSSSSSK..",
        "..KMMMMMMMMMMMMMMMMMMMMK..",
        "..KKKKKKKKKKKKKKKKKKKKKK..",
    ]
    cap = grid(rows, {'K': K, 'S': STEEL, 'W': (255, 255, 255, 255), 'M': BRASS})
    out = Image.new('RGBA', (26, 23), (0, 0, 0, 0))
    out.alpha_composite(h, (0, 2))
    out.alpha_composite(cap, (0, 2))
    # plume
    for (x, y, c) in [(12, 0, CYAN), (13, 0, CYAN), (11, 1, CYAN), (12, 1, CYAN2), (13, 1, CYAN), (14, 1, CYAN2),
                      (12, 2, K), (13, 2, K)]:
        px(out, x, y, c)
    return out


KHEAD = helmet(HEAD)


def jp_frame(pose, t=0):
    """pose: idle, run, jump, fall, atk0, atk1, hurt. t = animation step."""
    W, H = 40, 40
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ox = 4                                   # body offset so the sword fits on the right
    bob = 1 if (pose == 'idle' and t == 1) or (pose == 'run' and t in (1, 3)) else 0
    # cape (behind)
    flap = {'run': [0, 1, 2, 1][t % 4], 'jump': 2, 'fall': 3}.get(pose, 0)
    for y in range(23, 36):
        w = 2 + (y - 23) // 4 + (flap if y > 28 else 0)
        rect(im, ox + 2 - w + 3, y + bob, ox + 4, y + bob, CYAN2 if y % 3 else CYAN)
    # legs
    legs = {'idle': [(9, 0), (15, 0)], 'run': [[(7, 0), (16, -1)], [(9, -1), (14, 0)], [(11, 0), (12, -1)], [(9, -1), (14, 0)]][t % 4],
            'jump': [(8, -2), (15, 0)], 'fall': [(9, 0), (15, -1)], 'atk0': [(8, 0), (16, 0)], 'atk1': [(7, 0), (17, 0)],
            'hurt': [(9, -1), (14, 0)]}[pose]
    for lx, lift in legs:
        x = ox + lx
        rect(im, x, 34 + lift, x + 3, 37 + lift, STEEL2)
        rect(im, x, 34 + lift, x, 37 + lift, STEEL3)
        rect(im, x - 1, 38 + lift, x + 3, 39 + lift, K)
        rect(im, x, 38 + lift, x + 3, 38 + lift, STEEL3)
    # body armour
    y0 = 22 + bob
    rect(im, ox + 4, y0, ox + 21, y0 + 12, K)
    rect(im, ox + 5, y0 + 1, ox + 20, y0 + 11, STEEL)
    rect(im, ox + 5, y0 + 8, ox + 20, y0 + 11, STEEL2)
    rect(im, ox + 5, y0 + 1, ox + 6, y0 + 7, (255, 255, 255, 255))
    rect(im, ox + 5, y0 + 9, ox + 20, y0 + 9, BRASS)            # belt
    px(im, ox + 12, y0 + 9, BRASS2); px(im, ox + 13, y0 + 9, BRASS2)
    # $M emblem on the chest
    emb = ["..KKKK..", ".KBBBBK.", "KBKBBKBK", "KBBKKBBK", "KBBBBBBK", ".KBBBBK.", "..KKKK.."]
    im.alpha_composite(grid(emb, {'K': K, 'B': BRASS}), (ox + 9, y0 + 1))
    # pauldrons
    rect(im, ox + 2, y0, ox + 6, y0 + 3, K); rect(im, ox + 3, y0 + 1, ox + 6, y0 + 2, STEEL)
    rect(im, ox + 19, y0, ox + 23, y0 + 3, K); rect(im, ox + 19, y0 + 1, ox + 22, y0 + 2, STEEL)
    # head
    im.alpha_composite(KHEAD, (ox, bob - 1 if pose != 'hurt' else bob))
    # sword arm + sword
    def sword(hx, hy, dx, dy, n):
        # hilt
        rect(im, hx - 1, hy - 1, hx + 1, hy + 1, K); px(im, hx, hy, BRASS)
        for i in range(1, n + 1):
            x, y = hx + dx * i, hy + dy * i
            px(im, x, y, WHITE if i % 2 else CYAN)
            if dx and dy:
                px(im, x + (1 if dx < 0 else -1), y, STEEL2)
            elif dx:
                px(im, x, y + 1, STEEL2)
            else:
                px(im, x + 1, y, STEEL2)
        # guard
        if dx and not dy:
            rect(im, hx + dx, hy - 2, hx + dx, hy + 2, BRASS)
        else:
            rect(im, hx - 2, hy + dy, hx + 2, hy + dy, BRASS)
    if pose == 'atk0':
        rect(im, ox + 20, y0 - 2, ox + 23, y0 + 1, SKIN); sword(ox + 22, y0 - 2, 0, -1, 7)
    elif pose == 'atk1':
        rect(im, ox + 21, y0 + 4, ox + 24, y0 + 6, SKIN); sword(ox + 25, y0 + 5, 1, 0, 8)
    elif pose == 'hurt':
        rect(im, ox + 21, y0 + 2, ox + 23, y0 + 4, SKIN)
    else:
        rect(im, ox + 21, y0 + 5, ox + 23, y0 + 7, SKIN)
        sword(ox + 22, y0 + 6, 1, -1, 7)
    return im


# ---------------------------------------------------------------- Bolt the robot
BOLT = Image.open(os.path.join(ROOT, 'bolt.png')).convert('RGBA')


def bolt_frame(pose, t=0):
    W, H = 30, 30
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    top = BOLT.crop((0, 0, 24, 23))
    feet = BOLT.crop((0, 23, 24, 28))
    bob = 1 if (pose == 'run' and t % 2) or (pose == 'idle' and t == 1) else 0
    if pose == 'run':
        # alternate feet
        lf = BOLT.crop((4, 23, 11, 28)); rf = BOLT.crop((12, 23, 21, 28))
        a, b = [(0, -1), (-1, 0), (0, 0), (1, -1)][t % 4]
        im.alpha_composite(lf, (4 + 3 + a, 25 + min(0, a)))
        im.alpha_composite(rf, (12 + 3 - a, 25 + b))
    elif pose in ('jump', 'fall'):
        im.alpha_composite(feet, (3, 24 if pose == 'jump' else 25))
        # thruster flame
        for x in (9, 10, 17, 18):
            px(im, x, 29, CYAN if pose == 'jump' else BRASS)
    else:
        im.alpha_composite(feet, (3, 25))
    im.alpha_composite(top, (3, 2 + bob))
    if pose == 'atk1':
        for (x, y) in [(27, 19), (28, 18), (29, 19), (28, 20), (26, 18)]:
            px(im, x, y + bob, CYAN)
    if pose == 'hurt':
        # sparks
        for (x, y) in [(1, 3), (2, 2), (26, 4), (27, 3)]:
            px(im, x, y, BRASS)
    return im


# ---------------------------------------------------------------- enemies, boss, pickups
FUD = [
    ["....KKKKKK....", "..KKGGGGGGKK..", ".KGGGGGGGGGGK.", "KGGWWGGGGWWGGK", "KGGKWGGGGKWGGK", "KGGGGGGGGGGGGK",
     "KGGGGKKKKGGGGK", "KGGGKRRRRKGGGK", "KGGGGKKKKGGGGK", "KGGGGGGGGGGGGK", "KGGGGGGGGGGGGK", "KGKGGKGGKGGKGK",
     "KK.KK.KK.KK.KK"],
    ["....KKKKKK....", "..KKGGGGGGKK..", ".KGGGGGGGGGGK.", "KGGWWGGGGWWGGK", "KGGWKGGGGWKGGK", "KGGGGGGGGGGGGK",
     "KGGGGKKKKGGGGK", "KGGGKRRRRKGGGK", "KGGGGKKKKGGGGK", "KGGGGGGGGGGGGK", "KGGGGGGGGGGGGK", "KKGGKGGKGGKGGK",
     ".KK.KK.KK.KK.K"],
]
FUD_PAL = {'K': (40, 20, 60, 255), 'G': (150, 130, 190, 255), 'W': (255, 255, 255, 255), 'R': (214, 52, 70, 255)}

BEAR = [
    [".KK.........KK.........", "KWWK.......KWWK........", "KWWWKKKKKKKWWWWK.......", ".KWWWWWWWWWWWWWWKK.....",
     ".KWWKWWWWWWWWWWWWWK....", "KWWWWWWWWWWWWWWWWWWKK..", "KWNWWWWWWWWWWWWWWWWWWK.", "KWWWWKKWWWWWRRRRRWWWWWK",
     ".KKKKWWWWWWWWRRRWWWWWWK", "....KWWWWWWWWWRWWWWWWWK", "....KWWWWWWWWWWWWWWWWK.", "....KWWKWWWKKKKWWKWWWK.",
     "....KWWK.KWK...KWWKKWK.", "....KKKK.KKK...KKKK.KK."],
    [".KK.........KK.........", "KWWK.......KWWK........", "KWWWKKKKKKKWWWWK.......", ".KWWWWWWWWWWWWWWKK.....",
     ".KWWKWWWWWWWWWWWWWK....", "KWWWWWWWWWWWWWWWWWWKK..", "KWNWWWWWWWWWWWWWWWWWWK.", "KWWWWKKWWWWWRRRRRWWWWWK",
     ".KKKKWWWWWWWWRRRWWWWWWK", "....KWWWWWWWWWRWWWWWWWK", "....KWWWWWWWWWWWWWWWWK.", "....KWWWKWWKKKKWKWWWWK.",
     "....KKWWK.KK....KWWK.K.", ".....KKKK........KKKK.."],
]
BEAR_PAL = {'K': (20, 30, 50, 255), 'W': (236, 244, 252, 255), 'N': (20, 20, 30, 255), 'R': (214, 52, 70, 255)}

PAPER = [
    ["..KKKKKKKKK..", "..KPPPPPPPPK.", "..KPLLLLLPPPK", "..KPPPPPPPPPK", "..KPKPPPKPPPK", "..KPPPPPPPPPK",
     "KHKPPKKKPPPKHK", "KHKPPKPKPPPKHK", ".KKPPPPPPPPKK.", "..KPLLLLLLPPK", "..KPPPPPPPPPK", "..KPLLLLLPPPK",
     "..KKKKKKKKKKK", "...KK...KK...", "...KK...KK...", "..KKK...KKK.."],
    ["..KKKKKKKKK..", "..KPPPPPPPPK.", "..KPLLLLLPPPK", "..KPPPPPPPPPK", "..KPKPPPKPPPK", "..KPPPPPPPPPK",
     ".HKPPKKKPPPKH.", "KHKPPKPKPPPKHK", "KKKPPPPPPPPKKK", "..KPLLLLLLPPK", "..KPPPPPPPPPK", "..KPLLLLLPPPK",
     "..KKKKKKKKKKK", "....KK.KK....", "....KK.KK....", "...KKK.KKK..."],
]
PAPER_PAL = {'K': (30, 30, 40, 255), 'P': (250, 246, 232, 255), 'L': (150, 170, 200, 255), 'H': (243, 201, 165, 255)}

RUG = [
    ["....KKKKKKKK....", "..KKRRYRRYRRKK..", ".KRRYRRRRRRYRRK.", "KRYRRKKKKKKRRYRK", "KRRRKYYYYYYKRRRK", "KRRYKYKKKKYKYRRK",
     "KRRYKYKRRKYKYRRK", "KRRYKYKKKKYKYRRK", "KRRRKYYYYYYKRRRK", "KRYRRKKKKKKRRYRK", ".KRRYRRRRRRYRRK.", "..KKRRYRRYRRKK..",
     "....KKKKKKKK...."],
    ["....KKKKKKKK....", "..KKRYRRYRRRKK..", ".KRYRRRRRRRRYRK.", "KRRRRKKKKKKRRRRK", "KYRRKYYYYYYKRRYK", "KRRYKYKKKKYKYRRK",
     "KRRYKYKRRKYKYRRK", "KRRYKYKKKKYKYRRK", "KYRRKYYYYYYKRRYK", "KRRRRKKKKKKRRRRK", ".KRYRRRRRRRRYRK.", "..KKRYRRYRRRKK..",
     "....KKKKKKKK...."],
]
RUG_PAL = {'K': (40, 14, 20, 255), 'R': (170, 40, 60, 255), 'Y': (224, 180, 58, 255)}


def boss_frame(t, angry=False):
    """Lord Rugpull: a flying carpet with a top hat and a grin. 52x40."""
    W, H = 52, 40
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wave = [0, 1, 2, 1][t % 4]
    R = (190, 40, 66, 255) if not angry else (240, 70, 80, 255)
    R2 = (120, 22, 44, 255)
    # carpet body with wave
    for x in range(2, 50):
        dy = [0, 1, 2, 1][(x // 6 + wave) % 4]
        top = 20 + dy
        rect(im, x, top, x, top + 12, K)
        rect(im, x, top + 1, x, top + 11, R)
        if (x + wave) % 5 == 0:
            rect(im, x, top + 3, x, top + 9, BRASS)
        px(im, x, top + 2, R2); px(im, x, top + 10, R2)
        if x % 3 == 0:
            px(im, x, top + 13, BRASS)          # tassels
    # face on the carpet
    eye = (255, 255, 255, 255)
    for ex in (16, 32):
        rect(im, ex, 24, ex + 4, 27, K); rect(im, ex + 1, 25, ex + 3, 26, eye)
        px(im, ex + (3 if not angry else 1), 26, K)
        # eyebrows
        rect(im, ex - 1, 22 if not angry else 23, ex + 5, 22 if not angry else 23, K)
    rect(im, 20, 29, 32, 31, K); rect(im, 21, 30, 31, 30, (255, 255, 255, 255))
    for x in range(22, 31, 2):
        px(im, x, 30, K)
    # top hat
    rect(im, 19, 4, 33, 18, K); rect(im, 20, 5, 32, 17, (30, 30, 46, 255))
    rect(im, 20, 14, 32, 15, BRASS)
    rect(im, 15, 18, 37, 20, K); rect(im, 16, 19, 36, 19, (30, 30, 46, 255))
    # monocle ring around the right eye + chain
    for x in range(31, 38):
        px(im, x, 23, BRASS); px(im, x, 28, BRASS)
    for y in range(23, 29):
        px(im, 31, y, BRASS); px(im, 37, y, BRASS)
    for i in range(4):
        px(im, 37 + i, 29 + i, BRASS)
    return im


COIN = []
for t in range(4):
    w = [10, 8, 4, 8][t]
    im = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    x0 = (10 - w) // 2
    rect(im, x0, 1, x0 + w - 1, 8, K)
    rect(im, x0 + 1, 0, x0 + w - 2, 9, K)
    rect(im, x0 + 1, 1, x0 + w - 2, 8, BRASS)
    if w >= 8:
        rect(im, x0 + 1, 7, x0 + w - 2, 8, BRASS2)
        m = [(0, 3), (0, 4), (0, 5), (0, 6), (1, 4), (2, 5), (3, 4), (4, 3), (4, 4), (4, 5), (4, 6)] if w == 10 else \
            [(0, 3), (0, 4), (0, 5), (0, 6), (1, 4), (2, 4), (3, 3), (3, 4), (3, 5), (3, 6)]
        for (dx, y) in m:
            px(im, x0 + 2 + dx + (1 if w == 10 else 0) - 1, y, BRASS2 if False else K)
        px(im, x0 + 1, 2, (255, 240, 170, 255))
    else:
        rect(im, x0 + 1, 2, x0 + 1, 7, (255, 240, 170, 255))
    COIN.append(im)

HEART = grid([".KK.KK.", "KRRKRRK", "KRWRRRK", "KRRRRRK", ".KRRRK.", "..KRK..", "...K..."],
             {'K': K, 'R': RED, 'W': (255, 255, 255, 255)})
DIAMOND = grid(["..KKKKK..", ".KWCCCCK.", "KWCCCCCCK", "KKKKKKKKK", ".KCCCCCK.", "..KCCCK..", "...KCK...", "....K...."],
               {'K': K, 'C': CYAN, 'W': (255, 255, 255, 255)})
ROCKET = grid(["...KK...", "..KWWK..", "..KWWK..", ".KWCCWK.", ".KWCCWK.", ".KWWWWK.", "KRKWWKRK", "KRKKKKRK",
               "K.KYYK.K", "...KK..."],
              {'K': K, 'W': (240, 240, 250, 255), 'C': CYAN, 'R': RED, 'Y': BRASS})
BULL = grid(["K........K", "KW......WK", ".KW....WK.", "..KKKKKK..", "..KGGGGK..", ".KGKGGKGK.", ".KGGGGGGK.",
             "..KGRRGK..", "...KKKK..."],
            {'K': K, 'W': WHITE, 'G': (20, 200, 120, 255), 'R': (10, 90, 60, 255)})
ZAP = grid(["..KKK.", ".KCCK.", "KCCK..", "KCCCCK", ".KCCK.", "..KCK.", "..KK.."], {'K': K, 'C': CYAN})
RUGBALL = RUG[0]


def build():
    os.makedirs(OUT, exist_ok=True)
    frames = {}
    for p, n in [('idle', 2), ('run', 4), ('jump', 1), ('fall', 1), ('atk0', 1), ('atk1', 1), ('hurt', 1)]:
        frames['jp_' + p] = [jp_frame(p, t) for t in range(n)]
    for p, n in [('idle', 2), ('run', 4), ('jump', 1), ('fall', 1), ('atk0', 1), ('atk1', 1), ('hurt', 1)]:
        frames['bolt_' + p] = [bolt_frame(p, t) for t in range(n)]
    frames['fud'] = [grid(g, FUD_PAL) for g in FUD]
    frames['bear'] = [grid(g, BEAR_PAL) for g in BEAR]
    frames['paper'] = [grid(g, PAPER_PAL) for g in PAPER]
    frames['rug'] = [grid(g, RUG_PAL) for g in RUG]
    frames['boss'] = [boss_frame(t) for t in range(4)]
    frames['boss_angry'] = [boss_frame(t, True) for t in range(4)]
    frames['coin'] = COIN
    frames['heart'] = [HEART]
    frames['diamond'] = [DIAMOND]
    frames['rocket'] = [ROCKET]
    frames['bull'] = [BULL]
    frames['zap'] = [ZAP]
    frames['mint'] = [Image.open(os.path.join(ROOT, 'meme', 'pxmint.png')).convert('RGBA')]
    frames['eagle'] = [Image.open(os.path.join(ROOT, 'meme', 'pxeg.png')).convert('RGBA')]
    frames['crown'] = [Image.open(os.path.join(ROOT, 'meme', 'crown.png')).convert('RGBA')]
    frames['jphead'] = [KHEAD]
    frames['bolthead'] = [BOLT.crop((0, 0, 24, 16))]
    # pack in rows
    W = 256; x = y = 0; rowh = 0; atlas = {}; placed = []
    for name, fl in frames.items():
        atlas[name] = []
        for f in fl:
            if x + f.width > W:
                x = 0; y += rowh + 1; rowh = 0
            placed.append((f, x, y)); atlas[name].append([x, y, f.width, f.height])
            x += f.width + 1; rowh = max(rowh, f.height)
    sheet = Image.new('RGBA', (W, y + rowh + 1), (0, 0, 0, 0))
    for f, fx, fy in placed:
        sheet.alpha_composite(f, (fx, fy))
    sheet.save(os.path.join(OUT, 'sprites.png'), optimize=True)
    with open(os.path.join(OUT, 'atlas.json'), 'w') as fh:
        json.dump(atlas, fh, separators=(',', ':'))
    return sheet


if __name__ == '__main__':
    s = build()
    print('sprites.png', s.size)


def build_og():
    """1200x630 share image: img/raid/og-raid.png"""
    from PIL import ImageDraw, ImageFont
    sheet = Image.open(os.path.join(OUT, 'sprites.png')).convert('RGBA')
    atlas = json.load(open(os.path.join(OUT, 'atlas.json')))

    def fr(n, i=0):
        x, y, w, h = atlas[n][i]
        return sheet.crop((x, y, x + w, y + h))

    W, H = 1200, 630
    im = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        c = tuple(int(a + (b - a) * t) for a, b in zip((6, 18, 43), (26, 93, 138)))
        d.line([(0, y), (W, y)], fill=c + (255,))
    for i, col in enumerate([(56, 242, 255, 60), (20, 241, 149, 50)]):
        for x in range(0, W, 4):
            import math
            yy = 90 + i * 40 + math.sin(x / 90 + i) * 24
            d.rectangle([x, yy, x + 3, yy + 30], fill=col)
    d.rectangle([0, 520, W, H], fill=(243, 236, 217, 255))
    d.rectangle([0, 528, W, 534], fill=(191, 233, 245, 255))
    d.rectangle([0, 0, W, 12], fill=(224, 180, 58, 255)); d.rectangle([0, H - 12, W, H], fill=(224, 180, 58, 255))

    def put(img, x, y, s, flip=False):
        img = img.resize((img.width * s, img.height * s), Image.NEAREST)
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        im.alpha_composite(img, (x, y))
    put(fr('jp_atk1'), 70, 520 - 40 * 7, 7)
    put(fr('bolt_run', 1), 370, 520 - 30 * 6, 6)
    put(fr('boss'), 720, 150, 9, True)
    put(fr('bear'), 980, 520 - 14 * 5, 5, True)
    for k in range(5):
        put(fr('coin', k % 4), 400 + k * 60, 250, 4)
    try:
        f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 96)
        f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 34)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    for dx, dy, col in [(5, 5, (0, 0, 0, 255)), (0, 0, (224, 180, 58, 255))]:
        d.text((60 + dx, 40 + dy), 'MAIGA RAID', font=f1, fill=col)
    d.text((64, 150), 'Rescue Mintje from Lord Rugpull', font=f2, fill=(243, 236, 217, 255))
    d.text((64, 196), 'Free browser game · no wallet', font=f2, fill=(56, 242, 255, 255))
    d.text((760, 560), 'geopolcoins.xyz/raid', font=f2, fill=(10, 22, 48, 255))
    im.convert('RGB').save(os.path.join(OUT, 'og-raid.png'), optimize=True)


if __name__ == '__main__':
    build_og()
    print('og-raid.png')
