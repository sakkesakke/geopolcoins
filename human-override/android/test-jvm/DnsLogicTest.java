/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. JVM unit test for DnsLogic (run in CI). */
import xyz.geopolcoins.humanoverride.DnsLogic;
import java.util.*;
public class DnsLogicTest {
  static int fails = 0;
  static void ok(boolean c, String m) { System.out.println((c ? "PASS " : "FAIL ") + m); if (!c) fails++; }
  static byte[] query(String name, int id) {
    java.io.ByteArrayOutputStream d = new java.io.ByteArrayOutputStream();
    d.write(id >> 8); d.write(id); d.write(0x01); d.write(0x00); d.write(0); d.write(1); for (int i = 0; i < 6; i++) d.write(0);
    for (String l : name.split("\\.")) { d.write(l.length()); d.write(l.getBytes(), 0, l.length()); }
    d.write(0); d.write(0); d.write(1); d.write(0); d.write(1);
    byte[] dns = d.toByteArray(); byte[] p = new byte[28 + dns.length];
    p[0] = 0x45; p[2] = (byte) (p.length >> 8); p[3] = (byte) p.length; p[8] = 64; p[9] = 17;
    p[12] = 10; p[13] = 111; p[14] = (byte) 222; p[15] = 2;  p[16] = 10; p[17] = 111; p[18] = (byte) 222; p[19] = 1;
    p[20] = (byte) 0xC3; p[21] = 0x50; p[22] = 0; p[23] = 53; p[24] = (byte) ((8 + dns.length) >> 8); p[25] = (byte) (8 + dns.length);
    System.arraycopy(dns, 0, p, 28, dns.length); return p;
  }
  public static void main(String[] a) {
    Set<String> list = DnsLogic.parseList("# test\nchatgpt.com\nopenai.com\ngoogle.com\nBAD DOMAIN\nclaude.ai\n", 1000);
    ok(list.contains("chatgpt.com") && list.contains("claude.ai"), "list parsed");
    ok(!list.contains("google.com"), "protected google.com never in list");
    ok(list.size() == 3, "invalid line ignored (size " + list.size() + ")");
    ok(DnsLogic.blocked("chatgpt.com", list), "chatgpt.com blocked");
    ok(DnsLogic.blocked("cdn.oaistatic.chat.openai.com", list), "deep subdomain of openai.com blocked");
    ok(DnsLogic.blocked("CHATGPT.COM.", list), "case and trailing dot");
    ok(!DnsLogic.blocked("notchatgpt.com", list), "lookalike not blocked");
    ok(!DnsLogic.blocked("www.google.com", list), "google not blocked");
    byte[] q = query("www.chatgpt.com", 0x1234);
    int off = DnsLogic.dnsPayloadOffset(q, q.length);
    ok(off == 28, "finds DNS payload");
    ok("www.chatgpt.com".equals(DnsLogic.questionName(q, off, q.length)), "reads question name");
    byte[] nx = DnsLogic.nxdomain(q, off, q.length);
    ok((nx[0] & 0xFF) == 0x12 && (nx[1] & 0xFF) == 0x34, "reply keeps id");
    ok((nx[2] & 0x80) != 0 && (nx[3] & 0x0F) == 3, "QR set and NXDOMAIN");
    byte[] r = DnsLogic.udpReply(q, nx);
    ok(r[12] == 10 && (r[15] & 0xFF) == 1 && (r[19] & 0xFF) == 2, "addresses swapped");
    ok((r[22] & 0xFF) == 0xC3 && (r[23] & 0xFF) == 0x50 && r[21] == 53, "ports swapped");
    long s = 0; for (int i = 0; i < 20; i += 2) s += ((r[i] & 0xFF) << 8) | (r[i + 1] & 0xFF); while ((s >> 16) != 0) s = (s & 0xFFFF) + (s >> 16);
    ok(s == 0xFFFF, "IPv4 header checksum valid");
    ok(((r[2] & 0xFF) << 8 | (r[3] & 0xFF)) == r.length, "total length correct");
    // hostile inputs must not crash
    Random rnd = new Random(1); int crashes = 0;
    for (int i = 0; i < 20000; i++) { byte[] b = new byte[rnd.nextInt(80)]; rnd.nextBytes(b); if (b.length > 0) b[0] = 0x45;
      try { int o = DnsLogic.dnsPayloadOffset(b, b.length); if (o > 0) DnsLogic.questionName(b, o, b.length); } catch (Exception e) { crashes++; } }
    ok(crashes == 0, "20,000 random packets, no crash");
    byte[] loop = query("a.com", 1); loop[28 + 12] = (byte) 0xC0;   // compression pointer in question
    ok(DnsLogic.questionName(loop, 28, loop.length) == null, "rejects compression pointer");

    // SafeSearch (family filter)
    ok("forcesafesearch.google.com".equals(DnsLogic.safeTarget("www.google.com")), "google.com -> forcesafesearch");
    ok("forcesafesearch.google.com".equals(DnsLogic.safeTarget("www.google.co.uk.")), "google.co.uk -> forcesafesearch");
    ok("forcesafesearch.google.com".equals(DnsLogic.safeTarget("google.be")), "google.be -> forcesafesearch");
    ok(DnsLogic.safeTarget("mail.google.com") == null, "gmail untouched");
    ok(DnsLogic.safeTarget("forcesafesearch.google.com") == null, "no loop on the strict name");
    ok("strict.bing.com".equals(DnsLogic.safeTarget("www.bing.com")), "bing -> strict");
    ok("safe.duckduckgo.com".equals(DnsLogic.safeTarget("duckduckgo.com")), "duckduckgo -> safe");
    ok("restrict.youtube.com".equals(DnsLogic.safeTarget("m.youtube.com")), "youtube -> restrict");
    ok(DnsLogic.safeTarget("example.com") == null, "other sites untouched");
    byte[] g = query("www.google.com", 0x4321); int go = DnsLogic.dnsPayloadOffset(g, g.length);
    byte[] wq = DnsLogic.withQuestion(g, go, g.length, "forcesafesearch.google.com");
    ok(wq != null && (wq[0] & 0xFF) == 0x43 && (wq[1] & 0xFF) == 0x21, "rewritten query keeps id");
    byte[] wp = new byte[28 + wq.length]; System.arraycopy(g, 0, wp, 0, 28); System.arraycopy(wq, 0, wp, 28, wq.length);
    ok("forcesafesearch.google.com".equals(DnsLogic.questionName(wp, 28, wp.length)), "rewritten query asks the strict name");
    ok(wq[wq.length - 3] == 1 && wq[wq.length - 1] == 1, "type A, class IN kept");
    // upstream answer: question forcesafesearch.google.com, one CNAME-free A record 216.239.38.120 and one TXT record
    java.io.ByteArrayOutputStream up = new java.io.ByteArrayOutputStream();
    up.write(wq, 0, 2); up.write(0x81); up.write(0x80); up.write(0); up.write(1); up.write(0); up.write(2); for (int i = 0; i < 4; i++) up.write(0);
    up.write(wq, 12, wq.length - 12);
    up.write(0xC0); up.write(0x0C); up.write(0); up.write(1); up.write(0); up.write(1); up.write(0); up.write(0); up.write(1); up.write(0x2C); up.write(0); up.write(4);
    up.write(216); up.write(239); up.write(38); up.write(120);
    up.write(0xC0); up.write(0x0C); up.write(0); up.write(16); up.write(0); up.write(1); for (int i = 0; i < 4; i++) up.write(0); up.write(0); up.write(2); up.write(1); up.write('x');
    byte[] ub = up.toByteArray();
    byte[] ans = DnsLogic.rewriteAnswer(g, go, g.length, ub, ub.length);
    ok(ans != null && (ans[0] & 0xFF) == 0x43 && (ans[1] & 0xFF) == 0x21, "answer keeps the original id");
    ok(ans != null && (ans[7] & 0xFF) == 1, "only the A record is kept");
    byte[] ap = new byte[28 + ans.length]; System.arraycopy(g, 0, ap, 0, 28); System.arraycopy(ans, 0, ap, 28, ans.length);
    ok("www.google.com".equals(DnsLogic.questionName(ap, 28, ap.length)), "answer is for the original name");
    ok((ans[ans.length - 4] & 0xFF) == 216 && (ans[ans.length - 1] & 0xFF) == 120, "address of the strict server");
    ok(DnsLogic.rewriteAnswer(g, go, g.length, new byte[]{1, 2, 3}, 3) == null, "short upstream answer rejected");
    int crash2 = 0; for (int i = 0; i < 20000; i++) { byte[] b = new byte[rnd.nextInt(120)]; rnd.nextBytes(b);
      try { DnsLogic.rewriteAnswer(g, go, g.length, b, b.length); } catch (Exception e) { crash2++; } }
    ok(crash2 == 0, "20,000 random upstream answers, no crash");
    System.out.println(fails == 0 ? "ALL TESTS PASSED" : fails + " FAILED"); System.exit(fails == 0 ? 0 : 1);
  }
}
