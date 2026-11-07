"""Make a 26 s vertical Short (1080x1920) with Jean-Phil from one topic in topics.json.
Usage: python3 tools/shorts/make_short.py <topic-id> [outdir]   (or 'next' = first topic without "posted")
Writes <outdir>/<id>.mp4 and <outdir>/<id>_check.jpg. Needs ffmpeg, Pillow, numpy."""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
TOPICS = json.load(open(os.path.join(HERE, 'topics.json')))
ARG = sys.argv[1] if len(sys.argv) > 1 else 'next'
TOPIC = next(t for t in TOPICS if (t['id'] == ARG if ARG != 'next' else not t.get('posted')))
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(REPO, '.shorts')
W, H, FPS = 1080, 1920, 30
PIX = os.path.join(REPO, 'fonts', 'jersey-10.ttf')
SANS = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
if not os.path.exists(SANS):
    SANS = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
NIGHT, CAB, AMBER, CREAM, DIM, TEAL, RED, LILAC, INK = (18, 15, 30), (37, 28, 56), (255, 181, 71), (243, 236, 217), (179, 169, 196), (95, 211, 198), (255, 107, 107), (200, 168, 255), (26, 18, 6)
FC = {}
def font(p, s):
    k = (p, s)
    if k not in FC: FC[k] = ImageFont.truetype(p, s)
    return FC[k]
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):  # overshoot pop
    x = max(0.0, min(1.0, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- Jean-Phil sprite with talking mouth and blinking ----------
JP0 = Image.open(os.path.join(REPO, 'meme', 'pxjp.png')).convert('RGBA')
DARK, TONGUE, LID = (26, 26, 26, 255), (168, 40, 58, 255), (150, 100, 70, 255)
def jp_variant(mouth, blink):
    im = JP0.copy(); px = im.load()
    if mouth >= 1:
        for x in range(11, 15): px[x, 17] = DARK
    if mouth >= 2:
        px[10, 17] = DARK; px[15, 17] = DARK
        for x in range(11, 15): px[x, 17] = TONGUE
        for x in range(11, 15): px[x, 18] = DARK
    if blink:
        for x in (7, 8, 17, 18): px[x, 10] = LID
    return im
JPV = {(m, b): jp_variant(m, b) for m in range(3) for b in (0, 1)}
SC = {}
def jp(scale, t, talking):
    m = 0
    if talking:
        m = [2, 1, 2, 0, 1, 2, 1, 0][int(t * FPS / 3) % 8]
    b = 1 if (t % 2.9) > 2.78 else 0
    k = (scale, m, b)
    if k not in SC:
        im = JPV[(m, b)]; SC[k] = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return SC[k]

# ---------- drawing helpers ----------
def night_bg(t, glow=AMBER):
    im = Image.new('RGB', (W, H), NIGHT); d = ImageDraw.Draw(im)
    for x in range(0, W, 54): d.rectangle((x + 52, 0, x + 54, H), fill=(14, 11, 24))
    g = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(g)
    r = 620 + 30 * math.sin(t * 2)
    gd.ellipse((W / 2 - r, 980 - r, W / 2 + r, 980 + r), fill=70)
    g = g.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new('RGB', (W, H), tuple(int(c * .55) for c in glow)), im, g)
    return im

def kenburns(im, t, z0, z1, ay=0.2, ax=0.5):
    z = z0 + (z1 - z0) * t
    cw, ch = int(W / z), int(H / z)
    x = int((W - cw) * ax); y = int((H - ch) * ay)
    return im.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)

def wrap(d, text, f, maxw):
    out = []
    for para in text.split('\n'):
        cur = ''
        for w in para.split():
            tt = (cur + ' ' + w).strip()
            if d.textlength(tt, font=f) <= maxw: cur = tt
            else: out.append(cur); cur = w
        out.append(cur)
    return out

def pixtext(t):
    # the pixel font has no accents: strip them (É -> E, Ç -> C) for the big plates only
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c)).replace('ß', 'SS')


