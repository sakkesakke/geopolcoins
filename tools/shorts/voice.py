#!/usr/bin/env python3
"""Give a Short a human voice: Jean-Phil reads his speech bubbles out loud, at a calm natural pace.

Engine: Chatterbox Multilingual by Resemble AI (MIT license, https://github.com/resemble-ai/chatterbox).
The voice is either Chatterbox's built-in default voice or a short reference clip in tools/shorts/voices/
made with a synthetic Kokoro voice (Apache-2.0, https://github.com/hexgrad/kokoro), so no real person's
voice is ever cloned. Output carries Resemble's inaudible PerTh watermark (marks it as AI audio).

Three stages, so the video follows the voice instead of the voice being rushed to fit the video:
    python3 tools/shorts/voice.py lines --ids a,b --dir .shorts   # speak every line, write <dir>/<id>.timing.json
    SHORT_TIMING=.shorts/a.timing.json python3 tools/shorts/make_short.py a .shorts   # scenes stretch to fit
    python3 tools/shorts/voice.py mix --ids a,b --dir .shorts     # put the lines on the video, duck the music
    python3 tools/shorts/voice.py samples --dir .samples          # one clip per voice, to choose a voice
Add --engine stub to test everything without the model.
"""
import argparse, json, math, os, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
TOPICS = {t["id"]: t for t in json.load(open(os.path.join(HERE, "topics.json"), encoding="utf-8"))}
LANG = {"en": "en", "nl": "nl", "fr": "fr", "es": "es", "de": "de", "pt": "pt", "id": "ms", "tr": "tr"}  # Indonesian -> Malay (closest)
VOICES = os.path.join(HERE, "voices")
DEFAULT_VOICE = os.environ.get("SHORT_VOICE", "default")

# when each speech bubble starts inside its scene (same numbers as make_short.py), and the minimum scene lengths
LEAD = [0.5] + [0.25] * 5 + [0.9]
MIN = [3.5] + [3.5] * 5 + [5.0]
TAIL = [0.6] + [0.6] * 5 + [1.6]   # breathing room after a line (end card: time to read the URL)
PACE = 0.94                         # a touch slower than the model's natural speed (1.0 = unchanged)


def lines_of(t):
    return [t["hook_line"]] + [line for _, line in t["items"]] + [t.get("end_line", "")]


def half_up(x):
    return math.ceil(x * 2 - 1e-6) / 2   # whole beats at 120 BPM, so cuts stay on the music


class Stub:
    sr = 24000

    def say(self, text, lang):
        n = int(self.sr * min(5.0, 0.07 * len(text)))
        return [0.2 * math.sin(2 * math.pi * 220 * i / self.sr) for i in range(n)]


class Chatterbox:
    def __init__(self, voice):
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        self.m = ChatterboxMultilingualTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
        self.sr = self.m.sr
        self.ref = None if voice == "default" else os.path.join(VOICES, voice + ".wav")
        if self.ref and not os.path.exists(self.ref):
            sys.exit(f"voice {voice!r} not found in {VOICES}")

    def say(self, text, lang):
        # calm and clear: low exaggeration + low cfg_weight = slower, more deliberate delivery
        w = self.m.generate(text, language_id=lang, audio_prompt_path=self.ref, exaggeration=0.45, cfg_weight=0.3, temperature=0.7)
        return w.squeeze(0).numpy().tolist()


def write_wav(path, samples, sr):
    import struct
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode().strip())


def polish(raw, out):
    """Trim silence at both ends, slow down a little, even loudness."""
    af = (f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          f"atempo={PACE},loudnorm=I=-16:TP=-2:LRA=7,aresample=48000")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ac", "1", out], check=True)


