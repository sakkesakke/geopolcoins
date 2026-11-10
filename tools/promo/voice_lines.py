#!/usr/bin/env python3
"""Speak every line of a promo script (tools/promo/<name>.json) and CHECK it by listening back.

Engines (all synthetic voices, no real person is cloned):
  kokoro      hexgrad/kokoro (Apache-2.0), voice bm_george etc. Clear, stable pronunciation.
  chatterbox  Resemble AI Chatterbox (MIT) with a reference clip from tools/shorts/voices/.
Every line is transcribed with faster-whisper (MIT) and compared with the script. Chatterbox lines that
do not match are spoken again (up to 4 tries, best one kept). report.json lists every transcript.
Abbreviations are spelled for the voice only ("AI" -> "A.I."), captions keep the normal text.
    python3 tools/promo/voice_lines.py human-override --engine kokoro --voice bm_george --out .promo/human-override
"""
import argparse, difflib, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shorts"))
import voice as V  # write_wav(), polish(), dur(), Chatterbox, Stub

SPELL = {"AI": "A.I.", "DNS": "D.N.S.", "PIN": "pin"}
def spoken(t): return re.sub(r"\.\.", ".", re.sub(r"\b(" + "|".join(SPELL) + r")\b", lambda m: SPELL[m.group(1)], t))
def words(t):
    t = t.lower().replace("a.i.", "ai").replace("d.n.s.", "dns").replace("a. i.", "ai")
    t = re.sub(r"\bai\b|\ba i\b|\bay eye\b", "ai", t)
    return re.findall(r"[a-z0-9]+", t.replace("-", " "))
def score(a, b): return difflib.SequenceMatcher(None, words(a), words(b)).ratio()

class Kokoro:
    sr = 24000
    def __init__(self, voice, speed):
        from kokoro import KPipeline
        self.v = voice; self.speed = speed; self.p = KPipeline(lang_code="b" if voice.startswith("b") else "a")
    def say(self, text, lang):
        import numpy as np
        return np.concatenate([a.numpy() if hasattr(a, "numpy") else np.asarray(a) for _, _, a in self.p(text, voice=self.v, speed=self.speed)]).tolist()

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("--engine", choices=["kokoro", "chatterbox", "stub"], default="kokoro")
ap.add_argument("--voice", default="bm_george"); ap.add_argument("--speed", type=float, default=1.0)
ap.add_argument("--out", required=True); ap.add_argument("--no-check", action="store_true")
a = ap.parse_args()
if not re.fullmatch(r"[a-z0-9-]+", a.name): sys.exit("bad name")
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), a.name + ".json"), encoding="utf-8"))
eng = V.Stub() if a.engine == "stub" else Kokoro(a.voice, a.speed) if a.engine == "kokoro" else V.Chatterbox(a.voice)
asr = None
if not a.no_check and a.engine != "stub":
    from faster_whisper import WhisperModel
    asr = WhisperModel("small.en", device="cpu", compute_type="int8")
def hear(path):
    segs, _ = asr.transcribe(path, beam_size=5, language="en", condition_on_previous_text=False)
    return " ".join(s.text.strip() for s in segs)

os.makedirs(a.out, exist_ok=True); talk, rep, bad = [], [], 0
for k, text in enumerate(S["lines"]):
    tries = 1 if a.engine != "chatterbox" else 4
    best = None
    for n in range(tries):
        raw = os.path.join(a.out, f"raw{k}.wav"); cand = os.path.join(a.out, f"c{k}_{n}.wav")
        V.write_wav(raw, eng.say(spoken(text), "en"), eng.sr); V.polish(raw, cand); os.remove(raw)
        heard = hear(cand) if asr else text; sc = score(text, heard)
        print(f"{k} try{n} {sc:.2f} | {heard}", flush=True)
        if best is None or sc > best[0]: best = (sc, cand, heard)
        if sc >= 0.95: break
    for f in os.listdir(a.out):
        if f.startswith(f"c{k}_") and os.path.join(a.out, f) != best[1]: os.remove(os.path.join(a.out, f))
    os.replace(best[1], os.path.join(a.out, f"l{k}.wav"))
    talk.append(round(V.dur(os.path.join(a.out, f"l{k}.wav")), 3))
    rep.append({"k": k, "text": text, "heard": best[2], "score": round(best[0], 3)}); bad += best[0] < 0.9
json.dump({"name": a.name, "engine": a.engine, "voice": a.voice, "talk": talk}, open(os.path.join(a.out, "timing.json"), "w"))
json.dump(rep, open(os.path.join(a.out, "report.json"), "w"), indent=1)
print("lines below 0.90:", bad)
