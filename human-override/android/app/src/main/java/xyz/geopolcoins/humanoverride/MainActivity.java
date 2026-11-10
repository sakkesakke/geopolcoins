/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.net.VpnService;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final int BG = 0xFF0D0B16, CARD = 0xFF17142A, TXT = 0xFFF3ECD9, DIM = 0xFFA79FBF, RED = 0xFFFF4F4F, AMBER = 0xFFFFB547, PINK = 0xFFFF5E7A;
    private Button big, pinBtn;
    private TextView status, msg, pinNote;
    private EditText pin;
    private final Handler h = new Handler(Looper.getMainLooper());
    private final Runnable tick = new Runnable() { public void run() { refresh(); h.postDelayed(this, 1500); } };

    @Override
    protected void onCreate(Bundle s) {
        super.onCreate(s);
        getWindow().setStatusBarColor(BG);
        ScrollView sv = new ScrollView(this); sv.setBackgroundColor(BG);
        LinearLayout col = new LinearLayout(this); col.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(20); col.setPadding(pad, dp(28), pad, dp(28)); sv.addView(col);

        LinearLayout head = new LinearLayout(this); head.setGravity(Gravity.CENTER_VERTICAL);
        ImageView ic = new ImageView(this); ic.setImageResource(R.mipmap.ic_launcher); head.addView(ic, new LinearLayout.LayoutParams(dp(44), dp(44)));
        LinearLayout ht = new LinearLayout(this); ht.setOrientation(LinearLayout.VERTICAL); ht.setPadding(dp(12), 0, 0, 0);
        ht.addView(text(getString(R.string.app_title), 20, TXT, true)); ht.addView(text(getString(R.string.subtitle), 13, DIM, false));
        head.addView(ht); col.addView(head);

        big = new Button(this); big.setAllCaps(false); big.setTextSize(22); big.setTypeface(Typeface.DEFAULT_BOLD); big.setPadding(0, dp(22), 0, dp(22));
        big.setOnClickListener(v -> toggle());
        col.addView(big, lp(dp(22)));
        status = text("", 14, DIM, false); status.setGravity(Gravity.CENTER); col.addView(status, lp(dp(10)));
        msg = text("", 14, RED, false); msg.setGravity(Gravity.CENTER); col.addView(msg, lp(dp(6)));

        LinearLayout pc = card(col, getString(R.string.pin_title));
        pin = new EditText(this); pin.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        pin.setTextColor(TXT); pin.setHintTextColor(DIM); pin.setHint(getString(R.string.pin_hint)); pin.setTextSize(18);
        pc.addView(pin, lp(0));
        pinBtn = button("", AMBER, Color.BLACK); pinBtn.setOnClickListener(v -> pinAction()); pc.addView(pinBtn, lp(dp(8)));
        pinNote = text("", 12, DIM, false); pc.addView(pinNote, lp(dp(6)));

        LinearLayout ac = card(col, getString(R.string.always_title));
        ac.addView(text(getString(R.string.always_text), 14, DIM, false));
        Button vs = button(getString(R.string.open_vpn_settings), CARD, TXT);
        vs.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_VPN_SETTINGS))); ac.addView(vs, lp(dp(10)));

        LinearLayout sc = card(col, getString(R.string.sensor_title));
        sc.addView(text(getString(R.string.sensor_text), 14, DIM, false));
        Button sb = button(getString(R.string.sensor_btn), CARD, TXT); sb.setOnClickListener(v -> sensorCheck()); sc.addView(sb, lp(dp(10)));

        LinearLayout hc = card(col, getString(R.string.honest_title));
        hc.addView(text(getString(R.string.honest_text), 13, DIM, false));

        Button don = button(getString(R.string.donate), PINK, Color.BLACK);
        don.setOnClickListener(v -> open("https://ko-fi.com/geopolcoins")); col.addView(don, lp(dp(18)));
        TextView tl = text(getString(R.string.terms_link), 13, AMBER, false); tl.setGravity(Gravity.CENTER);
        tl.setOnClickListener(v -> open(TERMS_URL)); col.addView(tl, lp(dp(14)));
        TextView site = text(getString(R.string.footer), 12, DIM, false); site.setGravity(Gravity.CENTER);
        site.setOnClickListener(v -> open("https://geopolcoins.xyz/human-override.html")); col.addView(site, lp(dp(14)));
        setContentView(sv);
    }

    static final int TERMS_VERSION = 1;
    static final String TERMS_URL = "https://geopolcoins.xyz/human-override-terms.html";

    private boolean termsOk() { return Stats.prefs(this).getInt("terms_v", 0) >= TERMS_VERSION; }

    private void askTerms(Runnable then) {
        new AlertDialog.Builder(this)
            .setTitle(R.string.terms_title)
            .setMessage(R.string.terms_text)
            .setCancelable(false)
            .setPositiveButton(R.string.terms_agree, (d, w) -> { Stats.prefs(this).edit().putInt("terms_v", TERMS_VERSION).apply(); if (then != null) then.run(); })
            .setNeutralButton(R.string.terms_read, (d, w) -> { open(TERMS_URL); askTerms(then); })
            .setNegativeButton(R.string.terms_decline, (d, w) -> finish())
            .show();
    }

    @Override protected void onResume() { super.onResume(); h.post(tick); if (!termsOk()) askTerms(null); }
    @Override protected void onPause() { super.onPause(); h.removeCallbacks(tick); }

    private void refresh() {
        boolean on = BlockVpnService.running;
        big.setText(on ? getString(R.string.on) : getString(R.string.off));
        big.setTextColor(on ? Color.BLACK : Color.WHITE);
        big.setBackground(round(on ? RED : 0xFF5D5875, 18));
        big.setContentDescription(on ? getString(R.string.tap_off) : getString(R.string.tap_on));
        status.setText(getString(R.string.stats, Stats.today(this), Stats.total(this)));
        String pdm = null;
        try { pdm = Settings.Global.getString(getContentResolver(), "private_dns_mode"); } catch (Exception ignored) { }
        if (on && "hostname".equals(pdm)) { msg.setTextColor(AMBER); msg.setText(R.string.private_dns_warn); }
        boolean ps = Pin.isSet(this);
        pinBtn.setText(ps ? getString(R.string.pin_remove) : getString(R.string.pin_set));
        pinNote.setText(ps ? getString(R.string.pin_on) : getString(R.string.pin_off));
    }

    private void toggle() {
        msg.setTextColor(RED); msg.setText("");
        if (!termsOk()) { askTerms(this::toggle); return; }
        if (!BlockVpnService.running) {
            Intent prep = VpnService.prepare(this);
            if (prep != null) startActivityForResult(prep, 1); else onActivityResult(1, RESULT_OK, null);
            return;
        }
        final String p = pin.getText().toString().trim();
        if (Pin.isSet(this) && p.isEmpty()) { msg.setText(R.string.ask_pin); return; }
        new Thread(() -> {
            int r = Pin.check(this, p);
            runOnUiThread(() -> {
                if (r == 1) { startService(new Intent(this, BlockVpnService.class).setAction(BlockVpnService.ACTION_STOP)); pin.setText(""); }
                else msg.setText(r < 0 ? R.string.locked : R.string.bad_pin);
            });
        }).start();
    }

    private void pinAction() {
        msg.setText("");
        final String p = pin.getText().toString().trim();
        new Thread(() -> {
            boolean isSet = Pin.isSet(this);
            int r = isSet ? Pin.check(this, p) : (Pin.set(this, p) ? 1 : 2);
            if (isSet && r == 1) Pin.clear(this);
            runOnUiThread(() -> {
                if (r == 1) { pin.setText(""); msg.setText(""); refresh(); }
                else msg.setText(r == 2 ? R.string.pin_format : r < 0 ? R.string.locked : (p.isEmpty() ? R.string.ask_pin : R.string.bad_pin));
            });
        }).start();
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == 1 && res == RESULT_OK) startService(new Intent(this, BlockVpnService.class));
    }

    // ---------- Sensor check: nearby Wi-Fi radios that look like small DIY sensor boards (everything stays on the phone) ----------
    private static final int REQ_WIFI = 7;
    private boolean scanDone;
    private void sensorCheck() {
        String perm = Build.VERSION.SDK_INT >= 33 ? "android.permission.NEARBY_WIFI_DEVICES" : "android.permission.ACCESS_FINE_LOCATION";
        if (checkSelfPermission(perm) != PackageManager.PERMISSION_GRANTED) { requestPermissions(new String[]{perm}, REQ_WIFI); return; }
        final WifiManager wm = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        if (wm == null || !wm.isWifiEnabled()) { showSensor(getString(R.string.sensor_wifi_off)); return; }
        msg.setTextColor(DIM); msg.setText(R.string.sensor_scanning); scanDone = false;
        final BroadcastReceiver rc = new BroadcastReceiver() { @Override public void onReceive(Context c, Intent i) { finishScan(wm, this); } };
        IntentFilter f = new IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
        if (Build.VERSION.SDK_INT >= 33) registerReceiver(rc, f, Context.RECEIVER_NOT_EXPORTED); else registerReceiver(rc, f);
        try { wm.startScan(); } catch (Exception ignored) { }   // may be throttled by Android: then the last results are used
        h.postDelayed(() -> finishScan(wm, rc), 6000);
    }
    private void finishScan(WifiManager wm, BroadcastReceiver rc) {
        if (scanDone) return; scanDone = true;
        try { unregisterReceiver(rc); } catch (Exception ignored) { }
        msg.setText(""); msg.setTextColor(RED);
        java.util.List<String> ss = new java.util.ArrayList<>(), ms = new java.util.ArrayList<>(); java.util.List<Integer> ls = new java.util.ArrayList<>();
        try { for (ScanResult r : wm.getScanResults()) { ss.add(r.SSID); ms.add(r.BSSID); ls.add(r.level); } }
        catch (SecurityException e) { showSensor(getString(R.string.sensor_perm)); return; }
        if (ms.isEmpty()) { showSensor(getString(R.string.sensor_empty)); return; }
        java.util.List<SensorCheck.Finding> found = SensorCheck.check(ss, ms, ls);
        StringBuilder b = new StringBuilder(found.isEmpty() ? getString(R.string.sensor_clean, ms.size()) : getString(R.string.sensor_found, found.size(), ms.size()));
        String[] dist = { getString(R.string.sensor_far), getString(R.string.sensor_near), getString(R.string.sensor_close) };
        for (SensorCheck.Finding x : found) b.append("\n\n• ").append(x.name).append("  (").append(dist[SensorCheck.distance(x.level)]).append(")\n   ").append(x.mac);
        if (!found.isEmpty()) b.append("\n\n").append(getString(R.string.sensor_advice));
        showSensor(b.toString());
    }
    private void showSensor(String t) { new AlertDialog.Builder(this).setTitle(R.string.sensor_title).setMessage(t).setPositiveButton(android.R.string.ok, null).show(); }
    @Override public void onRequestPermissionsResult(int code, String[] p, int[] g) {
        super.onRequestPermissionsResult(code, p, g);
        if (code != REQ_WIFI) return;
        if (g.length > 0 && g[0] == PackageManager.PERMISSION_GRANTED) sensorCheck(); else showSensor(getString(R.string.sensor_perm));
    }

    private void open(String url) { try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception ignored) { } }
    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
    private LinearLayout.LayoutParams lp(int top) { LinearLayout.LayoutParams l = new LinearLayout.LayoutParams(-1, -2); l.topMargin = top; return l; }
    private TextView text(String t, int sp, int color, boolean bold) { TextView v = new TextView(this); v.setText(t); v.setTextSize(sp); v.setTextColor(color); if (bold) v.setTypeface(Typeface.DEFAULT_BOLD); return v; }
    private GradientDrawable round(int color, int r) { GradientDrawable g = new GradientDrawable(); g.setColor(color); g.setCornerRadius(dp(r)); g.setStroke(dp(3), Color.BLACK); return g; }
    private Button button(String t, int bg, int fg) { Button b = new Button(this); b.setText(t); b.setAllCaps(false); b.setTextColor(fg); b.setTypeface(Typeface.DEFAULT_BOLD); b.setBackground(round(bg, 12)); b.setMinHeight(dp(48)); return b; }
    private LinearLayout card(LinearLayout parent, String title) {
        LinearLayout c = new LinearLayout(this); c.setOrientation(LinearLayout.VERTICAL); c.setPadding(dp(14), dp(12), dp(14), dp(14));
        GradientDrawable g = new GradientDrawable(); g.setColor(CARD); g.setCornerRadius(dp(14)); c.setBackground(g);
        c.addView(text(title.toUpperCase(java.util.Locale.ROOT), 13, AMBER, true));
        parent.addView(c, lp(dp(16)));
        return c;
    }
}
