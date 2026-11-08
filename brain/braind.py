#!/usr/bin/env python3
"""The Brain: answers visitor questions on geopolcoins.xyz with a local AI model (Ollama + Qwen2.5 3B, Apache-2.0).

Strictly grounded: the prompt holds only our own notes (brain/facts.json + the site's guide-kb.json). The model
writes in English (its strongest language) and, for other languages, translates its own checked answer.
Every answer passes checks (no repetition, no outside links, no price/buy talk, nothing negative about $MAIGA);
if a check fails the visitor gets "no answer" instead of a bad one. Questions are deleted after 1 day.
"""
import json, os, re, time, urllib.request

SB = "https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/"
KEY = "sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN"   # public website key, not a secret
OLLAMA = "http://127.0.0.1:11434/api/"
MODEL = "qwen2.5:3b"
HERE = os.path.dirname(os.path.abspath(__file__))
KB_URL = "https://geopolcoins.xyz/guide-kb.json"
KB_FILE = "/opt/maiga/brain/kb.json"
LOG = "/opt/maiga/logs/brain.log"
LANGS = {"en": "English", "nl": "Dutch", "fr": "French", "es": "Spanish", "pt": "Portuguese", "de": "German",
         "tr": "Turkish", "id": "Indonesian", "vi": "Vietnamese", "ar": "Arabic"}
WORDRE = re.compile(r"[a-zà-ÿ0-9$]{3,}")
STOP = set("the and what how who why when where which can does did for are you your with this that from have has was were not but all any out get got its it's about into than then them they their there here is a an to of in on at be or do i me my we our us one more most very just also some".split())
class _W:
    @staticmethod
    def findall(t): return [w for w in WORDRE.findall(t) if w not in STOP]
WORD = _W()
FACTS = [(set(WORD.findall(k.lower())) | set(WORD.findall(v.lower())), set(WORD.findall(k.lower())), v)
         for k, v in json.load(open(os.path.join(HERE, "facts.json")))]
KB, KB_AT = [], 0.0
SYSTEM = ("You are The Brain, the friendly AI of geopolcoins.xyz (a free crypto-safety site). Answer the visitor's question "
          "in clear, simple English in at most 70 words, using ONLY the facts in NOTES. If the notes do not answer it, say: "
          "\"I don't know that one yet. Try the Token Checkup at /hq.html#checkup or ask in the live chat.\" Never predict prices, "
          "never tell anyone to buy, sell or hold, never ask for keys or seed phrases. No lists longer than 3 items. Do not repeat yourself.")


def log(s):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + s + "\n")


def post(url, body, timeout):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "apikey": KEY})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or "null")


def rpc(fn, body):
    return post(SB + fn, body, 20)


def gen(prompt, n=160):
    return post(OLLAMA + "generate", {"model": MODEL, "prompt": prompt, "stream": False,
                                       "options": {"temperature": 0.2, "num_predict": n, "repeat_penalty": 1.25}}, 240).get("response", "").strip()


def ensure_model():
    try:
        tags = json.loads(urllib.request.urlopen(OLLAMA + "tags", timeout=10).read())
        if any(m.get("name", "").startswith(MODEL) for m in tags.get("models", [])):
            return True
        log("pulling " + MODEL)
        post(OLLAMA + "pull", {"model": MODEL, "stream": False}, 3600)
        log("pulled " + MODEL)
        return True
    except Exception as e:
        log("model not ready " + type(e).__name__)
        return False


def en(x):
    return x.get("en", "") if isinstance(x, dict) else str(x or "")


def load_kb():
    global KB, KB_AT
    if KB and time.time() - KB_AT < 6 * 3600:
        return
    try:
        os.makedirs(os.path.dirname(KB_FILE), exist_ok=True)
        raw = urllib.request.urlopen(urllib.request.Request(KB_URL, headers={"User-Agent": "geopolcoins-brain/2.0"}), timeout=30).read()
        open(KB_FILE, "wb").write(raw)
    except Exception:
        raw = open(KB_FILE, "rb").read() if os.path.exists(KB_FILE) else b'{"topics":[]}'
    docs = []
    for t in json.loads(raw).get("topics", []):
        body = f"{en(t.get('title'))} ({t.get('url', '')}): {en(t.get('what'))}"
        docs.append((set(WORD.findall((t.get("kw", "") + " " + body).lower())), body[:420]))
    KB, KB_AT = docs, time.time()


