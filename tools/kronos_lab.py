#!/usr/bin/env python3
"""Build data/kronos-lab.json for kronos.html (Kronos Lab).

What it does (runs in GitHub Actions, see .github/workflows/kronos-lab.yml):
1. Downloads public 1-hour candles for BTC, ETH and SOL (no keys, read-only).
2. Picks moments in the PAST. For each moment it gives Kronos-small only the
   candles before that moment and asks for the next 24 hours, several times
   (several "paths", the spread shows how unsure the model is).
3. Compares with what really happened and with a "price stays the same" guess.

Only finished history is written. The newest moment always ends before the
data was downloaded, so the page never shows a forecast of the future.
Educational only: no signals, no advice.

Kronos: https://github.com/shiyu-coder/Kronos (MIT, Shi Yu et al.).
Usage: python3 tools/kronos_lab.py --kronos-dir /path/to/Kronos [--out data/kronos-lab.json]
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import time
import urllib.request

ASSETS = [("BTC", "BTCUSDT", "BTC-USD"), ("ETH", "ETHUSDT", "ETH-USD"), ("SOL", "SOLUSDT", "SOL-USD")]
CONTEXT = 400      # candles Kronos sees (max 512 for Kronos-small)
SHOW = 72          # candles of history shown on the page
HORIZON = 24       # hours forecast
MOMENTS = 30       # moments per asset
DAYS = 90          # spread moments over the last DAYS days
PATHS = 8          # forecast paths per moment
UA = {"User-Agent": "geopolcoins-kronos-lab/1.0 (educational, read-only)"}


def get_json(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001 - retry any network error
            if attempt == 3:
                raise
            print(f"  retry after {e}", file=sys.stderr)
            time.sleep(2 + attempt * 3)


def candles_binance(symbol, need):
    """Public market-data mirror of Binance (no account, no keys)."""
    out, end = [], None
    while len(out) < need:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1h&limit=1000"
        if end:
            url += f"&endTime={end}"
        rows = get_json(url)
        if not rows:
            break
        out = [[r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in rows] + out
        end = rows[0][0] - 1
    return out


def candles_coinbase(product, need):
    """Fallback: Coinbase Exchange public candles (300 per call)."""
    out, end = [], int(time.time()) // 3600 * 3600
    while len(out) < need:
        start = end - 300 * 3600
        url = (f"https://api.exchange.coinbase.com/products/{product}/candles?granularity=3600"
               f"&start={dt.datetime.utcfromtimestamp(start).isoformat()}Z&end={dt.datetime.utcfromtimestamp(end).isoformat()}Z")
        rows = get_json(url)  # [time, low, high, open, close, volume], newest first
        if not rows:
            break
        out = [[r[0], r[3], r[2], r[1], r[4], r[5]] for r in sorted(rows)] + out
        end = start
        time.sleep(0.4)
    return out


def load_candles(binance_sym, cb_product, need):
    try:
        rows, src = candles_binance(binance_sym, need), "Binance public market data (data-api.binance.vision)"
    except Exception as e:  # noqa: BLE001
        print(f"  Binance mirror failed ({e}), using Coinbase", file=sys.stderr)
        rows, src = candles_coinbase(cb_product, need), "Coinbase Exchange public candles"
    seen, clean = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            clean.append(r)
    clean.sort()
    # drop the candle that is still open
    now = int(time.time())
    clean = [r for r in clean if r[0] + 3600 <= now]
    return clean, src


def rnd(x):
    """Keep 5 significant digits so the JSON stays small."""
    if x == 0 or not math.isfinite(x):
        return 0
    return round(x, max(0, 4 - int(math.floor(math.log10(abs(x))))))


def pick_cuts(n):
    """Indexes where a forecast starts. Each needs CONTEXT before and HORIZON after."""
    last = n - HORIZON
    first = max(CONTEXT, last - DAYS * 24)
    step = (last - first) / (MOMENTS - 1)
    return sorted({int(round(first + i * step)) for i in range(MOMENTS)})


def build(kronos_dir, out_path):
    sys.path.insert(0, kronos_dir)
    import numpy as np
    import pandas as pd
    import torch
    from model import Kronos, KronosPredictor, KronosTokenizer  # noqa: E402

    torch.manual_seed(42)
    np.random.seed(42)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    tok = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
    pred = KronosPredictor(model, tok, device="cpu", max_context=512)

    need = CONTEXT + DAYS * 24 + HORIZON + 48
    result = {"assets": {}, "summary": {}}
    sources = set()
    for name, bsym, cbp in ASSETS:
        rows, src = load_candles(bsym, cbp, need)
        sources.add(src)
        print(f"{name}: {len(rows)} candles from {src}")
        df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
        df["timestamps"] = pd.to_datetime(df["ts"], unit="s")
        cols = ["open", "high", "low", "close", "volume"]
        moments = []
        for cut in pick_cuts(len(df)):
            x = df.iloc[cut - CONTEXT:cut]
            y = df.iloc[cut:cut + HORIZON]
            out = pred.predict_batch(
                df_list=[x[cols].reset_index(drop=True)] * PATHS,
                x_timestamp_list=[x["timestamps"].reset_index(drop=True)] * PATHS,
                y_timestamp_list=[y["timestamps"].reset_index(drop=True)] * PATHS,
                pred_len=HORIZON, T=1.0, top_p=0.9, sample_count=1, verbose=False)
            paths = np.array([o["close"].to_numpy() for o in out])  # PATHS x HORIZON
            mid = np.median(paths, axis=0)
            lo, hi = paths.min(axis=0), paths.max(axis=0)
            now = float(x["close"].iloc[-1])
            real = y["close"].to_numpy()
            up_pred, up_real = mid[-1] > now, real[-1] > now
            moments.append({
                "t": dt.datetime.utcfromtimestamp(int(df["ts"].iloc[cut])).strftime("%Y-%m-%dT%H:00Z"),
                "hist": [rnd(v) for v in x["close"].to_numpy()[-SHOW:]],
                "real": [rnd(v) for v in real],
                "mid": [rnd(v) for v in mid],
                "lo": [rnd(v) for v in lo],
                "hi": [rnd(v) for v in hi],
                "pred_up": bool(up_pred), "real_up": bool(up_real), "hit": bool(up_pred == up_real),
                "inside": bool(lo[-1] <= real[-1] <= hi[-1]),
                "err": round(abs(mid[-1] - real[-1]) / real[-1] * 100, 2),
                "naive_err": round(abs(now - real[-1]) / real[-1] * 100, 2),
                "spread": round((hi[-1] - lo[-1]) / now * 100, 2),
            })
            print(f"  {moments[-1]['t']} hit={moments[-1]['hit']} err={moments[-1]['err']}%")
        result["assets"][name] = moments
        result["summary"][name] = summarize(moments)
    allm = [m for ms in result["assets"].values() for m in ms]
    result["summary"]["ALL"] = summarize(allm)
    result["meta"] = {
        "model": "Kronos-small (NeoQuasar/Kronos-small + Kronos-Tokenizer-base)",
        "code": "https://github.com/shiyu-coder/Kronos",
        "license": "MIT",
        "interval": "1h", "context": CONTEXT, "horizon": HORIZON, "paths": PATHS,
        "moments_per_asset": MOMENTS, "days": DAYS,
        "source": " / ".join(sorted(sources)),
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "note": "Past moments only. Educational. Not a signal, not financial advice.",
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, separators=(",", ":"))
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes)")
    print(json.dumps(result["summary"], indent=1))


def summarize(ms):
    n = len(ms)
    if not n:
        return {}
    return {
        "n": n,
        "hits": sum(m["hit"] for m in ms),
        "inside": sum(m["inside"] for m in ms),
        "err": round(sum(m["err"] for m in ms) / n, 2),
        "naive_err": round(sum(m["naive_err"] for m in ms) / n, 2),
        "up_share": round(sum(m["real_up"] for m in ms) / n * 100),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kronos-dir", required=True)
    ap.add_argument("--out", default="data/kronos-lab.json")
    a = ap.parse_args()
    build(a.kronos_dir, a.out)
