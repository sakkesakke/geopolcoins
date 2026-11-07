/* track.js: counts one page view (page name + referring site only, no cookies, no personal data).
   Use: <script src="/track.js" data-page="rug" defer></script> */
(function () {
  try {
    var s = document.currentScript, page = (s && s.dataset.page) || 'other';
    if (navigator.webdriver || /bot|crawl|spider|slurp|preview|headless/i.test(navigator.userAgent)) return;
    var r = 'direct';
    if (document.referrer) {
      var h = new URL(document.referrer).hostname.replace(/^www\./, '').toLowerCase();
      r = h === location.hostname.replace(/^www\./, '').toLowerCase() ? 'internal' : (h === 't.co' ? 'x.com' : h);
    }
    fetch('https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/track_view', {
      method: 'POST', keepalive: true, credentials: 'omit',
      headers: { apikey: 'sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN', 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_page: page, p_ref: r })
    }).catch(function () {});
  } catch (e) {}
})();
