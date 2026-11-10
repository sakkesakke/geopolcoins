/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
const api = globalThis.browser || globalThis.chrome;
const L = (navigator.language || 'en').slice(0, 2);
const TX = {
  en: { on: 'AI BLOCKED', off: 'AI ALLOWED', tapOff: 'Tap to allow AI again', tapOn: 'Tap to block AI', st: '<b>{t}</b> AI attempts blocked today · {n} in total', cats: 'What to block', block: 'Also block', allow: 'Always allow', pin: 'PIN lock', setPin: 'Set', clear: 'Remove', pinOn: 'PIN is set: turning off or changing anything needs the PIN.', pinOff: 'Set a PIN (4-12 digits) so nobody else can turn it off.', askPin: 'Enter the PIN first (in the PIN box).', locked: 'Too many wrong PINs. Wait a moment and try again.', bad: 'Wrong PIN.', fmt: 'Use 4 to 12 digits.', saved: 'Saved.', dom: 'That is not a valid domain.', priv: 'No account, no tracking, nothing is sent', sites: 'sites', don: '❤ Free forever. Support it with a coffee',
        c: { chat: 'AI chatbots', search: 'AI search', image: 'AI images', media: 'AI video, voice & music', writing: 'AI writing & homework', coding: 'AI coding' } },
  nl: { on: 'AI GEBLOKKEERD', off: 'AI TOEGESTAAN', tapOff: 'Tik om AI weer toe te laten', tapOn: 'Tik om AI te blokkeren', st: 'Vandaag <b>{t}</b> AI-pogingen geblokkeerd · {n} in totaal', cats: 'Wat blokkeren', block: 'Ook blokkeren', allow: 'Altijd toelaten', pin: 'Pincode', setPin: 'Instellen', clear: 'Wissen', pinOn: 'Pincode staat aan: uitzetten of iets wijzigen vraagt de pincode.', pinOff: 'Stel een pincode in (4-12 cijfers) zodat niemand anders het kan uitzetten.', askPin: 'Vul eerst de pincode in (in het pincodevak).', locked: 'Te veel foute pincodes. Wacht even en probeer opnieuw.', bad: 'Verkeerde pincode.', fmt: 'Gebruik 4 tot 12 cijfers.', saved: 'Opgeslagen.', dom: 'Dat is geen geldig domein.', priv: 'Geen account, geen tracking, er wordt niets verstuurd', sites: 'sites', don: '❤ Altijd gratis. Steun het met een koffie',
        c: { chat: 'AI-chatbots', search: 'AI-zoekmachines', image: 'AI-afbeeldingen', media: 'AI-video, stem en muziek', writing: 'AI-schrijven en huiswerk', coding: 'AI-programmeren' } },
  fr: { on: 'IA BLOQUÉE', off: 'IA AUTORISÉE', tapOff: 'Touchez pour réautoriser l’IA', tapOn: 'Touchez pour bloquer l’IA', st: '<b>{t}</b> tentatives d’IA bloquées aujourd’hui · {n} au total', cats: 'Quoi bloquer', block: 'Bloquer aussi', allow: 'Toujours autoriser', pin: 'Code PIN', setPin: 'Définir', clear: 'Retirer', pinOn: 'PIN actif : désactiver ou modifier demande le PIN.', pinOff: 'Définissez un PIN (4 à 12 chiffres) pour que personne d’autre ne puisse le désactiver.', askPin: 'Entrez d’abord le PIN (dans la case PIN).', locked: 'Trop de PIN erronés. Patientez un peu et réessayez.', bad: 'Mauvais PIN.', fmt: 'Utilisez 4 à 12 chiffres.', saved: 'Enregistré.', dom: 'Ce n’est pas un domaine valide.', priv: 'Sans compte, sans pistage, rien n’est envoyé', sites: 'sites', don: '❤ Gratuit pour toujours. Soutenez-le avec un café',
        c: { chat: 'Chatbots IA', search: 'Recherche IA', image: 'Images IA', media: 'Vidéo, voix et musique IA', writing: 'Rédaction et devoirs IA', coding: 'Code IA' } }
};
const t = TX[L] || TX.en;
const $ = id => document.getElementById(id);
let S = null;
const send = m => new Promise(r => api.runtime.sendMessage(m, r));
function msg(s, ok) { $('msg').textContent = s || ''; $('msg').style.color = ok ? 'var(--green)' : 'var(--red)'; }
function pinVal() { return $('pin').value.trim(); }
async function change(m) {
  const r = await send(Object.assign({ t: 'set', pin: pinVal() }, m));
  if (!r || !r.ok) { msg(r && r.err === 'locked' ? t.locked : r && r.err === 'pin' ? (pinVal() ? t.bad : t.askPin) : t.dom); return false; }
  msg(t.saved, true); await load(); return true;
}
function tags(el, list, key) {
  el.textContent = '';
  list.forEach(d => {
    const s = document.createElement('span'); s.textContent = d;
    const x = document.createElement('button'); x.type = 'button'; x.textContent = '×'; x.setAttribute('aria-label', 'remove ' + d);
    x.onclick = () => change({ [key]: S[key].filter(v => v !== d) });
    s.appendChild(x); el.appendChild(s);
  });
}
async function load() {
  S = await send({ t: 'state' });
  const b = $('big'); b.className = 'big ' + (S.on ? 'on' : 'off');
  b.textContent = (S.on ? '✋ ' + t.on : '○ ' + t.off); b.title = S.on ? t.tapOff : t.tapOn;
  const st = $('status'); st.textContent = '';
  t.st.replace('{n}', S.count).split(/(<b>\{t\}<\/b>)/).forEach(part => { if (part === '<b>{t}</b>') { const b = document.createElement('b'); b.textContent = S.today; st.appendChild(b); } else st.appendChild(document.createTextNode(part)); });
  const box = $('cats'); box.textContent = '';
  Object.keys(t.c).forEach(k => {
    const l = document.createElement('label'); l.className = 'cat';
    const c = document.createElement('input'); c.type = 'checkbox'; c.checked = S.cats[k] !== false;
    c.onchange = async () => { const cats = Object.assign({}, S.cats, { [k]: c.checked }); if (!(await change({ cats }))) c.checked = !c.checked; };
    const n = document.createElement('span'); n.textContent = t.c[k];
    const sm = document.createElement('small'); sm.textContent = (S.cats_meta[k] || 0) + ' ' + t.sites;
    l.append(c, n, sm); box.appendChild(l);
  });
  tags($('tagsB'), S.custom, 'custom'); tags($('tagsA'), S.allow, 'allow');
  $('pinB').textContent = S.hasPin ? t.clear : t.setPin; $('pinNote').textContent = S.hasPin ? t.pinOn : t.pinOff;
}
['hCats', 'hBlock', 'hAllow', 'hPin'].forEach((id, i) => { $(id).textContent = [t.cats, t.block, t.allow, t.pin][i]; });
$('priv').textContent = t.priv; $('don').textContent = t.don;
$('big').onclick = () => change({ on: !S.on });
function clean(v) { v = v.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[\/?#]/)[0]; return v; }
$('addBb').onclick = () => { const d = clean($('addB').value); if (d) change({ custom: S.custom.concat(d) }).then(ok => ok && ($('addB').value = '')); };
$('addAb').onclick = () => { const d = clean($('addA').value); if (d) change({ allow: S.allow.concat(d) }).then(ok => ok && ($('addA').value = '')); };
$('pinB').onclick = async () => {
  if (S.hasPin) { const r = await send({ t: 'pin', pin: pinVal(), newPin: null }); if (!r.ok) return msg(r.err === 'locked' ? t.locked : pinVal() ? t.bad : t.askPin); $('pin').value = ''; msg(t.saved, true); return load(); }
  if (!/^[0-9]{4,12}$/.test(pinVal())) return msg(t.fmt);
  const r = await send({ t: 'pin', newPin: pinVal() }); if (r && r.ok) { $('pin').value = ''; msg(t.saved, true); load(); }
};
load();
