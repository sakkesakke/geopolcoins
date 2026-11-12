/* Mindveto - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
/* Paste guard: runs only on AI sites. When you paste text with a bank number, card number, several e-mail addresses,
   a secret key, an ID number or a "confidential" label, it asks first. The check happens on this device; the pasted
   text is never stored or sent. */
(() => {
  const api = globalThis.browser || globalThis.chrome;
  let on = true, words = [];
  api.storage.local.get(['guard', 'words']).then(s => { on = s.guard !== false; words = Array.isArray(s.words) ? s.words : []; }, () => {});
  api.storage.onChanged.addListener((c, area) => {
    if (area !== 'local') return;
    if (c.guard) on = c.guard.newValue !== false;
    if (c.words) words = Array.isArray(c.words.newValue) ? c.words.newValue : [];
  });

  const L = (navigator.language || 'en').slice(0, 2);
  const TX = {
    en: { h: 'Wait: this may be private', p: 'What you are pasting into this AI site seems to contain:', no: 'Don’t paste', mask: 'Paste without the private parts', yes: 'Paste anyway',
      k: { iban: 'a bank account number (IBAN)', card: 'a payment card number', id: 'a national ID number', email: 'a list of e-mail addresses', secret: 'a password or secret key', label: 'a “confidential” label', long: 'a very long text that is too big to check', custom: 'a word from your own private list' },
      f: 'Mindveto paste guard · checked on your device, nothing is sent' },
    nl: { h: 'Wacht: dit kan privé zijn', p: 'Wat je in deze AI-site plakt, lijkt dit te bevatten:', no: 'Niet plakken', mask: 'Plakken zonder de privé-stukken', yes: 'Toch plakken',
      k: { iban: 'een bankrekeningnummer (IBAN)', card: 'een betaalkaartnummer', id: 'een rijksregisternummer', email: 'een lijst e-mailadressen', secret: 'een wachtwoord of geheime sleutel', label: 'het label “vertrouwelijk”', long: 'een heel lange tekst die te groot is om te controleren', custom: 'een woord uit je eigen privélijst' },
      f: 'Mindveto plakbewaker · gecontroleerd op je toestel, er wordt niets verstuurd' },
    fr: { h: 'Attendez : ceci peut être privé', p: 'Ce que vous collez dans ce site d’IA semble contenir :', no: 'Ne pas coller', mask: 'Coller sans les parties privées', yes: 'Coller quand même',
      k: { iban: 'un numéro de compte (IBAN)', card: 'un numéro de carte de paiement', id: 'un numéro de registre national', email: 'une liste d’adresses e-mail', secret: 'un mot de passe ou une clé secrète', label: 'la mention « confidentiel »', long: 'un très long texte, trop grand pour être vérifié', custom: 'un mot de votre propre liste privée' },
      f: 'Garde-collage Mindveto · vérifié sur votre appareil, rien n’est envoyé' }
  };
  const t = TX[L] || TX.en;
  let open = false, cur = null;

  function insert(target, saved, text) {
    target.focus();
    if (saved.range) { const s = getSelection(); s.removeAllRanges(); s.addRange(saved.range); }
    else if (saved.start != null && target.setSelectionRange) target.setSelectionRange(saved.start, saved.end);
    if (document.execCommand('insertText', false, text)) return;   // works with chat boxes built on React/ProseMirror
    if (target.setRangeText) { target.setRangeText(text, target.selectionStart, target.selectionEnd, 'end'); target.dispatchEvent(new Event('input', { bubbles: true })); }
  }

  function ask(found, done) {
    open = true;
    const host = document.createElement('div');
    host.style.cssText = 'all:initial;position:fixed;inset:0;z-index:2147483647';
    const sh = host.attachShadow({ mode: 'closed' });
    const st = document.createElement('style');
    st.textContent = '.bg{position:fixed;inset:0;background:rgba(24,36,31,.45);display:flex;align-items:center;justify-content:center;font:15px/1.5 system-ui,sans-serif}' +
      '.box{background:#f6f7f3;color:#18241f;max-width:420px;margin:16px;padding:22px;border-radius:12px;border-top:6px solid #5b3ce0;box-shadow:0 1px 2px rgba(24,36,31,.08),0 16px 40px rgba(24,36,31,.28)}' +
      'h2{margin:0 0 8px;font-size:19px;font-weight:600;color:#18241f}ul{margin:8px 0 14px;padding-left:20px}button{display:block;width:100%;margin-top:8px;padding:11px;border-radius:10px;border:2px solid #18241f;font:600 15px system-ui,sans-serif;cursor:pointer}' +
      '.no{background:#18241f;color:#fff}.mask{background:transparent;color:#18241f}.yes{background:transparent;color:#4a5753;border-color:transparent;text-decoration:underline}small{display:block;margin-top:12px;color:#4a5753;font-size:12px}button:focus-visible{outline:3px solid #5b3ce0;outline-offset:2px}';
    const bg = document.createElement('div'); bg.className = 'bg';
    const box = document.createElement('div'); box.className = 'box'; box.setAttribute('role', 'alertdialog'); box.setAttribute('aria-modal', 'true');
    const h = document.createElement('h2'); h.textContent = t.h; box.setAttribute('aria-label', t.h);
    const p = document.createElement('div'); p.textContent = t.p;
    const ul = document.createElement('ul');
    [...new Set(found.map(f => f.kind))].forEach(k => { const li = document.createElement('li'); li.textContent = t.k[k]; ul.appendChild(li); });
    const btn = (cls, label, v) => { const b = document.createElement('button'); b.type = 'button'; b.className = cls; b.textContent = label; b.onclick = () => close(v); return b; };
    const bNo = btn('no', t.no, 'no'), canMask = !found.some(f => f.kind === 'long') && found.some(f => f.kind !== 'label');
    const sm = document.createElement('small'); sm.textContent = t.f;
    box.append(h, p, ul, bNo); if (canMask) box.append(btn('mask', t.mask, 'mask')); box.append(btn('yes', t.yes, 'yes'), sm);
    bg.appendChild(box); sh.append(st, bg);
    const key = e => { if (e.key === 'Escape') { e.stopPropagation(); close('no'); } };
    let closed = false;
    function drop() { closed = true; removeEventListener('keydown', key, true); host.remove(); if (cur && cur.host === host) { open = false; cur = null; } }
    function close(v) { if (closed) return; drop(); done(v); }
    addEventListener('keydown', key, true);
    (document.body || document.documentElement).appendChild(host); cur = { host, drop };
    bNo.focus();
  }

  addEventListener('paste', e => {
    if (open && cur && !cur.host.isConnected) cur.drop();   // the page removed our dialog: clean up and ask again (nothing was pasted)
    if (open) { e.preventDefault(); e.stopImmediatePropagation(); return; }   // one question at a time
    if (!on || !e.isTrusted || !e.clipboardData) return;
    const text = e.clipboardData.getData('text/plain');
    if (!text || text.length < 6 || !globalThis.HOPaste) return;
    const found = HOPaste.scan(text, words);
    if (!found.length) return;
    e.preventDefault(); e.stopImmediatePropagation();
    const target = e.target && e.target.closest ? (e.target.closest('textarea,input,[contenteditable],[contenteditable=""],[contenteditable="true"]') || e.target) : document.activeElement;
    const sel = getSelection(), saved = {};
    if (target && typeof target.selectionStart === 'number') { saved.start = target.selectionStart; saved.end = target.selectionEnd; }
    else if (sel && sel.rangeCount) saved.range = sel.getRangeAt(0).cloneRange();
    ask(found, v => {
      try { api.runtime.sendMessage({ t: 'paste', v }); } catch (err) { /* extension reloaded */ }
      if (v === 'yes') insert(target, saved, text); else if (v === 'mask') insert(target, saved, HOPaste.mask(text, words)); else target.focus && target.focus();
    });
  }, true);
})();
