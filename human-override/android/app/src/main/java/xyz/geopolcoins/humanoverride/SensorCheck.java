/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
package xyz.geopolcoins.humanoverride;

import java.util.*;

/** Pure logic (no Android) so it can be unit-tested: which nearby Wi-Fi radios look like small DIY sensor boards.
 *  Many Wi-Fi sensing / camera / tracker gadgets run on cheap Espressif (ESP8266/ESP32) chips. So do many normal smart
 *  plugs and lamps, so a finding is a hint ("do you know this device?"), never proof. Nothing leaves the phone. */
public final class SensorCheck {
    private SensorCheck() { }

    /** Espressif MAC prefixes (IEEE OUI registrations). */
    static final Set<String> ESPRESSIF = new HashSet<>(Arrays.asList(
        "08:3A:F2", "0C:DC:7E", "10:52:1C", "24:0A:C4", "24:62:AB", "24:6F:28", "24:DC:C3", "30:83:98", "30:AE:A4", "34:85:18",
        "34:94:54", "3C:61:05", "3C:71:BF", "3C:E9:0E", "40:F5:20", "48:27:E2", "48:3F:DA", "4C:11:AE", "54:5A:A6", "58:BF:25",
        "5C:CF:7F", "60:01:94", "64:E8:33", "68:C6:3A", "70:04:1D", "74:4D:BD", "78:21:84", "7C:9E:BD", "7C:DF:A1", "80:7D:3A",
        "84:0D:8E", "84:CC:A8", "84:F3:EB", "84:F7:03", "8C:AA:B5", "90:97:D5", "94:3C:C6", "94:B9:7E", "98:CD:AC", "A0:20:A6",
        "A4:7B:9D", "A4:CF:12", "A8:42:E3", "AC:67:B2", "B4:E6:2D", "BC:DD:C2", "C0:49:EF", "C4:4F:33", "C8:2B:96", "CC:50:E3",
        "D8:A0:1D", "DC:4F:22", "DC:54:75", "E0:5A:1B", "E8:68:E7", "E8:9F:6D", "E8:DB:84", "EC:62:60", "EC:FA:BC", "F0:08:D1",
        "F4:CF:A2"));

    public static final class Finding {
        public final String name, mac; public final int level; public final boolean byName;
        Finding(String name, String mac, int level, boolean byName) { this.name = name; this.mac = mac; this.level = level; this.byName = byName; }
    }

    static String norm(String mac) { return mac == null ? "" : mac.trim().toUpperCase(Locale.ROOT).replace('-', ':'); }

    /** A "locally administered" (random) address cannot be traced to a maker. */
    static boolean randomMac(String mac) {
        String m = norm(mac); if (m.length() < 2) return true;
        try { return (Integer.parseInt(m.substring(0, 2), 16) & 0x02) != 0; } catch (NumberFormatException e) { return true; }
    }

    static boolean espName(String ssid) {
        String s = ssid == null ? "" : ssid.toLowerCase(Locale.ROOT);
        return s.startsWith("esp_") || s.startsWith("esp-") || s.startsWith("esp32") || s.startsWith("esp8266") || s.startsWith("espressif");
    }

    /** ssids, macs, levels (dBm) are parallel lists from a Wi-Fi scan. Strongest first, one entry per MAC. */
    public static List<Finding> check(List<String> ssids, List<String> macs, List<Integer> levels) {
        Map<String, Finding> out = new LinkedHashMap<>();
        for (int i = 0; i < macs.size(); i++) {
            String mac = norm(macs.get(i)), ssid = i < ssids.size() && ssids.get(i) != null ? ssids.get(i) : "";
            int lvl = i < levels.size() ? levels.get(i) : -100;
            boolean vendor = mac.length() >= 8 && !randomMac(mac) && ESPRESSIF.contains(mac.substring(0, 8));
            boolean name = espName(ssid);
            if ((vendor || name) && !out.containsKey(mac)) out.put(mac, new Finding(ssid.isEmpty() ? "(hidden)" : ssid, mac, lvl, name && !vendor));
        }
        List<Finding> l = new ArrayList<>(out.values());
        l.sort((a, b) -> Integer.compare(b.level, a.level));
        return l;
    }

    /** 0 = far, 1 = nearby, 2 = very close (probably in the same home). */
    public static int distance(int dbm) { return dbm >= -55 ? 2 : dbm >= -72 ? 1 : 0; }
}
