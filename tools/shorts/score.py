"""Original chiptune soundtrack made in code (no samples) for make_short.py: 26 s, 120 BPM.
0-3.5 hook, 3.5-21 five items (3.5 s each), 21-26 end card."""
import numpy as np, wave, sys
SR, DUR = 48000, 26.0
N = int(SR * DUR); mix = np.zeros((N, 2)); beat = 0.5; bar = 2.0
rng = np.random.default_rng(11)
def note(m): return 440 * 2 ** ((m - 69) / 12)
def put(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if j <= i or i < 0: return
    s = sig[:j - i] * g; mix[i:j, 0] += s * (1 - pan) * .7; mix[i:j, 1] += s * (1 + pan) * .7
def env(n, a=.004, d=8.0):
    t = np.arange(n) / SR; e = np.exp(-t * d); A = max(1, int(a * SR)); e[:A] *= np.linspace(0, 1, A); return e
def sq(f, dur, duty=.5):
    t = np.arange(int(dur * SR)) / SR; return np.where((t * f) % 1 < duty, 1.0, -1.0)
chords = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 55, 60, 64, 67], [43, 50, 55, 59, 62]]  # Am F C G
def ch(t): return chords[int(t / bar) % 4]
# pad
for k in range(int(DUR / bar) + 1):
    t0 = k * bar; c = ch(t0); n = int((bar + .3) * SR); tt = np.arange(n) / SR
    sig = sum(np.sin(2 * np.pi * note(m) * tt) for m in c[1:]) * .5 + np.sin(2 * np.pi * note(c[0]) * tt) * .6
    e = np.minimum(1, tt / .3) * np.minimum(1, (bar + .3 - tt) / .3)
    put(sig * e * .045, t0)
# arpeggio all the way, brighter after the drop
k = 0; t = 0.0
while t < 24.0:
    c = ch(t); m = [c[2], c[3], c[4], c[3] + 12][k % 4] + 12
    s = sq(note(m), .13, .25) * env(int(.13 * SR), d=18)
    put(s, t, pan=-.3 if k % 2 else .3, g=.03 if t < 3.5 else .045); t += beat / 2; k += 1
# lead hook on the drop and in the tools section (simple 2-bar motif)
motif = [(0, 12), (.5, 15), (1.0, 19), (1.5, 17), (2.0, 15), (2.75, 12), (3.0, 10), (3.5, 12)]
for start in (3.5, 10.5, 17.5):
    for dt, iv in motif:
        tt = start + dt; base = ch(tt)[0] + 24
        put(sq(note(base + iv - 12 + 12), .32, .5) * env(int(.32 * SR), d=5), tt, g=.035)
# bass + drums: 4-8 and 10-26, light in 26-29
def kick():
    n = int(.25 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (130 * np.exp(-tt * 22) + 45) * tt) * np.exp(-tt * 10)
def snare():
    n = int(.18 * SR); return rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 22)
def hat():
    n = int(.04 * SR); return rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 90)
def groove(a, b, g=1.0):
    t = a; i = 0
    while t < b - 1e-6:
        c = ch(t); put(sq(note(c[0] - 12), .22, .5) * env(int(.22 * SR), d=9), t, g=.08 * g)
        put(kick(), t, g=.55 * g) if i % 2 == 0 else put(snare(), t, g=.17 * g)
        put(hat(), t + beat / 2, pan=.25, g=.06 * g); t += beat; i += 1
groove(3.5, 21); groove(21, 24, .5)
# riser into the drop and out of the break
def riser(t0, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n) * (tt / dur) ** 2
    put(noise, t0, g=.08)
riser(2.0, 1.5)
# impact on the drop and on the end card
def impact(t0, g=.5):
    n = int(1.4 * SR); tt = np.arange(n) / SR
    put((np.sin(2 * np.pi * 50 * tt) + .3 * rng.standard_normal(n) * np.exp(-tt * 18)) * np.exp(-tt * 3), t0, g=g)
impact(3.5); impact(21.0, .4)
# whoosh/tick on every cut
def blip(f0, f1, dur=.09):
    n = int(dur * SR); tt = np.arange(n) / SR; f = np.linspace(f0, f1, n)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt * 25)
for i, c in enumerate([3.5 + 3.5 * j for j in range(6)]):
    put(blip(700 + 50 * (i % 8), 1500 + 70 * (i % 8)), c - .01, g=.07)
# Jean-Phil "voice": soft square blips while he talks (typewriter)
talk = [(0.5, 39 / 34)] + [(3.5 + 3.5 * j + .25, L / 40) for j, L in enumerate([57, 50, 41, 51, 48])] + [(21.9, 26 / 30)]
for t0, d in talk:
    t = t0; i = 0
    while t < t0 + d:
        f = note(70 + [0, 3, 5, 3, 7, 5][i % 6])
        put(sq(f, .045, .3) * env(int(.045 * SR), d=40), t, pan=-.1, g=.035); t += .075; i += 1
# end coin sound
put(sq(note(83), .08, .5) * env(int(.08 * SR), d=10), 21.15, g=.07); put(sq(note(88), .4, .5) * env(int(.4 * SR), d=6), 21.23, g=.07)
fo = int(2.0 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
fi = int(.05 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9; mix *= .9
w = wave.open(sys.argv[1] if len(sys.argv) > 1 else 'score.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype('<i2').tobytes()); w.close(); print('ok')
