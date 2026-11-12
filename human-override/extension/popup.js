/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
const api = globalThis.browser || globalThis.chrome;
const L = (navigator.language || 'en').slice(0, 2);
const TX = {
  en: { holOff: 'School holidays: no difference', holSkip: 'AI allowed during school holidays', holOnly: 'Block only during school holidays', regs: { 'BE-NL': 'Belgium · Flanders', 'BE-FR': 'Belgium · Wallonia-Brussels', 'NL-NO': 'Netherlands · North', 'NL-MI': 'Netherlands · Middle', 'NL-ZU': 'Netherlands · South', 'FR-ZA': 'France · zone A', 'FR-ZB': 'France · zone B', 'FR-ZC': 'France · zone C' }, klass: 'Class · exam mode', clJoin: 'Join', clLeave: 'Leave this class', clNone: 'Not in a class.', clIn: 'In class {c}.', clExam: 'EXAM MODE: all AI is blocked for {m} more min.', clNote: 'A teacher can switch all AI off for the whole class during a test. Only the class code is sent to our server, once a minute. Teachers: geopolcoins.xyz/human-override-class.html', clBad: 'This class code does not exist.', clNet: 'Could not reach the server. Try again.', wordMax: 'The list is full (100 words).', allowSub: 'Allowing a site also allows every sub-site under it.', words: 'Your own private words', wordsPh: 'e.g. Project Zeus, KL-2024', wordsNote: 'Project names, customer names or numbers. The paste guard also warns for these. They stay on this device.', wordErr: 'Use 3 to 60 characters.', svNote: 'Tick the AI your school or company approves. Everything else stays blocked, and the paste guard keeps watching on approved AI.', allowMore: 'Other sites to allow', seenB: 'Mark as seen (PIN)', guard: 'Paste guard', guardOn: 'Warn before pasting private data into AI sites', guardNote: 'Bank and card numbers, ID numbers, e-mail lists, secret keys and “confidential” texts. Checked on this device only.', logH: 'Tamper log', logNone: 'Nothing happened yet.', ev: { examon: 'Exam mode started', examoff: 'Exam mode ended', classon: 'Joined a class', classoff: 'Left the class', off: 'Switched off', on: 'Switched on', pinbad: 'Wrong PIN tried', pinlock: 'Locked after 5 wrong PINs', pinoff: 'PIN removed', changed: 'Settings changed', guardoff: 'Paste guard switched off', paste_no: 'Paste stopped', paste_mask: 'Pasted without private parts', paste_yes: 'Private data pasted anyway' }, sched: 'Schedule', schedOn: 'Only block on these days and times', save: 'Save', schedNote: 'Example: school days 08:00-16:00, or every night 21:00-07:00.', paused: 'Paused by the schedule: AI is allowed right now.', schedErr: 'Pick at least one day and valid times.', days: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], on: 'AI BLOCKED', off: 'AI ALLOWED', tapOff: 'Tap to allow AI again', tapOn: 'Tap to block AI', st: '<b>{t}</b> AI attempts blocked today · {n} in total', cats: 'What to block', block: 'Also block', allow: 'Approved AI', pin: 'PIN lock', setPin: 'Set', clear: 'Remove', pinOn: 'PIN is set: turning off or changing anything needs the PIN.', pinOff: 'Set a PIN (4-12 digits) so nobody else can turn it off.', askPin: 'Enter the PIN first (in the PIN box).', locked: 'Too many wrong PINs. Wait a moment and try again.', bad: 'Wrong PIN.', fmt: 'Use 4 to 12 digits.', saved: 'Saved.', dom: 'That is not a valid domain.', priv: 'No account, no tracking. Nothing is sent, unless you join a class', sites: 'sites', don: '❤ Free forever. Support it with a coffee',
        c: { chat: 'AI chatbots', search: 'AI search', image: 'AI images', media: 'AI video, voice & music', writing: 'AI writing & homework', coding: 'AI coding', record: 'AI recorders & note-takers' } },
  nl: { holOff: 'Schoolvakanties: geen verschil', holSkip: 'AI mag tijdens schoolvakanties', holOnly: 'Alleen blokkeren tijdens schoolvakanties', regs: { 'BE-NL': 'België · Vlaanderen', 'BE-FR': 'België · Wallonië-Brussel', 'NL-NO': 'Nederland · Noord', 'NL-MI': 'Nederland · Midden', 'NL-ZU': 'Nederland · Zuid', 'FR-ZA': 'Frankrijk · zone A', 'FR-ZB': 'Frankrijk · zone B', 'FR-ZC': 'Frankrijk · zone C' }, klass: 'Klas · examenmodus', clJoin: 'Koppelen', clLeave: 'Deze klas verlaten', clNone: 'Niet in een klas.', clIn: 'In klas {c}.', clExam: 'EXAMENMODUS: alle AI is nog {m} min geblokkeerd.', clNote: 'Een leraar kan tijdens een toets alle AI uitzetten voor de hele klas. Alleen de klascode gaat naar onze server, één keer per minuut. Leraren: geopolcoins.xyz/human-override-class.html', clBad: 'Deze klascode bestaat niet.', clNet: 'De server is niet bereikbaar. Probeer opnieuw.', wordMax: 'De lijst is vol (100 woorden).', allowSub: 'Een site toelaten laat ook alle sub-sites eronder toe.', words: 'Je eigen privéwoorden', wordsPh: 'bv. Project Zeus, KL-2024', wordsNote: 'Projectnamen, klantnamen of nummers. De plakbewaker waarschuwt ook hiervoor. Ze blijven op dit toestel.', wordErr: 'Gebruik 3 tot 60 tekens.', svNote: 'Vink de AI aan die je school of bedrijf goedkeurt. Al de rest blijft geblokkeerd, en de plakbewaker blijft opletten op goedgekeurde AI.', allowMore: 'Andere sites toelaten', seenB: 'Gezien (pincode)', guard: 'Plakbewaker', guardOn: 'Waarschuw voor ik privégegevens in AI-sites plak', guardNote: 'Bank- en kaartnummers, rijksregisternummers, lijsten e-mailadressen, geheime sleutels en “vertrouwelijke” teksten. Alleen gecontroleerd op dit toestel.', logH: 'Sabotage-logboek', logNone: 'Nog niets gebeurd.', ev: { examon: 'Examenmodus gestart', examoff: 'Examenmodus gestopt', classon: 'Aan een klas gekoppeld', classoff: 'Klas verlaten', off: 'Uitgezet', on: 'Aangezet', pinbad: 'Verkeerde pincode geprobeerd', pinlock: 'Vergrendeld na 5 foute pincodes', pinoff: 'Pincode gewist', changed: 'Instellingen gewijzigd', guardoff: 'Plakbewaker uitgezet', paste_no: 'Plakken gestopt', paste_mask: 'Geplakt zonder privé-stukken', paste_yes: 'Privégegevens toch geplakt' }, sched: 'Schema', schedOn: 'Alleen blokkeren op deze dagen en uren', save: 'Opslaan', schedNote: 'Voorbeeld: schooldagen 08:00-16:00, of elke nacht 21:00-07:00.', paused: 'Gepauzeerd door het schema: AI mag nu.', schedErr: 'Kies minstens één dag en geldige uren.', days: ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo'], on: 'AI GEBLOKKEERD', off: 'AI TOEGESTAAN', tapOff: 'Tik om AI weer toe te laten', tapOn: 'Tik om AI te blokkeren', st: 'Vandaag <b>{t}</b> AI-pogingen geblokkeerd · {n} in totaal', cats: 'Wat blokkeren', block: 'Ook blokkeren', allow: 'Goedgekeurde AI', pin: 'Pincode', setPin: 'Instellen', clear: 'Wissen', pinOn: 'Pincode staat aan: uitzetten of iets wijzigen vraagt de pincode.', pinOff: 'Stel een pincode in (4-12 cijfers) zodat niemand anders het kan uitzetten.', askPin: 'Vul eerst de pincode in (in het pincodevak).', locked: 'Te veel foute pincodes. Wacht even en probeer opnieuw.', bad: 'Verkeerde pincode.', fmt: 'Gebruik 4 tot 12 cijfers.', saved: 'Opgeslagen.', dom: 'Dat is geen geldig domein.', priv: 'Geen account, geen tracking. Er wordt niets verstuurd, tenzij je een klas koppelt', sites: 'sites', don: '❤ Altijd gratis. Steun het met een koffie',
        c: { chat: 'AI-chatbots', search: 'AI-zoekmachines', image: 'AI-afbeeldingen', media: 'AI-video, stem en muziek', writing: 'AI-schrijven en huiswerk', coding: 'AI-programmeren', record: 'AI-opnames en notulisten' } },
  fr: { holOff: 'Vacances scolaires : aucune différence', holSkip: 'IA permise pendant les vacances scolaires', holOnly: 'Bloquer seulement pendant les vacances scolaires', regs: { 'BE-NL': 'Belgique · Flandre', 'BE-FR': 'Belgique · Wallonie-Bruxelles', 'NL-NO': 'Pays-Bas · Nord', 'NL-MI': 'Pays-Bas · Centre', 'NL-ZU': 'Pays-Bas · Sud', 'FR-ZA': 'France · zone A', 'FR-ZB': 'France · zone B', 'FR-ZC': 'France · zone C' }, klass: 'Classe · mode examen', clJoin: 'Rejoindre', clLeave: 'Quitter cette classe', clNone: 'Pas dans une classe.', clIn: 'Dans la classe {c}.', clExam: 'MODE EXAMEN : toute l’IA est bloquée encore {m} min.', clNote: 'Un enseignant peut couper toute l’IA pour la classe pendant un test. Seul le code de classe est envoyé à notre serveur, une fois par minute. Enseignants : geopolcoins.xyz/human-override-class.html', clBad: 'Ce code de classe n’existe pas.', clNet: 'Serveur injoignable. Réessayez.', wordMax: 'La liste est pleine (100 mots).', allowSub: 'Autoriser un site autorise aussi tous ses sous-sites.', words: 'Vos propres mots privés', wordsPh: 'p. ex. Projet Zeus, KL-2024', wordsNote: 'Noms de projets, de clients ou numéros. Le garde-collage avertit aussi pour ceux-ci. Ils restent sur cet appareil.', wordErr: 'Utilisez 3 à 60 caractères.', svNote: 'Cochez les IA approuvées par votre école ou entreprise. Tout le reste reste bloqué, et le garde-collage continue de surveiller sur les IA approuvées.', allowMore: 'Autres sites à autoriser', seenB: 'Marquer comme vu (PIN)', guard: 'Garde-collage', guardOn: 'M’avertir avant de coller des données privées dans un site d’IA', guardNote: 'Numéros de compte et de carte, numéros d’identité, listes d’e-mails, clés secrètes et textes « confidentiels ». Vérifié seulement sur cet appareil.', logH: 'Journal anti-sabotage', logNone: 'Rien ne s’est encore passé.', ev: { examon: 'Mode examen démarré', examoff: 'Mode examen terminé', classon: 'Classe rejointe', classoff: 'Classe quittée', off: 'Désactivé', on: 'Activé', pinbad: 'Mauvais PIN essayé', pinlock: 'Verrouillé après 5 mauvais PIN', pinoff: 'PIN retiré', changed: 'Réglages modifiés', guardoff: 'Garde-collage désactivé', paste_no: 'Collage arrêté', paste_mask: 'Collé sans les parties privées', paste_yes: 'Données privées collées quand même' }, sched: 'Horaire', schedOn: 'Bloquer seulement ces jours et heures', save: 'Enregistrer', schedNote: 'Exemple : jours d’école 08:00-16:00, ou chaque nuit 21:00-07:00.', paused: 'En pause selon l’horaire : l’IA est permise maintenant.', schedErr: 'Choisissez au moins un jour et des heures valides.', days: ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di'], on: 'IA BLOQUÉE', off: 'IA AUTORISÉE', tapOff: 'Touchez pour réautoriser l’IA', tapOn: 'Touchez pour bloquer l’IA', st: '<b>{t}</b> tentatives d’IA bloquées aujourd’hui · {n} au total', cats: 'Quoi bloquer', block: 'Bloquer aussi', allow: 'IA approuvées', pin: 'Code PIN', setPin: 'Définir', clear: 'Retirer', pinOn: 'PIN actif : désactiver ou modifier demande le PIN.', pinOff: 'Définissez un PIN (4 à 12 chiffres) pour que personne d’autre ne puisse le désactiver.', askPin: 'Entrez d’abord le PIN (dans la case PIN).', locked: 'Trop de PIN erronés. Patientez un peu et réessayez.', bad: 'Mauvais PIN.', fmt: 'Utilisez 4 à 12 chiffres.', saved: 'Enregistré.', dom: 'Ce n’est pas un domaine valide.', priv: 'Sans compte, sans pistage. Rien n’est envoyé, sauf si vous rejoignez une classe', sites: 'sites', don: '❤ Gratuit pour toujours. Soutenez-le avec un café',
        c: { chat: 'Chatbots IA', search: 'Recherche IA', image: 'Images IA', media: 'Vidéo, voix et musique IA', writing: 'Rédaction et devoirs IA', coding: 'Code IA', record: 'Enregistreurs et prise de notes IA' } }
};
const t = TX[L] || TX.en;
const $ = id => document.getElementById(id);
let S = null;
const send = m => new Promise(r => api.runtime.sendMessage(m, r));
function msg(s, ok) { $('msg').textContent = s || ''; $('msg').style.color = ok ? 'var(--green)' : 'var(--red)'; }
function pinVal() { return $('pin').value.trim(); }
async function change(m) {
  const r = await send(Object.assign({ t: 'set', pin: pinVal() }, m));
  if (!r || !r.ok) { msg(r && r.err === 'locked' ? t.locked : r && r.err === 'pin' ? (pinVal() ? t.bad : t.askPin) : r && r.err === 'sched' ? t.schedErr : r && r.err === 'word' ? t.wordErr : r && r.err === 'max' ? t.wordMax : r && r.err === 'class' ? t.clBad : r && r.err === 'net' ? t.clNet : t.dom); return false; }
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
  if (S.on && !S.active) { st.textContent = t.paused; b.className = 'big off'; }
  const sc = S.sched; $('scOn').checked = sc.on; $('scFrom').value = sc.from; $('scTo').value = sc.to;
  const opt = (sel, items, cur) => { sel.textContent = ''; for (const [v, txt] of items) { const o = document.createElement('option'); o.value = v; o.textContent = txt; o.selected = v === cur; sel.appendChild(o); } };
  opt($('scHol'), [['off', t.holOff], ['skip', t.holSkip], ['only', t.holOnly]], sc.hol || 'off');
  opt($('scReg'), Object.entries(t.regs), sc.region || 'BE-NL'); $('scReg').hidden = (sc.hol || 'off') === 'off';
  $('scHol').onchange = () => { $('scReg').hidden = $('scHol').value === 'off'; };
  const dd = $('scDays'); dd.textContent = '';
  [1, 2, 3, 4, 5, 6, 0].forEach((d, i) => {
    const x = document.createElement('button'); x.type = 'button'; x.textContent = t.days[i]; x.dataset.d = d;
    x.setAttribute('aria-pressed', sc.days.includes(d)); x.onclick = () => x.setAttribute('aria-pressed', x.getAttribute('aria-pressed') !== 'true');
    dd.appendChild(x);
  });
  const code = S.klass ? S.klass.slice(0, 4) + '-' + S.klass.slice(4) : '';
  $('clState').textContent = !S.klass ? t.clNone : S.examLeft > 0 ? t.clIn.replace('{c}', code) + ' ' + t.clExam.replace('{m}', S.examLeft) : t.clIn.replace('{c}', code);
  $('clState').style.color = S.examLeft > 0 ? 'var(--red)' : '';
  $('clJoin').hidden = !!S.klass; $('clLeave').hidden = !S.klass;
  if (S.examLeft > 0) { b.className = 'big on'; }
  $('gOn').checked = S.guard;
  $('seen').hidden = !S.alert;
  const lg = $('log'); lg.textContent = '';
  if (!S.log.length) { const li = document.createElement('li'); li.textContent = t.logNone; lg.appendChild(li); }
  S.log.forEach(e => { const li = document.createElement('li'); const tm = document.createElement('time'); tm.textContent = new Date(e.at).toLocaleString(navigator.language, { dateStyle: 'short', timeStyle: 'short' });
    li.append(tm, document.createTextNode(' ' + (t.ev[e.k] || e.k))); if (['pinbad', 'pinlock', 'paste_yes', 'off', 'pinoff', 'guardoff', 'classoff'].includes(e.k)) li.className = 'warn'; lg.appendChild(li); });
  tags($('tagsB'), S.custom, 'custom'); tags($('tagsA'), S.allow, 'allow'); tags($('tagsW'), S.words, 'words');
  const sv = $('svc'); sv.textContent = '';
  Object.entries(S.services).forEach(([k, name]) => {
    const l = document.createElement('label'); l.className = 'cat';
    const c = document.createElement('input'); c.type = 'checkbox'; c.checked = S.allowSvc.includes(k);
    c.onchange = async () => { const next = c.checked ? S.allowSvc.concat(k) : S.allowSvc.filter(v => v !== k); if (!(await change({ allowSvc: next }))) c.checked = !c.checked; };
    const n = document.createElement('span'); n.textContent = name;
    l.append(c, n); sv.appendChild(l);
  });
  $('pinB').textContent = S.hasPin ? t.clear : t.setPin; $('pinNote').textContent = S.hasPin ? t.pinOn : t.pinOff;
}
['hGuard', 'gLbl', 'gNote', 'hLog'].forEach((id, i) => { $(id).textContent = [t.guard, t.guardOn, t.guardNote, t.logH][i]; });
$('gOn').onchange = async () => { const v = $('gOn').checked; if (!(await change({ guard: v }))) $('gOn').checked = !v; };
['hCats', 'hBlock', 'hAllow', 'hPin', 'hSched', 'scLbl', 'scSave', 'scNote'].forEach((id, i) => { $(id).textContent = [t.cats, t.block, t.allow, t.pin, t.sched, t.schedOn, t.save, t.schedNote][i]; });
$('scSave').onclick = () => change({ sched: { on: $('scOn').checked, from: $('scFrom').value, to: $('scTo').value, hol: $('scHol').value, region: $('scReg').value,
  days: [...$('scDays').children].filter(x => x.getAttribute('aria-pressed') === 'true').map(x => Number(x.dataset.d)) } });
