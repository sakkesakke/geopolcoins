/* Live chat for geopolcoins.xyz. Every message is checked by our own server (links, addresses, scam words,
   swearing, plus a small AI model) before anyone sees it. Plain text only, no account, nothing to click. */
(function () {
  if (window.__maigaChat) return; window.__maigaChat = 1;
  var SB = 'https://zslzbfbqrtfpvgbjhssd.supabase.co', K = 'sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN';
  var ROOM = (document.currentScript && document.currentScript.getAttribute('data-room')) === 'world' ? 'world' : 'site';
  var L = (document.documentElement.lang || 'en').slice(0, 2);
  var T = {
    en: ['Live chat', 'Say hi…', 'Send', 'Your name', 'Checked by our server first: no links, no addresses, no scams. Never share keys or seed phrases.', 'Chat is closed right now. Back soon.', 'Checking…', 'Blocked or still in review.', 'Too fast, wait a moment.', 'Report', 'Mute', 'Reported, thanks.', 'No messages yet. Be the first!'],
    nl: ['Live chat', 'Zeg hoi…', 'Stuur', 'Je naam', 'Eerst gecontroleerd door onze server: geen links, geen adressen, geen scams. Deel nooit sleutels of seed phrases.', 'De chat is nu gesloten. Zo terug.', 'Wordt gecontroleerd…', 'Geblokkeerd of nog in controle.', 'Te snel, wacht even.', 'Melden', 'Dempen', 'Gemeld, bedankt.', 'Nog geen berichten. Wees de eerste!'],
    fr: ['Chat en direct', 'Dis bonjour…', 'Envoyer', 'Ton nom', "Vérifié d'abord par notre serveur : pas de liens, pas d'adresses, pas d'arnaques. Ne partage jamais tes clés ni ta seed phrase.", 'Le chat est fermé pour le moment.', 'Vérification…', 'Bloqué ou encore en vérification.', 'Trop vite, attends un peu.', 'Signaler', 'Masquer', 'Signalé, merci.', 'Pas encore de messages. Sois le premier !'],
    es: ['Chat en vivo', 'Saluda…', 'Enviar', 'Tu nombre', 'Primero lo revisa nuestro servidor: sin enlaces, sin direcciones, sin estafas. Nunca compartas claves ni frases semilla.', 'El chat está cerrado ahora.', 'Revisando…', 'Bloqueado o aún en revisión.', 'Muy rápido, espera un momento.', 'Reportar', 'Silenciar', 'Reportado, gracias.', 'Aún no hay mensajes. ¡Sé el primero!'],
    pt: ['Chat ao vivo', 'Diga oi…', 'Enviar', 'Seu nome', 'Verificado antes pelo nosso servidor: sem links, sem endereços, sem golpes. Nunca compartilhe chaves ou frases-semente.', 'O chat está fechado agora.', 'Verificando…', 'Bloqueado ou ainda em revisão.', 'Rápido demais, espere um pouco.', 'Denunciar', 'Silenciar', 'Denunciado, obrigado.', 'Nenhuma mensagem ainda. Seja o primeiro!'],
    de: ['Live-Chat', 'Sag hallo…', 'Senden', 'Dein Name', 'Zuerst von unserem Server geprüft: keine Links, keine Adressen, keine Scams. Teile nie Schlüssel oder Seed-Phrasen.', 'Der Chat ist gerade geschlossen.', 'Wird geprüft…', 'Blockiert oder noch in Prüfung.', 'Zu schnell, warte kurz.', 'Melden', 'Stumm', 'Gemeldet, danke.', 'Noch keine Nachrichten. Sei der Erste!'],
    tr: ['Canlı sohbet', 'Merhaba de…', 'Gönder', 'Adın', 'Önce sunucumuz kontrol eder: link yok, adres yok, dolandırıcılık yok. Anahtarlarını veya seed phrase’ini asla paylaşma.', 'Sohbet şu an kapalı.', 'Kontrol ediliyor…', 'Engellendi veya hâlâ inceleniyor.', 'Çok hızlı, biraz bekle.', 'Bildir', 'Sustur', 'Bildirildi, teşekkürler.', 'Henüz mesaj yok. İlk sen ol!'],
    id: ['Obrolan langsung', 'Sapa dulu…', 'Kirim', 'Namamu', 'Dicek dulu oleh server kami: tanpa tautan, tanpa alamat, tanpa penipuan. Jangan pernah bagikan kunci atau seed phrase.', 'Obrolan sedang tutup.', 'Sedang dicek…', 'Diblokir atau masih ditinjau.', 'Terlalu cepat, tunggu sebentar.', 'Laporkan', 'Bisukan', 'Dilaporkan, terima kasih.', 'Belum ada pesan. Jadilah yang pertama!'],
    vi: ['Trò chuyện trực tiếp', 'Chào mọi người…', 'Gửi', 'Tên bạn', 'Máy chủ của chúng tôi kiểm tra trước: không link, không địa chỉ, không lừa đảo. Đừng bao giờ chia sẻ khóa hay seed phrase.', 'Trò chuyện đang đóng.', 'Đang kiểm tra…', 'Bị chặn hoặc đang được xem xét.', 'Quá nhanh, chờ một chút.', 'Báo cáo', 'Ẩn', 'Đã báo cáo, cảm ơn.', 'Chưa có tin nhắn. Hãy là người đầu tiên!'],
    ar: ['دردشة مباشرة', 'قل مرحبا…', 'إرسال', 'اسمك', 'يفحصها خادمنا أولا: لا روابط ولا عناوين ولا احتيال. لا تشارك مفاتيحك أو عبارة الاسترداد أبدا.', 'الدردشة مغلقة الآن.', 'جار الفحص…', 'محظورة أو ما زالت قيد المراجعة.', 'بسرعة كبيرة، انتظر قليلا.', 'إبلاغ', 'كتم', 'تم الإبلاغ، شكرا.', 'لا توجد رسائل بعد. كن الأول!']
  }[L] || null;
  var S = T || ['Live chat', 'Say hi…', 'Send', 'Your name', 'Checked by our server first: no links, no addresses, no scams. Never share keys or seed phrases.', 'Chat is closed right now. Back soon.', 'Checking…', 'Blocked or still in review.', 'Too fast, wait a moment.', 'Report', 'Mute', 'Reported, thanks.', 'No messages yet. Be the first!'];

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  var me = store('maiga_chat_id');
  if (!me || !/^[a-z0-9]{8,32}$/.test(me)) { me = (Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2)).replace(/[^a-z0-9]/g, '').slice(0, 16); store('maiga_chat_id', me); }
  var name = store('maiga_chat_name') || store('maiga_raid_name') || ('Hunter' + Math.floor(100 + Math.random() * 900));
  name = String(name).replace(/[^A-Za-z0-9 _-]/g, '').slice(0, 16) || 'Hunter';
  var muted = {}; try { muted = JSON.parse(store('maiga_chat_mute') || '{}') || {}; } catch (e) { muted = {}; }
  var lastId = 0, open = false, timer = null, pending = 0;

  var css = '#mc-btn{position:fixed;left:14px;bottom:14px;z-index:9996;background:#0f1424;color:#f4ecd8;border:2px solid #f2b84b;border-radius:999px;padding:9px 14px;font:600 14px/1 system-ui,Segoe UI,Roboto,sans-serif;cursor:pointer;box-shadow:0 4px 18px #0006}' +
    '#mc-box{position:fixed;left:14px;bottom:62px;z-index:9996;width:min(340px,calc(100vw - 28px));height:min(440px,calc(100vh - 120px));background:#0f1424;color:#f4ecd8;border:2px solid #f2b84b;border-radius:14px;display:none;flex-direction:column;font:14px/1.4 system-ui,Segoe UI,Roboto,sans-serif;box-shadow:0 8px 30px #0008}' +
    '#mc-box.on{display:flex}#mc-h{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;border-bottom:1px solid #2a3150;font-weight:700}#mc-h button{background:none;border:0;color:#f4ecd8;font-size:18px;cursor:pointer}' +
    '#mc-list{flex:1;overflow-y:auto;padding:8px 12px;display:flex;flex-direction:column;gap:6px}.mc-m{word-wrap:break-word}.mc-m b{color:#f2b84b;margin-right:4px}.mc-m .mc-a{opacity:.0;font-size:11px;margin-left:6px;color:#9aa3c7;background:none;border:0;cursor:pointer;padding:0}.mc-m:hover .mc-a,.mc-m:focus-within .mc-a{opacity:1}' +
    '#mc-note{font-size:11px;color:#9aa3c7;padding:4px 12px}#mc-f{display:flex;gap:6px;padding:8px 10px;border-top:1px solid #2a3150}#mc-f input{min-width:0;background:#171d33;color:#f4ecd8;border:1px solid #2a3150;border-radius:8px;padding:7px 8px;font:inherit;font-size:16px}#mc-name{width:84px}#mc-in{flex:1}#mc-f button{background:#f2b84b;color:#0f1424;border:0;border-radius:8px;padding:7px 10px;font-weight:700;cursor:pointer}' +
    '#mc-st{font-size:12px;color:#f2b84b;padding:0 12px 6px;min-height:6px}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var btn = document.createElement('button'); btn.id = 'mc-btn'; btn.type = 'button'; btn.textContent = '💬 ' + S[0];
  var box = document.createElement('div'); box.id = 'mc-box'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', S[0]);
  box.innerHTML = '<div id="mc-h"><span></span><button type="button" aria-label="Close">×</button></div><div id="mc-list" aria-live="polite"></div><div id="mc-note"></div><div id="mc-st"></div>' +
    '<form id="mc-f"><input id="mc-name" maxlength="16" autocomplete="off"><input id="mc-in" maxlength="200" autocomplete="off"><button type="submit"></button></form>';
  document.body.appendChild(btn); document.body.appendChild(box);
  var $ = function (s) { return box.querySelector(s); };
  $('#mc-h span').textContent = '💬 ' + S[0]; $('#mc-note').textContent = S[4];
  $('#mc-name').value = name; $('#mc-name').placeholder = S[3]; $('#mc-name').setAttribute('aria-label', S[3]);
  $('#mc-in').placeholder = S[1]; $('#mc-in').setAttribute('aria-label', S[1]); $('#mc-f button').textContent = S[2];
  var list = $('#mc-list');
  function say(t) { $('#mc-st').textContent = t || ''; }

  function api(path, body) {
    return fetch(SB + path, { method: body ? 'POST' : 'GET', headers: { apikey: K, 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  function row(m) {
    if (muted[m.name]) return;
    var d = document.createElement('div'); d.className = 'mc-m';
    var b = document.createElement('b'); b.textContent = m.name; d.appendChild(b);
    d.appendChild(document.createTextNode(m.body));
    var r = document.createElement('button'); r.type = 'button'; r.className = 'mc-a'; r.textContent = S[9];
    r.onclick = function () { api('/rest/v1/rpc/chat_report', { p_id: m.id, p_client: me }).then(function () { say(S[11]); d.remove(); }); };
    var u = document.createElement('button'); u.type = 'button'; u.className = 'mc-a'; u.textContent = S[10];
    u.onclick = function () { muted[m.name] = 1; store('maiga_chat_mute', JSON.stringify(muted)); load(true); };
    d.appendChild(r); d.appendChild(u); list.appendChild(d);
  }
  function load(reset) {
    if (reset) { lastId = 0; list.textContent = ''; }
    api('/rest/v1/chat_messages?select=id,name,body&room=eq.' + ROOM + '&id=gt.' + lastId + '&order=id.desc&limit=60').then(function (rows) {
      if (!rows) return;
      var near = list.scrollHeight - list.scrollTop - list.clientHeight < 60;
      rows.reverse().forEach(function (m) { lastId = Math.max(lastId, m.id); row(m); });
      if (rows.length) { if (pending) { pending = 0; say(''); } }
      if (!list.children.length) { var e = document.createElement('div'); e.className = 'mc-m'; e.style.opacity = '.6'; e.textContent = S[12]; e.setAttribute('data-empty', '1'); list.appendChild(e); }
      else { var em = list.querySelector('[data-empty]'); if (em && list.children.length > 1) em.remove(); }
      if (near || reset) list.scrollTop = list.scrollHeight;
    });
  }
  function status() {
    api('/rest/v1/rpc/chat_status', {}).then(function (s) {
      var off = s !== 'open'; $('#mc-in').disabled = off; $('#mc-f button').disabled = off; say(off ? S[5] : (pending ? S[6] : ''));
    });
  }
  function toggle(on) {
    open = on; box.classList.toggle('on', on);
    clearInterval(timer);
    if (on) { status(); load(true); timer = setInterval(function () { if (!document.hidden) load(false); }, 4000); setTimeout(function () { $('#mc-in').focus(); }, 50); }
  }
  btn.onclick = function () { toggle(!open); };
  $('#mc-h button').onclick = function () { toggle(false); };
  $('#mc-f').onsubmit = function (e) {
    e.preventDefault();
    var n = $('#mc-name').value.replace(/[^A-Za-z0-9 _-]/g, '').trim().slice(0, 16), t = $('#mc-in').value.trim().slice(0, 200);
    if (!n || !t) return;
    store('maiga_chat_name', n);
    api('/rest/v1/rpc/chat_send', { p_room: ROOM, p_name: n, p_body: t, p_client: me }).then(function (r) {
      if (r === 'queued') { $('#mc-in').value = ''; pending = 1; say(S[6]); setTimeout(function () { if (pending) { pending = 0; say(S[7]); } }, 20000); }
      else if (r === 'slow' || r === 'busy') say(S[8]);
      else if (r === 'closed') status();
    });
  };
})();