def notes(q):
    w = set(WORD.findall(q.lower()))
    f = sorted(FACTS, key=lambda d: -(3 * len(w & d[1]) + len(w & d[0])))
    k = sorted(KB, key=lambda d: -len(w & d[0]))
    out = [d[2] for d in f[:2] if w & d[0]] + [d[1] for d in k[:2] if len(w & d[0]) >= 2]
    return out


def english_query(q, lang):
    if lang == "en":
        return q
    return gen(f"Translate this {LANGS.get(lang, 'foreign')} question into English. Reply with the English question only.\n\n{q}", 60) or q


OUTLINK = re.compile(r"(https?://(?!geopolcoins\.xyz)\S+|www\.\S+)", re.I)
BAD = re.compile(r"(will|going to) (moon|pump|rise|go up|10x|100x)|guaranteed|you should (buy|sell|hold)|buy now|"
                 r"(send|share|give|enter|type)\s+(me|us)?\s*(your)?\s*(seed|private key)", re.I)
MAIGA_NEG = re.compile(r"maiga[^.]{0,60}(rug|scam|fraud|honeypot|ponzi)|(rug|scam|fraud|honeypot|ponzi)[^.]{0,40}\$?maiga", re.I)
MAIGA_OK = re.compile(r"\bnot\b|satiric|entertainment|meme coin|niet|pas |kein|no es|não", re.I)


def maiga_bad(a):
    return any(MAIGA_NEG.search(s) and not MAIGA_OK.search(s) for s in re.split(r"[.!?\n]+", a))


def repetitive(a):
    sents = [s.strip().lower() for s in re.split(r"[.!?\n]+", a) if len(s.strip()) > 12]
    if len(sents) != len(set(sents)):
        return True
    words = a.lower().split()
    tri = [" ".join(words[i:i + 3]) for i in range(len(words) - 2)]
    return len(tri) > 12 and len(set(tri)) < 0.8 * len(tri)


def check(a):
    a = OUTLINK.sub("", a).strip()
    if not a or len(a) < 20 or BAD.search(a) or maiga_bad(a) or repetitive(a):
        return ""
    return a


def answer(item):
    lang = item.get("lang", "en") if item.get("lang") in LANGS else "en"
    q = item["q"][:300]
    qe = english_query(q, lang)
    ns = notes(qe + " " + q)
    if not ns:
        a = "I don't know that one yet. Try the Token Checkup at /hq.html#checkup or ask in the live chat."
    else:
        a = check(gen(SYSTEM + "\n\nNOTES:\n" + "\n".join("- " + n for n in ns) + f"\n\nQUESTION: {qe}\n\nANSWER:"))
    if not a:
        return "", "check-en"
    if lang != "en":
        tr = gen(f"Translate this text into {LANGS[lang]}. Keep paths like /hq.html exactly as they are. Reply with the translation only.\n\n{a}", 220)
        tr = check(tr)
        if not tr:
            return "", "check-tr"
        a = tr
    return a.rstrip() + ("" if "NFA" in a else " (NFA)"), "ok"


def main():
    token = open("/opt/maiga/secret/server-token").read().strip()
    log("braind v2 start")
    ready = False
    while True:
        try:
            if not ready:
                ready = ensure_model()
                if not ready:
                    time.sleep(30); continue
            load_kb()
            items = rpc("server_ask_pull", {"p_token": token}) or []
            for it in items:
                t0 = time.time()
                try:
                    a, why = answer(it)
                except Exception as e:
                    a, why = "", "error " + type(e).__name__
                rpc("server_ask_answer", {"p_token": token, "p_id": it["id"], "p_answer": a})
                log(f"#{it['id']} {it.get('lang')} {why} {time.time() - t0:.0f}s")
            time.sleep(2 if items else 3)
        except Exception as e:
            log("error " + type(e).__name__); time.sleep(10)


if __name__ == "__main__":
    main()
