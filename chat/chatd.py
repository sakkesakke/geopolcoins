#!/usr/bin/env python3
"""Live chat filter for geopolcoins.xyz (runs on the Oracle server, owner chose option 3).

Every visitor message passes here before anyone can see it:
  1. rules: links, domains, @handles, wallet/contract addresses, phone numbers are removed;
     messages with scam phrases or swearing are blocked;
  2. a small local AI model (Ollama + Qwen2.5 1.5B, Apache-2.0) answers SAFE or BLOCK for scams,
     harassment, hate, sexual content, personal data and financial promises.
If the AI is not running yet, only the rules apply and anything doubtful is blocked.
Only the server (with its own token, stored on this machine only) can publish messages.
"""
import json, os, re, time, urllib.request

SB = "https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/"
KEY = "sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN"   # public website key, not a secret
TOKEN = ""
OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:1.5b"
LOG = "/opt/maiga/logs/chat.log"

URL = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+(\.[\w-]+)*\.(com|net|org|io|xyz|app|me|gg|co|ly|link|site|online|fun|top|ru|cn|info|biz|club|live|pro|finance|exchange|money|cash|sol|eth|ton|bot|to|cc|tk|ml|ga|cf|gq|tv|in|us|uk|eu|de|fr|nl|be|es|pt|br|tr|id|vn|ae|ma)\b\S*|\bt\.me/\S*|\bdiscord(\.gg|app\.com)?/\S*)", re.I)
HANDLE = re.compile(r"(?<!\w)@\w{2,}")
ADDR = re.compile(r"\b(0x[a-fA-F0-9]{20,}|[1-9A-HJ-NP-Za-km-z]{32,44})\b")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
SCAM = re.compile(r"(seed\s*phrase|private\s*key|recovery\s*phrase|secret\s*phrase|dm\s*me|inbox\s*me|message\s*me|contact\s*me|"
                  r"whats\s*app|telegram|signal\s*group|airdrop|giveaway|claim\s*(now|your|free)|free\s*(sol|eth|btc|usdt|crypto|tokens?)|"
                  r"double\s*your|guaranteed|100x|1000x|send\s*\d|presale|pre-sale|wallet\s*connect|connect\s*your\s*wallet|"
                  r"support\s*team|validate\s*your|recover\s*your|investment\s*plan|profit\s*daily|"
                  r"phrase\s*secr[eè]te|cl[ée]\s*priv[ée]e|frase\s*semilla|zinnen?\s*herstel|herstelzin)", re.I)
SWEAR = re.compile(r"\b(fuck\w*|shit\w*|bitch\w*|cunt\w*|nigg\w*|fag\w*|retard\w*|whore\w*|slut\w*|kanker\w*|kut\w*|hoer\w*|"
                   r"tering\w*|klootzak\w*|putain|salope|connard\w*|encul\w*|merde|pute|puta\w*|mierda|cabr[oó]n\w*|gilipollas|"
                   r"caralho|porra|scheiße|scheisse|arschloch|hurensohn|fotze|orospu\w*|siktir\w*|amk|anjing|bangsat|kontol|"
                   r"đụ|địt|lồn|كس|شرموط\w*|زب)\b", re.I)
PROMPT = ("You moderate a public chat on a crypto-safety education website. Reply with exactly one word: SAFE or BLOCK.\n"
          "BLOCK if the message: promotes or asks to buy/sell a token, promises profit, asks anyone to contact them or move to "
          "another app, asks for wallets, keys or seed phrases, contains personal data, harasses or insults someone, is hateful, "
          "sexual, violent, or spam. Otherwise SAFE. Any language.\nMessage: ")


def rpc(fn, body):
    req = urllib.request.Request(SB + fn, json.dumps(body).encode(), {"apikey": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read() or "null")


def ai(text):
    """True = safe, False = block, None = AI not available."""
    try:
        body = {"model": MODEL, "prompt": PROMPT + json.dumps(text, ensure_ascii=False), "stream": False,
                "options": {"temperature": 0, "num_predict": 3}}
        req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=40) as r:
            ans = json.loads(r.read()).get("response", "").strip().upper()
        return ans.startswith("SAFE")
    except Exception:
        return None


def clean(text):
    t = URL.sub("[link removed]", text)
    t = HANDLE.sub("[removed]", t)
    t = ADDR.sub("[address removed]", t)
    t = PHONE.sub("[removed]", t)
    return re.sub(r"\s+", " ", t).strip()[:200]


def judge(m):
    raw = m["body"]
    if SCAM.search(raw) or SWEAR.search(raw) or SWEAR.search(m["name"]):
        return False, "", "rules"
    t = clean(raw)
    if not re.search(r"[^\W_]", t.replace("link removed", "").replace("address removed", "").replace("removed", "")):
        return False, "", "empty"
    v = ai(t)
    if v is None:   # no AI yet: only plain short messages without anything removed
        ok = t == raw and len(t) <= 120
        return ok, t, "rules-only"
    return v, t, "ai"


def log(s):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + s + "\n")


def main():
    global TOKEN
    TOKEN = open("/opt/maiga/secret/server-token").read().strip()
    log("chatd start")
    idle = 0
    while True:
        try:
            items = rpc("server_chat_pull", {"p_token": TOKEN}) or []
            if items:
                out = []
                for m in items:
                    ok, body, how = judge(m)
                    out.append({"id": m["id"], "ok": ok, "body": body})
                    log(f"#{m['id']} {how} {'ok' if ok else 'blocked'}")
                rpc("server_chat_verdict", {"p_token": TOKEN, "p_items": out})
                idle = 0
            else:
                idle += 1
        except Exception as e:
            log("error " + type(e).__name__)
            time.sleep(10)
        time.sleep(2 if idle < 30 else 4)


if __name__ == "__main__":
    main()
