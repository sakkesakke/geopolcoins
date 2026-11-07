/* Bolt the guide: knows every tool, game and page on geopolcoins.xyz and explains them in 10 languages.
   No AI, no tracking, nothing you type is sent anywhere. Knowledge: /guide-kb.json (rebuilt automatically
   from the pages). Search: MiniSearch by Luca Ongaro (MIT), /vendor/minisearch.min.js, loaded on first open. */
(function () {
  if (window.__boltGuide) return; window.__boltGuide = 1;
  if (!window.MAIGA_BADGES && !document.querySelector('script[src$="badges.js"]')) { var bj = document.createElement('script'); bj.src = '/badges.js'; bj.defer = true; document.head.appendChild(bj); }
  function pickLang() {
    var s = null; try { s = localStorage.getItem('maiga_lang'); } catch (e) {}
    var l = s || document.documentElement.lang || navigator.language || 'en';
    var m = /^(nl|fr|es|pt|de|tr|id|vi|ar)/i.exec(l); return m ? m[1].toLowerCase() : 'en';
  }
  var L = pickLang();
  var UIS = {
    en: { open: 'Ask Bolt', title: 'Bolt, your guide', hi: 'Hi, I\'m Bolt! I know every tool and game on this site. Ask me anything, or pick below.', here: 'You are on: ', ph: 'Ask about any tool or game…', send: 'Send', close: 'Close help',
      none: 'I didn\'t find that. Try other words, or pick a topic:', note: 'Simple guide, no AI. Nothing you type leaves your device. Not financial advice.', how: 'How it works:', also: 'Also related:', load: 'One moment…', fail: 'I can\'t load my notes right now. Check your connection, or start from the home page.',
      groups: { tool: 'Tools', game: 'Games', learn: 'Learn', business: 'For businesses', help: 'Help & safety', page: 'More pages' }, all: 'Show everything', here2: 'What can I do here?' },
    nl: { open: 'Vraag Bolt', title: 'Bolt, je gids', hi: 'Hoi, ik ben Bolt! Ik ken elke tool en game op deze site. Vraag me alles, of kies hieronder.', here: 'Je bent op: ', ph: 'Vraag over een tool of game…', send: 'Stuur', close: 'Hulp sluiten',
      none: 'Dat vond ik niet. Probeer andere woorden, of kies een onderwerp:', note: 'Eenvoudige gids, geen AI. Wat je typt verlaat je toestel niet. Geen financieel advies.', how: 'Zo werkt het:', also: 'Ook interessant:', load: 'Even geduld…', fail: 'Ik kan mijn notities nu niet laden. Controleer je verbinding, of begin op de homepage.',
      groups: { tool: 'Tools', game: 'Games', learn: 'Leren', business: 'Voor zaken', help: 'Hulp & veiligheid', page: 'Meer pagina\'s' }, all: 'Toon alles', here2: 'Wat kan ik hier doen?' },
    fr: { open: 'Demander à Bolt', title: 'Bolt, votre guide', hi: 'Salut, je suis Bolt ! Je connais chaque outil et jeu du site. Posez-moi une question, ou choisissez ci-dessous.', here: 'Vous êtes sur : ', ph: 'Une question sur un outil ou un jeu…', send: 'Envoyer', close: 'Fermer l\'aide',
      none: 'Je n\'ai pas trouvé. Essayez d\'autres mots, ou choisissez un sujet :', note: 'Guide simple, sans IA. Rien de ce que vous tapez ne quitte votre appareil. Pas un conseil financier.', how: 'Comment ça marche :', also: 'Voir aussi :', load: 'Un instant…', fail: 'Je ne peux pas charger mes notes. Vérifiez votre connexion, ou partez de l\'accueil.',
      groups: { tool: 'Outils', game: 'Jeux', learn: 'Apprendre', business: 'Pour les entreprises', help: 'Aide & sécurité', page: 'Autres pages' }, all: 'Tout afficher', here2: 'Que faire ici ?' }
  };
  /*UI-EXTRA-START (built by tools/build_guide_kb.py from tools/guide_i18n)*/
  Object.assign(UIS, {"es":{"open":"Pregunta a Bolt","title":"Bolt, tu guía","hi":"¡Hola, soy Bolt! Conozco cada herramienta y juego de este sitio. Pregúntame lo que quieras o elige abajo.","here":"Estás en: ","ph":"Pregunta por una herramienta o juego…","send":"Enviar","close":"Cerrar ayuda","none":"No lo encontré. Prueba con otras palabras o elige un tema:","note":"Guía sencilla, sin IA. Lo que escribes no sale de tu dispositivo. No es asesoramiento financiero.","how":"Cómo funciona:","also":"Relacionado:","load":"Un momento…","fail":"Ahora no puedo cargar mis notas. Revisa tu conexión o empieza desde la página de inicio.","groups":{"tool":"Herramientas","game":"Juegos","learn":"Aprender","business":"Para empresas","help":"Ayuda y seguridad","page":"Más páginas"},"all":"Ver todo","here2":"¿Qué puedo hacer aquí?"},"pt":{"open":"Pergunte ao Bolt","title":"Bolt, seu guia","hi":"Oi, eu sou o Bolt! Conheço cada ferramenta e jogo deste site. Pergunte o que quiser ou escolha abaixo.","here":"Você está em: ","ph":"Pergunte sobre uma ferramenta ou jogo…","send":"Enviar","close":"Fechar ajuda","none":"Não encontrei. Tente outras palavras ou escolha um tema:","note":"Guia simples, sem IA. O que você digita não sai do seu aparelho. Não é aconselhamento financeiro.","how":"Como funciona:","also":"Veja também:","load":"Um momento…","fail":"Não consigo carregar minhas anotações agora. Verifique sua conexão ou comece pela página inicial.","groups":{"tool":"Ferramentas","game":"Jogos","learn":"Aprender","business":"Para empresas","help":"Ajuda e segurança","page":"Mais páginas"},"all":"Mostrar tudo","here2":"O que posso fazer aqui?"},"de":{"open":"Frag Bolt","title":"Bolt, dein Guide","hi":"Hallo, ich bin Bolt! Ich kenne jedes Tool und Spiel auf dieser Seite. Frag mich alles oder wähle unten.","here":"Du bist hier: ","ph":"Frag nach einem Tool oder Spiel…","send":"Senden","close":"Hilfe schließen","none":"Das habe ich nicht gefunden. Versuch andere Wörter oder wähle ein Thema:","note":"Einfacher Guide, keine KI. Was du tippst, verlässt dein Gerät nicht. Keine Finanzberatung.","how":"So geht's:","also":"Auch interessant:","load":"Einen Moment…","fail":"Ich kann meine Notizen gerade nicht laden. Prüfe deine Verbindung oder starte auf der Startseite.","groups":{"tool":"Tools","game":"Spiele","learn":"Lernen","business":"Für Unternehmen","help":"Hilfe & Sicherheit","page":"Weitere Seiten"},"all":"Alles zeigen","here2":"Was kann ich hier tun?"},"tr":{"open":"Bolt'a sor","title":"Bolt, rehberin","hi":"Merhaba, ben Bolt! Bu sitedeki her aracı ve oyunu bilirim. Bana her şeyi sorabilir ya da aşağıdan seçebilirsin.","here":"Şu an buradasın: ","ph":"Bir araç ya da oyun hakkında sor…","send":"Gönder","close":"Yardımı kapat","none":"Bunu bulamadım. Başka kelimeler dene ya da bir konu seç:","note":"Basit rehber, yapay zekâ yok. Yazdıkların cihazından çıkmaz. Yatırım tavsiyesi değildir.","how":"Nasıl çalışır:","also":"Ayrıca:","load":"Bir saniye…","fail":"Notlarımı şu an yükleyemiyorum. Bağlantını kontrol et ya da ana sayfadan başla.","groups":{"tool":"Araçlar","game":"Oyunlar","learn":"Öğren","business":"İşletmeler için","help":"Yardım ve güvenlik","page":"Diğer sayfalar"},"all":"Hepsini göster","here2":"Burada ne yapabilirim?"},"id":{"open":"Tanya Bolt","title":"Bolt, pemandumu","hi":"Halo, aku Bolt! Aku kenal setiap alat dan game di situs ini. Tanya apa saja, atau pilih di bawah.","here":"Kamu sedang di: ","ph":"Tanya soal alat atau game…","send":"Kirim","close":"Tutup bantuan","none":"Aku tidak menemukannya. Coba kata lain, atau pilih topik:","note":"Pemandu sederhana, tanpa AI. Yang kamu ketik tidak keluar dari perangkatmu. Bukan nasihat keuangan.","how":"Cara kerjanya:","also":"Terkait:","load":"Sebentar…","fail":"Aku belum bisa memuat catatanku sekarang. Cek koneksimu, atau mulai dari beranda.","groups":{"tool":"Alat","game":"Game","learn":"Belajar","business":"Untuk bisnis","help":"Bantuan & keamanan","page":"Halaman lain"},"all":"Tampilkan semua","here2":"Apa yang bisa kulakukan di sini?"},"vi":{"open":"Hỏi Bolt","title":"Bolt, người hướng dẫn","hi":"Xin chào, mình là Bolt! Mình biết mọi công cụ và trò chơi trên trang này. Cứ hỏi mình, hoặc chọn bên dưới.","here":"Bạn đang ở: ","ph":"Hỏi về một công cụ hoặc trò chơi…","send":"Gửi","close":"Đóng trợ giúp","none":"Mình không tìm thấy. Hãy thử từ khác, hoặc chọn một chủ đề:","note":"Hướng dẫn đơn giản, không có AI. Những gì bạn gõ không rời khỏi thiết bị. Không phải lời khuyên tài chính.","how":"Cách dùng:","also":"Liên quan:","load":"Chờ một chút…","fail":"Mình chưa tải được ghi chú lúc này. Hãy kiểm tra kết nối, hoặc bắt đầu từ trang chủ.","groups":{"tool":"Công cụ","game":"Trò chơi","learn":"Học","business":"Cho doanh nghiệp","help":"Trợ giúp & an toàn","page":"Trang khác"},"all":"Xem tất cả","here2":"Mình làm được gì ở đây?"},"ar":{"open":"اسأل بولت","title":"بولت، دليلك","hi":"مرحبًا، أنا بولت! أعرف كل أداة ولعبة في هذا الموقع. اسألني أي شيء أو اختر من الأسفل.","here":"أنت الآن في: ","ph":"اسأل عن أداة أو لعبة…","send":"إرسال","close":"إغلاق المساعدة","none":"لم أجد ذلك. جرّب كلمات أخرى أو اختر موضوعًا:","note":"دليل بسيط بلا ذكاء اصطناعي. ما تكتبه لا يغادر جهازك. ليست نصيحة مالية.","how":"طريقة الاستخدام:","also":"مواضيع ذات صلة:","load":"لحظة…","fail":"لا أستطيع تحميل ملاحظاتي الآن. تحقّق من اتصالك أو ابدأ من الصفحة الرئيسية.","groups":{"tool":"أدوات","game":"ألعاب","learn":"تعلّم","business":"للشركات","help":"مساعدة وأمان","page":"صفحات أخرى"},"all":"عرض الكل","here2":"ماذا يمكنني أن أفعل هنا؟"}});
  /*UI-EXTRA-END*/
  if (!UIS[L]) L = 'en';
  var UI = UIS[L];
  var KB = null, MS = null, loading = null;
  var STOP = ' de het een is wat hoe ik je mijn mn van voor met en of op in te the a an what how do does i my me to for of and or on in it is le la les un une des est ce que qui je mon ma mes pour et ou en du au dois moet kan peux can where waar ou wie who qui this dit cette ceci there er il ';
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  function el(tag, css, text) { var e = document.createElement(tag); if (css) e.style.cssText = css; if (text != null) e.textContent = text; return e; }
  var root = el('div', 'position:fixed;right:14px;bottom:14px;z-index:9997;font:15px/1.45 system-ui,Segoe UI,Roboto,sans-serif'); root.id = 'bolt-guide';
  var btn = el('button', 'display:flex;align-items:center;gap:8px;background:#ffd800;color:#111;border:3px solid #000;border-radius:999px;padding:6px 14px 6px 6px;font-weight:900;cursor:pointer;box-shadow:4px 4px 0 #000;min-height:48px');
  btn.type = 'button'; btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'bolt-panel');
  var av = el('img', 'width:36px;height:36px;image-rendering:pixelated;background:#0b1a35;border-radius:50%;padding:3px'); av.src = '/bolt.png'; av.alt = '';
  var btnTxt = document.createTextNode(UI.open); btn.append(av, btnTxt);
  var panel = el('div', 'display:none;position:absolute;right:0;bottom:62px;width:min(380px,calc(100vw - 28px));height:min(600px,calc(100vh - 100px));background:#0b1a35;color:#f4f7ff;border:2px solid #ffd800;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,.55);flex-direction:column;overflow:hidden');
  panel.id = 'bolt-panel'; panel.dir = L === 'ar' ? 'rtl' : 'ltr'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', UI.title);
  var head = el('div', 'display:flex;align-items:center;gap:8px;padding:10px 12px;background:#071226;border-bottom:1px solid rgba(169,212,255,.25)');
  var hav = av.cloneNode(); hav.style.width = '30px'; hav.style.height = '30px';
  var ht = el('b', 'flex:1', UI.title);
  var x = el('button', 'background:none;border:0;color:#fff;font-size:22px;cursor:pointer;min-width:44px;min-height:44px', '×'); x.type = 'button'; x.setAttribute('aria-label', UI.close);
  head.append(hav, ht, x);
  var log = el('div', 'flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:8px'); log.setAttribute('aria-live', 'polite');
  var chips = el('div', 'display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px 4px;border-top:1px solid rgba(169,212,255,.12)');
  var form = el('form', 'display:flex;gap:6px;padding:8px 12px 10px');
  var inp = el('input', 'flex:1;min-width:0;padding:10px;border-radius:10px;border:1px solid rgba(169,212,255,.35);background:#050b1b;color:#fff;font:inherit');
  inp.placeholder = UI.ph; inp.maxLength = 200; inp.setAttribute('aria-label', UI.ph); inp.autocomplete = 'off';
  var sb = el('button', 'background:#38f2ff;color:#04121a;border:0;border-radius:10px;padding:0 14px;font-weight:900;cursor:pointer;min-height:44px', UI.send); sb.type = 'submit';
  form.append(inp, sb);
  var foot = el('div', 'font-size:11.5px;color:#9fb0cc;padding:0 12px 10px', UI.note);
  panel.append(head, log, chips, form, foot); root.append(panel, btn);

  function bubble(text, me) {
    var b = el('div', 'max-width:92%;padding:9px 11px;border-radius:12px;' + (me ? 'align-self:flex-end;background:#38f2ff;color:#04121a' : 'align-self:flex-start;background:#13254a'), text);
    log.append(b); log.scrollTop = log.scrollHeight; return b;
  }
  function linkBtn(url, label) {
    var a = el('a', 'display:inline-block;background:#ffd800;color:#111;border-radius:8px;padding:7px 11px;font-weight:800;text-decoration:none;font-size:13.5px;margin-top:8px', label);
    a.href = url; if (/^https?:/.test(url)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  }
  function chipBtn(label, fn) {
    var c = el('button', 'background:transparent;color:#ffd800;border:1px solid #ffd800;border-radius:999px;padding:5px 10px;font:inherit;font-size:13px;cursor:pointer;min-height:34px', label);
    c.type = 'button'; c.addEventListener('click', fn); return c;
  }
  function T(o) { return o && (o[L] || o.en) || ''; }
  function urlOf(t) { return t['url_' + L] || t.url; }
  function topic(id) { return KB.topics.filter(function (t) { return t.id === id; })[0]; }
  function here() {
    var p = location.pathname.replace(/^\//, '') || 'index.html';
    return KB.topics.filter(function (t) { var u = (t.url.split('#')[0].replace(/^\//, '') || 'index.html'); return u === p || t.url_nl === p || t.url_fr === p; })[0] ||
      KB.pages.filter(function (pg) { return pg.url === p; })[0];
  }
  function showTopic(t, related) {
    var b = bubble('');
    b.append(el('b', 'display:block;margin-bottom:4px', T(t.title)), el('div', '', T(t.what)));
    var st = t.steps && (t.steps[L] || t.steps.en);
    if (st && st.length) {
      b.append(el('div', 'margin-top:8px;font-weight:800;font-size:13.5px;color:#9fe9ff', UI.how));
      var ol = el('ol', 'margin:4px 0 0;padding-left:20px'); st.forEach(function (s) { ol.append(el('li', '', s)); }); b.append(ol);
    }
    b.append(linkBtn(urlOf(t), T(t.cta) + ' →'));
    if (related && related.length) {
      var row = el('div', 'display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;align-items:center');
      row.append(el('span', 'font-size:12.5px;color:#9fb0cc', UI.also));
      related.forEach(function (r) { row.append(chipBtn(r.t ? T(r.t.title) : r.p.title, function () { ask(r.t ? T(r.t.title) : r.p.title, r); })); });
      b.append(row);
    }
    log.scrollTop = log.scrollHeight;
  }
  function showPage(p) {
    var b = bubble(''); b.append(el('b', 'display:block;margin-bottom:4px', p.title.replace(/\s*\|.*$/, '')), el('div', '', p.desc), linkBtn(p.url, '→ ' + p.url.replace('.html', '')));
  }
  function showAll() {
    var b = bubble(''); var order = ['tool', 'game', 'learn', 'business', 'help'];
    order.forEach(function (k) {
      var list = KB.topics.filter(function (t) { return t.kind === k; }); if (!list.length) return;
      b.append(el('div', 'font-weight:900;margin:6px 0 4px;color:#ffd800', UI.groups[k]));
      var row = el('div', 'display:flex;flex-wrap:wrap;gap:6px');
      list.forEach(function (t) { row.append(chipBtn(T(t.title).replace(/:.*$/, ''), function () { bubble(T(t.title), true); showTopic(t, rel(t)); })); });
      b.append(row);
    });
    log.scrollTop = log.scrollHeight;
  }
  function rel(t) {
    if (!MS) return [];
    return MS.search(T(t.title) + ' ' + t.kind, { boost: { kw: 2 }, fuzzy: 0.2, prefix: true }).filter(function (r) { return r.id !== 't:' + t.id; }).slice(0, 2).map(toHit);
  }
  function toHit(r) { var id = String(r.id); return id.indexOf('t:') === 0 ? { t: topic(id.slice(2)) } : { p: KB.pages[+id.slice(2)] }; }

  function build() {
    MS = new window.MiniSearch({
      fields: ['title', 'kw', 'what', 'text'], storeFields: [],
      processTerm: function (term) { var w = norm(term); return (w.length < 2 || STOP.indexOf(' ' + w + ' ') >= 0) ? null : w; },
      searchOptions: { boost: { title: 3, kw: 2.5, what: 1, text: .6 }, fuzzy: 0.2, prefix: true, combineWith: 'OR' }
    });
    var docs = KB.topics.map(function (t) {
      return { id: 't:' + t.id, title: Object.keys(t.title).map(function (k) { return t.title[k]; }).join(' '), kw: t.kw, what: [T(t.what), t.what.en].join(' '), text: t.text || '' };
    });
    KB.pages.forEach(function (p, i) { docs.push({ id: 'p:' + i, title: p.title, kw: '', what: p.desc, text: p.text || '' }); });
    MS.addAll(docs);
  }
  function load() {
    if (loading) return loading;
    loading = new Promise(function (ok, no) {
      var done = 0, fail = function () { loading = null; no(); };
      function step() { if (++done === 2) { try { build(); ok(); } catch (e) { fail(); } } }
      fetch('/guide-kb.json').then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (j) { KB = j; step(); }).catch(fail);
      if (window.MiniSearch) step();
      else { var s = document.createElement('script'); s.src = '/vendor/minisearch.min.js'; s.onload = step; s.onerror = fail; document.head.appendChild(s); }
    });
    return loading;
  }
  var SAFE = /\b(seed|phrase|recovery|private key|prive sleutel|cle privee|scam|scammer|oplichter|arnaque|hack|hacked|gehackt|pirate|phishing|dm)\b/;
  function ask(q, hit) {
    bubble(q, true);
    if (window.MAIGA_BADGES) window.MAIGA_BADGES.earn('bolt');
    if (hit) { hit.t ? showTopic(hit.t, rel(hit.t)) : showPage(hit.p); return; }
    var n = norm(q);
    if (SAFE.test(n)) { showTopic(topic('safe'), [{ t: topic('check') }]); return; }
    if (/\b(alles|everything|tout|all tools|alle tools|tous les outils|overzicht|overview|liste|list)\b/.test(n)) { showAll(); return; }
    if (/\b(hier|here|ici|this page|deze pagina|cette page)\b/.test(n)) { greetHere(true); return; }
    var res = MS.search(q);
    if (!res.length || res[0].score < 2) {
      var b = bubble(UI.none); var row = el('div', 'display:flex;flex-wrap:wrap;gap:6px;margin-top:8px');
      ['site', 'garage', 'meme', 'raid', 'safe'].forEach(function (id) { var t = topic(id); row.append(chipBtn(T(t.title).replace(/:.*$/, ''), function () { bubble(T(t.title), true); showTopic(t, rel(t)); })); });
      row.append(chipBtn(UI.all, function () { bubble(UI.all, true); showAll(); })); b.append(row); return;
    }
    var top = toHit(res[0]), more = res.slice(1, 3).map(toHit);
    top.t ? showTopic(top.t, more) : (showPage(top.p), more.length && more[0].t && showTopic(more[0].t, []));
  }
  function greetHere(asked) {
    var h = here();
    if (!h) { if (asked) showTopic(topic('site'), []); return; }
    if (h.title && h.title.en !== undefined) { if (!asked) bubble(UI.here + T(h.title)); showTopic(h, rel(h)); }
    else showPage(h);
  }
  function setChips() {
    chips.textContent = '';
    chips.append(chipBtn(UI.here2, function () { bubble(UI.here2, true); greetHere(true); }),
      chipBtn(UI.all, function () { bubble(UI.all, true); showAll(); }),
      chipBtn(T(topic('safe').title), function () { bubble(T(topic('safe').title), true); showTopic(topic('safe'), []); }));
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault(); var q = inp.value.trim().slice(0, 200); if (!q) return; inp.value = '';
    if (MS) ask(q); else load().then(function () { ask(q); }, function () { bubble(q, true); bubble(UI.fail); });
  });
  var started = false;
  function relabel() {
    var nl = pickLang(); if (!UIS[nl]) nl = 'en'; if (nl === L) return; L = nl; UI = UIS[L]; panel.dir = L === 'ar' ? 'rtl' : 'ltr';
    btnTxt.nodeValue = UI.open; ht.textContent = UI.title; inp.placeholder = UI.ph; sb.textContent = UI.send; foot.textContent = UI.note; x.setAttribute('aria-label', UI.close);
    if (KB) setChips();
  }
  function toggle(open) {
    if (open) relabel();
    panel.style.display = open ? 'flex' : 'none'; btn.setAttribute('aria-expanded', String(open));
    if (open) {
      if (!started) {
        started = true; bubble(UI.hi); var w = bubble(UI.load);
        load().then(function () { w.remove(); setChips(); greetHere(false); }, function () { w.textContent = UI.fail; w.append(el('br'), linkBtn('/', 'Home')); started = false; });
      }
      inp.focus();
    } else btn.focus();
  }
  btn.addEventListener('click', function () { toggle(panel.style.display !== 'flex'); });
  x.addEventListener('click', function () { toggle(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel.style.display === 'flex') toggle(false); });
  document.addEventListener('click', function (e) { if (e.target && e.target.closest && e.target.closest('[data-l],.langs button,[data-lang]')) setTimeout(relabel, 50); });
  function mount() { document.body.appendChild(root); var off = document.getElementById('maiga-offline'); if (off) root.style.bottom = '64px'; }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  window.addEventListener('offline', function () { root.style.bottom = '64px'; }); window.addEventListener('online', function () { root.style.bottom = '14px'; });
  window.__bolt = { ask: function (q) { return load().then(function () { ask(q); }); }, open: function () { toggle(true); }, get kb() { return KB; } };
  /* read-only tools for AI agents (WebMCP), only in browsers that support it */
  if ((document.modelContext || navigator.modelContext) && !document.getElementById('maiga-agent-tools')) {
    var at = document.createElement('script'); at.id = 'maiga-agent-tools'; at.src = '/agent-tools.js'; at.defer = true; document.head.appendChild(at);
  }
})();