END = {'en': ('CHECK ANY TOKEN', 'Free Token Checkup  ·  No wallet', 'Solana  ·  10 languages', 'Education and entertainment. Not financial advice.'),
       'nl': ('CHECK ELKE TOKEN', 'Gratis Token Checkup  ·  Geen wallet', 'Solana  ·  10 talen', 'Educatie en entertainment. Geen financieel advies.'),
       'fr': ('VERIFIE UN TOKEN', 'Token Checkup gratuit  ·  Sans wallet', 'Solana  ·  10 langues', 'Éducation et divertissement. Pas un conseil financier.'),
       'es': ('REVISA UN TOKEN', 'Token Checkup gratis  ·  Sin wallet', 'Solana  ·  10 idiomas', 'Educación y entretenimiento. No es asesoría financiera.'),
       'de': ('PRUEF JEDEN TOKEN', 'Gratis Token Checkup  ·  Kein Wallet', 'Solana  ·  10 Sprachen', 'Bildung und Unterhaltung. Keine Finanzberatung.'),
       'pt': ('CONFIRA UM TOKEN', 'Token Checkup grátis  ·  Sem carteira', 'Solana  ·  10 idiomas', 'Educação e entretenimento. Não é conselho financeiro.'),
       'id': ('CEK TOKEN APA SAJA', 'Token Checkup gratis  ·  Tanpa dompet', 'Solana  ·  10 bahasa', 'Edukasi dan hiburan. Bukan nasihat keuangan.')}
LANG = TOPIC.get('lang', 'en') if TOPIC.get('lang', 'en') in END else 'en'


def marquee(d, text, f, cx, y, color, k=1.0, left=None):
    text = pixtext(text)
    """Arcade marquee plate. k = pop scale 0..1+ (applied as vertical squash)."""
    w = d.textlength(text, font=f); pad = 34; h = f.size + 26
    x0 = (cx - w / 2 - pad) if left is None else left
    x1 = x0 + w + 2 * pad
    sh = max(0.0, k)
    yc = y + h / 2; hh = h * sh / 2
    d.rounded_rectangle((x0 - 8, yc - hh - 8, x1 + 8, yc + hh + 12), 22, fill=INK)
    d.rounded_rectangle((x0, yc - hh, x1, yc + hh), 16, fill=color)
    if sh > 0.75:
        d.text((x0 + pad, y + 6), text, font=f, fill=INK)
    return x1

def bubble(base, text, x, y, maxw, t_local, start, cps=34, size=50, tail='left', color=CREAM):
    """Speech bubble with typewriter. Returns (talking, chars_shown)."""
    d = ImageDraw.Draw(base)
    f = font(SANS, size)
    lines = wrap(d, text, f, maxw - 60)
    n_total = len(text)
    shown = int(max(0, (t_local - start)) * cps)
    if t_local < start: return False, 0
    k = back((t_local - start) / 0.22)
    lh = int(size * 1.28)
    bw = max(d.textlength(l, font=f) for l in lines) + 60
    bh = len(lines) * lh + 44
    # pop: scale the plate from its tail corner
    sw, sh = bw * k, bh * k
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle((x + 6, y + 10, x + sw + 6, y + sh + 10), 30, fill=(0, 0, 0, 120))
    od.rounded_rectangle((x, y, x + sw, y + sh), 30, fill=color + (255,), outline=INK + (255,), width=6)
    if tail == 'left':
        od.polygon([(x + 10, y + sh - 50), (x - 46, y + sh + 14), (x + 70, y + sh - 6)], fill=color + (255,))
        od.line([(x + 6, y + sh - 52), (x - 46, y + sh + 14), (x + 72, y + sh - 4)], fill=INK + (255,), width=6)
    elif tail == 'down':
        tx = x + sw * 0.5
        od.polygon([(tx - 50, y + sh - 6), (tx, y + sh + 60), (tx + 30, y + sh - 6)], fill=color + (255,))
        od.line([(tx - 52, y + sh - 3), (tx, y + sh + 60), (tx + 32, y + sh - 3)], fill=INK + (255,), width=6)
    base.alpha_composite(ov)
    if k > 0.9:
        d = ImageDraw.Draw(base); left = shown; yy = y + 22
        for l in lines:
            part = l[:max(0, left)]
            d.text((x + 30, yy), part, font=f, fill=INK)
            left -= len(l) + 1; yy += lh
    return shown < n_total, min(shown, n_total)

def flash(im, t_local, dur=0.16):
    if t_local < dur:
        a = 1 - t_local / dur
        return Image.blend(im, Image.new('RGB', (W, H), (255, 246, 225)), a * 0.85)
    return im

