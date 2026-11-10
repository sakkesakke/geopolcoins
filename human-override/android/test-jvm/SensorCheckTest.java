/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. JVM unit test for SensorCheck (run in CI). */
import xyz.geopolcoins.humanoverride.SensorCheck;
import java.util.*;
public class SensorCheckTest {
  static int fails = 0;
  static void ok(boolean c, String m) { System.out.println((c ? "PASS " : "FAIL ") + m); if (!c) fails++; }
  public static void main(String[] a) {
    List<String> ssid = Arrays.asList("HomeWifi", "", "ESP_A1B2C3", "Neighbour", "ESP_A1B2C3", "esp32-cam", "Plug");
    List<String> mac = Arrays.asList("a4:91:b1:00:00:01", "24:0a:c4:11:22:33", "02:11:22:33:44:55", "3c:71:bf:aa:bb:cc", "24-0A-C4-11-22-33", "12:34:56:78:9a:bc", "DE:AD:BE:EF:00:01");
    List<Integer> lvl = Arrays.asList(-40, -60, -50, -80, -60, -45, -90);
    List<SensorCheck.Finding> f = SensorCheck.check(ssid, mac, lvl);
    Set<String> macs = new HashSet<>(); for (SensorCheck.Finding x : f) macs.add(x.mac);
    ok(macs.contains("24:0A:C4:11:22:33"), "Espressif MAC found (hidden name)");
    ok(macs.contains("3C:71:BF:AA:BB:CC"), "Espressif MAC found (normal name)");
    ok(macs.contains("02:11:22:33:44:55") && macs.contains("12:34:56:78:9A:BC"), "ESP-style names found even with random MAC");
    ok(!macs.contains("A4:91:B1:00:00:01") && !macs.contains("DE:AD:BE:EF:00:01"), "normal router and unknown maker not flagged");
    ok(f.size() == 4, "one entry per MAC (got " + f.size() + ")");
    ok(f.get(0).level >= f.get(f.size() - 1).level, "strongest first");
    ok(SensorCheck.distance(-40) == 2 && SensorCheck.distance(-65) == 1 && SensorCheck.distance(-85) == 0, "distance buckets");
    ok(SensorCheck.check(new ArrayList<>(), new ArrayList<>(), new ArrayList<>()).isEmpty(), "empty scan");
    ok(SensorCheck.check(Arrays.asList((String) null), Arrays.asList("garbage"), Arrays.asList(-50)).isEmpty(), "bad input ignored");
    System.out.println(fails == 0 ? "ALL PASS" : fails + " FAILED"); if (fails > 0) System.exit(1);
  }
}
