/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
/* Human Override: blocks AI services in this browser with declarativeNetRequest.
   Nothing is sent anywhere. The only network request is a daily download of the public block list
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
const DEFAULTS = { on: true, cats: { chat: true, search: true, image: true, media: true, writing: true, coding: true, record: true }, custom: [], allow: [], pin: null, count: 0, day: '', today: 0, guard: true, log: [], alert: false,
  sched: { on: false, days: [1, 2, 3, 4, 5], from: '08:00', to: '16:00' } };
const HHMM = /^([01][0-9]|2[0-3]):[0-5][0-9]$/;
const REMOVED_URL = 'https://geopolcoins.xyz/human-override-removed.html';
const ALERT = new Set(['pinbad', 'pinlock']);   // these light up a red "!" on the icon until the popup is opened

// Tamper log: what happened and when (never page content). Last 50 events, only on this device.
let logChain = Promise.resolve(), pinChain = Promise.resolve();
function serial(which, fn) { const r = (which === 'pin' ? pinChain : logChain).then(fn); const done = r.catch(() => {}); if (which === 'pin') pinChain = done; else logChain = done; return r; }
function note(k) { return serial('log', () => noteNow(k)); }
async function noteNow(k) {
  const s = await api.storage.local.get(['log', 'alert']);
  const log = (Array.isArray(s.log) ? s.log : []).concat({ k, at: Date.now() }).slice(-50);
  await api.storage.local.set({ log, alert: !!s.alert || ALERT.has(k) });
  badge();
}
async function badge() {
  const st = await getState(), act = active(st);
  api.action.setBadgeText({ text: st.alert ? '!' : !st.on ? 'OFF' : act ? '' : 'zz' });
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
function active(st) { return st.on && (!st.sched.on || inWindow(st.sched)); }

async function bundled() { const r = await fetch(api.runtime.getURL('lists.json')); return r.json(); }
async function lists() { const s = await api.storage.local.get('remote'); return (s.remote && s.remote.categories) ? s.remote : bundled(); }

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

async function apply() {
  const st = await getState(), L = await lists();
  const old = await api.declarativeNetRequest.getDynamicRules();
  const rules = [], act = active(st);
  if (act) {
    const allow = new Set(st.allow);
    let doms = [], paths = [];
    for (const [k, c] of Object.entries(L.categories || {})) {
      if (!st.cats[k]) continue;
      doms = doms.concat((c.domains || []).filter(d => DOMAIN.test(d)));
      paths = paths.concat((c.paths || []).filter(p => PATH.test(p)));
    }
    doms = doms.concat(st.custom.filter(d => DOMAIN.test(d)));
    doms = [...new Set(doms)].filter(d => !allow.has(d) && !(PROTECT.has(d) && !st.custom.includes(d)));
    paths = [...new Set(paths)].filter(p => !allow.has(p.split('/')[0]));
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
    if (st.cats.search) rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },   // Google "AI Mode"
      condition: { regexFilter: '^https?://(www\\.)?google\\.[a-z.]{2,12}/search\\?(.*&)?udm=50(&.*)?$', resourceTypes: ['main_frame'] } });
    if (rest.length) rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { extensionPath: '/blocked.html' } },
      condition: { requestDomains: rest, resourceTypes: ['main_frame'] } });
    if (doms.length) rules.push({ id: id++, priority: 1, action: { type: 'block' },
      condition: { requestDomains: doms, resourceTypes: ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other'] } });
  }
  await api.declarativeNetRequest.updateDynamicRules({ removeRuleIds: old.map(r => r.id), addRules: rules });
  await api.storage.local.set({ act });
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
api.runtime.onStartup && api.runtime.onStartup.addListener(() => { setUninstall(); api.alarms.create('sched', { periodInMinutes: 1 }); apply().catch(() => {}); });
api.alarms.onAlarm.addListener(async a => {
  if (a.name === 'list') refreshList();
  if (a.name === 'sched') { const st = await getState(), was = (await api.storage.local.get('act')).act; if (active(st) !== was) apply().catch(() => {}); }   // only rebuild rules when the schedule flips
});

api.runtime.onMessage.addListener((m, sender, reply) => {
  if (!m || typeof m !== 'object' || sender.id !== api.runtime.id) return false;   // only this extension
  const own = typeof sender.url === 'string' && sender.url.startsWith(api.runtime.getURL(''));
  if (!own && m.t !== 'paste') return false;   // content scripts on AI sites may only report a paste choice
  (async () => {
    const st = await getState();
    if (m.t === 'state') return reply({ guard: st.guard !== false, log: st.log.slice(-10).reverse(), alert: !!st.alert, on: st.on, active: active(st), sched: st.sched, cats: st.cats, custom: st.custom, allow: st.allow, hasPin: !!st.pin, count: st.count, today: st.day === new Date().toISOString().slice(0, 10) ? st.today : 0, cats_meta: Object.fromEntries(Object.entries((await lists()).categories).map(([k, c]) => [k, (c.domains || []).length + (c.paths || []).length])) });
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
      await api.storage.local.set(ch); await apply();
      if (ch.on === false && st.on) await note('off'); else if (ch.on === true && !st.on) await note('on');
      if (ch.guard === false && st.guard !== false) await note('guardoff');
      if (ch.cats || ch.custom || ch.allow || ch.sched) await note('changed');
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
