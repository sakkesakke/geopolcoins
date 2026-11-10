/* Human Override for Android - Copyright (c) 2026 Amghar Said. All rights reserved. */
package xyz.geopolcoins.humanoverride;

import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.LinkProperties;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Local DNS filter. Only DNS questions are routed into this app (route to 10.111.222.1/32); all other traffic goes
 * straight to the internet. AI domains get "does not exist"; everything else is forwarded to the phone's normal DNS.
 * Nothing leaves the phone except the normal DNS question itself.
 */
public class BlockVpnService extends VpnService implements Runnable {
    static final String ACTION_STOP = "xyz.geopolcoins.humanoverride.STOP";
    static final String DNS_IP = "10.111.222.1";
    static volatile boolean running = false;

    private ParcelFileDescriptor tun;
    private Thread thread;
    private ExecutorService pool;
    private ScheduledExecutorService timer;
    private volatile Set<String> list;
    private FileOutputStream out;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) { Tamper.want(this, false); stopVpn(); return START_NOT_STICKY; }
        startVpn();
        return START_STICKY;
    }

    private synchronized void startVpn() {
        if (running) return;
        list = Lists.load(this);
        Builder b = new Builder()
            .setSession(getString(R.string.app_name))
            .addAddress("10.111.222.2", 32)
            .addDnsServer(DNS_IP)
            .addRoute(DNS_IP, 32)
            .setBlocking(true);
        try { b.addDisallowedApplication(getPackageName()); } catch (Exception ignored) { }
        if (android.os.Build.VERSION.SDK_INT >= 29) b.setMetered(false);
        try { tun = b.establish(); } catch (Exception e) { tun = null; }
        if (tun == null) { stopSelf(); return; }
        out = new FileOutputStream(tun.getFileDescriptor());
        running = true;
        Tamper.want(this, true);
        pool = Executors.newFixedThreadPool(4);
        thread = new Thread(this, "ho-dns");
        thread.start();
        timer = Executors.newSingleThreadScheduledExecutor();
        PrivacyGuard.start(this);
        timer.scheduleWithFixedDelay(() -> { Set<String> n = Lists.update(this); if (n != null) list = n; }, 5, 3 * 3600, TimeUnit.SECONDS);
    }

    synchronized void stopVpn() {
        running = false;
        PrivacyGuard.stop(this);
        if (timer != null) timer.shutdownNow();
        if (pool != null) pool.shutdownNow();
        try { if (tun != null) tun.close(); } catch (IOException ignored) { }
        tun = null;
        stopSelf();
    }

    // Android calls onRevoke when the VPN is switched off outside this app (VPN settings or another VPN app): a tamper alert.
    @Override public void onRevoke() { stopVpn(); Tamper.alert(this, "revoked", getString(R.string.tamper_revoked_text)); super.onRevoke(); }
    @Override public void onDestroy() { running = false; PrivacyGuard.stop(this); try { if (tun != null) tun.close(); } catch (IOException ignored) { } super.onDestroy(); }

    @Override
    public void run() {
        byte[] buf = new byte[32767];
        try (FileInputStream in = new FileInputStream(tun.getFileDescriptor())) {
            while (running) {
                int n = in.read(buf);
                if (n <= 0) continue;
                int off = DnsLogic.dnsPayloadOffset(buf, n);
                if (off < 0) continue;
                final byte[] pkt = Arrays.copyOf(buf, n);
                final int o = off;
                String name = DnsLogic.questionName(pkt, off, n);
                if (name != null && DnsLogic.blocked(name, list)) {
                    write(DnsLogic.udpReply(pkt, DnsLogic.nxdomain(pkt, off, n)));
                    Stats.inc(this);
                } else if (pool != null && !pool.isShutdown()) {
                    try { pool.execute(() -> forward(pkt, o)); } catch (Exception ignored) { }
                }
            }
        } catch (Exception ignored) {
            // tunnel closed
        }
    }

    private void forward(byte[] pkt, int off) {
        byte[] q = Arrays.copyOfRange(pkt, off, pkt.length);
        for (InetAddress up : upstreams()) {
            try (DatagramSocket s = new DatagramSocket()) {
                protect(s);                                    // goes around this VPN, straight to the network
                s.setSoTimeout(4000);
                s.send(new DatagramPacket(q, q.length, up, 53));
                byte[] r = new byte[4096];
                DatagramPacket rp = new DatagramPacket(r, r.length);
                s.receive(rp);
                if (rp.getLength() >= 12 && r[0] == q[0] && r[1] == q[1]) {   // same query id
                    write(DnsLogic.udpReply(pkt, Arrays.copyOf(r, rp.getLength())));
                    return;
                }
            } catch (Exception ignored) { }
        }
    }

    private synchronized void write(byte[] p) {
        try { if (running && out != null) out.write(p); } catch (IOException ignored) { }
    }

    /** DNS servers of the real network (Wi-Fi or mobile), then public fallbacks. */
    private List<InetAddress> upstreams() {
        List<InetAddress> l = new ArrayList<>();
        try {
            ConnectivityManager cm = getSystemService(ConnectivityManager.class);
            for (Network nw : cm.getAllNetworks()) {
                NetworkCapabilities nc = cm.getNetworkCapabilities(nw);
                if (nc == null || nc.hasTransport(NetworkCapabilities.TRANSPORT_VPN) || !nc.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)) continue;
                LinkProperties lp = cm.getLinkProperties(nw);
                if (lp != null) for (InetAddress a : lp.getDnsServers()) if (!l.contains(a)) l.add(a);
            }
        } catch (Exception ignored) { }
        try { l.add(InetAddress.getByAddress(new byte[]{1, 1, 1, 1})); l.add(InetAddress.getByAddress(new byte[]{9, 9, 9, 9})); } catch (Exception ignored) { }
        return l;
    }
}
