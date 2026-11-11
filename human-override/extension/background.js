/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
/* Human Override: blocks AI services in this browser with declarativeNetRequest.
   Nothing about you is sent anywhere. Network requests: a daily download of the public block list and, only when this
   browser joined a class, a question once a minute whether the teacher's exam mode is on (only the class code is sent).
   The public block list comes
   from geopolcoins.xyz (no data about you is included). */
const api = globalThis.browser || globalThis.chrome;
const LIST_URL = 'https://geopolcoins.xyz/human-override/lists.json';
const DOMAIN = /^(?=.{3,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,24}$/;
const PATH = /^([a-z0-9-]{1,63}\.)+[a-z]{2,24}\/[a-z0-9\-\/_.]{1,80}$/;
// Big everyday sites that a block list may never block (protects against a broken or tampered list).
const PROTECT = new Set(['google.com', 'www.google.com', 'youtube.com', 'gmail.com', 'microsoft.com', 'live.com', 'outlook.com', 'office.com', 'apple.com', 'icloud.com',
  'github.com', 'wikipedia.org', 'amazon.com', 'facebook.com', 'instagram.com', 'whatsapp.com', 'x.com', 'twitter.com', 'linkedin.com', 'bing.com', 'duckduckgo.com',
  'geopolcoins.xyz', 'mozilla.org', 'firefox.com', 'chrome.google.com', 'microsoftedge.microsoft.com', 'addons.mozilla.org', 'gov.uk', 'europa.eu']);
const MAX_REGEX = 450;   // plus the translate.goog copies, stays below the ~1000 regex rules browsers allow
const DEFAULTS = { on: true, cats: { chat: true, search: true, image: true, media: true, writing: true, coding: true, record: true }, custom: [], allow: [], allowSvc: [], words: [], klass: null, exam: { until: 0 }, pin: null, count: 0, day: '', today: 0, guard: true, log: [], alert: false,
  sched: { on: false, days: [1, 2, 3, 4, 5], from: '08:00', to: '16:00' } };
const HHMM = /^([01][0-9]|2[0-3]):[0-5][0-9]$/;
// Exam mode (only when this browser joined a class): once a minute the extension asks how long the teacher's exam still
// lasts. Only the class code is sent; no name, no browsing data.
const EXAM_URL = 'https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/exam_status';
const EXAM_KEY = 'sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN';   // public by design (read-only question)
const CODE = /^[A-HJ-NP-Z2-9]{8}$/;
const REMOVED_URL = 'https://geopolcoins.xyz/human-override-removed.html';
const ALERT = new Set(['pinbad', 'pinlock']);   // these light up a red "!" on the icon until the popup is opened

// Tamper log: what happened and when (never page content). Last 50 events, only on this device.
// One queue per kind of work ('log', 'pin', 'apply'): jobs of the same kind run one after the other, never mixed.
const chains = {};
function serial(name, fn) { const r = (chains[name] || Promise.resolve()).then(fn); chains[name] = r.catch(() => {}); return r; }
function note(k) { return serial('log', () => noteNow(k)); }
async function noteNow(k) {
  const s = await api.storage.local.get(['log', 'alert']);
  const log = (Array.isArray(s.log) ? s.log : []).concat({ k, at: Date.now() }).slice(-50);
  await api.storage.local.set({ log, alert: !!s.alert || ALERT.has(k) });
  badge();
}
async function badge() {
  const st = await getState(), act = active(st);
  api.action.setBadgeText({ text: st.alert ? '!' : examOn(st) ? 'EX' : !st.on ? 'OFF' : act ? '' : 'zz' });
  api.action.setBadgeBackgroundColor({ color: '#c0392b' });
}

async function getState() { const s = await api.storage.local.get(null); return Object.assign({}, DEFAULTS, s, { cats: Object.assign({}, DEFAULTS.cats, s.cats || {}), sched: Object.assign({}, DEFAULTS.sched, s.sched || {}) }); }

// Schedule: block only on the chosen days between "from" and "to" (a window may run past midnight, e.g. 21:00-07:00).
function mins(hhmm) { const [h, m] = hhmm.split(':').map(Number); return h * 60 + m; }
function inWindow(sc, d = new Date()) {
  const now = d.getHours() * 60 + d.getMinutes(), f = mins(sc.from), t = mins(sc.to), day = d.getDay(), prev = (day + 6) % 7;
  if (f === t) return sc.days.includes(day);                         // whole day
  if (f < t) return sc.days.includes(day) && now >= f && now < t;
  return (sc.days.includes(day) && now >= f) || (sc.days.includes(prev) && now < t);   // past midnight
}
function examOn(st) { return !!st.klass && !!st.exam && Date.now() < st.exam.until; }
function active(st) { return examOn(st) || (st.on && (!st.sched.on || inWindow(st.sched))); }
function mode(st) { return examOn(st) ? 'exam' : active(st) ? 'on' : 'off'; }   // rules are rebuilt whenever this changes

async function examAsk(code) {   // seconds left, 0 = no exam, -1 = unknown class, null = could not ask
  try {
    const r = await fetch(EXAM_URL, { method: 'POST', cache: 'no-store', credentials: 'omit', headers: { apikey: EXAM_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ p_code: code }) });
    if (!r.ok) return null;
    const n = await r.json();
    return Number.isInteger(n) && n >= -1 && n <= 14400 ? n : null;
  } catch (e) { return null; }
}
async function examPoll() {
  const st = await getState();
  if (!st.klass) return;
  const left = await examAsk(st.klass);
  if (left === null) return;                       // offline: keep what we know, a running exam simply runs out
  if ((await getState()).klass !== st.klass) return;   // joined or left another class while we were asking: this answer is stale
  const was = examOn(st), until = left > 0 ? Date.now() + left * 1000 : 0;   // counted from the server's answer, so changing the PC clock does not end an exam
  await api.storage.local.set({ exam: { until } });
  const now = until > Date.now();
  if (now !== was) { await note(now ? 'examon' : 'examoff'); await apply(); }
}

