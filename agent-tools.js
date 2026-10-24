/* $MAIGA tools for AI agents in the browser (WebMCP, read-only).
   Loaded by guide.js only when the browser offers document.modelContext (or the older navigator.modelContext).
   Every tool only READS public info or RETURNS a link. Nothing is posted, bought, signed or sent,
   and no tool touches wallets, keys or accounts. */
(function () {
  'use strict';
  var mc = (document.modelContext && typeof document.modelContext.registerTool === 'function') ? document.modelContext
         : (navigator.modelContext && typeof navigator.modelContext.registerTool === 'function') ? navigator.modelContext : null;
  if (!mc || window.__maigaAgentTools) return;
  window.__maigaAgentTools = 1;

  var SITE = location.origin + '/';
  var NOTE = 'Entertainment only. Not financial advice. DYOR. Never share a seed phrase or private key.';
  function out(obj) { return JSON.stringify(obj); }
  function str(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, n || 100); }
  var RO = { readOnlyHint: true };

  var TOOLS = [
    { url: 'meme.html', name: 'Meme Studio', what: 'Free meme generator: 190+ classic templates, MAIGA pixel scenes, own photo, stickers, PNG download. Runs in the browser.' },
    { url: 'factory.html', name: 'Meme Factory', what: 'Type one idea and a pixel crew drafts a meme-coin launch pack (name, ticker, meme, safety check, X post drafts). Nothing is launched or posted. Offline zip download.' },
    { url: 'garage.html', name: 'Bot Garage', what: 'Copy or build your own AI assistant prompt; test it with your own AI key, which stays in your browser.' },
    { url: 'free-ai-api.html', name: 'Free AI keys guide', what: 'What an API key is and free or cheap AI options for bots, with safety tips.' },
    { url: 'index.html#checkup', name: 'Token Checkup', what: 'Checklist of public red flags for a Solana token, based on GeckoTerminal data. Not a safety guarantee.' },
    { url: 'chain.html', name: 'Mini-Chain', what: 'Learn how a blockchain works: hash, mine and break blocks in the browser.' },
    { url: 'lend.html', name: 'Bot Bank', what: 'Play-money game about lending to AI agents: backers, fees, history, defaults. No real money.' },
    { url: 'app.html', name: '$MAIGA app', what: 'Installable app with all tools in one place.' },
    { url: 'custom-ai-bot.html', name: 'Custom AI bot', what: 'Request a custom AI assistant for a business (EN; NL: ai-bot-op-maat.html, FR: bot-ia-sur-mesure.html).' }
  ];

  var defs = [
    {
      name: 'maiga_list_tools',
      description: 'List the free tools on geopolcoins.xyz with a short description and link for each.',
      inputSchema: { type: 'object', properties: {} },
      annotations: RO,
      execute: async function () {
        return out({ tools: TOOLS.map(function (t) { return { name: t.name, url: SITE + t.url, description: t.what }; }), note: NOTE });
      }
    },
    {
      name: 'maiga_search_meme_templates',
      description: 'Search the Meme Studio templates by name or keyword (for example "drake", "cat", "fine"). Returns template ids, names, how many text lines each has, and a ready link.',
      inputSchema: { type: 'object', properties: { query: { type: 'string', description: 'Word to search for' }, limit: { type: 'integer', minimum: 1, maximum: 25 } }, required: ['query'] },
      annotations: RO,
      execute: async function (a) {
        var q = str(a && a.query, 40).toLowerCase(), lim = Math.max(1, Math.min(25, parseInt(a && a.limit, 10) || 10));
        var r = await fetch(SITE + 'meme/templates.json', { credentials: 'omit' });
        var list = await r.json();
        var hits = list.filter(function (t) { return (t.n + ' ' + t.id + ' ' + (t.k || []).join(' ')).toLowerCase().indexOf(q) >= 0; }).slice(0, lim);
        return out({ results: hits.map(function (t) { return { id: t.id, name: t.n, text_lines: t.b.length, example: t.e, studio_url: SITE + 'meme.html#tpl=' + encodeURIComponent(t.id) }; }),
          pixel_templates: ['mw1', 'mw2', 'mw3', 'mw4', 'mw5', 'mw6'], credit: 'Templates: memegen by Jace Browning (MIT).' });
      }
    },
    {
      name: 'maiga_meme_studio_link',
      description: 'Build a link that opens the Meme Studio with a template and top/bottom text filled in. The user downloads the image themselves.',
      inputSchema: { type: 'object', properties: { template_id: { type: 'string', description: 'Template id from maiga_search_meme_templates, or mw1-mw6 for MAIGA pixel scenes' }, top: { type: 'string', maxLength: 120 }, bottom: { type: 'string', maxLength: 120 } } },
      annotations: RO,
      execute: async function (a) {
        a = a || {};
        var p = new URLSearchParams();
        var id = str(a.template_id, 40).replace(/[^a-z0-9-]/gi, '');
        if (id) p.set('tpl', id);
        if (a.top) p.set('top', str(a.top, 120));
        if (a.bottom) p.set('bottom', str(a.bottom, 120));
        return out({ url: SITE + 'meme.html#' + p.toString(), rules: 'No price promises, fake giveaways or words put in real people\'s mouths.' });
      }
    },
    {
      name: 'maiga_factory_link',
      description: 'Build a link that runs the Meme Factory in free-template mode for an idea of 1 to 3 words. It only drafts a launch pack; nothing is launched or posted.',
      inputSchema: { type: 'object', properties: { idea: { type: 'string', maxLength: 24, description: 'One to three words, for example "sleepy cat"' } }, required: ['idea'] },
      annotations: RO,
      execute: async function (a) {
        var idea = str(a && a.idea, 24).replace(/[^A-Za-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
        if (idea.length < 2) return out({ error: 'Give an idea of 1 to 3 words.' });
        return out({ url: SITE + 'factory.html?idea=' + encodeURIComponent(idea) + '&go=1', note: 'Drafts only. ' + NOTE });
      }
    },
    {
      name: 'maiga_free_ai_options',
      description: 'Summary of free or cheap AI providers for running a bot, as checked by the site, with the link to the full guide.',
      inputSchema: { type: 'object', properties: {} },
      annotations: RO,
      execute: async function () {
        return out({ checked: '2026-10-23', guide: SITE + 'free-ai-api.html',
          options: ['OpenRouter models ending in :free', 'Groq free plan', 'Mistral Experiment plan (phone verification, data may be used for training)', 'Google Gemini free tier (data may be used; not for apps serving EU/UK/CH users)', 'Cloudflare Workers AI free daily allowance', 'Ollama on your own computer (private)', 'Paid: Anthropic, OpenAI'],
          safety: 'Keep keys private, set a spending limit, never paste a key on a site you do not trust.' });
      }
    },
    {
      name: 'maiga_coin_facts',
      description: 'Public facts about the $MAIGA meme coin (chain and contract address) and links to check it yourself. No price predictions.',
      inputSchema: { type: 'object', properties: {} },
      annotations: RO,
      execute: async function () {
        var ca = '3eMVbLZndiVZc4kPvLwUs4wdW1ChQ9R47seZv3Jppump';
        return out({ name: '$MAIGA (Make AI Great Again)', type: 'satirical meme coin', chain: 'Solana (Token-2022)', contract_address: ca,
          verify: ['https://solscan.io/token/' + ca, 'https://www.geckoterminal.com/solana/tokens/' + ca],
          note: NOTE + ' Always compare the contract address letter by letter. The free tools do not need a wallet.' });
      }
    }
  ];

  defs.forEach(function (d) {
    try { var p = mc.registerTool(d); if (p && p.catch) p.catch(function () {}); } catch (e) {}
  });
})();
