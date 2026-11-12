/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/** Pure Java helpers (no Android): read DNS questions from IPv4/UDP packets, decide, and build replies. */
public final class DnsLogic {
    private DnsLogic() {}

    /** Everyday sites a downloaded list may never block (protects against a broken or tampered list). */
    public static final Set<String> PROTECT = new HashSet<>(java.util.Arrays.asList(
        "google.com", "www.google.com", "youtube.com", "gmail.com", "microsoft.com", "live.com", "outlook.com", "office.com",
        "apple.com", "icloud.com", "github.com", "wikipedia.org", "amazon.com", "facebook.com", "instagram.com", "whatsapp.com",
        "whatsapp.net", "x.com", "twitter.com", "linkedin.com", "bing.com", "duckduckgo.com", "geopolcoins.xyz", "mozilla.org",
        "android.com", "googleapis.com", "gstatic.com", "play.google.com", "googleusercontent.com", "gov.uk", "europa.eu"));

    private static final java.util.regex.Pattern DOMAIN =
        java.util.regex.Pattern.compile("^(?=.{3,253}$)([a-z0-9-]{1,63}\\.)+[a-z]{2,24}$");

    public static boolean validDomain(String d) { return d != null && DOMAIN.matcher(d).matches(); }

    /** True if the host or one of its parent domains is in the set. */
    public static boolean blocked(String host, Set<String> list) {
        if (host == null || list == null) return false;
        String h = host.toLowerCase(Locale.ROOT);
        if (h.endsWith(".")) h = h.substring(0, h.length() - 1);
        while (true) {
            if (list.contains(h)) return true;
            int i = h.indexOf('.');
            if (i < 0 || h.indexOf('.', i + 1) < 0) return false;   // stop at the registrable part (a.b)
            h = h.substring(i + 1);
        }
    }

    /** Offset of the UDP payload if this is an IPv4/UDP packet to port 53, else -1. */
    public static int dnsPayloadOffset(byte[] p, int len) {
        if (len < 28 || (p[0] >> 4 & 0xF) != 4) return -1;
        int ihl = (p[0] & 0x0F) * 4;
        if (ihl < 20 || len < ihl + 8 + 12 || (p[9] & 0xFF) != 17) return -1;   // UDP only
        int dport = ((p[ihl + 2] & 0xFF) << 8) | (p[ihl + 3] & 0xFF);
        return dport == 53 ? ihl + 8 : -1;
    }

    /** First question name of a DNS message, or null when malformed. */
    public static String questionName(byte[] p, int off, int len) {
        if (len - off < 12) return null;
        int qd = ((p[off + 4] & 0xFF) << 8) | (p[off + 5] & 0xFF);
        if (qd < 1) return null;
        StringBuilder sb = new StringBuilder();
        int i = off + 12, guard = 0;
        while (i < len && guard++ < 128) {
            int l = p[i] & 0xFF;
            if (l == 0) return sb.length() == 0 ? null : sb.toString().toLowerCase(Locale.ROOT);
            if ((l & 0xC0) != 0 || l > 63 || i + 1 + l > len) return null;   // no compression in questions
            if (sb.length() > 0) sb.append('.');
            for (int k = 0; k < l; k++) {
                int c = p[i + 1 + k] & 0xFF;
                if (c < 0x21 || c > 0x7E) return null;
                sb.append((char) c);
            }
            if (sb.length() > 253) return null;
            i += 1 + l;
        }
        return null;
    }

    /** Copy of the DNS query turned into an NXDOMAIN answer (same id and question, no answers). */
    public static byte[] nxdomain(byte[] p, int off, int len) {
        byte[] d = java.util.Arrays.copyOfRange(p, off, len);
        d[2] = (byte) (0x80 | (p[off + 2] & 0x01));              // QR=1 (answer), keep RD
        d[3] = (byte) (0x80 | 0x03);                            // RA=1, RCODE=3 (name does not exist)
        d[6] = d[7] = d[8] = d[9] = d[10] = d[11] = 0;          // no answers / authority / additional
        return trimToQuestion(d);
    }

    private static byte[] trimToQuestion(byte[] d) {
        int i = 12;
        while (i < d.length && d[i] != 0) i += 1 + (d[i] & 0xFF);
        int end = Math.min(d.length, i + 1 + 4);               // name end + QTYPE + QCLASS
        return java.util.Arrays.copyOf(d, end);
    }

    /** Builds an IPv4/UDP packet that answers the original request packet with the given DNS payload. */
    public static byte[] udpReply(byte[] req, byte[] dns) {
        int ihl = (req[0] & 0x0F) * 4;
        int total = 20 + 8 + dns.length;
        byte[] o = new byte[total];
        o[0] = 0x45; o[1] = 0;
        o[2] = (byte) (total >> 8); o[3] = (byte) total;
        o[4] = req[4]; o[5] = req[5];                           // same id
        o[6] = 0x40; o[7] = 0;                                  // don't fragment
        o[8] = 64; o[9] = 17;                                   // TTL, UDP
        System.arraycopy(req, 16, o, 12, 4);                    // src = original dst (our DNS address)
        System.arraycopy(req, 12, o, 16, 4);                    // dst = original src (the app)
        int ck = checksum(o, 0, 20); o[10] = (byte) (ck >> 8); o[11] = (byte) ck;
        o[20] = req[ihl + 2]; o[21] = req[ihl + 3];             // src port 53
        o[22] = req[ihl]; o[23] = req[ihl + 1];                 // dst port = app port
        int ul = 8 + dns.length; o[24] = (byte) (ul >> 8); o[25] = (byte) ul;
        o[26] = 0; o[27] = 0;                                   // UDP checksum optional on IPv4
        System.arraycopy(dns, 0, o, 28, dns.length);
        return o;
    }