async function bundled() { const r = await fetch(api.runtime.getURL('lists.json')); return r.json(); }
// Known AI services for the "approved AI" picker. Always read from the list shipped inside the extension:
// the daily online list can add blocked sites, but can never decide what gets unblocked.
async function services() {
  const sv = (await bundled()).services || {}, out = {};
  for (const [k, v] of Object.entries(sv)) {
    if (!/^[a-z0-9]{2,20}$/.test(k) || !v || typeof v.name !== 'string') continue;
    out[k] = { name: v.name.slice(0, 40), domains: (v.domains || []).filter(d => DOMAIN.test(d)), paths: (v.paths || []).filter(p => PATH.test(p)) };
  }
  return out;
}
async function lists() { const s = await api.storage.local.get('remote'); return (s.remote && s.remote.categories) ? s.remote : bundled(); }

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

// One rebuild at a time: two rebuilds at once (popup change + minute check) would write half of each other's rules.
function apply() { return serial('apply', applyNow); }
async function applyNow() {
  const st = await getState(), L = await lists();
  const old = await api.declarativeNetRequest.getDynamicRules();
  const rules = [], act = active(st), ex = examOn(st);   // during an exam every category is blocked and nothing is "approved"
  if (act) {
    const SV = await services(), allow = new Set(ex ? [] : st.allow), okPaths = new Set();
    if (!ex) for (const k of st.allowSvc) if (SV[k]) { SV[k].domains.forEach(d => allow.add(d)); SV[k].paths.forEach(p => okPaths.add(p)); }
    const allowed = d => { for (const a of allow) if (d === a || d.endsWith('.' + a)) return true; return false; };   // an allowed site includes its sub-sites
    let doms = [], paths = [];
    for (const [k, c] of Object.entries(L.categories || {})) {
      if (!ex && !st.cats[k]) continue;
      doms = doms.concat((c.domains || []).filter(d => DOMAIN.test(d)));
      paths = paths.concat((c.paths || []).filter(p => PATH.test(p)));
    }
    doms = doms.concat(st.custom.filter(d => DOMAIN.test(d)));
    doms = [...new Set(doms)].filter(d => !allowed(d) && !(PROTECT.has(d) && !st.custom.includes(d)));
    paths = [...new Set(paths)].filter(p => !allowed(p.split('/')[0]) && !okPaths.has(p) && !okPaths.has(p.replace(/^www\./, '')));
    const page = api.runtime.getURL('blocked.html');
    let id = 1;
    const viaRegex = doms.slice(0, MAX_REGEX - Math.min(paths.length, 100)), rest = doms.slice(viaRegex.length);
    for (const d of viaRegex) {
      rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },
        condition: { regexFilter: '^https?://([a-z0-9-]+\\.)*' + esc(d) + '\\.?(:[0-9]+)?(/.*)?$', resourceTypes: ['main_frame'] } });
    }
    for (const p of paths.slice(0, 100)) {
      rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },
        condition: { regexFilter: '^https?://([a-z0-9-]+\\.)*' + esc(p) + '([/?#].*)?$', resourceTypes: ['main_frame'] } });
    }
    // Google Translate can show any site through <site-with-dashes>.translate.goog: block those copies too
    for (const d of viaRegex.slice(0, 300)) {
      const t = d.replace(/-/g, '--').replace(/\./g, '-');
      rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },
        condition: { regexFilter: '^https?://' + esc(t) + '\\.translate\\.goog\\.?(/.*)?$', resourceTypes: ['main_frame', 'sub_frame'] } });
    }
    if (ex || st.cats.search) rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },   // Google "AI Mode"
      condition: { regexFilter: '^https?://(www\\.)?google\\.[a-z.]{2,12}/search\\?(.*&)?udm=50(&.*)?$', resourceTypes: ['main_frame'] } });
    if (rest.length) rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { extensionPath: '/blocked.html' } },
      condition: { requestDomains: rest, resourceTypes: ['main_frame'] } });
    // allowed sites win over every block rule (for example: chat.mistral.ai allowed while mistral.ai is on the list)
    if (allow.size) rules.push({ id: id++, priority: 2, action: { type: 'allow' },
      condition: { requestDomains: [...allow], resourceTypes: ['main_frame', 'sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other'] } });
    if (doms.length) rules.push({ id: id++, priority: 1, action: { type: 'block' },
      condition: { requestDomains: doms, resourceTypes: ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other'] } });
  }
  await api.declarativeNetRequest.updateDynamicRules({ removeRuleIds: old.map(r => r.id), addRules: rules });
  await api.storage.local.set({ act: mode(st) });
  await badge();
}

async function refreshList() {
  try {
    const r = await fetch(LIST_URL, { cache: 'no-store', credentials: 'omit' });
    if (!r.ok) return;
    const j = await r.json();
    if (!j || typeof j.categories !== 'object' || JSON.stringify(j).length > 200000) return;
    let n = 0;
    for (const c of Object.values(j.categories)) {
      if (!Array.isArray(c.domains) || !c.domains.every(d => DOMAIN.test(d) && !PROTECT.has(d))) return;
      if (c.paths && (!Array.isArray(c.paths) || !c.paths.every(p => PATH.test(p)))) return;
      n += c.domains.length;
    }
    if (n > 3000) return;
    await api.storage.local.set({ remote: j });
    await apply();
  } catch (e) { /* offline: keep the list we have */ }
}

async function kdf(salt, pin) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(pin), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: new TextEncoder().encode(salt), iterations: 210000 }, key, 256);
  return [...new Uint8Array(bits)].map(x => x.toString(16).padStart(2, '0')).join('');
}
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
function unlocked(pin) { return serial('pin', () => unlockedNow(pin)); }   // one PIN try at a time, so the lockout cannot be raced
async function unlockedNow(pin) {
  const st = await getState();
  if (!st.pin) return true;
  const lock = (await api.storage.local.get('lock')).lock || { fails: 0, until: 0 };
  if (Date.now() < lock.until) return 'locked';
  if (typeof pin !== 'string' || pin.length < 4 || pin.length > 12) return false;
  const ok = st.pin.kdf === 'pbkdf2' ? (await kdf(st.pin.salt, pin)) === st.pin.hash : (await sha(st.pin.salt + pin)) === st.pin.hash;
  if (ok) {
    const ch = { lock: { fails: 0, until: 0 } };
    if (st.pin.kdf !== 'pbkdf2') ch.pin = { kdf: 'pbkdf2', salt: st.pin.salt, hash: await kdf(st.pin.salt, pin) };   // upgrade old PINs
    await api.storage.local.set(ch); return true;
  }
  lock.fails += 1;
  if (lock.fails >= 5) lock.until = Date.now() + Math.min(3600000, 60000 * Math.pow(2, lock.fails - 5));
  await api.storage.local.set({ lock });
  await note(lock.fails >= 5 ? 'pinlock' : 'pinbad');
  return false;
}

