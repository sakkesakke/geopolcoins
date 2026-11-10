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
  const RULES = [
    { kind: 'iban', re: /\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,3})?\b/g, ok: ibanOk, tag: '[IBAN]' },
    { kind: 'card', re: /\b(?:\d[ -]?){12,18}\d\b/g, ok: luhn, tag: '[CARD]' },
    { kind: 'id', re: /\b\d{2}\.?\d{2}\.?\d{2}[-.]?\d{3}\.?\d{2}\b/g, ok: rrnOk, tag: '[ID]' },
    { kind: 'email', re: /\b[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}\b/g, ok: () => true, tag: '[EMAIL]', min: 2 },
    { kind: 'secret', re: /\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abpr]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})|-----BEGIN [A-Z ]*PRIVATE KEY-----/g, ok: () => true, tag: '[SECRET]' },
    { kind: 'label', re: /\b(?:strictly confidential|confidential|internal use only|do not distribute|vertrouwelijk|strikt vertrouwelijk|intern gebruik|niet verspreiden|confidentiel|usage interne|ne pas diffuser|vertraulich)\b/gi, ok: () => true, tag: null }
  ];
  function scan(text) {
    const t = String(text || ''), out = [], taken = [];
    if (t.length > MAX) return [{ kind: 'long', start: 0, end: 0 }];
    for (const r of RULES) {
      const hits = []; let seen = 0;
      for (const m of t.matchAll(r.re)) {
        if (++seen > SEEN || hits.length >= HITS) break;
        const a = m.index, b = a + m[0].length;
        if (taken.some(([x, y]) => a < y && b > x) || !r.ok(m[0])) continue;   // a number counts only once (IBAN before card)
        hits.push({ kind: r.kind, start: a, end: b });
      }
      if (hits.length >= (r.min || 1)) { hits.forEach(h => { out.push(h); taken.push([h.start, h.end]); }); }
    }
    return out;
  }
  function mask(text) {
    const tag = Object.fromEntries(RULES.map(r => [r.kind, r.tag]).concat([['long', null]]));
    const s = String(text || ''), parts = []; let at = 0;
    scan(s).filter(f => tag[f.kind]).sort((x, y) => x.start - y.start).forEach(f => { parts.push(s.slice(at, f.start), tag[f.kind]); at = f.end; });
    parts.push(s.slice(at));
    return parts.join('');
  }
  const api = { scan, mask };
  if (typeof module === 'object' && module.exports) module.exports = api; else root.HOPaste = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
