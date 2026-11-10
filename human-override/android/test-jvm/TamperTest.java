/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. JVM unit test for the tamper log (run in CI). */
import xyz.geopolcoins.humanoverride.TamperLog;
import java.util.*;
public class TamperTest {
  static int fails = 0;
  static void ok(boolean c, String m) { System.out.println((c ? "PASS " : "FAIL ") + m); if (!c) fails++; }
  public static void main(String[] a) {
    String log = TamperLog.add("", "revoked", 1000L);
    ok(log.equals("revoked:1000"), "first entry");
    log = TamperLog.add(log, "pinbad", 2000L);
    List<String[]> e = TamperLog.entries(log);
    ok(e.size() == 2 && e.get(0)[0].equals("pinbad") && e.get(0)[1].equals("2000"), "newest first");
    String big = ""; for (int i = 0; i < 40; i++) big = TamperLog.add(big, "pinbad", i);
    ok(TamperLog.entries(big).size() == TamperLog.MAX, "keeps only the last " + TamperLog.MAX);
    ok(TamperLog.entries(big).get(0)[1].equals("39"), "drops the oldest");
    ok(TamperLog.add("x", "bad kind!", 5L).equals("x"), "unknown kind ignored");
    ok(TamperLog.entries("garbage;;pinbad:abc;off:7").size() == 1, "broken entries skipped");
    ok(TamperLog.entries(null).isEmpty(), "null is empty");
    System.out.println(fails == 0 ? "ALL PASS" : fails + " FAILED"); if (fails > 0) System.exit(1);
  }
}
