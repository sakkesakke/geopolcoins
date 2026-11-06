/* lang-more.js: adds the extra languages (from /i18n/<page>.js) to the page's EN/NL/FR switch.
   The extra buttons sit in a small "more" menu inside .langs, so the page's own
   ".langs button" click handlers pick them up. Also sets dir="rtl" for Arabic. */
(function () {
  'use strict';
  var NAMES = { es: 'Español', pt: 'Português', de: 'Deutsch', tr: 'Türkçe', id: 'Bahasa Indonesia', vi: 'Tiếng Việt', ar: 'العربية' };
  var have = window.MAIGA_I18N || {};
  var codes = Object.keys(NAMES).filter(function (c) { return have[c]; });
  var root = document.documentElement, menus = [];
  function syncDir() { root.dir = root.lang === 'ar' ? 'rtl' : 'ltr'; }
  syncDir();
  new MutationObserver(function () { syncDir(); mark(); }).observe(root, { attributes: true, attributeFilter: ['lang'] });
  if (!codes.length) return;

  var css = document.createElement('style');
  css.textContent = '.langs{position:relative}.lmore{position:relative;display:flex}' +
    '.lmore>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:3px;font:700 13px system-ui;padding:7px 9px;border-radius:8px;min-height:34px;color:inherit;opacity:.85}' +
    '.lmore>summary::-webkit-details-marker{display:none}.lmore[open]>summary,.lmore.on>summary{background:var(--amber,#ffb547);color:#1a1206;opacity:1}' +
    '.lmore>div{position:absolute;top:calc(100% + 6px);inset-inline-end:0;z-index:60;display:grid;min-width:170px;padding:6px;border-radius:10px;background:#1d1830;border:1px solid rgba(241,235,224,.18);box-shadow:0 12px 30px rgba(0,0,0,.45)}' +
    '.lmore>div button{display:flex!important;justify-content:space-between;gap:10px;width:100%;text-align:start;color:#f1ebe0!important;font:600 14px system-ui!important;padding:9px 10px!important;min-height:38px}' +
    '.lmore>div button small{opacity:.6;font-weight:700}.lmore>div button[aria-pressed="true"]{background:var(--amber,#ffb547)!important;color:#1a1206!important}' +
    '.lmore>summary{white-space:nowrap}[dir="rtl"] body{text-align:right}[dir="rtl"] :is(.brand,.logo){direction:ltr;unicode-bidi:isolate}' +
    /* the pixel font has no Arabic or Vietnamese letters: use the system font there */
    'html[lang="ar"] :is(h1,h2,h3,h4,.zones button,[data-i]),html[lang="vi"] :is(h1,h2,h3,h4,.zones button,[data-i]){font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Noto Sans Arabic",sans-serif!important}' +
    'html[lang="ar"] :is(h1,h2,h3),html[lang="vi"] :is(h1,h2,h3){font-weight:800;letter-spacing:0!important;line-height:1.2}html[lang="ar"] *{letter-spacing:0!important}';
  document.head.appendChild(css);

  document.querySelectorAll('.langs').forEach(function (g) {
    var d = document.createElement('details'); d.className = 'lmore';
    var s = document.createElement('summary'); s.setAttribute('aria-label', 'More languages'); d.appendChild(s);
    var box = document.createElement('div'); box.setAttribute('role', 'group');
    codes.forEach(function (c) {
      var b = document.createElement('button'); b.type = 'button'; b.dataset.l = c; b.lang = c;
      var n = document.createElement('span'); n.textContent = NAMES[c]; b.appendChild(n);
      var k = document.createElement('small'); k.textContent = c.toUpperCase(); b.appendChild(k);
      b.addEventListener('click', function () { d.open = false; });
      box.appendChild(b);
    });
    d.appendChild(box); g.appendChild(d); menus.push(d);
  });
  document.addEventListener('click', function (e) { menus.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; }); });
  function mark() {
    var on = codes.indexOf(root.lang) >= 0;
    menus.forEach(function (d) { d.classList.toggle('on', on); d.firstChild.textContent = (on ? root.lang.toUpperCase() : '+' + codes.length) + ' ▾'; });
  }
  mark();
})();
