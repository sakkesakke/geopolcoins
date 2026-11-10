/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Set;

/** Block list: bundled copy, plus a daily update of the public list from geopolcoins.xyz (nothing about the user is sent). */
final class Lists {
    private Lists() {}
    static final String URL_LIST = "https://geopolcoins.xyz/human-override/domains.txt";
    static final int MAX = 5000;

    static Set<String> load(Context c) {
        File f = new File(c.getFilesDir(), "domains.txt");
        try {
            if (f.exists()) {
                Set<String> s = DnsLogic.parseList(new String(java.nio.file.Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8), MAX);
                if (s.size() >= 20) return s;
            }
        } catch (Exception ignored) { }
        try (InputStream in = c.getAssets().open("domains.txt")) {
            return DnsLogic.parseList(read(in, 1 << 20), MAX);
        } catch (Exception e) {
            return new java.util.HashSet<>();
        }
    }

    /** Downloads the newest list at most every 12 hours. Returns the new list or null. */
    static Set<String> update(Context c) {
        File f = new File(c.getFilesDir(), "domains.txt");
        if (f.exists() && System.currentTimeMillis() - f.lastModified() < 12L * 3600 * 1000) return null;
        HttpURLConnection h = null;
        try {
            h = (HttpURLConnection) new URL(URL_LIST).openConnection();
            h.setConnectTimeout(15000); h.setReadTimeout(15000); h.setUseCaches(false);
            h.setRequestProperty("User-Agent", "HumanOverride-Android");
            if (h.getResponseCode() != 200) return null;
            String txt;
            try (InputStream in = h.getInputStream()) { txt = read(in, 512 * 1024); }
            Set<String> s = DnsLogic.parseList(txt, MAX);
            if (s.size() < 20) return null;                    // looks wrong: keep the old list
            File tmp = new File(c.getFilesDir(), "domains.tmp");
            try (FileOutputStream o = new FileOutputStream(tmp)) { o.write(txt.getBytes(StandardCharsets.UTF_8)); }
            if (!tmp.renameTo(f)) return null;
            return s;
        } catch (Exception e) {
            return null;
        } finally {
            if (h != null) h.disconnect();
        }
    }

    private static String read(InputStream in, int max) throws java.io.IOException {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        byte[] buf = new byte[8192]; int n;
        while ((n = in.read(buf)) > 0) { b.write(buf, 0, n); if (b.size() > max) throw new java.io.IOException("too big"); }
        return b.toString("UTF-8");
    }
}
