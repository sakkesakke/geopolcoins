"""Mindveto: the optional social media category is off by default, can be switched on,
is not forced on by exam mode, and is never part of the public network lists.
Run: python3 human-override/test/e2e/social_media.py"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import start, Checks, opens
from playwright.async_api import async_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


async def fake(route):
    await route.fulfill(status=200, content_type='text/html', body='<h1>ok</h1>')


async def main():
    ok = Checks()
    for f in ('hosts.txt', 'domains.txt', 'adblock.txt'):
        ok('tiktok.com' not in open(os.path.join(ROOT, f)).read(), f'{f} has no social media domains')
    async with async_playwright() as p:
        ctx, sw, ext = await start(p, 'social', routes=[('**/*', fake)])
        pop = await ctx.new_page(); await pop.goto(f'chrome-extension://{ext}/popup.html')
        setc = lambda social: pop.evaluate('(v) => new Promise(r => chrome.runtime.sendMessage({t: "set", cats: {chat:true,search:true,image:true,media:true,writing:true,coding:true,record:true,social:v}}, r))', social)
        ok(await opens(ctx, 'https://www.tiktok.com/'), 'social media is NOT blocked by default')
        ok(not await opens(ctx, 'https://chatgpt.com/'), 'AI is still blocked by default')
        st = await sw.evaluate("chrome.storage.local.get('cats').then(s => s.cats || null)")
        ok(st is None or st.get('social') is not True, 'stored default for social is off')
        # switch social on the way the popup does
        r = await setc(True); ok(r and r.get('ok'), 'popup message accepted')
        await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://www.tiktok.com/'), 'social media IS blocked after switching it on')
        # exam mode must not force social media on
        await sw.evaluate("chrome.storage.local.set({klass: {code:'ABCDEFGH'}, exam: {until: Date.now() + 600000}})")
        await setc(False)   # saving settings rebuilds the rules, now with exam mode on
        await asyncio.sleep(1.5)
        ok(await opens(ctx, 'https://www.instagram.com/'), 'exam mode does not block social media')
        ok(not await opens(ctx, 'https://chatgpt.com/'), 'exam mode still blocks AI')
        await ctx.close()
    ok.done()

asyncio.run(main())
