import asyncio, json, time, os
os.environ['PW_EXPERIMENTAL_SERVICE_WORKER_NETWORK_EVENTS'] = '1'   # lets the routes below also answer the extension's own requests
from playwright.async_api import async_playwright
from common import start, Checks, opens as _opens
PAGE = '<html><body><h1>AI SITE</h1></body></html>'
DB = {}   # fake server with the same rules as the SQL functions
async def api(route):
    u = route.request.url; b = json.loads(route.request.post_data or '{}'); out = None
    if u.endswith('exam_create'): DB['ABCD2345'] = {'key': 'a' * 64, 'until': 0}; out = {'code': 'ABCD2345', 'key': 'a' * 64}
    elif u.endswith('exam_set'):
        c = DB.get(b.get('p_code'))
        if not c or c['key'] != b.get('p_key'): out = {'err': 'bad'}
        else: c['until'] = time.time() + b['p_minutes'] * 60 if b['p_minutes'] else 0; out = {'ok': True, 'left': b['p_minutes'] * 60}
    elif u.endswith('exam_status'):
        c = DB.get(b.get('p_code')); out = -1 if not c else max(0, int(c['until'] - time.time()))
    await route.fulfill(status=200, content_type='application/json', body=json.dumps(out), headers={'access-control-allow-origin': '*', 'access-control-allow-headers': '*'})
async def main():
    async with async_playwright() as p:
        async def site(route):
            if route.request.method == 'OPTIONS': return await route.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST'})
            await route.fulfill(status=200, content_type='text/html', body=PAGE)
        async def sb(route):
            if route.request.method == 'OPTIONS': return await route.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST'})
            await api(route)
        ctx, sw, eid = await start(p, 'exam', [('https://**/*', site), ('https://zslzbfbqrtfpvgbjhssd.supabase.co/**', sb)])
        check = Checks()
        opens = lambda url: _opens(ctx, url)
        tp = await ctx.new_page(); await tp.set_viewport_size({'width': 390, 'height': 900})
        await tp.goto('http://127.0.0.1:8765/human-override-class.html'); await asyncio.sleep(0.5)
        await tp.click('#mk'); await asyncio.sleep(0.8)
        check(await tp.inner_text('#code') == 'ABCD-2345', 'teacher page: class made, code shown: ' + await tp.inner_text('#code'))
        check(await tp.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 1, 'teacher page fits a phone')
        pop = await ctx.new_page(); await pop.set_viewport_size({'width': 380, 'height': 1900})
        await pop.goto(f'chrome-extension://{eid}/popup.html'); await asyncio.sleep(0.8)
        await pop.fill('#clCode', 'ZZZZ9999'); await pop.click('#clJoinB'); await asyncio.sleep(1)
        check('does not exist' in await pop.inner_text('#msg'), 'unknown class code refused: ' + await pop.inner_text('#msg'))
        await pop.fill('#clCode', 'abcd-2345'); await pop.click('#clJoinB'); await asyncio.sleep(1.2)
        check('ABCD-2345' in await pop.inner_text('#clState'), 'pupil browser joined: ' + await pop.inner_text('#clState'))
        await pop.locator('#svc label', has_text='ChatGPT').locator('input').check(); await asyncio.sleep(1.2)
        check(await opens('https://chatgpt.com/'), 'before the exam: approved ChatGPT opens')
        await tp.select_option('#mins', '60'); await tp.click('#go'); await asyncio.sleep(0.8)
        check('EXAM MODE IS ON' in await tp.inner_text('#state'), 'teacher page shows exam on: ' + await tp.inner_text('#state'))
        await sw.evaluate("examPoll()"); await asyncio.sleep(1)
        check(not await opens('https://chatgpt.com/'), 'exam on: even approved ChatGPT is blocked')
        check(await sw.evaluate("chrome.action.getBadgeText({})") == 'EX', 'badge shows EX')
        await pop.reload(); await asyncio.sleep(0.8)
        check('EXAM MODE' in await pop.inner_text('#clState'), 'popup shows exam mode: ' + await pop.inner_text('#clState'))
        await pop.click('#big'); await asyncio.sleep(1.2)
        check(not await opens('https://claude.ai/'), 'switching the big switch off does not end the exam')
        await pop.click('#big'); await asyncio.sleep(1.2)
        await pop.fill('#pin', '1234'); await pop.click('#pinB'); await asyncio.sleep(1.5)
        await pop.click('#clLeave'); await asyncio.sleep(1.5)
        check((await sw.evaluate("chrome.storage.local.get('klass')"))['klass'] == 'ABCD2345', 'with a PIN set, a pupil cannot leave the class')
        await tp.click('#stop'); await asyncio.sleep(0.8)
        check('off' in (await tp.inner_text('#state')).lower(), 'teacher stops: page shows off')
        await sw.evaluate("examPoll()"); await asyncio.sleep(1)
        check(await opens('https://chatgpt.com/'), 'exam stopped: approved ChatGPT opens again')
        check(not await opens('https://claude.ai/'), 'and other AI is blocked as before')
        # exam that runs out while offline: the minute check notices the change and rebuilds the rules
        await sw.evaluate("chrome.storage.local.set({exam:{until:Date.now()+1500}}).then(() => apply())"); await asyncio.sleep(0.3)
        check(not await opens('https://chatgpt.com/'), 'running exam blocks (offline case)')
        await asyncio.sleep(1.6)
        r = await sw.evaluate("getState().then(async st => [mode(st), (await chrome.storage.local.get('act')).act])")
        check(r == ['on', 'exam'], 'after the end time the minute check sees the change: ' + str(r))
        log = await sw.evaluate("chrome.storage.local.get('log').then(s => s.log.map(e => e.k))")
        check('classon' in log and 'examon' in log and 'examoff' in log, 'tamper log has class and exam events')
        # teacher link restores the class on another device, wrong key cannot start
        t2 = await ctx.new_page(); await t2.goto('http://127.0.0.1:8765/human-override-class.html#ABCD2345.' + 'b' * 64); await asyncio.sleep(0.6)
        await t2.evaluate("localStorage.clear()"); await t2.goto('about:blank'); await t2.goto('http://127.0.0.1:8765/human-override-class.html#ABCD2345.' + 'b' * 64); await asyncio.sleep(0.6)
        await t2.click('#go'); await asyncio.sleep(0.8)
        check(DB['ABCD2345']['until'] == 0 and 'not valid' in await t2.inner_text('#msg'), 'a wrong teacher key cannot start an exam')
        check('#' not in t2.url, 'the key is removed from the address bar')
        await t2.evaluate("localStorage.setItem('ho_class', JSON.stringify({code:'ABCD2345', key:'a'.repeat(64)}))"); await tp.goto('about:blank')
        await tp.goto('http://127.0.0.1:8765/human-override-class.html#WXYZ2345.' + 'c' * 64); await asyncio.sleep(0.6)
        check(await tp.inner_text('#code') == 'ABCD-2345' and 'another class' in await tp.inner_text('#msg'), 'a link cannot silently replace the class this device already has')
        await pop.reload(); await asyncio.sleep(0.8); await pop.screenshot(path='/tmp/ho-e2e-popup3.png', full_page=True); await tp.screenshot(path='/tmp/ho-e2e-teacher.png', full_page=True)
        await ctx.close(); check.done()
asyncio.run(main())
