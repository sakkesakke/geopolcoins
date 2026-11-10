/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
/* Human Override: blocks AI services in this browser with declarativeNetRequest.
   Nothing is sent anywhere. The only network request is a daily download of the public block list
   from geopolcoins.xyz (no data about you is included). */
const api = globalThis.browser || globalThis.chrome;
const LIST_URL = 'https://geopolcoins.xyz/human-override/lists.json';
const DOMAIN = /^(?=.{3,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,24}$/;
const PATH = /^([a-z0-9-]{1,63}\.)+[a-z]{2,24}\/[a-z0-9\-\/_.]{1,80}$/;
const DEFAULTS = { on: true, cats: { chat: true, search: true, image: true, media: true, writing: true, coding: true }, custom: [], allow: [], pin: null, count: 0, day: '', today: 0 };

async function getState() { const s = await api.storage.local.get(null); return Object.assign({}, DEFAULTS, s, { cats: Object.assign({}, DEFAULTS.cats, s.cats || {}) }); }

async function bundled() { const r = await fetch(api.runtime.getURL('lists.json')); return r.json(); }
async function lists() { const s = await api.storage.local.get('remote'); return (s.remote && s.remote.categories) ? s.remote : bundled(); }

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

async function apply() {
  const st = await getState(), L = await lists();
  const old = await api.declarativeNetRequest.getDynamicRules();
  const rules = [];
  if (st.on) {
    const allow = new Set(st.allow);
    let doms = [], paths = [];
    for (const [k, c] of Object.entries(L.categories || {})) {
      if (!st.cats[k]) continue;
      doms = doms.concat((c.domains || []).filter(d => DOMAIN.test(d)));
      paths = paths.concat((c.paths || []).filter(p => PATH.test(p)));
    }
    doms = doms.concat(st.custom.filter(d => DOMAIN.test(d)));
    doms = [...new Set(doms)].filter(d => !allow.has(d));
    paths = [...new Set(paths)].filter(p => !allow.has(p.split('/')[0]));
    const page = api.runtime.getURL('blocked.html');
    let id = 1;
    for (const d of doms) {
      rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },
        condition: { regexFilter: '^https?://([a-z0-9-]+\\.)*' + esc(d) + '(:[0-9]+)?(/.*)?$', resourceTypes: ['main_frame'] } });
    }
    for (const p of paths) {
      rules.push({ id: id++, priority: 1, action: { type: 'redirect', redirect: { regexSubstitution: page + '#\\0' } },
        condition: { regexFilter: '^https?://([a-z0-9-]+\\.)*' + esc(p) + '([/?#].*)?$', resourceTypes: ['main_frame'] } });
    }
    if (doms.length) rules.push({ id: id++, priority: 1, action: { type: 'block' },
      condition: { requestDomains: doms, resourceTypes: ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other'] } });
  }
  await api.declarativeNetRequest.updateDynamicRules({ removeRuleIds: old.map(r => r.id), addRules: rules });
  api.action.setBadgeText({ text: st.on ? '' : 'OFF' });
  api.action.setBadgeBackgroundColor({ color: '#c0392b' });
}

async function refreshList() {
  try {
    const r = await fetch(LIST_URL, { cache: 'no-store', credentials: 'omit' });
    if (!r.ok) return;
    const j = await r.json();
    if (!j || typeof j.categories !== 'object' || JSON.stringify(j).length > 200000) return;
    for (const c of Object.values(j.categories)) {
      if (!Array.isArray(c.domains) || !c.domains.every(d => DOMAIN.test(d))) return;
      if (c.paths && (!Array.isArray(c.paths) || !c.paths.every(p => PATH.test(p)))) return;
    }
    await api.storage.local.set({ remote: j });
    await apply();
  } catch (e) { /* offline: keep the list we have */ }
}

async function sha(s) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join(''); }
async function unlocked(pin) {
  const st = await getState();
  if (!st.pin) return true;
  const lock = (await api.storage.local.get('lock')).lock || { fails: 0, until: 0 };
  if (Date.now() < lock.until) return 'locked';
  if (typeof pin !== 'string' || pin.length < 4 || pin.length > 12) return false;
  const ok = (await sha(st.pin.salt + pin)) === st.pin.hash;
  if (ok) { await api.storage.local.set({ lock: { fails: 0, until: 0 } }); return true; }
  lock.fails += 1;
  if (lock.fails >= 5) lock.until = Date.now() + Math.min(3600000, 60000 * Math.pow(2, lock.fails - 5));
  await api.storage.local.set({ lock });
  return false;
}

api.runtime.onInstalled.addListener(async () => { await apply(); refreshList(); api.alarms.create('list', { periodInMinutes: 720 }); });
api.runtime.onStartup && api.runtime.onStartup.addListener(apply);
api.alarms.onAlarm.addListener(a => { if (a.name === 'list') refreshList(); });

api.runtime.onMessage.addListener((m, sender, reply) => {
  (async () => {
    const st = await getState();
    if (m.t === 'state') return reply({ on: st.on, cats: st.cats, custom: st.custom, allow: st.allow, hasPin: !!st.pin, count: st.count, today: st.day === new Date().toISOString().slice(0, 10) ? st.today : 0, cats_meta: Object.fromEntries(Object.entries((await lists()).categories).map(([k, c]) => [k, (c.domains || []).length + (c.paths || []).length])) });
    if (m.t === 'blocked') {
      const day = new Date().toISOString().slice(0, 10);
      await api.storage.local.set({ count: st.count + 1, day, today: (st.day === day ? st.today : 0) + 1 });
      return reply({ ok: true });
    }
    // every change below needs the PIN if one is set
    const needsPin = ['set', 'pin'].includes(m.t);
    if (needsPin) { const u = await unlocked(m.pin); if (u !== true) return reply({ ok: false, err: u === 'locked' ? 'locked' : 'pin' }); }
    if (m.t === 'set') {
      const ch = {};
      if (typeof m.on === 'boolean') ch.on = m.on;
      if (m.cats && typeof m.cats === 'object') ch.cats = Object.fromEntries(Object.keys(DEFAULTS.cats).map(k => [k, m.cats[k] !== false]));
      if (Array.isArray(m.custom)) ch.custom = [...new Set(m.custom.map(d => String(d).toLowerCase().trim()).filter(d => DOMAIN.test(d)))].slice(0, 500);
      if (Array.isArray(m.allow)) ch.allow = [...new Set(m.allow.map(d => String(d).toLowerCase().trim()).filter(d => DOMAIN.test(d)))].slice(0, 500);
      await api.storage.local.set(ch); await apply(); return reply({ ok: true });
    }
    if (m.t === 'pin') {
      if (m.newPin === null) { await api.storage.local.remove('pin'); return reply({ ok: true }); }
      if (!/^[0-9]{4,12}$/.test(m.newPin || '')) return reply({ ok: false, err: 'format' });
      const salt = [...crypto.getRandomValues(new Uint8Array(16))].map(x => x.toString(16).padStart(2, '0')).join('');
      await api.storage.local.set({ pin: { salt, hash: await sha(salt + m.newPin) } }); return reply({ ok: true });
    }
    reply({ ok: false });
  })();
  return true;
});
