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

    /** Bundled list plus the downloaded one (union): an online list can add blocks but never remove the built-in ones. */
    static Set<String> load(Context c) {
        Set<String> all = bundled(c);
        File f = new File(c.getFilesDir(), "domains.txt");
        try {
            if (f.exists()) {
                Set<String> s = DnsLogic.parseList(new String(java.nio.file.Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8), MAX);
                if (s.size() >= 20) all.addAll(s);
            }
        } catch (Exception ignored) { }
        return all;
    }

    private static Set<String> bundled(Context c) {
        try (InputStream in = c.getAssets().open("domains.txt")) {
            return new java.util.HashSet<>(DnsLogic.parseList(read(in, 1 << 20), MAX));
        } catch (Exception e) {
            return new java.util.HashSet<>();
        }
    }

    /** Family filter: the adult-content list bundled with the app (about 64,000 domains, read once, only when switched on). */
    private static volatile Set<String> adult;
    static Set<String> adult(Context c) {
        Set<String> a = adult;
        if (a != null) return a;
        synchronized (Lists.class) {
            if (adult == null) {
                try (InputStream in = c.getAssets().open("adult.txt")) { adult = DnsLogic.parseList(read(in, 4 << 20), 200000); }
                catch (Exception e) { adult = new java.util.HashSet<>(); }
            }
            return adult;
        }
    }
    static boolean adultOn(Context c) { return Stats.prefs(c).getBoolean("adult", false); }
    static boolean safeOn(Context c) { return Stats.prefs(c).getBoolean("safe", false); }

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
            Set<String> all = bundled(c); all.addAll(s);
            return all;
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