$('priv').textContent = t.priv; $('don').textContent = t.don;
$('big').onclick = () => change({ on: !S.on });
function clean(v) { v = v.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[\/?#]/)[0]; return v; }
$('addBb').onclick = () => { const d = clean($('addB').value); if (d) change({ custom: S.custom.concat(d) }).then(ok => ok && ($('addB').value = '')); };
['hWords', 'wNote', 'svNote', 'hAllowMore', 'aNote'].forEach((id, i) => { $(id).textContent = [t.words, t.wordsNote, t.svNote, t.allowMore, t.allowSub][i]; });
$('addW').placeholder = t.wordsPh;
$('addWb').onclick = () => { const w = $('addW').value.trim(); if (w) change({ words: S.words.concat(w.toLowerCase()) }).then(ok => ok && ($('addW').value = '')); };
['hClass', 'clJoinB', 'clLeave', 'clNote'].forEach((id, i) => { $(id).textContent = [t.klass, t.clJoin, t.clLeave, t.clNote][i]; });
$('clJoinB').onclick = () => { const c = $('clCode').value.trim(); if (c) change({ klass: c }).then(ok => ok && ($('clCode').value = '')); };
$('clLeave').onclick = () => change({ klass: null });
$('addAb').onclick = () => { const d = clean($('addA').value); if (d) change({ allow: S.allow.concat(d) }).then(ok => ok && ($('addA').value = '')); };
$('pinB').onclick = async () => {
  if (S.hasPin) { const r = await send({ t: 'pin', pin: pinVal(), newPin: null }); if (!r.ok) return msg(r.err === 'locked' ? t.locked : pinVal() ? t.bad : t.askPin); $('pin').value = ''; msg(t.saved, true); return load(); }
  if (!/^[0-9]{4,12}$/.test(pinVal())) return msg(t.fmt);
  const r = await send({ t: 'pin', newPin: pinVal() }); if (r && r.ok) { $('pin').value = ''; msg(t.saved, true); load(); }
};
$('seen').textContent = t.seenB;
$('seen').onclick = async () => { const r = await send({ t: 'seen', pin: pinVal() }); if (!r || !r.ok) return msg(r && r.err === 'locked' ? t.locked : pinVal() ? t.bad : t.askPin); msg(t.saved, true); load(); };
load();
