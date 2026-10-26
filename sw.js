/* $MAIGA service worker: makes the site installable and usable offline.
   Pages: network first (always fresh when online), cached copy only when offline.
   Own static files: served from cache, refreshed in the background.
   Other sites (Supabase, AI providers, swap, Ko-fi) are never cached. */
var VERSION = 'maiga-2026-10-26b';
var CORE = ['/', '/hq.html', '/app.html', '/garage.html', '/chain.html', '/offline.html', '/pwa.js', '/site.webmanifest',
  '/icon-192.png', '/icon-512.png', '/favicon-32.png', '/apple-touch-icon.png', '/logo.png', '/jp-pump.png', '/guide.js', '/bolt.png', '/free-ai-api.html', '/meme.html', '/lend.html', '/agent-tools.js', '/meme/templates.json',
  '/meme/mw1.png', '/meme/mw2.png', '/meme/mw3.png', '/meme/mw4.png', '/meme/mw5.png', '/meme/mw6.png', '/meme/pxjp.png', '/meme/pxeg.png', '/meme/pxmint.png', '/meme/shades.png', '/meme/crown.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function fromNetwork(req) {
  return fetch(req).then(function (res) {
    if (res && res.ok && res.type === 'basic') {
      var copy = res.clone();
      caches.open(VERSION).then(function (c) { c.put(req, copy); });
    }
    return res;
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;   // never touch other sites
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').indexOf('text/html') >= 0) {
    e.respondWith(fromNetwork(req).catch(function () {
      return caches.match(req, { ignoreSearch: true }).then(function (hit) { return hit || caches.match('/offline.html'); });
    }));
    return;
  }
  e.respondWith(caches.match(req).then(function (hit) {
    var net = fromNetwork(req).catch(function () { return hit; });
    return hit || net;
  }));
});
