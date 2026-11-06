/* geo-guard.js: legal guard for pages that link to buying or swapping $MAIGA.
   1. Shows the Belgian FSMA risk warning at the top of the page (EN/NL/FR), when <html data-risk="1">.
   2. Hides every element marked [data-trade] for visitors whose browser time zone points to a country
      where promoting or trading crypto is restricted (UK financial-promotion rules, crypto bans,
      comprehensive sanctions). The check runs only in the browser: nothing is sent anywhere.
   Not perfect (VPNs, travel), but a reasonable, privacy-friendly step. List: see legal.html#countries. */
(function () {
  'use strict';
  var TZ = {
    'Europe/London': 'GB', 'Europe/Belfast': 'GB', 'Europe/Guernsey': 'GB', 'Europe/Jersey': 'GB', 'Europe/Isle_of_Man': 'GB',
    'Asia/Shanghai': 'CN', 'Asia/Urumqi': 'CN', 'Asia/Chongqing': 'CN', 'Asia/Harbin': 'CN', 'PRC': 'CN',
    'Africa/Algiers': 'DZ', 'Asia/Dhaka': 'BD', 'Africa/Cairo': 'EG', 'Egypt': 'EG', 'Asia/Kathmandu': 'NP', 'Asia/Katmandu': 'NP',
    'Asia/Kabul': 'AF', 'Africa/Casablanca': 'MA', 'Africa/El_Aaiun': 'MA',
    'Asia/Tehran': 'IR', 'Iran': 'IR', 'Asia/Pyongyang': 'KP', 'Asia/Damascus': 'SY', 'America/Havana': 'CU', 'Cuba': 'CU', 'Europe/Minsk': 'BY',
    'Europe/Moscow': 'RU', 'W-SU': 'RU', 'Europe/Kaliningrad': 'RU', 'Europe/Samara': 'RU', 'Europe/Volgograd': 'RU', 'Europe/Saratov': 'RU',
    'Europe/Ulyanovsk': 'RU', 'Europe/Astrakhan': 'RU', 'Europe/Kirov': 'RU', 'Asia/Yekaterinburg': 'RU', 'Asia/Omsk': 'RU',
    'Asia/Novosibirsk': 'RU', 'Asia/Barnaul': 'RU', 'Asia/Tomsk': 'RU', 'Asia/Novokuznetsk': 'RU', 'Asia/Krasnoyarsk': 'RU',
    'Asia/Irkutsk': 'RU', 'Asia/Chita': 'RU', 'Asia/Yakutsk': 'RU', 'Asia/Khandyga': 'RU', 'Asia/Vladivostok': 'RU',
    'Asia/Ust-Nera': 'RU', 'Asia/Magadan': 'RU', 'Asia/Sakhalin': 'RU', 'Asia/Srednekolymsk': 'RU', 'Asia/Kamchatka': 'RU', 'Asia/Anadyr': 'RU'
  };
  var tz = '';
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
  var forced = '';
  try { forced = new URLSearchParams(location.search).get('geo') || ''; } catch (e) {}  /* ?geo=GB to test */
  var country = /^[A-Z]{2}$/.test(forced) ? forced : (TZ[tz] || '');
  var root = document.documentElement;
  var blocked = !!country;
  if (blocked) root.classList.add('geo-block');
  window.MAIGA_GEO = { blocked: blocked, country: country };

  var css = document.createElement('style');
  css.textContent = '.geo-block [data-trade]{display:none!important}' +
    '.mg-risk{position:relative;z-index:50;background:#1b1408;color:#ffe2a8;border-bottom:2px solid #ffb547;font:600 13.5px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:7px 14px;text-align:center}' +
    '.mg-risk a{color:#ffb547;font-weight:800;margin-left:6px;white-space:nowrap}.mg-risk b{color:#fff}' +
    '.mg-geo{background:#251c38;color:#f1ebe0;border-bottom:1px solid rgba(241,235,224,.15);font:500 13.5px/1.45 system-ui,sans-serif;padding:7px 14px;text-align:center}';
  document.head.appendChild(css);

  var T = {
    en: { r: 'Virtual currencies, real risks. The only guarantee in crypto is risk.', more: 'Full risk warning',
          g: 'Buy and swap links are hidden in your region because local rules restrict crypto promotion. All tools and games stay free.' },
    nl: { r: 'Virtuele munten, reële risico’s. De enige garantie in crypto is het risico.', more: 'Volledige waarschuwing',
          g: 'Koop- en swaplinks zijn verborgen in jouw regio, omdat lokale regels cryptopromotie beperken. Alle tools en games blijven gratis.' },
    fr: { r: 'Monnaie virtuelle, risques réels. En crypto seul le risque est garanti.', more: 'Avertissement complet',
          g: 'Les liens d’achat et d’échange sont masqués dans votre région, car les règles locales limitent la promotion des cryptos. Tous les outils et jeux restent gratuits.' }
  };
  /*LANGS-START (built by tools/build_i18n.py)*/
  T.es = {"r": "Monedas virtuales, riesgos reales. La única garantía en cripto es el riesgo.", "more": "Aviso de riesgo completo", "g": "Los enlaces de compra e intercambio están ocultos en tu región porque las normas locales limitan la promoción de cripto. Todas las herramientas y juegos siguen siendo gratis."};
  T.pt = {"r": "Moedas virtuais, riscos reais. A única garantia em cripto é o risco.", "more": "Aviso de risco completo", "g": "Os links de compra e troca estão ocultos na sua região porque as regras locais limitam a promoção de cripto. Todas as ferramentas e jogos continuam grátis."};
  T.de = {"r": "Virtuelle Währungen, reale Risiken. Die einzige Garantie bei Krypto ist das Risiko.", "more": "Vollständiger Risikohinweis", "g": "Kauf- und Swap-Links sind in deiner Region ausgeblendet, weil lokale Regeln Krypto-Werbung einschränken. Alle Tools und Spiele bleiben kostenlos."};
  T.tr = {"r": "Sanal paralar, gerçek riskler. Kriptoda tek garanti risktir.", "more": "Tam risk uyarısı", "g": "Yerel kurallar kripto tanıtımını kısıtladığı için bölgende alım ve takas bağlantıları gizlendi. Tüm araçlar ve oyunlar ücretsiz kalıyor."};
  T.id = {"r": "Mata uang virtual, risiko nyata. Satu-satunya jaminan di kripto adalah risiko.", "more": "Peringatan risiko lengkap", "g": "Tautan beli dan swap disembunyikan di wilayahmu karena aturan setempat membatasi promosi kripto. Semua alat dan game tetap gratis."};
  T.vi = {"r": "Tiền ảo, rủi ro thật. Điều duy nhất được đảm bảo trong crypto là rủi ro.", "more": "Cảnh báo rủi ro đầy đủ", "g": "Liên kết mua và hoán đổi bị ẩn ở khu vực của bạn vì quy định địa phương hạn chế quảng bá crypto. Mọi công cụ và trò chơi vẫn miễn phí."};
  T.ar = {"r": "عملات افتراضية، ومخاطر حقيقية. الشيء الوحيد المضمون في الكريبتو هو المخاطرة.", "more": "تحذير المخاطر الكامل", "g": "روابط الشراء والمبادلة مخفية في منطقتك لأن القواعد المحلية تقيّد الترويج للكريبتو. كل الأدوات والألعاب تبقى مجانية."};
  /*LANGS-END*/
  function lang() {
    var l = '';
    try { l = localStorage.getItem('maiga_lang') || ''; } catch (e) {}
    l = l || (root.lang || 'en').slice(0, 2);
    return T[l] ? l : 'en';
  }
  function render() {
    var t = T[lang()], body = document.body;
    if (!body) return;
    if (root.getAttribute('data-risk') === '1') {
      var r = document.getElementById('mg-risk');
      if (!r) { r = document.createElement('div'); r.id = 'mg-risk'; r.className = 'mg-risk'; r.setAttribute('role', 'note'); body.insertBefore(r, body.firstChild); }
      r.textContent = '';
      var b = document.createElement('b'); b.textContent = t.r; r.appendChild(b);
      var a = document.createElement('a'); a.href = '/legal.html#risk'; a.textContent = t.more; r.appendChild(a);
    }
    if (blocked) {
      var g = document.getElementById('mg-geo');
      if (!g) { g = document.createElement('div'); g.id = 'mg-geo'; g.className = 'mg-geo'; g.setAttribute('role', 'status');
        var after = document.getElementById('mg-risk'); body.insertBefore(g, after ? after.nextSibling : body.firstChild); }
      g.textContent = t.g;
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render); else render();
  /* follow the page's language buttons */
  document.addEventListener('click', function (e) { var el = e.target && e.target.closest ? e.target.closest('[data-l]') : null; if (el) setTimeout(render, 0); });
})();
