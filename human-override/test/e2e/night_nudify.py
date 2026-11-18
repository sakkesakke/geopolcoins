"""Mindveto 1.7.0: the night-mode button sets the schedule to every night 22:00-07:00, and the family filter (adult
switch) also blocks AI 'undress' / fake-nude sites.
Run: python3 human-override/test/e2e/night_nudify.py"""
import asyncio, datetime, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import start, Checks, opens
from playwright.async_api import async_playwright


async def fake(route):
    if route.request.url.startswith('chrome-extension://'): return await route.continue_()
    await route.fulfill(status=200, content_type='text/html', body='<h1>ok</h1>')


async def main():
    ok = Checks()
    async with async_playwright() as p:
        ctx, sw, ext = await start(p, 'night', routes=[('**/*', fake)])
        pop = await ctx.new_page(); await pop.goto(f'chrome-extension://{ext}/popup.html')
        send = lambda m: pop.evaluate('(m) => new Promise(r => chrome.runtime.sendMessage(m, r))', m)
        label = await pop.locator('#scNight').text_content()
        ok(label and '22:00' in label, 'night-mode button is shown with its times')
        await pop.locator('#scNight').click(); await asyncio.sleep(1)
        st = await send({'t': 'state'})
        sc = st['sched']
        ok(sc['on'] and sc['from'] == '22:00' and sc['to'] == '07:00' and sorted(sc['days']) == list(range(7)), 'one tap sets the schedule to every night 22:00-07:00')
        h = datetime.datetime.now().hour
        night = h >= 22 or h < 7
        ok(st['active'] == night, f'AI blocking follows the night window (hour {h}, blocking={st["active"]})')
        ok(await opens(ctx, 'https://undress.app/'), 'fake-nude site is NOT blocked while the family filter is off')
        cats = dict(st['cats']); cats['adult'] = True
        r = await send({'t': 'set', 'cats': cats}); await asyncio.sleep(1.5)
        ok(r and r.get('ok'), 'family filter (adult) switched on')
        for u in ('https://undress.app/', 'https://clothoff.io/', 'https://www.nudify.online/'):
            ok(not await opens(ctx, u), f'blocked with the family filter: {u}')
        await ctx.close()
    ok.done()

asyncio.run(main())
