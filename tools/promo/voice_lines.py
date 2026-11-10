#!/usr/bin/env python3
"""Speak every line of a promo script (tools/promo/<name>.json) with Chatterbox (MIT) and a synthetic
Kokoro reference voice from tools/shorts/voices/ (no real person's voice is cloned).
Writes <out>/l<k>.wav (trimmed, 48 kHz, even loudness) and <out>/timing.json with each line's length.
    python3 tools/promo/voice_lines.py human-override --voice george --out .promo/human-override [--engine stub]
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shorts"))
import voice as V  # reuses the engine, polish() and dur() from the Shorts pipeline

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("--voice", default="george"); ap.add_argument("--out", required=True)
ap.add_argument("--engine", choices=["chatterbox", "stub"], default="chatterbox")
a = ap.parse_args()
if not a.name.replace("-", "").isalnum(): sys.exit("bad name")
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), a.name + ".json"), encoding="utf-8"))
eng = V.Stub() if a.engine == "stub" else V.Chatterbox(a.voice)
os.makedirs(a.out, exist_ok=True); talk = []
for k, text in enumerate(S["lines"]):
    raw = os.path.join(a.out, f"raw{k}.wav"); out = os.path.join(a.out, f"l{k}.wav")
    V.write_wav(raw, eng.say(text, S.get("lang", "en")), eng.sr); V.polish(raw, out); os.remove(raw)
    talk.append(round(V.dur(out), 3)); print(k, talk[-1], text)
json.dump({"name": a.name, "voice": a.voice, "talk": talk}, open(os.path.join(a.out, "timing.json"), "w"))