api.runtime.onInstalled.addListener(async (d) => { await apply().catch(() => {}); refreshList();
  setUninstall();
  if (d && d.reason === 'install') api.tabs.create({ url: api.runtime.getURL('welcome.html') }); api.alarms.create('list', { periodInMinutes: 720 }); api.alarms.create('sched', { periodInMinutes: 1 }); });
function setUninstall() { try { const r = api.runtime.setUninstallURL(REMOVED_URL); if (r && r.catch) r.catch(() => {}); } catch (e) { /* not supported */ } }
api.runtime.onStartup && api.runtime.onStartup.addListener(() => { setUninstall(); api.alarms.create('sched', { periodInMinutes: 1 }); apply().catch(() => {}).then(() => examPoll()).catch(() => {}); });
api.alarms.onAlarm.addListener(async a => {
  if (a.name === 'list') refreshList();
  if (a.name === 'sched') { await examPoll().catch(() => {}); const st = await getState(), was = (await api.storage.local.get('act')).act; if (mode(st) !== was) apply().catch(() => {}); }   // only rebuild rules when the schedule flips
});

api.runtime.onMessage.addListener((m, sender, reply) => {
  if (!m || typeof m !== 'object' || sender.id !== api.runtime.id) return false;   // only this extension
  const own = typeof sender.url === 'string' && sender.url.startsWith(api.runtime.getURL(''));
  if (!own && m.t !== 'paste') return false;   // content scripts on AI sites may only report a paste choice
  (async () => {
    const st = await getState();
    if (m.t === 'state') return reply({ guard: st.guard !== false, log: st.log.slice(-10).reverse(), alert: !!st.alert, on: st.on, active: active(st), sched: st.sched, cats: st.cats, klass: st.klass, examLeft: examOn(st) ? Math.ceil((st.exam.until - Date.now()) / 60000) : 0, custom: st.custom, allow: st.allow, allowSvc: st.allowSvc, words: st.words, services: Object.fromEntries(Object.entries(await services()).map(([k, v]) => [k, v.name])), hasPin: !!st.pin, count: st.count, today: st.day === new Date().toISOString().slice(0, 10) ? st.today : 0, cats_meta: Object.fromEntries(Object.entries((await lists()).categories).map(([k, c]) => [k, (c.domains || []).length + (c.paths || []).length])) });
    if (m.t === 'blocked') {
      const day = new Date().toISOString().slice(0, 10);
      await api.storage.local.set({ count: st.count + 1, day, today: (st.day === day ? st.today : 0) + 1 });
      return reply({ ok: true });
    }
    if (m.t === 'paste') { if (['no', 'mask', 'yes'].includes(m.v)) await note('paste_' + m.v); return reply({ ok: true }); }
    // every change below needs the PIN if one is set
    const needsPin = ['set', 'pin', 'seen'].includes(m.t);
    if (needsPin) { const u = await unlocked(m.pin); if (u !== true) return reply({ ok: false, err: u === 'locked' ? 'locked' : 'pin' }); }
    if (m.t === 'seen') { await api.storage.local.set({ alert: false }); await badge(); return reply({ ok: true }); }   // clearing the red ! needs the PIN
    if (m.t === 'set') {
      const ch = {};
      if (typeof m.on === 'boolean') ch.on = m.on;
      if (typeof m.guard === 'boolean') ch.guard = m.guard;
      if (m.cats && typeof m.cats === 'object') ch.cats = Object.fromEntries(Object.keys(DEFAULTS.cats).map(k => [k, m.cats[k] !== false]));
      if (Array.isArray(m.custom)) ch.custom = [...new Set(m.custom.map(d => String(d).toLowerCase().trim()).filter(d => DOMAIN.test(d)))].slice(0, 500);
      if (m.sched && typeof m.sched === 'object') {
        const sc = m.sched, days = Array.isArray(sc.days) ? [...new Set(sc.days.map(Number).filter(d => Number.isInteger(d) && d >= 0 && d <= 6))] : [];
        if (typeof sc.on !== 'boolean' || !HHMM.test(sc.from) || !HHMM.test(sc.to) || (sc.on && !days.length)) return reply({ ok: false, err: 'sched' });
        ch.sched = { on: sc.on, days, from: sc.from, to: sc.to };
      }
      if (Array.isArray(m.allow)) ch.allow = [...new Set(m.allow.map(d => String(d).toLowerCase().trim()).filter(d => DOMAIN.test(d)))].slice(0, 500);
      if (Array.isArray(m.allowSvc)) { const SV = await services(); ch.allowSvc = [...new Set(m.allowSvc.map(String).filter(k => Object.prototype.hasOwnProperty.call(SV, k)))]; }
      if (Array.isArray(m.words)) {
        const all = m.words.map(x => typeof x === 'string' ? x.trim().toLowerCase() : '');
        if (all.some(x => x.length < 3 || x.length > 60)) return reply({ ok: false, err: 'word' });
        const w = [...new Set(all)];   // the same word twice is simply kept once
        if (w.length > 100) return reply({ ok: false, err: 'max' });
        ch.words = w;
      }
      if (m.klass === null && st.klass) { ch.klass = null; ch.exam = { until: 0 }; }
      else if (typeof m.klass === 'string') {
        const code = m.klass.toUpperCase().replace(/[^A-Z0-9]/g, '');
        if (!CODE.test(code)) return reply({ ok: false, err: 'class' });
        const left = await examAsk(code);
        if (left === null) return reply({ ok: false, err: 'net' });
        if (left < 0) return reply({ ok: false, err: 'class' });
        ch.klass = code; ch.exam = { until: left > 0 ? Date.now() + left * 1000 : 0 };
      }
      await api.storage.local.set(ch); await apply();
      if ('klass' in ch) await note(ch.klass ? 'classon' : 'classoff');
      if (ch.on === false && st.on) await note('off'); else if (ch.on === true && !st.on) await note('on');
      if (ch.guard === false && st.guard !== false) await note('guardoff');
      if (ch.cats || ch.custom || ch.allow || ch.allowSvc || ch.words || ch.sched) await note('changed');
      return reply({ ok: true });
    }
    if (m.t === 'pin') {
      if (m.newPin === null) { await api.storage.local.remove('pin'); await note('pinoff'); return reply({ ok: true }); }
      if (!/^[0-9]{4,12}$/.test(m.newPin || '')) return reply({ ok: false, err: 'format' });
      const salt = [...crypto.getRandomValues(new Uint8Array(16))].map(x => x.toString(16).padStart(2, '0')).join('');
      await api.storage.local.set({ pin: { kdf: 'pbkdf2', salt, hash: await kdf(salt, m.newPin) }, lock: { fails: 0, until: 0 } }); return reply({ ok: true });
    }
    reply({ ok: false });
  })().catch(() => reply({ ok: false, err: 'error' }));
  return true;
});
