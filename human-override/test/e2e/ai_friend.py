"""Mindveto AI friend heads-up (B4): companion apps (Character.AI, Replika, Talkie...) are their own category, on by default.
A blocked try adds one tamper-log line "AI friend app tried" (kind + time only, no site name) and the red "!" badge,
at most one line per 5 minutes. The friend switch alone decides about these apps, independent of the chatbot switch.
Run: python3 human-override/test/e2e/ai_friend.py"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import start, Checks, opens
from playwright.async_api import async_playwright


async def fake(route):
    if route.request.url.startswith('chrome-extension://'): return await route.continue_()
    await route.fulfill(status=200, content_type='text/html', body='<h1>ok</h1>')


async def main():
    ok = Checks()
    async with async_playwright() as p:
        ctx, sw, ext = await start(p, 'friend', routes=[('**/*', fake)], args=['--lang=en-US'])
        pop = await ctx.new_page(); await pop.goto(f'chrome-extension://{ext}/popup.html')
        send = lambda m: pop.evaluate('(m) => new Promise(r => chrome.runtime.sendMessage(m, r))', m)
        friends = lambda: sw.evaluate("chrome.storage.local.get('log').then(s => (s.log || []).filter(e => e.k === 'friend'))")
        alert = lambda: sw.evaluate("chrome.storage.local.get('alert').then(s => !!s.alert)")
        base = {'chat': True, 'search': True, 'image': True, 'media': True, 'writing': True, 'coding': True, 'record': True, 'friend': True, 'social': False}

        ok(not await opens(ctx, 'https://chatgpt.com/'), 'chatgpt.com blocked'); await asyncio.sleep(0.8)
        ok(len(await friends()) == 0, 'a normal AI chatbot adds no AI friend log line')
        ok(not await alert(), 'a normal AI chatbot does not raise the alert')

        ok(not await opens(ctx, 'https://character.ai/'), 'character.ai blocked by default'); await asyncio.sleep(0.8)
        fr = await friends()
        ok(len(fr) == 1, 'one AI friend log line')
        ok(fr and sorted(fr[0].keys()) == ['at', 'k'], 'log line holds only the kind and the time (no site name)')
        ok(await alert(), 'alert switched on')
        ok(await sw.evaluate('chrome.action.getBadgeText({})') == '!', 'badge shows "!"')

        ok(not await opens(ctx, 'https://www.replika.com/'), 'www.replika.com blocked'); await asyncio.sleep(0.8)
        ok(len(await friends()) == 1, 'no second line within 5 minutes')

        await sw.evaluate('chrome.storage.local.set({ friendAt: 0 })')
        ok(not await opens(ctx, 'https://beta.character.ai/chat'), 'beta.character.ai/chat blocked'); await asyncio.sleep(0.8)
        ok(len(await friends()) == 2, 'second line after the 5-minute gap')

        await pop.reload(); await pop.locator('#log li').first.wait_for(timeout=5000)
        ok('AI friend app tried' in await pop.inner_text('#log'), 'popup log shows "AI friend app tried"')
        ok('AI friend apps' in await pop.inner_text('#cats'), 'popup has an "AI friend apps" switch')
        ok(await pop.locator('#seen').is_visible(), '"Mark as seen" button visible')

        await send({'t': 'set', 'cats': dict(base, friend=False)}); await asyncio.sleep(1.5)
        ok(await opens(ctx, 'https://character.ai/'), 'friend switch off: character.ai opens')
        ok(not await opens(ctx, 'https://chatgpt.com/'), 'friend switch off: chatgpt stays blocked')

        await send({'t': 'set', 'cats': dict(base, chat=False)}); await asyncio.sleep(1.5)
        ok(not await opens(ctx, 'https://character.ai/'), 'chatbots off, friend on: character.ai blocked')
        ok(await opens(ctx, 'https://chatgpt.com/'), 'chatbots off: chatgpt opens')

        r = await send({'t': 'seen'})
        ok(r and r.get('ok') and not await alert(), '"seen" clears the alert')
        await ctx.close()
    ok.done()

asyncio.run(main())
