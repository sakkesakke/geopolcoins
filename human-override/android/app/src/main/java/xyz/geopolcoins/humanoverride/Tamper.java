/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
package xyz.geopolcoins.humanoverride;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

/** Tamper alerts: keeps a short log on the phone (kind + time) and shows a notification when protection is
 *  switched off outside the app (Android VPN settings, another VPN app) or was found not running. Nothing is sent. */
final class Tamper {
    private Tamper() { }
    private static final String CH = "tamper";

    static synchronized void record(Context c, String kind) {
        SharedPreferences p = Stats.prefs(c);
        p.edit().putString("tlog", TamperLog.add(p.getString("tlog", ""), kind, System.currentTimeMillis())).apply();
    }

    static String text(Context c) {
        StringBuilder b = new StringBuilder();
        java.text.DateFormat f = java.text.DateFormat.getDateTimeInstance(java.text.DateFormat.SHORT, java.text.DateFormat.SHORT);
        int n = 0;
        for (String[] e : TamperLog.entries(Stats.prefs(c).getString("tlog", ""))) {
            if (n++ == 8) break;
            int id = label(e[0]);
            b.append(b.length() > 0 ? "\n" : "").append(f.format(new java.util.Date(Long.parseLong(e[1])))).append("  ").append(id != 0 ? c.getString(id) : e[0]);
        }
        return b.length() > 0 ? b.toString() : c.getString(R.string.tamper_none);
    }

    private static int label(String k) {
        switch (k) {
            case "revoked": return R.string.tamper_revoked;
            case "stopped": return R.string.tamper_stopped;
            case "off": return R.string.tamper_off;
            case "pinbad": return R.string.tamper_pinbad;
            case "pinlock": return R.string.tamper_pinlock;
            case "pinoff": return R.string.tamper_pinoff;
            default: return 0;
        }
    }

    /** Remember whether the user wants protection on, so the app can notice when it was stopped behind its back. */
    static void want(Context c, boolean on) { Stats.prefs(c).edit().putBoolean("want_on", on).apply(); }
    static boolean wanted(Context c) { return Stats.prefs(c).getBoolean("want_on", false); }

    static void alert(Context ctx, String kind, String text) {
        Context c = ctx.getApplicationContext();
        record(c, kind);
        try {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            if (nm == null) return;
            nm.createNotificationChannel(new NotificationChannel(CH, c.getString(R.string.tamper_title), NotificationManager.IMPORTANCE_HIGH));
            PendingIntent pi = PendingIntent.getActivity(c, 1, new Intent(c, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
            nm.notify(201, new Notification.Builder(c, CH).setSmallIcon(R.mipmap.ic_launcher).setContentTitle(c.getString(R.string.tamper_title))
                .setContentText(text).setStyle(new Notification.BigTextStyle().bigText(text)).setContentIntent(pi).setAutoCancel(true).build());
        } catch (Exception ignored) { }   // no notification permission: the log still shows it
    }
}
