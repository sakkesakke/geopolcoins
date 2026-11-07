/* MAIGA Token Checkup widget. Free to use. Keep the "Powered by" link visible.
   Put this where the widget should appear:
     <div class="maiga-checkup" data-mint="OPTIONAL_TOKEN_ADDRESS" data-theme="dark"></div>
     <script src="https://geopolcoins.xyz/widget.js" async></script>
   data-theme: dark (default) or light. data-fixed="1" hides the address box when data-mint is set. */
(function () {
  'use strict';
  var ORIGIN = 'https://geopolcoins.xyz', B58 = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
  var frames = [];
  function mount(box) {
    if (box.getAttribute('data-maiga-done')) return;
    box.setAttribute('data-maiga-done', '1');
    var q = [], mint = box.getAttribute('data-mint') || '', theme = box.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    if (B58.test(mint)) q.push('mint=' + encodeURIComponent(mint));
    q.push('theme=' + theme);
    if (box.getAttribute('data-fixed') === '1') q.push('fixed=1');
    var f = document.createElement('iframe');
    f.src = ORIGIN + '/embed.html?' + q.join('&');
    f.title = 'Token Checkup by geopolcoins.xyz';
    f.loading = 'lazy';
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    f.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups allow-forms');
    f.style.cssText = 'width:100%;max-width:420px;height:150px;border:0;border-radius:14px;display:block;color-scheme:normal';
    box.appendChild(f); frames.push(f);
  }
  window.addEventListener('message', function (e) {
    if (e.origin !== ORIGIN || !e.data || e.data.maiga !== 'checkup-height') return;
    var h = Math.max(120, Math.min(900, Number(e.data.h) || 0));
    frames.forEach(function (f) { if (f.contentWindow === e.source) f.style.height = h + 'px'; });
  });
  function init() { var b = document.querySelectorAll('.maiga-checkup'); for (var i = 0; i < b.length; i++) mount(b[i]); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
