"""Mindveto family filter: adult sites and SafeSearch are off by default, can be switched on, keep working when AI is
allowed, respect the user's allow list, do not break AI blocking, and never end in a redirect loop.
Run: python3 human-override/test/e2e/family_filter.py"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import start, Checks, opens
from playwright.async_api import async_playwright

import http.server, threading
HDR = {}


class Echo(http.server.BaseHTTPRequestHandler):   # stands in for www.youtube.com, records the request headers the browser really sent
    def do_GET(self):
        HDR.update({k.lower(): v for k, v in self.headers.items()}); self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self, *a): pass


async def fake(route):
    if ':8797/' in route.request.url or route.request.url.startswith('chrome-extension://'): return await route.continue_()
    await route.fulfill(status=200, content_type='text/html', body='<h1>ok</h1>')


async def final_url(ctx, url):
    pg = await ctx.new_page(); err = None
    try: await pg.goto(url, timeout=8000)
    except Exception as e: err = str(e)
    await asyncio.sleep(0.4); u = pg.url; await pg.close()
    return u, err


async def main():
    ok = Checks()
    srv = http.server.HTTPServer(('127.0.0.1', 8797), Echo); threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        ctx, sw, ext = await start(p, 'family', routes=[('**/*', fake)], args=['--host-resolver-rules=MAP www.youtube.com 127.0.0.1'])
        pop = await ctx.new_page(); await pop.goto(f'chrome-extension://{ext}/popup.html')
        send = lambda m: pop.evaluate('(m) => new Promise(r => chrome.runtime.sendMessage(m, r))', m)
        base = {'chat': True, 'search': True, 'image': True, 'media': True, 'writing': True, 'coding': True, 'record': True, 'social': False}
        ok(await opens(ctx, 'https://www.pornhub.com/'), 'adult sites are NOT blocked by default')
        u, _ = await final_url(ctx, 'https://www.google.com/search?q=test')
        ok('safe=active' not in u, 'SafeSearch is NOT forced by default')
        ok(await opens(ctx, 'https://www.croxyproxy.com/'), 'proxy sites are NOT blocked by default')
        # anti-bypass alone (without the adult list)
        await send({'t': 'set', 'cats': dict(base, bypass=True)}); await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://www.croxyproxy.com/'), 'web proxy blocked')
        ok(not await opens(ctx, 'https://nordvpn.com/download/'), 'VPN service blocked')
        ok(not await opens(ctx, 'https://dns.google/resolve?name=x'), 'secure-DNS address blocked')
        ok(await opens(ctx, 'https://www.pornhub.com/'), 'anti-bypass alone does not switch on the adult list')
        ok(await opens(ctx, 'https://proton.me/mail'), 'Proton Mail still opens (only Proton VPN is listed)')
        pg = await ctx.new_page()
        try: await pg.goto('https://www.croxyproxy.com/', timeout=8000)
        except Exception: pass
        await pg.locator('#p', has_text='VPN').wait_for(timeout=5000); txt = await pg.inner_text('body'); await pg.close()
        ok('vpn, proxy' in txt.lower(), 'blocked page explains the anti-bypass filter')
        # gambling + dating (each its own switch)
        ok(await opens(ctx, 'https://www.bet365.com/'), 'gambling NOT blocked by default')
        await send({'t': 'set', 'cats': dict(base, gamble=True)}); await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://www.bet365.com/'), 'gambling site blocked')
        ok(not await opens(ctx, 'https://sports.unibet.be/'), 'gambling sub-domain blocked')
        ok(await opens(ctx, 'https://tinder.com/'), 'gambling switch does not block dating')
        ok(await opens(ctx, 'https://sporza.be/nl/'), 'sport news still opens')
        await send({'t': 'set', 'cats': dict(base, dating=True)}); await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://tinder.com/'), 'dating app blocked')
        ok(not await opens(ctx, 'https://chatroulette.com/'), 'random video chat blocked')
        ok(await opens(ctx, 'https://www.bet365.com/'), 'gambling open again after switching it off')
        pg = await ctx.new_page()
        try: await pg.goto('https://tinder.com/', timeout=8000)
        except Exception: pass
        await pg.locator('#p', has_text='dating').wait_for(timeout=5000); await pg.close()
        ok(True, 'blocked page names dating')
        r = await send({'t': 'set', 'cats': dict(base, adult=True, safe=True)}); ok(r and r.get('ok'), 'family filter switched on')
        await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://www.pornhub.com/'), 'adult site blocked (www.)')
        ok(not await opens(ctx, 'https://xvideos.com/video123'), 'adult site blocked (bare domain)')
        ok(await opens(ctx, 'https://en.wikipedia.org/wiki/Test'), 'normal site still opens')
        ok(not await opens(ctx, 'https://chatgpt.com/'), 'AI still blocked')
        pg = await ctx.new_page()
        try: await pg.goto('https://www.pornhub.com/', timeout=8000)
        except Exception: pass
        await pg.locator('#p', has_text='family filter').wait_for(timeout=5000); txt = await pg.inner_text('body'); await pg.close()
        ok('family filter' in txt.lower() and 'no ai' not in txt.lower(), 'blocked page says family filter, not AI')
        u, err = await final_url(ctx, 'https://www.google.com/search?q=test')
        ok('safe=active' in u and not err, f'Google SafeSearch forced without a loop ({u})')
        u, err = await final_url(ctx, 'https://www.google.be/search?q=test&safe=off')
        ok('safe=active' in u and 'safe=off' not in u and not err, 'safe=off is overridden')
        u, err = await final_url(ctx, 'https://www.bing.com/search?q=test')
        ok('adlt=strict' in u and not err, 'Bing strict forced')
        u, err = await final_url(ctx, 'https://duckduckgo.com/?q=test')
        ok('kp=1' in u and not err, 'DuckDuckGo strict forced')
        await final_url(ctx, 'http://www.youtube.com:8797/watch?v=x')   # mapped to a local server that records the headers
        ok(HDR.get('youtube-restrict') == 'Strict', 'YouTube-Restrict: Strict header sent')
        ok(not await opens(ctx, 'https://www.google.com/search?q=x&udm=50'), 'Google AI Mode still blocked with SafeSearch on')
        # AI allowed: the family filter keeps working
        r = await send({'t': 'set', 'on': False}); await asyncio.sleep(1.5)
        ok(await opens(ctx, 'https://chatgpt.com/'), 'AI allowed after switching AI off')
        ok(not await opens(ctx, 'https://www.pornhub.com/'), 'adult site still blocked while AI is allowed')
        u, _ = await final_url(ctx, 'https://www.google.com/search?q=test')
        ok('safe=active' in u, 'SafeSearch still forced while AI is allowed')
        # the user's allow list wins
        await send({'t': 'set', 'on': True, 'allow': ['pornhub.com']}); await asyncio.sleep(1.5)
        ok(await opens(ctx, 'https://www.pornhub.com/'), 'allow list beats the family filter')
        # switching off again
        await send({'t': 'set', 'allow': [], 'cats': base}); await asyncio.sleep(1.5)
        ok(await opens(ctx, 'https://www.pornhub.com/'), 'adult site opens after switching the filter off')
        u, _ = await final_url(ctx, 'https://www.google.com/search?q=test')
        ok('safe=active' not in u, 'SafeSearch no longer forced after switching off')
        log = await sw.evaluate("chrome.storage.local.get('log').then(s => (s.log || []).map(e => e.k))")
        ok('famon' in log and 'famoff' in log, 'tamper log records family filter on/off')
        ok(await opens(ctx, 'https://www.croxyproxy.com/'), 'proxy site opens again after switching everything off')
        await ctx.close()
    ok.done()

asyncio.run(main())
