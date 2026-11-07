#!/usr/bin/env python3
"""Give a Short a human voice: Jean-Phil reads his speech bubbles out loud.

Engine: Chatterbox Multilingual by Resemble AI (MIT license, https://github.com/resemble-ai/chatterbox),
using its built-in default voice (no cloning of real people). Output carries Resemble's inaudible
PerTh watermark, which marks it as AI-generated audio.

    python3 tools/shorts/voice.py --ids redflags-5,seed-phrase-nl --dir .shorts
    python3 tools/shorts/voice.py --ids redflags-5 --dir .shorts --engine stub   # test the mixing without the model

For each id, <dir>/<id>.mp4 (made by make_short.py, with music) is replaced by a voiced version:
the lines are placed on the scene timings of make_short.py, sped up a little when a line is longer
than its scene, and the music is ducked under the voice.
"""
import argparse, json, os, subprocess, sys, tempfile, wave

HERE = os.path.dirname(os.path.abspath(__file__))
TOPICS = {t["id"]: t for t in json.load(open(os.path.join(HERE, "topics.json"), encoding="utf-8"))}
LANG = {"en": "en", "nl": "nl", "fr": "fr", "es": "es", "de": "de", "pt": "pt", "id": "ms", "tr": "tr"}  # Indonesian -> Malay (closest)


def timeline(t):
    """(start seconds, text, max seconds) in sync with make_short.py: hook 0-3.5, five items x 3.5 s, end card 21-26."""
    out = [(0.45, t["hook_line"], 3.0)]
    for j, (_, line) in enumerate(t["items"]):
        out.append((3.5 + 3.5 * j + 0.25, line, 3.15))
    out.append((21.85, t.get("end_line", ""), 3.6))
    return [x for x in out if x[1].strip()]


class Stub:
    sr = 24000

    def say(self, text, lang):
        import math
        n = int(self.sr * min(4.0, 0.06 * len(text)))
        return [0.2 * math.sin(2 * math.pi * 220 * i / self.sr) for i in range(n)]


class Chatterbox:
    def __init__(self):
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        self.m = ChatterboxMultilingualTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
        self.sr = self.m.sr

    def say(self, text, lang):
        # a lively but clear read; cfg_weight a bit lower = calmer pacing
        w = self.m.generate(text, language_id=lang, exaggeration=0.6, cfg_weight=0.4, temperature=0.75)
        return w.squeeze(0).numpy().tolist()


def write_wav(path, samples, sr):
    import struct
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode().strip())


def voice_one(engine, tid, d):
    t = TOPICS[tid]
    lang = LANG.get(t.get("lang", "en"), "en")
    src = os.path.join(d, tid + ".mp4")
    if not os.path.exists(src):
        sys.exit(f"missing {src}: render it first with make_short.py")
    work = tempfile.mkdtemp(prefix="voice_")
    inputs, filters = [], []
    for k, (start, text, room) in enumerate(timeline(t)):
        raw = os.path.join(work, f"l{k}.wav")
        write_wav(raw, engine.say(text, lang), engine.sr)
        speed = min(1.35, max(1.0, dur(raw) / room))  # fit the scene, never slower than natural
        inputs += ["-i", raw]
        filters.append(f"[{k + 1}:a]atempo={speed:.3f},aresample=48000,adelay={int(start * 1000)}|{int(start * 1000)},volume=1.0[v{k}]")
    n = len(inputs) // 2
    mix = "".join(f"[v{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,loudnorm=I=-15:TP=-1.5[voice]"
    duck = "[0:a]volume=0.32[music]"
    out = os.path.join(work, "out.mp4")
    fc = ";".join(filters + [mix, duck, "[music][voice]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src] + inputs + ["-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    os.replace(out, src)
    print("voiced", tid, lang, f"{n} lines")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--dir", default=".shorts")
    ap.add_argument("--engine", choices=["chatterbox", "stub"], default="chatterbox")
    a = ap.parse_args()
    eng = Stub() if a.engine == "stub" else Chatterbox()
    for tid in [x.strip() for x in a.ids.split(",") if x.strip()]:
        voice_one(eng, tid, a.dir)
