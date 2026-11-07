/* checkup-core.js: the Token Checkup rules, shared by hq.html (full checkup) and embed.html (widget).
   Reads public GeckoTerminal data only. A checklist, not advice. */
(function () {
  "use strict";
  var API = "https://api.geckoterminal.com/api/v2/networks/solana";
  function num(x){if(x===null||x===undefined||x==="")return null;var n=Number(x);return isFinite(n)?n:null;}
  function clean(t,max){return String(t==null?"":t).replace(/[\u0000-\u001f\u007f​-‏‪-‮⁦-⁩]/g,"").replace(/\s+/g," ").trim().slice(0,max);}
  function usd(n){if(n===null)return "—";if(n>=1e9)return "$"+(n/1e9).toFixed(2)+"B";if(n>=1e6)return "$"+(n/1e6).toFixed(2)+"M";if(n>=1e3)return "$"+(n/1e3).toFixed(1)+"K";return "$"+n.toFixed(2);}
  function get(u){return new Promise(function(res,rej){
    var ctl=("AbortController" in window)?new AbortController():null,t=setTimeout(function(){if(ctl)ctl.abort();rej(new Error("timeout"));},9000);
    fetch(u,{headers:{"Accept":"application/json"},signal:ctl?ctl.signal:undefined}).then(function(r){clearTimeout(t);if(!r.ok)throw new Error("http "+r.status);return r.json();}).then(res,function(e){clearTimeout(t);rej(e);});
  });}
  function wrap(u){return get(u).then(function(j){return {ok:true,j:j};},function(e){return {ok:false,e:String(e&&e.message||e)};});}
  function auth(v){
    if(v===undefined||v===null)return "unk";
    if(v===false)return "none";
    if(v===true)return "active";
    if(typeof v==="string"){var t=v.trim();if(!t)return "unk";if(/^(no|no[_ -]?authority|none|revoked|disabled|false|null)$/i.test(t))return "none";if(/^(unknown|n\/a|-)$/i.test(t))return "unk";return "active";}
    return "unk";
  }
  var RWA=/\b(rwa|real[- ]world|real estate|property|properties|gold|silver|oil|treasur(y|ies)|bonds?|asset[- ]backed|backed by|tokeni[sz]ed|equity|stocks?|shares|dividends?|yield|apy|collateral|vault|reserves?)\b/i;
  var PROMISE=/(guarantee|risk[- ]free|100x|1000x|passive income|get rich|can'?t lose|no risk)/i;
  function ago(iso){var t=Date.parse(iso);if(!isFinite(t))return null;return (Date.now()-t)/36e5;}
  function fmtAge(h){if(h<1)return "under 1 hour";if(h<48)return Math.floor(h)+" hours";return Math.floor(h/24)+" days";}
  function analyse(mint,R){
    var tok=R.tok.ok&&R.tok.j&&R.tok.j.data&&R.tok.j.data.attributes||null;
    var inf=R.inf.ok&&R.inf.j&&R.inf.j.data&&R.inf.j.data.attributes||null;
    var pools=R.pools.ok&&R.pools.j&&R.pools.j.data||[];
    var out={mint:mint,name:"",sym:"",checks:[],rwa:false,red:0,yellow:0,unk:0,data:!!(tok||inf||pools.length)};
    out.name=clean((tok&&tok.name)||(inf&&inf.name)||"Unknown token",32);out.sym=clean((tok&&tok.symbol)||(inf&&inf.symbol)||"",12).replace(/^\$+/,"");
    function add(l,title,text){out.checks.push({l:l,t:title,x:text});if(l==="bad")out.red++;else if(l==="warn")out.yellow++;else if(l==="unk")out.unk++;}
    if(!out.data){add("unk","No data found","We found no trading pool or token page for this address. It may be new, never traded, or not a token. Open Solscan to look yourself.");return out;}
    var liq=tok?num(tok.total_reserve_in_usd):null;
    if(liq===null&&pools.length){var s=0,any=false;pools.forEach(function(p){var v=p&&p.attributes?num(p.attributes.reserve_in_usd):null;if(v!==null){s+=v;any=true;}});if(any)liq=s;}
    if(liq===null)add("unk","Liquidity","Not available. Check DexScreener.");
    else if(liq<2000)add("bad","Very thin liquidity ("+usd(liq)+")","Prices can jump a lot and selling can be hard or impossible at size.");
    else if(liq<20000)add("warn","Thin liquidity ("+usd(liq)+")","A small trade can move the price a lot.");
    else add("ok","Liquidity "+usd(liq),"Not thin, but liquidity can be removed by whoever controls it.");
    var oldest=null;pools.forEach(function(p){var h=p&&p.attributes?ago(p.attributes.pool_created_at):null;if(h!==null&&(oldest===null||h>oldest))oldest=h;});
    if(oldest===null)add("unk","Age","Pool age not available.");
    else if(oldest<24)add("warn","Brand new: trading for "+fmtAge(oldest),"Most scams and rugs happen in the first hours and days.");
    else if(oldest<24*7)add("info","Young: trading for "+fmtAge(oldest),"Still early. Little history to judge.");
    else add("ok","Trading for "+fmtAge(oldest),"Age alone proves nothing, but it has survived the first days.");
    var ma=auth(inf&&inf.mint_authority),fa=auth(inf&&inf.freeze_authority);
    if(!inf||ma==="unk")add("unk","Mint authority","Unknown here. Check on Solscan: if it is not revoked, more tokens can be created.");
    else if(ma==="active")add("warn","Mint authority is NOT revoked","The controller can create more tokens, which dilutes holders.");
    else add("ok","Mint authority revoked","No new tokens can be created.");
    if(!inf||fa==="unk")add("unk","Freeze authority","Unknown here. Check on Solscan: if it is not revoked, wallets can be frozen.");
    else if(fa==="active")add("warn","Freeze authority is NOT revoked","The controller can freeze token accounts, so you may be unable to sell.");
    else add("ok","Freeze authority revoked","Token accounts cannot be frozen by an authority.");
    var hd=inf&&inf.holders;
    if(!hd)add("unk","Holders","Holder data not available. Check Solscan.");
    else{
      var cnt=num(hd.count),t10=hd.distribution_percentage?num(hd.distribution_percentage.top_10):null;
      if(cnt!==null)add(cnt<50?"warn":"info","Holders: "+cnt,cnt<50?"Very few holders.":"Number of wallets holding the token. It can include bots and the same person many times.");
      if(t10!==null){var pct=t10.toFixed(1)+"%";
        if(t10>80)add("bad","Top 10 wallets hold "+pct,"A handful of wallets hold almost everything. This can include the liquidity pool, so open the holder list on Solscan.");
        else if(t10>50)add("warn","Top 10 wallets hold "+pct,"Concentrated. Check on Solscan which of them are pools or exchanges.");
        else add("ok","Top 10 wallets hold "+pct,"Not extremely concentrated, though one person can use many wallets.");}
    }
    var dev=inf?num(inf.developer_holding_percentage):null;
    if(dev!==null){var dp=dev.toFixed(1)+"%";
      if(dev>=20)add("bad","Creator wallet holds "+dp,"The wallet that launched the token can sell a big part at once and crash the price.");
      else if(dev>=5)add("warn","Creator wallet holds "+dp,"A noticeable share. Watch whether it gets sold.");
      else add("ok","Creator wallet holds "+dp,"Small share. The creator can still use other wallets.");}
    var hp=inf&&typeof inf.is_honeypot==="string"?inf.is_honeypot.toLowerCase():"";
    if(hp==="yes")add("bad","Honeypot warning","GeckoTerminal flags this as a possible honeypot: you may be able to buy but not sell.");
    else if(hp==="no")add("ok","No honeypot flag","GeckoTerminal saw no sign that selling is blocked. Not a guarantee.");
    var lp=(inf&&inf.launchpad_details)||(tok&&tok.launchpad_details);
    if(lp&&typeof lp==="object"){
      if(lp.completed===true)add("info","Left its launchpad","It graduated from its launchpad (for example pump.fun) and now trades in a normal pool.");
      else{var gp=num(lp.graduation_percentage);add("warn","Still on its launchpad"+(gp!==null?" ("+gp.toFixed(0)+"% to graduation)":""),"Still on a bonding curve. Prices move very fast and most such tokens never graduate.");}}
    var b24=0,s24=0,v24=0,ch24=null,anyTx=false;
    pools.forEach(function(p){var a=p&&p.attributes;if(!a)return;var t=a.transactions&&a.transactions.h24;if(t){anyTx=true;b24+=num(t.buys)||0;s24+=num(t.sells)||0;}
      v24+=a.volume_usd?(num(a.volume_usd.h24)||0):0;var c=a.price_change_percentage?num(a.price_change_percentage.h24):null;if(c!==null&&ch24===null)ch24=c;});
    if(anyTx){
      if(b24>=10&&s24===0)add("bad","Buys but no sells in 24h ("+b24+" / 0)","Many buys and not one sell is a typical sign that selling is blocked.");
      else if(b24+s24===0)add("info","No trades in 24h","Nobody bought or sold in the last day. Hard to get out at a fair price.");
      else add("info","Trades in 24h: "+b24+" buys / "+s24+" sells","Counts only. Bots can make many small trades.");}
    if(liq!==null&&liq>0&&v24>liq*50)add("warn","Volume is "+Math.round(v24/liq)+"x the liquidity","Trading this heavy against a small pool can be fake volume from bots.");
    if(ch24!==null&&ch24>=300)add("warn","Price +"+Math.round(ch24)+"% in 24h","Huge jumps often fall back just as fast. Late buyers usually pay for it.");
    else if(ch24!==null&&ch24<=-60)add("warn","Price "+Math.round(ch24)+"% in 24h","A crash this big can mean holders or the creator are leaving.");
    var gts=inf?num(inf.gt_score):null;
    if(gts!==null)add("info","GeckoTerminal score "+Math.round(gts)+"/100","Their own mix of pool, holders, info and age. A score, not a verdict.");
    var desc=clean(inf&&inf.description,400),blob=out.name+" "+desc;
    var sites=(inf&&inf.websites&&inf.websites.length)||0,tw=inf&&inf.twitter_handle;
    add(sites||tw?"info":"info",sites||tw?"Has public links listed":"No website or X listed",sites||tw?"Links on a token page can be copied from real projects. Check them yourself.":"That alone says little, but real projects usually have somewhere to ask questions.");
    if(PROMISE.test(blob))add("bad","Promise wording found","Words like guaranteed, risk-free or 100x are a classic scam sign. Nobody can promise returns.");
    if(RWA.test(blob)){out.rwa=true;add("warn","Claims about real assets or yield","A token is only a record on a blockchain. It is worth no more than the legal and physical structure behind it. See the questions below.");}
    return out;
  }
  function fetchAll(mint) {
    return Promise.all([wrap(API + "/tokens/" + mint), wrap(API + "/tokens/" + mint + "/info"), wrap(API + "/tokens/" + mint + "/pools?page=1")])
      .then(function (a) { return { tok: a[0], inf: a[1], pools: a[2] }; });
  }
  function verdict(o) {
    if (!o.data) return { c: "warn", t: "Not enough data", s: "Not enough data" };
    if (o.red) return { c: "bad", t: "No. Red flags.", s: "No. Red flags" };
    if (o.yellow) return { c: "warn", t: "Hmm. Read the yellow.", s: "Hmm. Read the yellow" };
    return { c: "ok", t: "Nothing alarming. Not a safety stamp.", s: "Nothing alarming" };
  }
  window.MAIGA_CORE = { API: API, B58: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/, num: num, clean: clean, usd: usd, get: get, wrap: wrap, auth: auth, ago: ago, fmtAge: fmtAge, analyse: analyse, fetchAll: fetchAll, verdict: verdict };
})();
