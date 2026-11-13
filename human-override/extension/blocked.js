/* Mindveto - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
const api = globalThis.browser || globalThis.chrome;
const L = (navigator.language || 'en').slice(0, 2);
const F = new URLSearchParams(location.search).get('f');
const FAM = F === 'adult' || F === 'bypass';   // blocked by the family filter, not as AI
const T = (F === 'bypass' ? { en: ['This site is <em>blocked</em> here.', 'The Mindveto family filter blocks VPN, proxy and secure-DNS sites on this browser, so the filter cannot be skipped.', ''],
  nl: ['Deze site is hier <em>geblokkeerd</em>.', 'De Mindveto-gezinsfilter blokkeert VPN-, proxy- en secure-DNS-sites in deze browser, zodat de filter niet omzeild kan worden.', ''],
  fr: ['Ce site est <em>bloqué</em> ici.', 'Le filtre familial Mindveto bloque les sites de VPN, de proxy et de DNS sécurisé sur ce navigateur, pour que le filtre ne puisse pas être contourné.', ''] }
  : FAM ? { en: ['This site is <em>blocked</em> here.', 'The Mindveto family filter blocks adult sites on this browser.', ''],
  nl: ['Deze site is hier <em>geblokkeerd</em>.', 'De Mindveto-gezinsfilter blokkeert sites voor volwassenen in deze browser.', ''],
  fr: ['Ce site est <em>bloqué</em> ici.', 'Le filtre familial Mindveto bloque les sites pour adultes sur ce navigateur.', ''] }
  : { en: ['A human said <em>no AI</em> here.', 'Mindveto blocked {s} on this browser.', 'AI attempts blocked today: {n}'],
  nl: ['Een mens zei hier <em>geen AI</em>.', 'Mindveto blokkeerde {s} in deze browser.', 'AI-pogingen vandaag geblokkeerd: {n}'],
  fr: ['Un humain a dit <em>pas d’IA</em> ici.', 'Mindveto a bloqué {s} sur ce navigateur.', 'Tentatives d’IA bloquées aujourd’hui : {n}'] })[L] || null;
let host = 'this AI service';
try { host = new URL(decodeURIComponent(location.hash.slice(1))).hostname || host; } catch (e) {}
const t = T || (F === 'bypass' ? ['This site is <em>blocked</em> here.', 'The Mindveto family filter blocks VPN, proxy and secure-DNS sites on this browser, so the filter cannot be skipped.', ''] : FAM ? ['This site is <em>blocked</em> here.', 'The Mindveto family filter blocks adult sites on this browser.', ''] : ['A human said <em>no AI</em> here.', 'Mindveto blocked {s} on this browser.', 'AI attempts blocked today: {n}']);
const h = document.getElementById('h'); h.textContent = '';
t[0].split(/<em>|<\/em>/).forEach((part, i) => { if (i % 2) { const e = document.createElement('em'); e.textContent = part; h.appendChild(e); } else h.appendChild(document.createTextNode(part)); });
const p = document.getElementById('p');
if (FAM) p.textContent = t[1];   // the family filter does not show which site, and is not counted as an AI attempt
else {
  const [a, b] = t[1].split('{s}'); p.textContent = a; const c = document.createElement('code'); c.textContent = host; p.append(c, b);
  api.runtime.sendMessage({ t: 'blocked' }, () => api.runtime.sendMessage({ t: 'state' }, s => { if (s) document.getElementById('c').textContent = t[2].replace('{n}', s.today); }));
}
