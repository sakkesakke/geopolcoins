// Ko-fi webhook -> CRM.
// Ko-fi posts application/x-www-form-urlencoded with one field "data" (a JSON string).
// We only accept it when data.verification_token matches the secret KOFI_VERIFICATION_TOKEN
// (set by the owner in Supabase > Edge Functions > Secrets; copied from Ko-fi > Settings > API).
// The sale is stored by public.kofi_record (service role only). Nothing else is reachable from here.

const MAX_BODY = 32_000;

function safeEqual(a: string, b: string): boolean {
  const ea = new TextEncoder().encode(a);
  const eb = new TextEncoder().encode(b);
  let diff = ea.length ^ eb.length;
  for (let i = 0; i < Math.max(ea.length, eb.length); i++) diff |= (ea[i] ?? 0) ^ (eb[i] ?? 0);
  return diff === 0;
}

function serviceKey(): { header: Record<string, string> } | null {
  try {
    const keys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
    if (keys.default) return { header: { apikey: keys.default } };
  } catch (_) { /* fall through to the legacy key */ }
  const legacy = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  return legacy ? { header: { apikey: legacy, Authorization: `Bearer ${legacy}` } } : null;
}

const text = (status: number, body: string) => new Response(body, { status, headers: { "content-type": "text/plain" } });

Deno.serve(async (req) => {
  if (req.method !== "POST") return text(405, "POST only");
  const expected = Deno.env.get("KOFI_VERIFICATION_TOKEN") ?? "";
  if (expected.length < 8) return text(503, "not configured");

  const raw = await req.text();
  if (raw.length > MAX_BODY) return text(413, "too large");

  let data: Record<string, unknown>;
  try {
    const ct = req.headers.get("content-type") ?? "";
    const json = ct.includes("application/json") ? JSON.parse(raw).data ?? raw : new URLSearchParams(raw).get("data");
    data = typeof json === "string" ? JSON.parse(json) : (json as Record<string, unknown>);
    if (!data || typeof data !== "object") throw new Error("no data");
  } catch (_) {
    return text(400, "bad payload");
  }

  if (!safeEqual(String(data.verification_token ?? ""), expected)) return text(401, "unauthorized");
  delete data.verification_token;

  const key = serviceKey();
  if (!key) return text(503, "no service key");
  const r = await fetch(`${Deno.env.get("SUPABASE_URL")}/rest/v1/rpc/kofi_record`, {
    method: "POST",
    headers: { ...key.header, "content-type": "application/json" },
    body: JSON.stringify({ p: data }),
  });
  if (!r.ok) {
    console.error("kofi_record failed", r.status, (await r.text()).slice(0, 300));
    return text(500, "store failed"); // Ko-fi retries on non-200
  }
  return text(200, "ok");
});
