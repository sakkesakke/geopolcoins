"""Shared setup for the Human Override browser tests (Playwright + Chromium).
Run one test:  python3 human-override/test/e2e/paste_guard.py   (exam_mode.py also needs: python3 -m http.server 8765)"""
import asyncio, os, shutil, sys

EXT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'extension'))


async def start(p, name, routes=(), args=()):
    """Fresh Chromium with the extension loaded. routes: (pattern, handler) pairs set before the extension starts.
    Returns (context, service worker, extension id)."""
    prof = f'/tmp/ho-e2e-{name}'
    shutil.rmtree(prof, ignore_errors=True)
    ctx = await p.chromium.launch_persistent_context(prof, channel='chromium', headless=True,
        args=[f'--disable-extensions-except={EXT}', f'--load-extension={EXT}', *args], permissions=['clipboard-read', 'clipboard-write'])
    for pattern, handler in routes:
        await ctx.route(pattern, handler)
    sw = ctx.service_workers[0] if ctx.service_workers else await ctx.wait_for_event('serviceworker')
    await asyncio.sleep(1.5)
    for pg in ctx.pages:
        if 'welcome' in pg.url:
            await pg.close()
    return ctx, sw, sw.url.split('/')[2]


class Checks:
    def __init__(self):
        self.ok = True

    def __call__(self, cond, msg):
        print(('PASS ' if cond else 'FAIL ') + msg)
        self.ok = self.ok and bool(cond)

    def done(self):
        sys.exit(0 if self.ok else 1)


async def opens(ctx, url):
    """True when the page opens, False when the extension redirects it to its blocked page."""
    pg = await ctx.new_page()
    try:
        await pg.goto(url, timeout=8000)
    except Exception:
        pass
    await asyncio.sleep(0.4)
    u = pg.url
    await pg.close()
    return not u.startswith('chrome-extension://')
