import json,html,re
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','answers.html')
G='garage.html'; FREE='free-ai-api.html'
KF20='https://ko-fi.com/s/3805e02171'; KFSAL='https://ko-fi.com/s/5ba0d6d48c'; KFRE='https://ko-fi.com/s/6b98e0ae7e'; KFRES='https://ko-fi.com/s/7e8e8ec0e1'
SECTIONS=[
('Getting started',[
('Is an AI chatbot worth it for a small business?',
f'<p>It is worth it when the same questions come in again and again: opening hours, prices you already publish, how to book, where to park, what to bring. A bot can answer those at night and on busy days, and hand everything else to you. It is not worth it if you only get a few messages a week, or if every question needs your personal judgement.</p><p>A good test: write down the last 20 messages you received. If more than half could be answered from a short fact sheet, a bot will save you time. Start small with one channel and one job, and check its answers for the first weeks.</p>'),
('Can I make an AI chatbot for my business without coding, for free?',
f'<p>Yes. A chatbot is mostly a good set of instructions (a "prompt") plus your business facts. You can write those yourself, test them for free in our <a href="{G}">Bot Garage</a> with canned answers, and later connect a free or cheap AI key. Our <a href="{FREE}">free AI keys guide</a> lists options such as OpenRouter free models, Groq and Cloudflare Workers AI.</p><p>Putting the bot on WhatsApp, Instagram or your website usually needs a connector tool or a small script. The Bot Garage can export starter code for Telegram and Discord.</p>'),
('What is the difference between using ChatGPT and having my own bot?',
'<p>When you chat in ChatGPT, you are the user and you start from zero each time. "Your own bot" means the AI gets fixed instructions before every customer message: who it works for, your facts, what it may and may not say, and when to hand over to a human. Customers then talk to that bot on your channel. The model underneath can be the same; the difference is the instructions, the facts and where it runs.</p>'),
('What is a prompt or system prompt?',
'<p>A system prompt is the hidden briefing the AI reads before every conversation. A good one has: the role ("You are the booking assistant of Studio X"), your facts (hours, services, prices you publish), clear rules ("never invent a price", "no medical advice", "if the customer is upset, offer a call"), the tone and language, and what to do when it does not know. Most bad bots come from vague prompts, not from bad AI.</p>'),
('How much does it cost to run an AI assistant per month?',
f'<p>For a small business it is often a few dollars or less per month in AI usage, because one customer question costs a fraction of a cent with small models. Some providers have free tiers with daily limits. Costs grow with long conversations, big models and many users. Always set a spending limit at your AI provider. Tools that host the bot for you (website widgets, WhatsApp connectors) add their own monthly fee. See our <a href="{FREE}">free and cheap AI options</a>.</p>'),
]),
('Safety, privacy and the law',[
('Will an AI bot make up prices or wrong information?',
'<p>It can. AI models sometimes "hallucinate": they fill gaps with something that sounds right. You reduce this a lot by giving the bot a short fact sheet, telling it to only use those facts, and adding a rule such as "If the answer is not in the facts, say you will check with the team." Never let a bot confirm prices, availability or anything legal on its own unless those facts are written in its instructions, and test it with tricky questions before customers see it.</p>'),
('Do I have to tell customers they are talking to an AI?',
'<p>Being open is the safest choice everywhere, and in the EU it becomes a legal duty: under the EU AI Act, systems that chat with people must make clear they are AI, with these transparency rules applying from August 2026. A simple first line such as "Hi, I am the digital assistant of [business]. A human can take over at any time." covers it. Several US states also have disclosure rules for bots in sales or political contexts.</p>'),
('Is an AI chatbot allowed under GDPR and US privacy laws?',
'<p>Yes, if you handle data carefully. Collect only what you need (for example a name and a time slot, not a date of birth), tell people in your privacy notice that you use an AI provider, choose providers with a data processing agreement, and do not paste sensitive data such as health details or ID numbers into the bot. Some free AI tiers may use your data to improve their models, so read the terms before you put customer messages through them. This is general information, not legal advice.</p>'),
('Is it safe to paste my API key into a website?',
f'<p>Only into tools you trust and that explain where the key goes. On our tools the key goes straight from your browser to the AI provider you pick, never to us. Good habits: create a separate key per tool, set a monthly spending limit, never share a key in a chat or screenshot, and delete the key at the provider if you have any doubt. More in our <a href="{FREE}">API key guide</a>.</p>'),
]),
('Hair and beauty salons',[
('Can an AI assistant reduce no-shows at my salon?',
f'<p>It can help with the parts that cause no-shows: friendly reminders the day before, an easy way to cancel or move a booking, and a clear message about your cancellation policy. The bot should not invent new rules or fines; it should repeat the policy you wrote. Real bookings still go through your booking system. Our <a href="{KFSAL}">salon bot pack</a> includes a no-show and reminder assistant you can adapt.</p>'),
('Can a bot answer "how much is a balayage?"',
'<p>Only with prices you give it. Colour work often depends on hair length and condition, so a good salon bot gives the published "from" price, explains that the final price follows a consultation, and offers to book one. It should never promise results or give advice about allergies or skin reactions; those go to a stylist.</p>'),
]),
('Real estate agents',[
('Can I use ChatGPT to write property listing descriptions?',
'<p>Yes, it is one of the most popular uses. Give it the real facts (rooms, size, energy rating, location, features) and ask for a clear, honest description. Check every fact before publishing, because the AI may add things that are not true. In the US, avoid wording about who the property is "ideal for" (families, singles, religion, origin and so on) because fair housing rules forbid discriminatory language; describe the property, not the buyer.</p>'),
('Can an AI bot qualify leads and book viewings?',
f'<p>A bot can ask the first questions (buy or rent, budget range, area, timing) and propose viewing slots that you have made available, then pass the lead to you. It should not give opinions about property value, mortgages or legal matters, and it should store only the data you need. Our <a href="{KFRE}">real-estate bot pack</a> has lead, viewing and follow-up assistants with these rules built in.</p>'),
]),
('Restaurants and cafés',[
('Can a restaurant chatbot answer allergen questions?',
'<p>It can share your written allergen information and must then send the guest to staff for confirmation. Recipes and suppliers change, and a wrong answer can be dangerous, so a bot should never say a dish is "safe" for an allergy. In the EU, businesses must be able to inform guests about the 14 major allergens; let the bot point to that information and to a human.</p>'),
('Can AI write replies to Google reviews?',
f'<p>Yes, as drafts you check. Ask for a short, personal reply that thanks the guest, mentions something specific they wrote, and for complaints apologises and invites them to contact you privately. Do not let AI post automatically and do not argue or share private details in public. Our <a href="{KFRES}">restaurant bot pack</a> includes a review reply assistant.</p>'),
]),
('Choosing tools',[
('Which AI is free for a small business bot?',
f'<p>Free options change often. In our latest check we listed OpenRouter models marked ":free", Groq\'s free plan, Mistral\'s Experiment plan, Google Gemini\'s free tier (not for apps serving EU or UK users) and Cloudflare Workers AI\'s daily free allowance, plus running a model on your own computer with Ollama. Free tiers have limits and may use your data, so they are best for testing. See the <a href="{FREE}">full guide</a>.</p>'),
('Where should I put my bot: website, WhatsApp, Instagram or Telegram?',
'<p>Put it where your customers already message you. For many salons and restaurants that is Instagram or WhatsApp; for real estate it is often the website and email. Telegram and Discord are the easiest to start with technically. Each platform has its own rules for automated messages, so read them before you go live, and always offer a way to reach a human.</p>'),
]),
]
def text(h): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',h))).strip()
faq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":text(a)}} for _,qs in SECTIONS for q,a in qs]}
n=sum(len(qs) for _,qs in SECTIONS)
body=''
toc=''
for i,(title,qs) in enumerate(SECTIONS):
    sid='s%d'%(i+1)
    toc+=f'<li><a href="#{sid}">{title}</a> ({len(qs)})</li>'
    body+=f'<h2 id="{sid}">{title}</h2>\n'
    for q,a in qs:
        qid=re.sub(r'[^a-z0-9]+','-',q.lower()).strip('-')[:60]
        body+=f'<details id="{qid}"><summary><h3>{html.escape(q)}</h3></summary><div class="a">{a}</div></details>\n'
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Bots for Small Business: {n} Questions Answered</title>
<meta name="description" content="Honest answers to the questions small businesses ask about AI chatbots: cost, free tools, privacy, hallucinations, salons, real estate and restaurants.">
<link rel="canonical" href="https://geopolcoins.xyz/answers.html">
<meta property="og:type" content="article"><meta property="og:title" content="AI bots for small business: {n} real questions, honest answers"><meta property="og:description" content="Cost, free tools, privacy, safety rules and examples for salons, real estate and restaurants."><meta property="og:url" content="https://geopolcoins.xyz/answers.html"><meta property="og:image" content="https://geopolcoins.xyz/og-garage.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><meta name="theme-color" content="#050b1b">
<script type="application/ld+json">{json.dumps(faq,ensure_ascii=False)}</script>
<style>
:root{{--bg:#050b1b;--panel:#0b1a35;--text:#f4f7ff;--dim:#c3cfe4;--gold:#ffd800;--line:rgba(169,212,255,.25)}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:17px/1.65 system-ui,Segoe UI,Roboto,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:16px 16px 60px}}a{{color:var(--gold)}}
.skip{{position:absolute;left:8px;top:-60px;background:var(--gold);color:#000;padding:10px 14px;border-radius:8px;font-weight:800}}.skip:focus{{top:8px}}
.top{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:14px}}.top a{{display:inline-block;padding:6px 0}}
h1{{font-size:clamp(28px,5vw,42px);line-height:1.15;margin:18px 0 6px}}.lead{{color:var(--dim);font-size:18px}}
h2{{font-size:22px;color:var(--gold);margin:34px 0 10px}}
details{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:10px 0;overflow:hidden}}
summary{{cursor:pointer;padding:14px 46px 14px 16px;list-style:none;position:relative}}summary::-webkit-details-marker{{display:none}}
summary::after{{content:"+";position:absolute;right:16px;top:10px;font-size:24px;color:var(--gold)}}details[open] summary::after{{content:"–"}}
summary h3{{display:inline;font-size:17px;margin:0}}
.a{{padding:0 16px 8px;color:var(--dim)}}.a p{{margin:0 0 12px}}
.toc{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px 16px 12px 34px;font-size:15px}}
.cta{{background:linear-gradient(160deg,#16305e,#0a1730);border:2px solid var(--gold);border-radius:16px;padding:16px;margin-top:30px}}
.btn{{display:inline-block;margin:6px 8px 0 0;padding:10px 14px;border-radius:10px;background:var(--gold);color:#111;font-weight:800;text-decoration:none}}.btn.alt{{background:transparent;color:#fff;border:1px solid var(--gold)}}
.note{{color:var(--dim);font-size:14px}}
footer{{text-align:center;color:var(--dim);font-size:13px;margin-top:40px}}footer a{{display:inline-block;padding:6px 2px}}
</style></head><body>
<a class="skip" href="#main">Skip to content</a>
<main id="main">
<div class="top"><a href="/">&larr; geopolcoins.xyz</a><nav aria-label="More"><a href="{G}">Bot Garage</a> · <a href="{FREE}">Free AI keys</a> · <a href="https://ko-fi.com/geopolcoins/shop" target="_blank" rel="noopener">Bot packs</a></nav></div>
<h1>AI bots for small business: {n} real questions, honest answers</h1>
<p class="lead">The questions owners of salons, agencies, restaurants and shops actually ask before they use an AI assistant. Short, practical answers, including the limits.</p>
<p class="note">Last updated: 24 October 2026. General information only, not legal or financial advice.</p>
<ol class="toc">{toc}</ol>
{body}
<div class="cta"><h2 style="margin-top:0">Try it yourself</h2><p>Build and test a business bot for free in your browser, or start from a ready-made pack with prompts, test questions and safety rules.</p>
<a class="btn" href="{G}">Open the free Bot Garage</a><a class="btn alt" href="{KF20}" target="_blank" rel="noopener">20-bot pack (from $9)</a><a class="btn alt" href="custom-ai-bot.html">Ask for a custom bot</a></div>
<footer>© 2026 $MAIGA • <a href="/">HOME</a> • <a href="{G}">BOT GARAGE</a> • <a href="ai-bots-salon.html">SALONS</a> • <a href="ai-bots-real-estate.html">REAL ESTATE</a> • <a href="ai-bots-restaurant.html">RESTAURANTS</a> • <a href="privacy.html">PRIVACY</a> • <a href="cookies.html">COOKIES</a> • <a href="legal.html">LEGAL</a></footer>
</main>
<script>(function(){{try{{if(navigator.webdriver||/bot|crawl|spider|slurp|preview|headless/i.test(navigator.userAgent))return;var r='direct';if(document.referrer){{var h=new URL(document.referrer).hostname.replace(/^www\\./,'').toLowerCase();r=h===location.hostname.replace(/^www\\./,'').toLowerCase()?'internal':(h==='t.co'?'x.com':h);}}fetch('https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/track_view',{{method:'POST',keepalive:true,credentials:'omit',headers:{{apikey:'sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN','Content-Type':'application/json'}},body:JSON.stringify({{p_page:'ai',p_ref:r}})}}).catch(function(){{}});}}catch(e){{}}}})();</script>
<script>if(location.hash){{var d=document.getElementById(location.hash.slice(1));if(d&&d.tagName==='DETAILS')d.open=true;}}</script>
<script src="pwa.js" defer></script>
<script src="guide.js" defer></script>
</body></html>
'''
open(OUT,'w').write(page); print(n,len(page))
