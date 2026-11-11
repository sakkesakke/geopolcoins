import asyncio
from playwright.async_api import async_playwright
from common import start, Checks, opens as _opens
PAGE = '<html><body><h1 id=ok>AI SITE</h1><textarea id=a></textarea></body></html>'
async def main():
    async with async_playwright() as p:
        ctx, sw, eid = await start(p, 'approved', [('https://**/*', lambda r: r.fulfill(status=200, content_type='text/html', body=PAGE))])
        check = Checks()
        opens = lambda url: _opens(ctx, url)
        check(not await opens('https://chatgpt.com/'), 'chatgpt.com blocked by default')
        check(not await opens('https://chat.mistral.ai/'), 'chat.mistral.ai blocked by default')
        pop = await ctx.new_page(); await pop.set_viewport_size({'width': 380, 'height': 1700})
        await pop.goto(f'chrome-extension://{eid}/popup.html'); await asyncio.sleep(0.8)
        labels = await pop.locator('#svc label').all_inner_texts()
        check('ChatGPT' in labels and 'Claude' in labels and len(labels) == 9, 'picker lists the services: ' + str(labels))
        await pop.locator('#svc label', has_text='ChatGPT').locator('input').check(); await asyncio.sleep(1.2)
        check(await opens('https://chatgpt.com/'), 'ChatGPT ticked: chatgpt.com opens')
        check(await opens('https://chat.openai.com/'), 'ChatGPT ticked: chat.openai.com opens too')
        check(not await opens('https://claude.ai/'), 'other AI stays blocked')
        check(not await opens('https://character.ai/'), 'character.ai stays blocked')
        await pop.locator('#svc label', has_text='Mistral').locator('input').check(); await asyncio.sleep(1.2)
        check(await opens('https://chat.mistral.ai/'), 'Mistral ticked: chat.mistral.ai opens')
        await pop.fill('#addA', 'docs.perplexity.ai'); await pop.click('#addAb'); await asyncio.sleep(1.2)
        check(await opens('https://docs.perplexity.ai/x'), 'allowed sub-site opens while its parent is on the list')
        check(not await opens('https://www.perplexity.ai/'), 'the parent stays blocked')
        # own words
        await pop.fill('#addW', 'ab'); await pop.click('#addWb'); await asyncio.sleep(0.6)
        check('3' in await pop.inner_text('#msg'), 'too short word refused: ' + await pop.inner_text('#msg'))
        await pop.fill('#addW', 'Project Zeus'); await pop.click('#addWb'); await asyncio.sleep(1)
        check('project zeus' in await pop.inner_text('#tagsW'), 'own word saved')
        page = await ctx.new_page(); await page.goto('https://chatgpt.com/'); await asyncio.sleep(0.5)
        async def paste(text):
            await page.evaluate('t => navigator.clipboard.writeText(t)', text); await page.click('#a'); await page.keyboard.press('Control+V'); await asyncio.sleep(0.5)
        await paste('Summary for project ZEUS budget')
        check(await page.input_value('#a') == '', 'own word on an approved AI site: paste stopped')
        await page.keyboard.press('Tab'); await page.keyboard.press('Enter'); await asyncio.sleep(0.4)
        check(await page.input_value('#a') == 'Summary for [PRIVATE] budget', 'mask hides the own word: ' + repr(await page.input_value('#a')))
        # PIN protects the new settings
        await pop.fill('#pin', '1234'); await pop.click('#pinB'); await asyncio.sleep(1.5)
        await pop.fill('#pin', '9999'); await pop.locator('#svc label', has_text='Claude').locator('input').click(); await asyncio.sleep(1.5)
        check(not await opens('https://claude.ai/'), 'wrong PIN cannot approve another AI')
        await pop.locator('#tagsW button').first.click(); await asyncio.sleep(1.5)
        st = await sw.evaluate("chrome.storage.local.get(['words','allowSvc'])")
        check(st['words'] == ['project zeus'] and st['allowSvc'] == ['chatgpt', 'mistral'], 'wrong PIN cannot remove words: ' + str(st))
        # a tampered online list cannot change what "ChatGPT" unblocks
        await sw.evaluate("bundled().then(j => { j.services.chatgpt.domains.push('character.ai'); return chrome.storage.local.set({remote: j}).then(() => apply()); })")
        check(not await opens('https://character.ai/'), 'online list cannot widen an approved service')
        await pop.reload(); await asyncio.sleep(0.8); await pop.screenshot(path='/tmp/ho-e2e-popup2.png', full_page=True)
        ov = await pop.evaluate("document.documentElement.scrollWidth - window.innerWidth"); check(ov <= 1, 'popup has no sideways scroll')
        await ctx.close(); check.done()
asyncio.run(main())
