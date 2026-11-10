/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
package xyz.geopolcoins.humanoverride;

import java.util.ArrayList;
import java.util.List;

/** Tamper log as one short text: "kind:time;kind:time". Only the kind of event and the time, never anything else. */
public final class TamperLog {
    private TamperLog() { }
    public static final int MAX = 20;
    private static final java.util.regex.Pattern KIND = java.util.regex.Pattern.compile("[a-z]{2,12}");

    public static String add(String log, String kind, long at) {
        if (kind == null || !KIND.matcher(kind).matches()) return log == null ? "" : log;
        List<String> keep = new ArrayList<>();
        for (String[] e : entries(log)) keep.add(0, e[0] + ":" + e[1]);
        keep.add(kind + ":" + at);
        while (keep.size() > MAX) keep.remove(0);
        return String.join(";", keep);
    }

    /** Newest first; each entry is {kind, time in ms}. Broken parts are skipped. */
    public static List<String[]> entries(String log) {
        List<String[]> out = new ArrayList<>();
        if (log == null) return out;
        for (String part : log.split(";")) {
            String[] kv = part.split(":");
            if (kv.length != 2 || !KIND.matcher(kv[0]).matches() || !kv[1].matches("[0-9]{1,15}")) continue;
            out.add(0, kv);
        }
        return out.size() > MAX ? new ArrayList<>(out.subList(0, MAX)) : out;
    }
}
