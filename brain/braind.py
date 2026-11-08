#!/usr/bin/env python3
"""The Brain: answers visitor questions on geopolcoins.xyz with the local AI model (Ollama + Qwen2.5 1.5B).

Grounded in the site's own knowledge file (guide-kb.json): the best 3 matching topics/pages go into the
prompt. Education only: no price predictions, no buy/sell advice, never asks for keys or seed phrases.
The answer is cleaned (no outside links) before the visitor sees it. Questions are deleted after 1 day.
"""
import json, os, re, time, urllib.request

SB = "https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/"
KEY = "sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN"   # public website key, not a secret
OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:1.5b"
KB_URL = "https://geopolcoins.xyz/guide-kb.json"
KB_FILE = "/opt/maiga/brain/kb.json"
LOG = "/opt/maiga/logs/brain.log"
LANGS = {"en": "English", "nl": "Dutch", "fr": "French", "es": "Spanish", "pt": "Portuguese", "de": "German",
         "tr": "Turkish", "id": "Indonesian", "vi": "Vietnamese", "ar": "Arabic"}
SYSTEM = ("You are The Brain, the friendly AI of geopolcoins.xyz, a free crypto-safety education site around the satirical "
          "meme coin $MAIGA. Answer in {lang}, in at most 80 words, plainly and kindly. Use the site notes when they help and "
          "mention the page path (like /radar.html) if useful. Rules: education only; never predict prices; never tell anyone to "
          "buy, sell or hold anything; never ask for or accept wallet keys or seed phrases; for a specific token say to check it "
          "with the free Token Checkup at /hq.html#checkup; if you are not sure, say so. Always end with: Entertainment only, NFA.")
WORD = re.compile(r"[a-zà-ÿ0-9]{3,}")
KB, KB_AT = [], 0.0


def log(s):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + s + "\n")


def rpc(fn, body):
    req = urllib.request.Request(SB + fn, json.dumps(body).encode(), {"apikey": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read() or "null")


def en(x):
    return x.get("en", "") if isinstance(x, dict) else str(x or "")


def load_kb():
    global KB, KB_AT
    if KB and time.time() - KB_AT < 6 * 3600:
        return
    try:
        os.makedirs(os.path.dirname(KB_FILE), exist_ok=True)
        req = urllib.request.Request(KB_URL, headers={"User-Agent": "geopolcoins-brain/1.0"})
        raw = urllib.request.urlopen(req, timeout=30).read()
        open(KB_FILE, "wb").write(raw)
    except Exception:
        raw = open(KB_FILE, "rb").read() if os.path.exists(KB_FILE) else b'{"topics":[],"pages":[]}'
    j = json.loads(raw); docs = []
    for t in j.get("topics", []):
        steps = t.get("steps"); steps = steps.get("en", []) if isinstance(steps, dict) else []
        body = f"{en(t.get('title'))} ({t.get('url', '')}): {en(t.get('what'))} Steps: {'; '.join(steps)}"
        docs.append((set(WORD.findall((t.get("kw", "") + " " + body).lower())), body[:600]))
    for p in j.get("pages", []):
        body = f"{p.get('title', '')} (/{p.get('url', '')}): {p.get('desc', '')}"
        docs.append((set(WORD.findall((body + " " + p.get("text", "")).lower())), body[:400]))
    KB, KB_AT = docs, time.time()


def context(q):
    words = set(WORD.findall(q.lower()))
    scored = sorted(KB, key=lambda d: -len(words & d[0]))
    return "\n".join("- " + d[1] for d in scored[:3] if words & d[0])


OUTLINK = re.compile(r"(https?://(?!geopolcoins\.xyz)\S+|www\.\S+)", re.I)
BAD = re.compile(r"(seed\s*phrase|private\s*key).{0,30}(send|share|give|enter|type)|guaranteed|will (moon|pump|go up)|buy now", re.I)


def answer(item):
    lang = LANGS.get(item.get("lang", "en"), "English")
    q = item["q"][:300]
    ctx = context(q)
    prompt = (SYSTEM.format(lang=lang) + ("\n\nSite notes:\n" + ctx if ctx else "") +
              "\n\nVisitor question: " + json.dumps(q, ensure_ascii=False) + "\n\nThe Brain:")
    body = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.3, "num_predict": 170}}
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=150) as r:
        a = json.loads(r.read()).get("response", "").strip()
    a = OUTLINK.sub("", a)
    if not a or BAD.search(a):
        return ""
    if "NFA" not in a:
        a += " Entertainment only, NFA."
    return a[:1500]


def main():
    global TOKEN
    TOKEN = open("/opt/maiga/secret/server-token").read().strip()
    log("braind start")
    while True:
        try:
            load_kb()
            items = rpc("server_ask_pull", {"p_token": TOKEN}) or []
            for it in items:
                t0 = time.time()
                try:
                    a = answer(it)
                except Exception as e:
                    a = ""; log("ai error " + type(e).__name__)
                rpc("server_ask_answer", {"p_token": TOKEN, "p_id": it["id"], "p_answer": a})
                log(f"#{it['id']} {it.get('lang')} {'ok' if a else 'failed'} {time.time() - t0:.1f}s")
            time.sleep(2 if items else 3)
        except Exception as e:
            log("error " + type(e).__name__); time.sleep(10)


if __name__ == "__main__":
    main()
