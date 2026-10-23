/* $MAIGA app helper (shared by every page that includes it):
   registers the offline worker, shows "Install the app" buttons ([data-install]) only when useful,
   explains iPhone/iPad and in-app-browser installs, and shows a small offline notice. No tracking. */
(function () {
  var L = /^nl/i.test(navigator.language || '') ? 'nl' : /^fr/i.test(navigator.language || '') ? 'fr' : 'en';
  var T = {
    en: { install: 'Install the app', offline: 'You are offline. Saved pages and My bots still work; live data needs internet.',
      iosT: 'Add $MAIGA to your home screen', ios: ['Tap the Share button (square with an arrow) in Safari.', 'Scroll and tap "Add to Home Screen".', 'Tap "Add". The app icon appears on your home screen.'],
      inappT: 'Open in your browser first', inapp: ['This app\'s built-in browser cannot install apps.', 'Use the menu (⋯) and choose "Open in browser" (Safari or Chrome).', 'Then tap "Install the app" again.'], close: 'Close' },
    nl: { install: 'Installeer de app', offline: 'Je bent offline. Opgeslagen pagina\'s en Mijn bots werken nog; live gegevens hebben internet nodig.',
      iosT: 'Zet $MAIGA op je beginscherm', ios: ['Tik in Safari op de Deel-knop (vierkant met pijl).', 'Scroll en tik op "Zet op beginscherm".', 'Tik op "Voeg toe". Het app-icoon staat nu op je beginscherm.'],
      inappT: 'Open eerst in je browser', inapp: ['De ingebouwde browser van deze app kan geen apps installeren.', 'Kies in het menu (⋯) "Open in browser" (Safari of Chrome).', 'Tik daarna opnieuw op "Installeer de app".'], close: 'Sluiten' },
    fr: { install: 'Installer l\'appli', offline: 'Vous êtes hors ligne. Les pages enregistrées et Mes bots fonctionnent ; les données en direct demandent Internet.',
      iosT: 'Ajouter $MAIGA à l\'écran d\'accueil', ios: ['Dans Safari, touchez le bouton Partager (carré avec une flèche).', 'Faites défiler et touchez « Sur l\'écran d\'accueil ».', 'Touchez « Ajouter ». L\'icône apparaît sur votre écran d\'accueil.'],
      inappT: 'Ouvrez d\'abord dans votre navigateur', inapp: ['Le navigateur intégré de cette appli ne peut pas installer d\'applis.', 'Dans le menu (⋯), choisissez « Ouvrir dans le navigateur » (Safari ou Chrome).', 'Touchez ensuite à nouveau « Installer l\'appli ».'], close: 'Fermer' }
  }[L];
  window.MAIGA_LANG = L;

  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });
  }

  var ua = navigator.userAgent || '';
  var standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  var ios = /iphone|ipad|ipod/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var inApp = /FBAN|FBAV|Instagram|Line\/|TikTok|Snapchat|; wv\)/i.test(ua);
  var deferred = null;

  function buttons() { return Array.prototype.slice.call(document.querySelectorAll('[data-install]')); }
  function show(on) { buttons().forEach(function (b) { b.hidden = !on; b.style.display = on ? '' : 'none'; if (!b.textContent.trim()) b.textContent = '📲 ' + T.install; }); }

  function dialog(title, steps) {
    var d = document.createElement('div');
    d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true'); d.setAttribute('aria-label', title);
    d.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.6);display:flex;align-items:flex-end;justify-content:center;padding:16px';
    var box = document.createElement('div');
    box.style.cssText = 'background:#0b1a35;color:#f4f7ff;border:2px solid #ffd800;border-radius:16px;max-width:420px;width:100%;padding:18px;font:16px/1.5 system-ui,sans-serif';
    var h = document.createElement('h2'); h.textContent = title; h.style.cssText = 'margin:0 0 8px;font-size:19px';
    var ol = document.createElement('ol'); ol.style.cssText = 'margin:0 0 12px;padding-left:20px';
    steps.forEach(function (s) { var li = document.createElement('li'); li.textContent = s; ol.appendChild(li); });
    var c = document.createElement('button'); c.type = 'button'; c.textContent = T.close;
    c.style.cssText = 'background:#ffd800;color:#111;border:0;border-radius:10px;padding:10px 16px;font-weight:800;cursor:pointer';
    function close() { d.remove(); document.removeEventListener('keydown', esc); }
    function esc(e) { if (e.key === 'Escape') close(); }
    c.addEventListener('click', close); d.addEventListener('click', function (e) { if (e.target === d) close(); });
    document.addEventListener('keydown', esc);
    box.appendChild(h); box.appendChild(ol); box.appendChild(c); d.appendChild(box); document.body.appendChild(d); c.focus();
  }

  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); deferred = e; if (!standalone) show(true); });
  window.addEventListener('appinstalled', function () { deferred = null; show(false); });

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-install]');
    if (!b) return;
    e.preventDefault();
    if (deferred) { deferred.prompt(); deferred.userChoice.then(function () { deferred = null; show(false); }); }
    else if (inApp) dialog(T.inappT, T.inapp);
    else dialog(T.iosT, T.ios);
  });

  function offlineBar() {
    var id = 'maiga-offline', el = document.getElementById(id);
    document.documentElement.classList.toggle('is-offline', !navigator.onLine);
    if (navigator.onLine) { if (el) el.remove(); return; }
    if (el) return;
    el = document.createElement('div'); el.id = id; el.setAttribute('role', 'status'); el.textContent = '📴 ' + T.offline;
    el.style.cssText = 'position:fixed;left:8px;right:8px;bottom:8px;z-index:9998;background:#1d2a3a;color:#fff;border:1px solid #ffd800;border-radius:12px;padding:10px 12px;font:14px/1.4 system-ui,sans-serif;text-align:center';
    document.body.appendChild(el);
  }
  window.addEventListener('online', offlineBar); window.addEventListener('offline', offlineBar);
  document.addEventListener('DOMContentLoaded', function () {
    show(!standalone && (inApp || (ios && !deferred)));
    offlineBar();
  });
})();
