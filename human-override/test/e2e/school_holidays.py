"""School holidays in the schedule: 'skip' and 'only' modes, region picker, holidays never come from the online list.
Run: python3 human-override/test/e2e/school_holidays.py"""
import asyncio, datetime, json, os
from playwright.async_api import async_playwright
from common import start, Checks, opens as _opens
PAGE = '<html><body><h1>AI SITE</h1></body></html>'
EXT = os.path.join(os.path.dirname(__file__), '..', '..', 'extension')
ALL = [0, 1, 2, 3, 4, 5, 6]

async def main():
    today = datetime.date.today().isoformat()
    regions = json.load(open(os.path.join(EXT, 'lists.json')))['holidays']['regions']
    hol_today = [k for k, v in regions.items() if any(a <= today <= b for a, b in v)]
    free = next(k for k in regions if k not in hol_today)   # a region with school today
    # a tampered online list that marks every day as a holiday everywhere
    evil = json.load(open(os.path.join(EXT, 'lists.json')))
    evil['holidays'] = {'regions': {k: [['2000-01-01', '2099-12-31']] for k in regions}}
    async def route_list(r): await r.fulfill(status=200, content_type='application/json', body=json.dumps(evil))
    async with async_playwright() as p:
        ctx, sw, eid = await start(p, 'holidays', [('https://geopolcoins.xyz/human-override/lists.json', route_list),
                                                   ('https://**/*', lambda r: r.fulfill(status=200, content_type='text/html', body=PAGE))])
        check = Checks(); opens = lambda url: _opens(ctx, url)
        pop = await ctx.new_page(); await pop.set_viewport_size({'width': 380, 'height': 1700})
        await pop.goto(f'chrome-extension://{eid}/popup.html'); await asyncio.sleep(0.8)
        send = lambda m: pop.evaluate('m => new Promise(r => chrome.runtime.sendMessage(m, r))', m)
        await sw.evaluate('refreshList()'); await asyncio.sleep(1)
        whole = {'on': True, 'days': ALL, 'from': '00:00', 'to': '00:00'}
        r = await send({'t': 'set', 'sched': dict(whole, hol='skip', region=free)}); await asyncio.sleep(1)
        check(r.get('ok') and not await opens('https://chatgpt.com/'), f'skip, {free} has school today: blocked (tampered online list ignored)')
        r = await send({'t': 'set', 'sched': dict(whole, hol='only', region=free)}); await asyncio.sleep(1)
        check(await opens('https://chatgpt.com/'), 'only during holidays, school day: AI allowed')
        if hol_today:
            r = await send({'t': 'set', 'sched': dict(whole, hol='skip', region=hol_today[0])}); await asyncio.sleep(1)
            check(await opens('https://chatgpt.com/'), f'skip, {hol_today[0]} has a holiday today: AI allowed')
        r = await send({'t': 'set', 'sched': dict(whole, hol='evil', region='XX-YY')}); await asyncio.sleep(1)
        s = await send({'t': 'state'})
        check(s['sched']['hol'] == 'off' and s['sched']['region'] == 'BE-NL', 'bad values fall back to off / BE-NL')
        check(not await opens('https://chatgpt.com/'), 'hol off: blocked as usual')
        await pop.reload(); await asyncio.sleep(0.8)
        opts = await pop.locator('#scHol option').all_inner_texts()
        check(len(opts) == 3, 'popup shows 3 holiday choices: ' + str(opts))
        await pop.select_option('#scHol', 'skip'); await asyncio.sleep(0.2)
        check(await pop.is_visible('#scReg') and await pop.locator('#scReg option').count() == 8, 'region picker appears with 8 regions')
        await ctx.close()
    check.done()

asyncio.run(main())