def progress(base, T, DUR):
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, W, 12), fill=(0, 0, 0, 160))
    d.rectangle((0, 0, int(W * T / DUR), 12), fill=AMBER + (255,))

def bottom_fade(base, h=760):
    g = Image.new('L', (1, h))
    for i in range(h): g.putpixel((0, i), int(255 * min(1, (i / h) ** 1.4 * 1.15)))
    g = g.resize((W, h))
    shade = Image.new('RGBA', (W, h), NIGHT + (0,)); shade.putalpha(g)
    base.alpha_composite(shade, (0, H - h))

def top_fade(base, h=360):
    g = Image.new('L', (1, h))
    for i in range(h): g.putpixel((0, i), int(220 * (1 - i / h) ** 1.2))
    g = g.resize((W, h))
    shade = Image.new('RGBA', (W, h), NIGHT + (0,)); shade.putalpha(g)
    base.alpha_composite(shade, (0, 0))

BLIPS = []  # (time, kind) for the soundtrack


# ---------- scenes ----------
# Optional timing from voice.py (SHORT_TIMING=<json file>): scenes stretch to fit the spoken lines,
# and the speech bubble types at the speed of the voice.
TIMING = json.load(open(os.environ['SHORT_TIMING'])) if os.environ.get('SHORT_TIMING') else None
def cps(k, text, default):
    if TIMING and TIMING['talk'][k]: return max(8.0, len(text) / TIMING['talk'][k])
    return default
SCENES = []
def scene(dur):
    def deco(fn): SCENES.append((dur, fn)); return fn
    return deco

