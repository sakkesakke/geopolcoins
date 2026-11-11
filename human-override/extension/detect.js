/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
/* Paste guard detector: finds bank numbers, card numbers, lists of e-mail addresses, secret keys, ID numbers and
   "confidential" labels in text. Runs only on this device; nothing is stored or sent. */
(function (root) {
  const MAX = 200000;    // longer pastes are not scanned; the guard asks first instead ("too long to check")
  const HITS = 500, SEEN = 2000;   // limits per rule, so crafted text can never freeze the page
  const mod97 = s => { let r = 0; for (const ch of s) r = (r * 10 + (ch.charCodeAt(0) - 48)) % 97; return r; };
  function ibanOk(raw) {
    const s = raw.replace(/\s/g, '').toUpperCase();
    if (s.length < 15 || s.length > 34) return false;
    const n = (s.slice(4) + s.slice(0, 4)).replace(/[A-Z]/g, c => String(c.charCodeAt(0) - 55));
    return mod97(n) === 1;
  }
  function luhn(raw) {
    const d = raw.replace(/\D/g, '');
    if (d.length < 13 || d.length > 19 || /^(\d)\1+$/.test(d)) return false;
    let sum = 0;
    for (let i = 0; i < d.length; i++) { let x = +d[d.length - 1 - i]; if (i % 2) { x *= 2; if (x > 9) x -= 9; } sum += x; }
    return sum % 10 === 0;
  }
  function rrnOk(raw) {   // Belgian national register number: 9 digits + 2 check digits (born from 2000: "2" in front)
    const d = raw.replace(/\D/g, ''), base = d.slice(0, 9), chk = +d.slice(9);
    return 97 - mod97(base) === chk || 97 - mod97('2' + base) === chk;
  }
  // IBAN length per country, so an IBAN is found exactly even when other text follows it ("... 6769 BIC GEBABEBB").
  const IBAN_LEN = { AD: 24, AE: 23, AL: 28, AT: 20, AZ: 28, BA: 20, BE: 16, BG: 22, BH: 22, BR: 29, BY: 28, CH: 21, CR: 22, CY: 28, CZ: 24, DE: 22, DK: 18, DO: 28, EE: 20, EG: 29, ES: 24,
    FI: 18, FO: 18, FR: 27, GB: 22, GE: 22, GI: 23, GL: 18, GR: 27, GT: 28, HR: 21, HU: 28, IE: 22, IL: 23, IS: 26, IT: 27, JO: 30, KW: 30, KZ: 20, LB: 28, LI: 21, LT: 20, LU: 20, LV: 21,
    MA: 28, MC: 27, MD: 24, ME: 22, MK: 19, MT: 31, MU: 30, NL: 18, NO: 15, PK: 24, PL: 28, PT: 25, QA: 29, RO: 24, RS: 22, SA: 24, SE: 24, SI: 19, SK: 24, SM: 27, TN: 24, TR: 26, UA: 29, VG: 24, XK: 20 };
  function* ibans(t) {
    const re = /\b([A-Z]{2})\d{2}/g; let m;
    while ((m = re.exec(t))) {
      const len = IBAN_LEN[m[1]]; if (!len) continue;
      let i = m.index, n = 0, end = i;
      while (n < len && i < t.length) {
        const c = t.charCodeAt(i);
        if ((c >= 48 && c <= 57) || (c >= 65 && c <= 90)) { n++; i++; end = i; }
        else if (c === 32 && t.charCodeAt(i - 1) !== 32) i++;   // one space between groups
        else break;
      }
      if (n === len && !/[A-Za-z0-9]/.test(t.charAt(end))) { yield { index: m.index, 0: t.slice(m.index, end) }; re.lastIndex = end; }
    }
  }
  const RULES = [
    { kind: 'iban', find: ibans, ok: ibanOk, tag: '[IBAN]' },
    { kind: 'card', re: /\b(?:\d[ -]?){12,18}\d\b/g, ok: luhn, tag: '[CARD]' },
    { kind: 'id', re: /\b\d{2}\.?\d{2}\.?\d{2}[-.]?\d{3}\.?\d{2}\b/g, ok: rrnOk, tag: '[ID]' },
    { kind: 'email', re: /\b[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}\b/g, ok: () => true, tag: '[EMAIL]', min: 2 },
    { kind: 'secret', re: /\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abpr]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})|-----BEGIN [A-Z ]*PRIVATE KEY-----/g, ok: () => true, tag: '[SECRET]' },
    { kind: 'label', re: /\b(?:strictly confidential|confidential|internal use only|do not distribute|vertrouwelijk|strikt vertrouwelijk|intern gebruik|niet verspreiden|confidentiel|usage interne|ne pas diffuser|vertraulich)\b/gi, ok: () => true, tag: null }
  ];
  // Own private words (project names, customer numbers...): plain text, compared without capitals, never as a pattern.
  function cleanWords(words) {
    const out = [];
    for (const w of Array.isArray(words) ? words : []) {
      if (typeof w !== 'string') continue;
      const v = w.trim().toLowerCase();
      if (v.length >= 3 && v.length <= 60 && !out.includes(v)) out.push(v);
      if (out.length >= 100) break;
    }
    return out.sort((a, b) => b.length - a.length);   // longest first, so "project zeus" wins over "zeus"
  }
  function scan(text, words) {
    const t = String(text || ''), out = [], taken = []; let cut = false;   // cut = a limit was reached: not everything could be checked
    if (t.length > MAX) return [{ kind: 'long', start: 0, end: 0 }];
    for (const r of RULES) {
      const hits = []; let seen = 0;
      for (const m of (r.find ? r.find(t) : t.matchAll(r.re))) {
        if (++seen > SEEN || hits.length >= HITS) { cut = true; break; }
        const a = m.index, b = a + m[0].length;
        if (taken.some(([x, y]) => a < y && b > x) || !r.ok(m[0])) continue;   // a number counts only once (IBAN before card)
        hits.push({ kind: r.kind, start: a, end: b });
      }
      if (hits.length >= (r.min || 1)) { hits.forEach(h => { out.push(h); if (r.tag) taken.push([h.start, h.end]); }); }
    }
    const list = cleanWords(words);
    if (list.length) {
      let low = t.toLowerCase(), n = 0;
      if (low.length !== t.length) low = t.replace(/[A-Z]/g, c => c.toLowerCase());   // rare letters change length in lower case: keep positions exact
      for (const w of list) {
        for (let i = low.indexOf(w); i !== -1; i = low.indexOf(w, i + w.length)) {
          if (n >= HITS) { cut = true; break; }
          const a = i, b = i + w.length;
          if (taken.some(([x, y]) => a < y && b > x)) continue;
          out.push({ kind: 'custom', start: a, end: b }); taken.push([a, b]); n++;
        }
      }
    }
    if (cut) out.push({ kind: 'long', start: 0, end: 0 });   // the guard then offers no "paste without the private parts"
    return out;
  }
  function mask(text, words) {
    const tag = Object.fromEntries(RULES.map(r => [r.kind, r.tag]).concat([['long', null], ['custom', '[PRIVATE]']]));
    const s = String(text || ''), parts = []; let at = 0;
    scan(s, words).filter(f => tag[f.kind]).sort((x, y) => x.start - y.start).forEach(f => { parts.push(s.slice(at, f.start), tag[f.kind]); at = f.end; });
    parts.push(s.slice(at));
    return parts.join('');
  }
  const api = { scan, mask, cleanWords };
  if (typeof module === 'object' && module.exports) module.exports = api; else root.HOPaste = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