    static int checksum(byte[] b, int off, int len) {
        long s = 0;
        for (int i = off; i < off + len - 1; i += 2) s += ((b[i] & 0xFF) << 8) | (b[i + 1] & 0xFF);
        if ((len & 1) == 1) s += (b[off + len - 1] & 0xFF) << 8;
        while ((s >> 16) != 0) s = (s & 0xFFFF) + (s >> 16);
        return (int) (~s & 0xFFFF);
    }

    /** Parses a downloaded or bundled domain list: one domain per line, # comments, validated, protected sites removed. */
    public static Set<String> parseList(String text, int max) {
        Set<String> out = new HashSet<>();
        if (text == null) return out;
        for (String line : text.split("\n")) {
            String d = line.trim().toLowerCase(Locale.ROOT);
            if (d.isEmpty() || d.startsWith("#")) continue;
            if (validDomain(d) && !PROTECT.contains(d)) out.add(d);
            if (out.size() >= max) break;
        }
        return out;
    }

    // ---------- SafeSearch (family filter): answer search engines' names with the address of their strict version ----------
    private static final java.util.regex.Pattern GOOGLE = java.util.regex.Pattern.compile("^(www\\.)?google\\.(com|[a-z]{2}|co\\.[a-z]{2}|com\\.[a-z]{2})$");
    private static final Set<String> YOUTUBE = new HashSet<>(java.util.Arrays.asList("www.youtube.com", "m.youtube.com", "youtube.com",
        "youtubei.googleapis.com", "youtube.googleapis.com", "www.youtube-nocookie.com"));

    /** The official strict-mode name for a search engine host (Google, Bing, DuckDuckGo, YouTube), or null. */
    public static String safeTarget(String host) {
        if (host == null) return null;
        String h = host.toLowerCase(Locale.ROOT);
        if (h.endsWith(".")) h = h.substring(0, h.length() - 1);
        if (GOOGLE.matcher(h).matches()) return "forcesafesearch.google.com";
        if (h.equals("bing.com") || h.equals("www.bing.com")) return "strict.bing.com";
        if (h.equals("duckduckgo.com") || h.equals("www.duckduckgo.com") || h.equals("start.duckduckgo.com") || h.equals("html.duckduckgo.com")) return "safe.duckduckgo.com";
        if (YOUTUBE.contains(h)) return "restrict.youtube.com";
        return null;
    }

    /** The same DNS query (id, flags, type, class) but asking for another name. */
    public static byte[] withQuestion(byte[] p, int off, int len, String name) {
        int i = off + 12;
        while (i < len && p[i] != 0) i += 1 + (p[i] & 0xFF);
        if (i + 5 > len) return null;
        java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream();
        o.write(p, off, 4); o.write(0); o.write(1); for (int k = 0; k < 6; k++) o.write(0);   // id + flags, 1 question, no other records
        for (String l : name.split("\\.")) { byte[] b = l.getBytes(java.nio.charset.StandardCharsets.US_ASCII); o.write(b.length); o.write(b, 0, b.length); }
        o.write(0); o.write(p, i + 1, 4);                                                    // end of name, then QTYPE + QCLASS
        return o.toByteArray();
    }

    /** Builds the answer to the original query from the upstream answer for the strict name: the A/AAAA records are
     *  kept and given the original name, so the app connects to the strict server while asking for the normal one. */
    public static byte[] rewriteAnswer(byte[] q, int off, int len, byte[] r, int rlen) {
        if (rlen < 12 || len - off < 12) return null;
        int qend = off + 12;
        while (qend < len && q[qend] != 0) qend += 1 + (q[qend] & 0xFF);
        qend += 5;
        if (qend > len) return null;
        int qd = ((r[4] & 0xFF) << 8) | (r[5] & 0xFF), an = ((r[6] & 0xFF) << 8) | (r[7] & 0xFF);
        int i = 12;
        for (int k = 0; k < qd; k++) { i = skipName(r, i, rlen); if (i < 0 || i + 4 > rlen) return null; i += 4; }
        java.io.ByteArrayOutputStream rr = new java.io.ByteArrayOutputStream(); int count = 0;
        for (int k = 0; k < an && i < rlen; k++) {
            i = skipName(r, i, rlen); if (i < 0 || i + 10 > rlen) return null;
            int type = ((r[i] & 0xFF) << 8) | (r[i + 1] & 0xFF), dl = ((r[i + 8] & 0xFF) << 8) | (r[i + 9] & 0xFF);
            if (i + 10 + dl > rlen) return null;
            if (type == 1 || type == 28) { rr.write(0xC0); rr.write(0x0C); rr.write(r, i, 10 + dl); count++; }   // name = pointer to the question
            i += 10 + dl;
        }
        java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream();
        o.write(q, off, 2); o.write(0x80 | (q[off + 2] & 0x01)); o.write(0x80 | (r[3] & 0x0F));   // QR + RD, RA + upstream RCODE
        o.write(0); o.write(1); o.write(count >> 8); o.write(count); for (int k = 0; k < 4; k++) o.write(0);
        o.write(q, off + 12, qend - off - 12);
        byte[] a = rr.toByteArray(); o.write(a, 0, a.length);
        return o.toByteArray();
    }

    private static int skipName(byte[] b, int i, int len) {
        for (int guard = 0; guard < 128 && i < len; guard++) {
            int l = b[i] & 0xFF;
            if (l == 0) return i + 1;
            if ((l & 0xC0) == 0xC0) return i + 2 <= len ? i + 2 : -1;
            if (l > 63) return -1;
            i += 1 + l;
        }
        return -1;
    }
}
