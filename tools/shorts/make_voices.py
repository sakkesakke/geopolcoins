#!/usr/bin/env python3
"""Make reference clips for voice.py from synthetic Kokoro voices (hexgrad/kokoro, Apache-2.0).
Chatterbox then speaks every language in the style of that clip. Kokoro voices are synthetic, so no
real person's voice is cloned.   python3 tools/shorts/make_voices.py tools/shorts/voices
"""
import os, sys
import numpy as np, soundfile as sf
from kokoro import KPipeline

TEXT = ("Hello friends, welcome back. Today we look at five simple red flags before you buy any token. "
        "Take your time, check the facts, and never trust a promise of quick money.")
VOICES = {"george": ("b", "bm_george"),   # calm, deep British man
          "michael": ("a", "am_michael"), # warm American man
          "fenrir": ("a", "am_fenrir"),   # deeper, energetic American man
          "heart": ("a", "af_heart")}     # friendly American woman
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "voices")
os.makedirs(out, exist_ok=True)
pipes = {}
for name, (lc, v) in VOICES.items():
    p = pipes.setdefault(lc, KPipeline(lang_code=lc))
    audio = [a.numpy() if hasattr(a, "numpy") else np.asarray(a) for _, _, a in p(TEXT, voice=v, speed=0.95)]
    sf.write(os.path.join(out, name + ".wav"), np.concatenate(audio), 24000)
    print("voice", name, v)
