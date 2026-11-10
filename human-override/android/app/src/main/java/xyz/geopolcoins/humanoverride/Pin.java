/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import android.content.Context;
import android.content.SharedPreferences;
import java.security.SecureRandom;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/** PIN lock: stored only as a salted PBKDF2 hash; 5 wrong tries lock it for 1 minute, doubling up to 1 hour. */
final class Pin {
    private Pin() {}
    private static final int ITER = 120000;
    static boolean isSet(Context c) { return Stats.prefs(c).contains("pin_hash"); }

    static String hash(String pin, byte[] salt) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(pin.toCharArray(), salt, ITER, 256);
        byte[] h = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
        StringBuilder sb = new StringBuilder();
        for (byte b : h) sb.append(String.format(java.util.Locale.ROOT, "%02x", b));
        return sb.toString();
    }

    static boolean set(Context c, String pin) {
        if (pin == null || !pin.matches("[0-9]{4,12}")) return false;
        try {
            byte[] salt = new byte[16]; new SecureRandom().nextBytes(salt);
            Stats.prefs(c).edit().putString("pin_salt", android.util.Base64.encodeToString(salt, android.util.Base64.NO_WRAP))
                .putString("pin_hash", hash(pin, salt)).putInt("pin_fails", 0).putLong("pin_until", 0).apply();
            return true;
        } catch (Exception e) { return false; }
    }

    static void clear(Context c) { Stats.prefs(c).edit().remove("pin_salt").remove("pin_hash").putInt("pin_fails", 0).putLong("pin_until", 0).apply(); }

    /** 1 = ok, 0 = wrong, -1 = locked for now. */
    static int check(Context c, String pin) {
        SharedPreferences p = Stats.prefs(c);
        if (!isSet(c)) return 1;
        if (System.currentTimeMillis() < p.getLong("pin_until", 0)) return -1;
        boolean ok = false;
        try {
            byte[] salt = android.util.Base64.decode(p.getString("pin_salt", ""), android.util.Base64.NO_WRAP);
            ok = pin != null && pin.matches("[0-9]{4,12}") && java.security.MessageDigest.isEqual(
                hash(pin, salt).getBytes(), p.getString("pin_hash", "").getBytes());
        } catch (Exception ignored) { }
        if (ok) { p.edit().putInt("pin_fails", 0).putLong("pin_until", 0).apply(); return 1; }
        int f = p.getInt("pin_fails", 0) + 1;
        long until = f >= 5 ? System.currentTimeMillis() + Math.min(3600000L, 60000L << Math.min(6, f - 5)) : 0;
        p.edit().putInt("pin_fails", f).putLong("pin_until", until).apply();
        return 0;
    }
}
