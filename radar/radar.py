#!/usr/bin/env python3
"""Rug Radar 24/7 for geopolcoins.xyz (runs every 5 minutes on the Oracle server).

Watches new and trending Solana pools through the free public GeckoTerminal API, keeps each pool for
48 hours and notices when its liquidity is pulled. Only totals go to the website (never a token name,
never a signal): pools scanned, share with each red flag, liquidity pulls per hour.
Red-flag rules are the same as on radar.html.
"""
import json, os, sqlite3, time, urllib.request

GT = "https://api.geckoterminal.com/api/v2/networks/solana"
SB = "https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/"
KEY = "sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN"   # public website key, not a secret
DB = "/opt/maiga/radar/state.db"
KEEP = 48 * 3600


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "geopolcoins-radar/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def num(x):
    try:
        v = float(x); return v if v == v else None
    except (TypeError, ValueError):
        return None


def flags_of(a):
    f = []
    liq = num(a.get("reserve_in_usd"))
    t = (a.get("transactions") or {}).get("h24") or {}
    b, s = num(t.get("buys")) or 0, num(t.get("sells")) or 0
    vol = num((a.get("volume_usd") or {}).get("h24"))
    ch = num((a.get("price_change_percentage") or {}).get("h24"))
    if liq is not None and liq < 10000: f.append("thin")
    if b >= 10 and s == 0: f.append("nosell")
    if liq and vol is not None and vol > liq * 50: f.append("vol")
    if ch is not None and ch >= 300: f.append("pump")
    if ch is not None and ch <= -60: f.append("crash")
    return f


def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript("""
    create table if not exists pools(addr text primary key, first real, last_check real, src text,
        liq_max real, liq_now real, flags text, pulled real);
    create table if not exists events(at real, kind text);
    """)
    return c


def seen(c, a, src, now):
    addr = str(a.get("address") or "")[:64]
    if not addr: return
    liq = num(a.get("reserve_in_usd")) or 0.0
    fl = ",".join(flags_of(a))
    r = c.execute("select liq_max, flags, pulled from pools where addr=?", (addr,)).fetchone()
    if r is None:
        c.execute("insert into pools values(?,?,?,?,?,?,?,null)", (addr, now, now, src, liq, liq, fl))
        c.execute("insert into events values(?,?)", (now, "new" if src == "new" else "trend"))
        return
    mx, old, pulled = r
    allf = ",".join(sorted(set(filter(None, (old or "").split(",") + fl.split(",")))))
    mx = max(mx or 0, liq)
    c.execute("update pools set last_check=?, liq_max=?, liq_now=?, flags=? where addr=?", (now, mx, liq, allf, addr))
    if pulled is None and mx >= 5000 and liq < mx * 0.1:
        c.execute("update pools set pulled=? where addr=?", (now, addr))
        c.execute("insert into events values(?,?)", (now, "pulled"))


def scan(c, now):
    calls = 0
    for kind, pages in (("new_pools", 2), ("trending_pools", 2)):
        for p in range(1, pages + 1):
            try:
                for d in get(f"{GT}/{kind}?page={p}").get("data") or []:
                    seen(c, d.get("attributes") or {}, "new" if kind == "new_pools" else "trend", now)
            except Exception:
                pass
            calls += 1; time.sleep(2.2)
    # re-check older pools (oldest check first), 30 per call, max 8 calls per run
    rows = [r[0] for r in c.execute("select addr from pools where first > ? and pulled is null order by last_check limit 240", (now - KEEP,))]
    for i in range(0, len(rows), 30):
        try:
            j = get(f"{GT}/pools/multi/{','.join(rows[i:i + 30])}")
            for d in j.get("data") or []:
                seen(c, d.get("attributes") or {}, "recheck", now)
        except Exception:
            pass
        time.sleep(2.2)
    c.execute("delete from pools where first < ?", (now - KEEP - 3600,))
    c.execute("delete from events where at < ?", (now - 8 * 86400,))
    c.commit()


def stats(c, now):
    day = now - 86400
    rows = c.execute("select flags, pulled from pools where first > ?", (day,)).fetchall()
    n = len(rows)
    def pct(k): return round(100 * sum(1 for f, _ in rows if k in (f or "").split(",")) / n) if n else 0
    s = {"pools24": n, "new24": c.execute("select count(*) from events where kind='new' and at>?", (day,)).fetchone()[0],
         "pulled24": c.execute("select count(*) from events where kind='pulled' and at>?", (day,)).fetchone()[0],
         "pulled7d": c.execute("select count(*) from events where kind='pulled' and at>?", (now - 7 * 86400,)).fetchone()[0],
         "thin": pct("thin"), "nosell": pct("nosell"), "vol": pct("vol"), "pump": pct("pump"), "crash": pct("crash"),
         "any": round(100 * sum(1 for f, _ in rows if f) / n) if n else 0, "hours": []}
    for h in range(23, -1, -1):
        a, b = now - (h + 1) * 3600, now - h * 3600
        s["hours"].append([c.execute("select count(*) from events where kind in ('new','trend') and at>? and at<=?", (a, b)).fetchone()[0],
                           c.execute("select count(*) from events where kind='pulled' and at>? and at<=?", (a, b)).fetchone()[0]])
    s["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    return s


def push(s):
    token = open("/opt/maiga/secret/server-token").read().strip()
    req = urllib.request.Request(SB + "server_radar_push", json.dumps({"p_token": token, "p_stats": s}).encode(),
                                 {"apikey": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode()


if __name__ == "__main__":
    import fcntl
    lock = open("/opt/maiga/radar/.lock" if os.path.isdir("/opt/maiga/radar") else "/tmp/maiga-radar.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit(0)
    now = time.time(); c = db(); scan(c, now); s = stats(c, now)
    print(time.strftime("%FT%TZ", time.gmtime()), "pools24", s["pools24"], "pulled24", s["pulled24"], "push", push(s))
