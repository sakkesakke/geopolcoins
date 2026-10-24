/* Bolt the guide: a small help bot for geopolcoins.xyz. No AI, no tracking, nothing is sent anywhere.
   It matches the visitor's question to a short answer with links, in EN / NL / FR. */
(function () {
  if (window.__boltGuide) return; window.__boltGuide = 1;
  var L = /^nl/i.test(navigator.language || '') ? 'nl' : /^fr/i.test(navigator.language || '') ? 'fr' : 'en';
  var CUSTOM = { en: 'custom-ai-bot.html', nl: 'ai-bot-op-maat.html', fr: 'bot-ia-sur-mesure.html' }[L];
  var UI = {
    en: { open: 'Help', title: 'Bolt, your guide', hi: 'Hi, I\'m Bolt! Ask me how the site works, or pick a topic.', ph: 'Ask a question…', send: 'Send', close: 'Close help',
      none: 'I\'m a simple guide bot, so I didn\'t catch that. Try one of these topics:', note: 'Simple guide, no AI. Not financial advice.' },
    nl: { open: 'Hulp', title: 'Bolt, je gids', hi: 'Hoi, ik ben Bolt! Vraag me hoe de site werkt, of kies een onderwerp.', ph: 'Stel een vraag…', send: 'Stuur', close: 'Hulp sluiten',
      none: 'Ik ben een eenvoudige gids-bot, dus dat begreep ik niet. Probeer een van deze onderwerpen:', note: 'Eenvoudige gids, geen AI. Geen financieel advies.' },
    fr: { open: 'Aide', title: 'Bolt, votre guide', hi: 'Salut, je suis Bolt ! Demandez-moi comment fonctionne le site, ou choisissez un sujet.', ph: 'Posez une question…', send: 'Envoyer', close: 'Fermer l\'aide',
      none: 'Je suis un simple bot guide, je n\'ai pas compris. Essayez un de ces sujets :', note: 'Guide simple, sans IA. Pas un conseil financier.' }
  }[L];
  // topic: [keywords (all languages), {en,nl,fr} label, {en,nl,fr} answer, links [[url,{label}]]]
  var K = [
    ['site', 'maiga site overview about over presentation start begin commencer home', { en: 'What is this site?', nl: 'Wat is deze site?', fr: 'C\'est quoi ce site ?' },
      { en: '$MAIGA is a satirical Solana meme coin with free tools: the Bot Garage (AI bots), Token Checkup, Meme Factory, games and an installable app. No wallet needed to use the tools.',
        nl: '$MAIGA is een satirische Solana-meme coin met gratis tools: de Bot Garage (AI-bots), Token Checkup, Meme Factory, games en een installeerbare app. Voor de tools heb je geen wallet nodig.',
        fr: '$MAIGA est un meme coin satirique sur Solana avec des outils gratuits : le Bot Garage (bots IA), le Token Checkup, la Meme Factory, des jeux et une appli installable. Pas besoin de wallet pour les outils.' },
      [['app.html', { en: 'Open the app', nl: 'Open de app', fr: 'Ouvrir l\'appli' }]]],
    ['bot', 'bot garage build make create bouwen maken creer creer chatbot assistant assistent assistente', { en: 'Build a bot', nl: 'Een bot bouwen', fr: 'Créer un bot' },
      { en: 'In the Bot Garage: 1) copy a ready-made bot or build your own, 2) pick its job, tone and look, 3) test-drive it, 4) share it or export it (prompt for ChatGPT/Claude, Telegram/Discord kit). Save it to My bots to keep it in the app.',
        nl: 'In de Bot Garage: 1) kopieer een kant-en-klare bot of bouw er zelf een, 2) kies taak, toon en uiterlijk, 3) test hem, 4) deel of exporteer hem (prompt voor ChatGPT/Claude, Telegram/Discord-pakket). Bewaar hem in Mijn bots om hem in de app te houden.',
        fr: 'Dans le Bot Garage : 1) copiez un bot prêt ou créez le vôtre, 2) choisissez son rôle, son ton et son look, 3) testez-le, 4) partagez-le ou exportez-le (prompt pour ChatGPT/Claude, kit Telegram/Discord). Enregistrez-le dans Mes bots pour le garder dans l\'appli.' },
      [['garage.html', { en: 'Open the Bot Garage', nl: 'Open de Bot Garage', fr: 'Ouvrir le Bot Garage' }]]],
    ['free', 'free gratis gratuit gratuite cheap goedkoop pas cher groq mistral gemini ollama openrouter cloudflare kost cost prix price api', { en: 'Free AI options', nl: 'Gratis AI-opties', fr: 'IA gratuite' },
      { en: 'Free options with limits: OpenRouter free models (ID ends in :free, easiest with the Bot Garage), Groq free plan, Mistral Experiment plan, Cloudflare Workers AI, or Ollama on your own computer. Free tiers may use your data and limits change, so check the provider page.',
        nl: 'Gratis opties met limieten: gratis modellen op OpenRouter (ID eindigt op :free, het makkelijkst met de Bot Garage), het gratis plan van Groq, het Experiment-plan van Mistral, Cloudflare Workers AI, of Ollama op je eigen computer. Gratis niveaus kunnen je gegevens gebruiken en limieten veranderen, dus kijk de pagina van de aanbieder na.',
        fr: 'Options gratuites avec limites : modèles gratuits OpenRouter (identifiant terminant par :free, le plus simple avec le Bot Garage), offre gratuite Groq, offre Experiment de Mistral, Cloudflare Workers AI, ou Ollama sur votre ordinateur. Les offres gratuites peuvent utiliser vos données et les limites changent : vérifiez la page du fournisseur.' },
      [['free-ai-api.html', { en: 'Free AI guide', nl: 'Gids gratis AI', fr: 'Guide IA gratuite' }]]],
    ['key', 'api key sleutel cle clef token anthropic openai claude gpt', { en: 'What is an API key?', nl: 'Wat is een API-sleutel?', fr: 'Une clé API ?' },
      { en: 'An API key lets your bot use an AI model from a provider (OpenRouter, Anthropic, OpenAI…). Treat it like a password: never share it, set a spending limit. In the Bot Garage your key stays in the browser tab and goes only to the provider you pick.',
        nl: 'Met een API-sleutel mag je bot een AI-model van een aanbieder gebruiken (OpenRouter, Anthropic, OpenAI…). Behandel hem als een wachtwoord: nooit delen, stel een uitgavelimiet in. In de Bot Garage blijft je sleutel in het browsertabblad en gaat hij alleen naar de aanbieder die je kiest.',
        fr: 'Une clé API permet à votre bot d\'utiliser un modèle d\'IA d\'un fournisseur (OpenRouter, Anthropic, OpenAI…). Traitez-la comme un mot de passe : ne la partagez jamais, fixez une limite de dépenses. Dans le Bot Garage, votre clé reste dans l\'onglet et ne va qu\'au fournisseur choisi.' },
      [['free-ai-api.html', { en: 'Full guide', nl: 'Volledige gids', fr: 'Guide complet' }]]],
    ['run', 'telegram discord whatsapp 24 run host server online live deploy kit starter export draaien hosten heberger', { en: 'Run my bot 24/7', nl: 'Bot 24/7 laten draaien', fr: 'Bot 24 h/24' },
      { en: 'Download the starter kit in the Bot Garage (Step 4): ready code for Telegram and Discord with a guide. Put your AI key in the .env file and run it on your computer or a small server. Nothing is posted or bought for you.',
        nl: 'Download het startpakket in de Bot Garage (stap 4): kant-en-klare code voor Telegram en Discord met uitleg. Zet je AI-sleutel in het .env-bestand en draai het op je computer of een kleine server. Er wordt niets voor je gepost of gekocht.',
        fr: 'Téléchargez le kit de démarrage dans le Bot Garage (étape 4) : du code prêt pour Telegram et Discord avec un guide. Mettez votre clé IA dans le fichier .env et lancez-le sur votre ordinateur ou un petit serveur. Rien n\'est publié ni acheté pour vous.' },
      [['garage.html#export', { en: 'Go to export', nl: 'Naar exporteren', fr: 'Vers l\'export' }]]],
    ['factory', 'meme factory launch pack ticker name idea naam idee lancer lancement memecoin', { en: 'Meme Factory', nl: 'Meme Factory', fr: 'Meme Factory' },
      { en: 'Type one word and the Meme Factory drafts a launch pack: name, ticker, meme, a safety check and post ideas. It is for fun and planning; nothing is launched or posted for you.',
        nl: 'Typ één woord en de Meme Factory maakt een launch pack: naam, ticker, meme, een veiligheidscheck en post-ideeën. Voor de fun en om te plannen; er wordt niets gelanceerd of gepost.',
        fr: 'Tapez un mot et la Meme Factory prépare un pack de lancement : nom, ticker, meme, un contrôle de sécurité et des idées de posts. Pour le fun et la préparation ; rien n\'est lancé ni publié.' },
      [['factory.html', { en: 'Open the Factory', nl: 'Open de Factory', fr: 'Ouvrir la Factory' }]]],
    ['lend', 'lend lending loan loans borrow lenen lening uitlenen pret preter emprunt bank backer borg garant interest rente interet agent agents', { en: 'Lending to AI bots', nl: 'Lenen aan AI-bots', fr: 'Prêter à des bots IA' },
      { en: 'Some crypto projects lend real money to AI agents. Our Bot Bank is a free game with play coins that shows how it works: backers, fees, public history and defaults. MAIGA does not offer real lending, and real crypto lending is risky and regulated.',
        nl: 'Sommige cryptoprojecten lenen echt geld uit aan AI-agents. Onze Bot Bank is een gratis spel met speelmunten dat toont hoe het werkt: borg, vergoedingen, openbaar verleden en wanbetalingen. MAIGA biedt geen echte leningen aan, en echte crypto-leningen zijn riskant en gereguleerd.',
        fr: 'Certains projets crypto prêtent de l\'argent réel à des agents IA. Notre Bot Bank est un jeu gratuit avec des pièces de jeu qui montre comment ça marche : garants, frais, historique public et défauts. MAIGA ne propose pas de vrais prêts, et le prêt crypto réel est risqué et réglementé.' },
      [['lend.html', { en: 'Play the Bot Bank', nl: 'Speel de Bot Bank', fr: 'Jouer à la Bot Bank' }]]],
    ['meme', 'meme memes generator maker studio template sjabloon modele image picture foto photo sticker download telecharger', { en: 'Make a meme', nl: 'Een meme maken', fr: 'Faire un mème' },
      { en: 'The Meme Studio has 190+ classic templates, MAIGA pixel scenes and your own photo. Type your text, drag it, add pixel stickers and download a PNG. It all happens in your browser.',
        nl: 'De Meme Studio heeft 190+ klassieke sjablonen, MAIGA-pixelscènes en je eigen foto. Typ je tekst, sleep hem, plak pixelstickers en download een PNG. Alles gebeurt in je browser.',
        fr: 'Le Meme Studio propose 190+ modèles classiques, des scènes pixel MAIGA et ta propre photo. Écris ton texte, déplace-le, ajoute des stickers pixel et télécharge un PNG. Tout se passe dans ton navigateur.' },
      [['meme.html', { en: 'Open the Meme Studio', nl: 'Open de Meme Studio', fr: 'Ouvrir le Meme Studio' }]]],
    ['check', 'token checkup check scam rug safe veilig sur arnaque oplichting red flag contract address ca', { en: 'Check a token', nl: 'Een token checken', fr: 'Vérifier un token' },
      { en: 'Paste a Solana token address in the Token Checkup. It reads public data and lists what looks fine, risky or unknown. "Nothing alarming" never means safe. Always do your own research.',
        nl: 'Plak een Solana-tokenadres in de Token Checkup. Hij leest openbare gegevens en toont wat goed, riskant of onbekend is. "Niets alarmerends" betekent nooit veilig. Doe altijd je eigen onderzoek.',
        fr: 'Collez une adresse de token Solana dans le Token Checkup. Il lit les données publiques et liste ce qui semble correct, risqué ou inconnu. « Rien d\'alarmant » ne veut jamais dire sûr. Faites toujours vos propres recherches.' },
      [['/#checkup', { en: 'Open the Checkup', nl: 'Open de Checkup', fr: 'Ouvrir le Checkup' }]]],
    ['safe', 'seed phrase private key wachtwoord password mot de passe dm scammer hack security beveiliging securite wallet phantom', { en: 'Stay safe', nl: 'Veilig blijven', fr: 'Rester en sécurité' },
      { en: 'Never share your seed phrase, private key or passwords. We never DM first and never ask for them. The site never connects to your wallet for the tools. Only trust the contract address shown on this site.',
        nl: 'Deel nooit je seed phrase, private key of wachtwoorden. Wij sturen nooit als eerste een DM en vragen daar nooit om. De tools koppelen nooit met je wallet. Vertrouw alleen het contractadres op deze site.',
        fr: 'Ne partagez jamais votre phrase secrète, votre clé privée ou vos mots de passe. Nous n\'envoyons jamais de DM en premier et ne les demandons jamais. Les outils ne se connectent jamais à votre wallet. Ne faites confiance qu\'à l\'adresse de contrat affichée sur ce site.' },
      [['/#live', { en: 'Official coin info', nl: 'Officiële coin info', fr: 'Infos officielles' }]]],
    ['app', 'app install installeren installer phone gsm telephone mobile offline home screen beginscherm', { en: 'Install the app', nl: 'De app installeren', fr: 'Installer l\'appli' },
      { en: 'Open the app page and tap "Install the app". On iPhone use Safari: Share, then "Add to Home Screen". It works offline for the Garage and My bots.',
        nl: 'Open de app-pagina en tik op "Installeer de app". Op iPhone in Safari: Deel, dan "Zet op beginscherm". De Garage en Mijn bots werken ook offline.',
        fr: 'Ouvrez la page de l\'appli et touchez « Installer l\'appli ». Sur iPhone, dans Safari : Partager puis « Sur l\'écran d\'accueil ». Le Garage et Mes bots marchent hors ligne.' },
      [['app.html', { en: 'Open the app', nl: 'Open de app', fr: 'Ouvrir l\'appli' }]]],
    ['custom', 'business zaak bedrijf entreprise salon kapsalon kapper coiffure restaurant cafe horeca winkel shop boutique makelaar immo agence custom op maat sur mesure quote offerte devis hire klanten clients customers', { en: 'Bot for my business', nl: 'Bot voor mijn zaak', fr: 'Bot pour mon entreprise' },
      { en: 'We can set up a bot for your business with your prices, hours and FAQ. You get a clear price by email first and pay nothing unless you agree. Ready-made packs are on our Ko-fi shop.',
        nl: 'We kunnen een bot voor je zaak instellen met je prijzen, uren en FAQ. Je krijgt eerst een duidelijke prijs per mail en betaalt niets tenzij je akkoord gaat. Kant-en-klare pakketten staan in onze Ko-fi-winkel.',
        fr: 'Nous pouvons installer un bot pour votre entreprise avec vos prix, horaires et FAQ. Vous recevez d\'abord un prix clair par e-mail et ne payez rien sans votre accord. Des packs prêts sont sur notre boutique Ko-fi.' },
      [[CUSTOM, { en: 'Ask for a quote', nl: 'Vraag een offerte', fr: 'Demander un devis' }], ['https://ko-fi.com/geopolcoins/shop', { en: 'Ko-fi shop', nl: 'Ko-fi-winkel', fr: 'Boutique Ko-fi' }]]],
    ['coin', 'buy kopen acheter price prijs prix chart koers cours pump moon maan lune invest investeren investir worth waard coin munt token value waarde valeur', { en: 'About the coin', nl: 'Over de coin', fr: 'À propos du coin' },
      { en: 'The app and coin info page show live public data and links to the chart and Solscan. We don\'t give price predictions or buying advice: it is entertainment only. Only spend what you can afford to lose and do your own research.',
        nl: 'De app en de coin-info tonen live openbare gegevens en links naar de grafiek en Solscan. We geven geen koersvoorspellingen of koopadvies: het is alleen voor de fun. Besteed alleen wat je kunt missen en doe je eigen onderzoek.',
        fr: 'L\'appli et la page infos affichent des données publiques en direct et des liens vers le graphique et Solscan. Nous ne donnons ni prévisions ni conseils d\'achat : c\'est du divertissement. N\'engagez que ce que vous pouvez perdre et faites vos recherches.' },
      [['/#live', { en: 'Coin info', nl: 'Coin info', fr: 'Infos coin' }]]],
    ['chain', 'blockchain how does work hoe werkt comment fonctionne mining hash block blok bloc learn leren apprendre', { en: 'How a blockchain works', nl: 'Hoe werkt een blockchain?', fr: 'Comment marche une blockchain ?' },
      { en: 'Try the Mini-Chain: type data, mine blocks and see why one changed letter breaks the whole chain. It runs in your browser.',
        nl: 'Probeer de Mini-Chain: typ gegevens, mine blokken en zie waarom één veranderde letter de hele keten breekt. Het draait in je browser.',
        fr: 'Essayez la Mini-Chain : tapez des données, minez des blocs et voyez pourquoi une seule lettre modifiée casse toute la chaîne. Tout se passe dans votre navigateur.' },
      [['chain.html', { en: 'Open the Mini-Chain', nl: 'Open de Mini-Chain', fr: 'Ouvrir la Mini-Chain' }]]]
  ];
  var QUICK = ['bot', 'meme', 'free', 'key', 'run', 'check', 'custom'];

  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9: ]+/g, ' '); }
  function match(q) {
    var STOP = ' de het een is wat hoe ik je mijn mn van voor met en of op in te the a an is what how do does i my me to for of and or on in it le la les un une des est ce que qui je mon ma mes pour et ou en du au dois moet kan peux can ';
    var words = norm(q).split(/\s+/).filter(function (w) { return w.length > 1 && STOP.indexOf(' ' + w + ' ') < 0; }), best = null, score = 0;
    K.forEach(function (k) {
      var kw = ' ' + norm(k[1]) + ' ', s = 0;
      words.forEach(function (w) { if (kw.indexOf(' ' + w + ' ') >= 0) s += 2; else if (w.length > 3 && kw.indexOf(w) >= 0) s += 1; });
      if (k[0] === 'safe' && /\b(seed|phrase|private|password|wachtwoord|passe|scam|scammer|oplichter|arnaque|hack|phishing|dm)\b/.test(norm(q))) s += 3;  // safety questions win
      if (k[0] === 'custom' && /\b(zaak|bedrijf|business|entreprise|kapsalon|salon|restaurant|horeca|winkel|shop|boutique|makelaar|agence|klanten|clients|customers)\b/.test(norm(q))) s += 3;
      if (k[0] === 'meme' && /\b(meme|memes|meme's|template|sjabloon|modele|sticker|stickers)\b/.test(norm(q)) && !/\b(launch|lancer|lancement|ticker|pack|coin|token)\b/.test(norm(q))) s += 2;
      if (k[0] === 'free' && /\b(free|gratis|gratuit|gratuite|goedkoop|cheap)\b/.test(norm(q))) s += 3;
      if (s > score) { score = s; best = k; }
    });
    return score >= 2 ? best : null;
  }
  function el(tag, css, text) { var e = document.createElement(tag); if (css) e.style.cssText = css; if (text != null) e.textContent = text; return e; }

  var css = 'position:fixed;right:14px;bottom:14px;z-index:9997;font:15px/1.45 system-ui,Segoe UI,Roboto,sans-serif';
  var root = el('div', css); root.id = 'bolt-guide';
  var btn = el('button', 'display:flex;align-items:center;gap:8px;background:#ffd800;color:#111;border:3px solid #000;border-radius:999px;padding:6px 14px 6px 6px;font-weight:900;cursor:pointer;box-shadow:4px 4px 0 #000;min-height:48px');
  btn.type = 'button'; btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'bolt-panel');
  var av = el('img', 'width:36px;height:36px;image-rendering:pixelated;background:#0b1a35;border-radius:50%;padding:3px'); av.src = '/bolt.png'; av.alt = '';
  btn.append(av, document.createTextNode(UI.open));
  var panel = el('div', 'display:none;position:absolute;right:0;bottom:62px;width:min(360px,calc(100vw - 28px));max-height:min(560px,calc(100vh - 100px));background:#0b1a35;color:#f4f7ff;border:2px solid #ffd800;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,.55);flex-direction:column;overflow:hidden');
  panel.id = 'bolt-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', UI.title);
  var head = el('div', 'display:flex;align-items:center;gap:8px;padding:10px 12px;background:#071226;border-bottom:1px solid rgba(169,212,255,.25)');
  var hav = av.cloneNode(); hav.style.width = '30px'; hav.style.height = '30px';
  var ht = el('b', 'flex:1', UI.title);
  var x = el('button', 'background:none;border:0;color:#fff;font-size:22px;cursor:pointer;min-width:44px;min-height:44px', '×'); x.type = 'button'; x.setAttribute('aria-label', UI.close);
  head.append(hav, ht, x);
  var log = el('div', 'flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:8px'); log.setAttribute('aria-live', 'polite');
  var chips = el('div', 'display:flex;flex-wrap:wrap;gap:6px;padding:0 12px 8px');
  var form = el('form', 'display:flex;gap:6px;padding:10px 12px;border-top:1px solid rgba(169,212,255,.25)');
  var inp = el('input', 'flex:1;min-width:0;padding:10px;border-radius:10px;border:1px solid rgba(169,212,255,.35);background:#050b1b;color:#fff;font:inherit');
  inp.placeholder = UI.ph; inp.maxLength = 200; inp.setAttribute('aria-label', UI.ph);
  var sb = el('button', 'background:#38f2ff;color:#04121a;border:0;border-radius:10px;padding:0 14px;font-weight:900;cursor:pointer;min-height:44px', UI.send); sb.type = 'submit';
  form.append(inp, sb);
  var foot = el('div', 'font-size:11.5px;color:#9fb0cc;padding:0 12px 10px', UI.note);
  panel.append(head, log, chips, form, foot); root.append(panel, btn);

  function bubble(text, me) {
    var b = el('div', 'max-width:88%;padding:8px 11px;border-radius:12px;' + (me ? 'align-self:flex-end;background:#38f2ff;color:#04121a' : 'align-self:flex-start;background:#13254a'), text);
    log.append(b); log.scrollTop = log.scrollHeight; return b;
  }
  function answer(k) {
    var b = bubble(k[3][L]);
    var links = el('div', 'display:flex;flex-wrap:wrap;gap:6px;margin-top:8px');
    k[4].forEach(function (l) {
      var a = el('a', 'background:#ffd800;color:#111;border-radius:8px;padding:6px 10px;font-weight:800;text-decoration:none;font-size:13.5px', l[1][L]);
      a.href = l[0]; if (/^https?:/.test(l[0])) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
      links.append(a);
    });
    b.append(links);
  }
  function chip(id) {
    var k = K.filter(function (t) { return t[0] === id; })[0];
    var c = el('button', 'background:transparent;color:#ffd800;border:1px solid #ffd800;border-radius:999px;padding:6px 10px;font:inherit;font-size:13px;cursor:pointer;min-height:36px', k[2][L]);
    c.type = 'button'; c.addEventListener('click', function () { bubble(k[2][L], true); answer(k); });
    return c;
  }
  QUICK.forEach(function (id) { chips.append(chip(id)); });
  form.addEventListener('submit', function (e) {
    e.preventDefault(); var q = inp.value.trim(); if (!q) return; inp.value = '';
    bubble(q, true); var k = match(q);
    if (k) answer(k);
    else { var b = bubble(UI.none); var row = el('div', 'display:flex;flex-wrap:wrap;gap:6px;margin-top:8px'); ['site', 'bot', 'free', 'safe', 'app', 'chain'].forEach(function (id) { row.append(chip(id)); }); b.append(row); }
  });
  var started = false;
  function toggle(open) {
    panel.style.display = open ? 'flex' : 'none'; btn.setAttribute('aria-expanded', String(open));
    if (open) { if (!started) { bubble(UI.hi); started = true; } inp.focus(); } else btn.focus();
  }
  btn.addEventListener('click', function () { toggle(panel.style.display !== 'flex'); });
  x.addEventListener('click', function () { toggle(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel.style.display === 'flex') toggle(false); });
  function mount() { document.body.appendChild(root); var off = document.getElementById('maiga-offline'); if (off) root.style.bottom = '64px'; }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
  window.addEventListener('offline', function () { root.style.bottom = '64px'; }); window.addEventListener('online', function () { root.style.bottom = '14px'; });
  /* read-only tools for AI agents (WebMCP), only in browsers that support it */
  if ((document.modelContext || navigator.modelContext) && !document.getElementById('maiga-agent-tools')) {
    var at = document.createElement('script'); at.id = 'maiga-agent-tools'; at.src = '/agent-tools.js'; at.defer = true; document.head.appendChild(at);
  }
})();
