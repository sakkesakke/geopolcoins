/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import android.content.Context;
import android.content.SharedPreferences;

/** Counts blocked AI lookups on this phone only. */
final class Stats {
    private Stats() {}
    static SharedPreferences prefs(Context c) { return c.getSharedPreferences("ho", Context.MODE_PRIVATE); }
    static String today() { return new java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.ROOT).format(new java.util.Date()); }
    static synchronized void inc(Context c) {
        SharedPreferences p = prefs(c);
        String d = today();
        int t = d.equals(p.getString("day", "")) ? p.getInt("today", 0) : 0;
        p.edit().putString("day", d).putInt("today", t + 1).putLong("total", p.getLong("total", 0) + 1).apply();
    }
    static int today(Context c) { SharedPreferences p = prefs(c); return today().equals(p.getString("day", "")) ? p.getInt("today", 0) : 0; }
    static long total(Context c) { return prefs(c).getLong("total", 0); }
}
