const api = globalThis.browser || globalThis.chrome;
const L = (navigator.language || 'en').slice(0, 2);
const T = { en: ['A human said <em>no AI</em> here.', 'Human Override blocked {s} on this browser.', 'AI attempts blocked today: {n}'],
  nl: ['Een mens zei hier <em>geen AI</em>.', 'Human Override blokkeerde {s} in deze browser.', 'AI-pogingen vandaag geblokkeerd: {n}'],
  fr: ['Un humain a dit <em>pas d’IA</em> ici.', 'Human Override a bloqué {s} sur ce navigateur.', 'Tentatives d’IA bloquées aujourd’hui : {n}'] }[L] || null;
let host = 'this AI service';
try { host = new URL(decodeURIComponent(location.hash.slice(1))).hostname || host; } catch (e) {}
const t = T || ['A human said <em>no AI</em> here.', 'Human Override blocked {s} on this browser.', 'AI attempts blocked today: {n}'];
const h = document.getElementById('h'); h.textContent = '';
t[0].split(/<em>|<\/em>/).forEach((part, i) => { if (i % 2) { const e = document.createElement('em'); e.textContent = part; h.appendChild(e); } else h.appendChild(document.createTextNode(part)); });
const p = document.getElementById('p'); const [a, b] = t[1].split('{s}'); p.textContent = a; const c = document.createElement('code'); c.textContent = host; p.append(c, b);
api.runtime.sendMessage({ t: 'blocked' }, () => api.runtime.sendMessage({ t: 'state' }, s => { if (s) document.getElementById('c').textContent = t[2].replace('{n}', s.today); }));