def stage_lines(engine, tid, d):
    t = TOPICS[tid]; lang = LANG.get(t.get("lang", "en"), "en")
    wd = os.path.join(d, tid + ".voice"); os.makedirs(wd, exist_ok=True)
    talk, scenes = [], []
    for k, text in enumerate(lines_of(t)):
        if not text.strip():
            talk.append(0); scenes.append(MIN[k]); continue
        raw = os.path.join(wd, f"raw{k}.wav"); out = os.path.join(wd, f"l{k}.wav")
        write_wav(raw, engine.say(text, lang), engine.sr); polish(raw, out); os.remove(raw)
        L = dur(out); talk.append(round(L, 3))
        scenes.append(max(MIN[k], half_up(LEAD[k] + L + TAIL[k])))
    json.dump({"scenes": scenes, "talk": talk, "lead": LEAD}, open(os.path.join(d, tid + ".timing.json"), "w"))
    print("lines", tid, lang, "talk", talk, "scenes", scenes, "total", sum(scenes))


def stage_mix(tid, d):
    tm = json.load(open(os.path.join(d, tid + ".timing.json")))
    src = os.path.join(d, tid + ".mp4"); wd = os.path.join(d, tid + ".voice")
    if not os.path.exists(src):
        sys.exit(f"missing {src}: render it first with make_short.py (with SHORT_TIMING)")
    inputs, filters, acc = [], [], 0.0
    for k, (sc, L) in enumerate(zip(tm["scenes"], tm["talk"])):
        if L:
            ms = int((acc + tm["lead"][k]) * 1000); n = len(inputs) // 2 + 1
            inputs += ["-i", os.path.join(wd, f"l{k}.wav")]
            filters.append(f"[{n}:a]adelay={ms}|{ms}[v{n}]")
        acc += sc
    n = len(inputs) // 2
    mix = "".join(f"[v{k}]" for k in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:dropout_transition=0[voice]"
    out = os.path.join(wd, "out.mp4")
    fc = ";".join(filters + [mix, "[0:a]volume=0.30[music]", "[music][voice]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src] + inputs + ["-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    os.replace(out, src)
    print("voiced", tid, f"{n} lines", f"{dur(src):.1f}s")


SAMPLE = {"nl": "Hoi, ik ben Jean-Phil. Rode vlag nummer één: het team is anoniem en de liquiditeit is niet vergrendeld.",
          "en": "Hi, I'm Jean-Phil. Red flag number one: the team is anonymous and the liquidity is not locked."}


def stage_samples(engine_for, d):
    os.makedirs(d, exist_ok=True)
    names = ["default"] + sorted(f[:-4] for f in os.listdir(VOICES) if f.endswith(".wav")) if os.path.isdir(VOICES) else ["default"]
    for v in names:
        eng = engine_for(v); parts = []
        for lang, text in SAMPLE.items():
            raw = os.path.join(d, f"_{v}_{lang}.wav"); out = os.path.join(d, f"_{v}_{lang}_p.wav")
            write_wav(raw, eng.say(text, lang), eng.sr); polish(raw, out); parts.append(out)
        lst = os.path.join(d, "_l.txt"); open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "libmp3lame", "-q:a", "3",
                        os.path.join(d, f"voice-{v}.mp3")], check=True)
        print("sample", v)
    for f in os.listdir(d):
        if f.startswith("_"): os.remove(os.path.join(d, f))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["lines", "mix", "samples"])
    ap.add_argument("--ids", default="")
    ap.add_argument("--dir", default=".shorts")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help="'default' or a file name (without .wav) in tools/shorts/voices/")
    ap.add_argument("--engine", choices=["chatterbox", "stub"], default="chatterbox")
    a = ap.parse_args()
    ids = [x.strip() for x in a.ids.split(",") if x.strip()]
    if a.stage == "samples":
        if a.engine == "stub":
            stage_samples(lambda v: Stub(), a.dir)
        else:
            cb = Chatterbox("default")
            def engine_for(v):
                cb.ref = None if v == "default" else os.path.join(VOICES, v + ".wav"); return cb
            stage_samples(engine_for, a.dir)
    elif a.stage == "lines":
        eng = Stub() if a.engine == "stub" else Chatterbox(a.voice)
        for tid in ids: stage_lines(eng, tid, a.dir)
    else:
        for tid in ids: stage_mix(tid, a.dir)