def redflag(im, cx, cy, s, tl):
    """Pixel red flag on a pole, waving."""
    d = ImageDraw.Draw(im)
    d.rectangle((cx - s // 2, cy - 9 * s, cx + s // 2, cy + 5 * s), fill=CREAM)
    for r in range(4):
        off = int(s * 0.6 * math.sin(tl * 7 + r))
        d.rectangle((cx + s // 2, cy - 9 * s + r * s, cx + s // 2 + 6 * s + off, cy - 8 * s + r * s), fill=RED)

@scene(3.5)
def s_hook(tl, T):
    im = night_bg(tl, RED).convert('RGBA'); d = ImageDraw.Draw(im)
    marquee(d, TOPIC['hook'][0], font(PIX, 150 if len(TOPIC['hook'][0]) < 12 else 112 if len(TOPIC['hook'][0]) < 16 else 92), W / 2, 190, RED, back(tl / 0.3))
    marquee(d, TOPIC['hook'][1], font(PIX, 112 if len(TOPIC['hook'][1]) < 15 else 88 if len(TOPIC['hook'][1]) < 19 else 74), W / 2, 380, AMBER, back((tl - 0.18) / 0.3))
    tmp = Image.new('RGBA', (W, H))
    talking, _ = bubble(tmp, TOPIC['hook_line'], 120, 640, 840, tl, 0.5, cps=cps(0, TOPIC['hook_line'], 34), size=60, tail='down')
    sp = jp(22, tl, talking); zin = ease(tl / 0.35)
    im.alpha_composite(sp, ((W - sp.width) // 2, int(1180 - 40 * (1 - zin)) + int(10 * math.sin(tl * 5))))
    im.alpha_composite(tmp)
    return im.convert('RGB')

FLAGS = [tuple(x) for x in TOPIC['items']]
for i, (name, line) in enumerate(FLAGS):
    def mk(name=name, line=line, i=i):
        def fn(tl, T):
            im = flash(night_bg(tl + i, RED), tl).convert('RGBA'); d = ImageDraw.Draw(im)
            chip = f'{i + 1}/5'; fc = font(PIX, 70); cw = d.textlength(chip, font=fc)
            d.rounded_rectangle((W - 48 - cw - 44, 70, W - 48, 70 + 104), 18, fill=NIGHT, outline=RED, width=6)
            d.text((W - 48 - cw - 22, 82), chip, font=fc, fill=RED)
            marquee(d, name, font(PIX, 104 if len(name) < 14 else 88 if len(name) < 19 else 72), W / 2, 260, AMBER if i % 2 else CREAM, back(tl / 0.22))
            k = back((tl - 0.1) / 0.3)
            if k > 0: redflag(im, W // 2 - 140, int(1000 - 60 * (1 - min(1, k))), 40, tl)
            tmp = Image.new('RGBA', (W, H))
            talking, _ = bubble(tmp, line, 320, 1380, 720, tl, 0.25, cps=cps(i + 1, line, 40), size=54)
            sp = jp(10, tl, talking); im.alpha_composite(sp, (40, H - sp.height - 70 + int(6 * math.sin(tl * 6 + i))))
            im.alpha_composite(tmp)
            return im.convert('RGB')
        return fn
    SCENES.append((3.5, mk()))

@scene(5.0)
def s_end(tl, T):
    im = flash(night_bg(tl, TEAL), tl).convert('RGBA'); d = ImageDraw.Draw(im)
    marquee(d, END[LANG][0], font(PIX, 112 if len(END[LANG][0]) < 16 else 96), W / 2, 170, TEAL, back(tl / 0.3))
    marquee(d, 'geopolcoins.xyz', font(PIX, 120), W / 2, 360, AMBER, back((tl - 0.12) / 0.3))
    f = font(SANS, 52)
    for j, (txt, col) in enumerate([(END[LANG][1], CREAM), (END[LANG][2], TEAL)]):
        a = ease((tl - 0.5 - j * 0.2) / 0.35)
        if a > 0:
            w = d.textlength(txt, font=f); d.text(((W - w) / 2, 640 + j * 86 + 30 * (1 - a)), txt, font=f, fill=tuple(int(c * a) for c in col))
    tmp = Image.new('RGBA', (W, H))
    talking, _ = bubble(tmp, TOPIC.get('end_line', 'Follow for more!'), 220, 930, 660, tl, 0.9, cps=cps(6, TOPIC.get('end_line', 'Follow for more!'), 30), size=56, tail='down')
    sp = jp(18, tl, talking); im.alpha_composite(sp, ((W - sp.width) // 2, 1200 + int(8 * math.sin(tl * 5))))
    im.alpha_composite(tmp)
    d = ImageDraw.Draw(im); fs = font(SANS, 34); txt = END[LANG][3]
    w = d.textlength(txt, font=fs); d.text(((W - w) / 2, 1820), txt, font=fs, fill=DIM)
    return im.convert('RGB')

if TIMING: SCENES = [(d, fn) for d, (_, fn) in zip(TIMING['scenes'], SCENES)]
STARTS = []; acc = 0.0
for dur, fn in SCENES: STARTS.append(acc); acc += dur
DUR = acc

def frame(T):
    for j, (dur, fn) in enumerate(SCENES):
        if STARTS[j] <= T < STARTS[j] + dur or j == len(SCENES) - 1: break
    tl = T - STARTS[j]
    im = fn(tl, T).convert('RGBA'); progress(im, T, DUR)
    out = im.convert('RGB')
    if T > DUR - 0.5: out = Image.blend(out, Image.new('RGB', (W, H), NIGHT), (T - (DUR - 0.5)) / 0.5)
    return out

if __name__ == '__main__':
    import shutil, tempfile
    os.makedirs(OUT, exist_ok=True)
    work = tempfile.mkdtemp(prefix='short_')
    parts = []
    for j, (dur, fn) in enumerate(SCENES):
        out = os.path.join(work, f's{j:02d}.mp4'); parts.append(out)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), out], stdin=subprocess.PIPE)
        for k in range(int(round(dur * FPS))):
            ff.stdin.write(frame(STARTS[j] + k / FPS).tobytes())
        ff.stdin.close()
        if ff.wait() != 0: sys.exit('scene %d failed' % j)
    open(os.path.join(work, 'list.txt'), 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(work, 'list.txt'), '-c', 'copy', os.path.join(work, 'v.mp4')], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'score.py'), os.path.join(work, 'score.wav')] + ([json.dumps([d for d, _ in SCENES])] if TIMING else []), check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(work, 'score.wav'), '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '48000', os.path.join(work, 'n.wav')], check=True)
    final = os.path.join(OUT, TOPIC['id'] + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(work, 'v.mp4'), '-i', os.path.join(work, 'n.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    sheet = Image.new('RGB', (270 * 4, 480))
    for i, ts in enumerate((2.5, STARTS[1] + 2.0, STARTS[3] + 2.5, STARTS[6] + 3.0)): sheet.paste(frame(ts).resize((270, 480)), (i * 270, 0))
    sheet.save(os.path.join(OUT, TOPIC['id'] + '_check.jpg'), quality=85)
    shutil.rmtree(work, ignore_errors=True)
    print(final)
