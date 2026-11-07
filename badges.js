/* Scam Hunter badges for geopolcoins.xyz.
   Everything stays in this browser (localStorage key "maiga_badges"): no account, nothing is sent anywhere.
   Badges are earned by learning the red flags: checking tokens, playing Spot the Rug Pull, reading guides, asking Bolt...
   API: window.MAIGA_BADGES = { list, state, earn(id), rank(n), name(id), desc(id), lang() } */
(function () {
  'use strict';
  if (window.MAIGA_BADGES) return;
  var KEY = 'maiga_badges';
  var ICONS = { checkup: '🔍', checkup5: '🕵️', rug: '🧶', rug5: '🏆', radar: '📡', reader: '📖', bolt: '🤖', raider: '🎮', team: '🌍', world: '🗺️', explorer: '🧭', legend: '👑' };
  var LIST = Object.keys(ICONS);
  var N = {
    en: { checkup: 'Token Detective', checkup5: 'Red Flag Pro', rug: 'Rug Spotter', rug5: 'Rug Master', radar: 'Radar Watcher', reader: 'Bookworm', bolt: 'Bolt’s Friend', raider: 'Raider', team: 'Language Warrior', world: 'World Walker', explorer: 'Explorer', legend: 'Scam Hunter Legend' },
    nl: { checkup: 'Tokendetective', checkup5: 'Rode-vlag-pro', rug: 'Rugspotter', rug5: 'Rugmeester', radar: 'Radarwachter', reader: 'Boekenwurm', bolt: 'Vriend van Bolt', raider: 'Raider', team: 'Taalstrijder', world: 'Wereldwandelaar', explorer: 'Ontdekker', legend: 'Scamjager-legende' },
    fr: { checkup: 'Détective de tokens', checkup5: 'Pro des alertes', rug: 'Chasseur de rugs', rug5: 'Maître du rug', radar: 'Veilleur radar', reader: 'Rat de bibliothèque', bolt: 'Ami de Bolt', raider: 'Raider', team: 'Guerrier des langues', world: 'Promeneur du monde', explorer: 'Explorateur', legend: 'Légende anti-arnaque' },
    es: { checkup: 'Detective de tokens', checkup5: 'Pro de alertas', rug: 'Cazador de rugs', rug5: 'Maestro del rug', radar: 'Vigía del radar', reader: 'Ratón de biblioteca', bolt: 'Amigo de Bolt', raider: 'Raider', team: 'Guerrero de idiomas', world: 'Caminante', explorer: 'Explorador', legend: 'Leyenda cazaestafas' },
    pt: { checkup: 'Detetive de tokens', checkup5: 'Pro dos alertas', rug: 'Caçador de rugs', rug5: 'Mestre do rug', radar: 'Vigia do radar', reader: 'Rato de biblioteca', bolt: 'Amigo do Bolt', raider: 'Raider', team: 'Guerreiro dos idiomas', world: 'Andarilho', explorer: 'Explorador', legend: 'Lenda caça-golpes' },
    de: { checkup: 'Token-Detektiv', checkup5: 'Warnzeichen-Profi', rug: 'Rug-Spürnase', rug5: 'Rug-Meister', radar: 'Radar-Wächter', reader: 'Leseratte', bolt: 'Bolts Freund', raider: 'Raider', team: 'Sprachkrieger', world: 'Weltenbummler', explorer: 'Entdecker', legend: 'Betrugsjäger-Legende' },
    tr: { checkup: 'Token Dedektifi', checkup5: 'Uyarı Ustası', rug: 'Rug Avcısı', rug5: 'Rug Ustası', radar: 'Radar Bekçisi', reader: 'Kitap Kurdu', bolt: 'Bolt’un Dostu', raider: 'Akıncı', team: 'Dil Savaşçısı', world: 'Dünya Gezgini', explorer: 'Kaşif', legend: 'Dolandırıcı Avcısı Efsanesi' },
    id: { checkup: 'Detektif Token', checkup5: 'Pro Tanda Bahaya', rug: 'Pemburu Rug', rug5: 'Master Rug', radar: 'Penjaga Radar', reader: 'Kutu Buku', bolt: 'Teman Bolt', raider: 'Raider', team: 'Pejuang Bahasa', world: 'Penjelajah Dunia', explorer: 'Penjelajah', legend: 'Legenda Pemburu Penipuan' },
    vi: { checkup: 'Thám tử token', checkup5: 'Chuyên gia cờ đỏ', rug: 'Thợ săn rug', rug5: 'Bậc thầy rug', radar: 'Người canh radar', reader: 'Mọt sách', bolt: 'Bạn của Bolt', raider: 'Raider', team: 'Chiến binh ngôn ngữ', world: 'Kẻ lang thang', explorer: 'Nhà thám hiểm', legend: 'Huyền thoại săn lừa đảo' },
    ar: { checkup: 'محقق العملات', checkup5: 'خبير الإشارات الحمراء', rug: 'كاشف الاحتيال', rug5: 'سيد كشف الاحتيال', radar: 'مراقب الرادار', reader: 'محب القراءة', bolt: 'صديق بولت', raider: 'المغامر', team: 'محارب اللغة', world: 'جوال العالم', explorer: 'المستكشف', legend: 'أسطورة صيد الاحتيال' }
  };
  var D = {
    en: { checkup: 'Check a token in the free Token Checkup.', checkup5: 'Check 5 different tokens.', rug: 'Finish a game of Spot the Rug Pull.', rug5: 'Score 5/5 in Spot the Rug Pull.', radar: 'Open the MAIGA Radar.', reader: 'Read a guide on the blog.', bolt: 'Ask Bolt a question.', raider: 'Save a score in MAIGA Raid.', team: 'Join a team in the Language War.', world: 'Walk around in the Pixel World.', explorer: 'Visit 6 different parts of the site.', legend: 'Earn 10 other badges.' },
    nl: { checkup: 'Check een token in de gratis Token Checkup.', checkup5: 'Check 5 verschillende tokens.', rug: 'Speel Spot the Rug Pull uit.', rug5: 'Haal 5/5 in Spot the Rug Pull.', radar: 'Open de MAIGA Radar.', reader: 'Lees een gids op de blog.', bolt: 'Stel Bolt een vraag.', raider: 'Bewaar een score in MAIGA Raid.', team: 'Kies een team in de Talenoorlog.', world: 'Wandel rond in de Pixel World.', explorer: 'Bezoek 6 verschillende delen van de site.', legend: 'Verdien 10 andere badges.' },
    fr: { checkup: 'Vérifie un token dans le Token Checkup gratuit.', checkup5: 'Vérifie 5 tokens différents.', rug: 'Termine une partie de Spot the Rug Pull.', rug5: 'Fais 5/5 à Spot the Rug Pull.', radar: 'Ouvre le MAIGA Radar.', reader: 'Lis un guide du blog.', bolt: 'Pose une question à Bolt.', raider: 'Enregistre un score dans MAIGA Raid.', team: 'Rejoins une équipe de la Guerre des langues.', world: 'Promène-toi dans le Pixel World.', explorer: 'Visite 6 parties différentes du site.', legend: 'Gagne 10 autres badges.' }
  };
  var UI = {
    en: { got: 'Badge earned', see: 'See my badges' }, nl: { got: 'Badge verdiend', see: 'Mijn badges' }, fr: { got: 'Badge gagné', see: 'Mes badges' },
    es: { got: 'Insignia ganada', see: 'Mis insignias' }, pt: { got: 'Medalha ganha', see: 'Minhas medalhas' }, de: { got: 'Abzeichen verdient', see: 'Meine Abzeichen' },
    tr: { got: 'Rozet kazanıldı', see: 'Rozetlerim' }, id: { got: 'Lencana didapat', see: 'Lencanaku' }, vi: { got: 'Đã nhận huy hiệu', see: 'Huy hiệu của tôi' }, ar: { got: 'حصلت على شارة', see: 'شاراتي' }
  };
  var RANKS = {
    en: ['Rookie', 'Scout', 'Hunter', 'Detective', 'Legend'], nl: ['Beginner', 'Verkenner', 'Jager', 'Detective', 'Legende'], fr: ['Débutant', 'Éclaireur', 'Chasseur', 'Détective', 'Légende'],
    es: ['Novato', 'Explorador', 'Cazador', 'Detective', 'Leyenda'], pt: ['Novato', 'Batedor', 'Caçador', 'Detetive', 'Lenda'], de: ['Neuling', 'Späher', 'Jäger', 'Detektiv', 'Legende'],
    tr: ['Çaylak', 'İzci', 'Avcı', 'Dedektif', 'Efsane'], id: ['Pemula', 'Pengintai', 'Pemburu', 'Detektif', 'Legenda'], vi: ['Tân binh', 'Trinh sát', 'Thợ săn', 'Thám tử', 'Huyền thoại'], ar: ['مبتدئ', 'كشاف', 'صياد', 'محقق', 'أسطورة']
  };

  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function lang() { var l = ls('maiga_lang') || document.documentElement.lang || 'en'; l = String(l).slice(0, 2); return N[l] ? l : 'en'; }
  function state() { try { var s = JSON.parse(ls(KEY) || '{}'); s.b = s.b || {}; s.p = s.p || []; return s; } catch (e) { return { b: {}, p: [] }; } }
  function save(s) { ls(KEY, JSON.stringify(s)); }
  function name(id, l) { l = l || lang(); return (N[l] || N.en)[id] || N.en[id]; }
  function desc(id, l) { l = l || lang(); return (D[l] || D.en)[id] || D.en[id]; }
  function rank(n, l) { var r = RANKS[l || lang()] || RANKS.en; return r[n >= 12 ? 4 : n >= 9 ? 3 : n >= 6 ? 2 : n >= 3 ? 1 : 0]; }

  var queue = [], showing = false;
  function toast(id) {
    queue.push(id); if (showing) return; next();
    function next() {
      var b = queue.shift(); if (!b) { showing = false; return; } showing = true;
      var l = lang(), u = UI[l] || UI.en, el = document.createElement('a');
      el.href = '/badges.html'; el.setAttribute('role', 'status');
      el.style.cssText = 'position:fixed;left:16px;bottom:16px;z-index:2147483000;display:flex;gap:10px;align-items:center;max-width:calc(100vw - 32px);' +
        'background:#251c38;color:#f1ebe0;border:2px solid #ffb547;border-radius:14px;padding:10px 14px;font:600 14px/1.3 system-ui,sans-serif;' +
        'text-decoration:none;box-shadow:0 8px 24px rgba(0,0,0,.45);transition:transform .3s,opacity .3s;transform:translateY(20px);opacity:0';
      var i = document.createElement('span'); i.textContent = ICONS[b]; i.style.fontSize = '28px';
      var t = document.createElement('span'), s = document.createElement('small'), n = document.createElement('b');
      s.textContent = u.got + ' · ' + u.see + ' →'; s.style.cssText = 'display:block;color:#b3a9c4;font-weight:500';
      n.textContent = name(b, l); n.style.color = '#ffb547'; t.appendChild(n); t.appendChild(s);
      el.appendChild(i); el.appendChild(t); document.body.appendChild(el);
      requestAnimationFrame(function () { el.style.transform = 'none'; el.style.opacity = '1'; });
      setTimeout(function () { el.style.opacity = '0'; setTimeout(function () { el.remove(); next(); }, 350); }, 4200);
    }
  }

  function earn(id) {
    if (!ICONS[id]) return false;
    var s = state(); if (s.b[id]) return false;
    s.b[id] = Date.now(); save(s);
    if (document.body) toast(id);
    if (id !== 'legend' && Object.keys(s.b).filter(function (k) { return k !== 'legend'; }).length >= 10) earn('legend');
    return true;
  }

  // Passive checks: read only this site's own localStorage keys, plus which page is open.
  function check() {
    try {
      var h = JSON.parse(ls('maiga_checkups_v1') || '[]');
      if (h.length >= 1) earn('checkup');
      if (h.length >= 5) earn('checkup5');
    } catch (e) {}
    var rb = +(ls('maiga_rug_best') || -1);
    if (rb >= 0) earn('rug');
    if (rb >= 5) earn('rug5');
    if (ls('maiga_raid_name')) earn('raider');
    if (ls('maiga_raid_team')) earn('team');
  }
  function visit() {
    var p = location.pathname.replace(/\/index\.html$/, '/'), s = state(), page = p === '/' ? 'home' : p.replace(/^\/|\.html$/g, '');
    if (/^blog-/.test(page)) page = 'blog';
    if (page && s.p.indexOf(page) < 0 && s.p.length < 60) { s.p.push(page); save(s); }
    if (page === 'radar') earn('radar');
    if (page === 'blog') earn('reader');
    if (page === 'world') earn('world');
    if (state().p.length >= 6) earn('explorer');
  }

  window.MAIGA_BADGES = { list: LIST, icons: ICONS, state: state, earn: earn, rank: rank, name: name, desc: desc, lang: lang };
  function start() { visit(); check(); setInterval(check, 4000); window.addEventListener('storage', check); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
