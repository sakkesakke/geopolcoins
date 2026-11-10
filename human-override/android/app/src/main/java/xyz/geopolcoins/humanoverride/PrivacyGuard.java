/* Human Override - Copyright (c) 2026 Amghar Said. All rights reserved. See LICENSE.txt. */
package xyz.geopolcoins.humanoverride;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.hardware.camera2.CameraManager;
import android.media.AudioManager;
import android.media.AudioRecordingConfiguration;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Camera & microphone guard (opt-in): while Human Override runs, show a notification when the camera or the microphone
 *  starts being used. Android does not tell normal apps WHICH app it is, only that it happens. Nothing is stored or sent. */
final class PrivacyGuard {
    private PrivacyGuard() { }
    private static final String CH = "guard";
    private static CameraManager.AvailabilityCallback camCb;
    private static AudioManager.AudioRecordingCallback micCb;
    private static final Set<String> camsInUse = new HashSet<>();
    private static boolean micInUse = false;
    private static long lastCam = 0, lastMic = 0;

    static boolean enabled(Context c) { return Stats.prefs(c).getBoolean("guard", false); }

    static synchronized void start(Context ctx) {
        final Context c = ctx.getApplicationContext();
        if (!enabled(c) || camCb != null) return;
        Handler h = new Handler(Looper.getMainLooper());
        channel(c);
        CameraManager cm = (CameraManager) c.getSystemService(Context.CAMERA_SERVICE);
        if (cm != null) {
            camCb = new CameraManager.AvailabilityCallback() {
                @Override public void onCameraUnavailable(String id) {
                    boolean first = camsInUse.isEmpty(); camsInUse.add(id);
                    long now = System.currentTimeMillis();
                    if (first && now - lastCam > 60000) { lastCam = now; alert(c, 101, c.getString(R.string.guard_cam)); }
                }
                @Override public void onCameraAvailable(String id) { camsInUse.remove(id); }
            };
            try { cm.registerAvailabilityCallback(camCb, h); } catch (Exception e) { camCb = null; }
        }
        AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
        if (am != null) {
            micCb = new AudioManager.AudioRecordingCallback() {
                @Override public void onRecordingConfigChanged(List<AudioRecordingConfiguration> cfgs) {
                    boolean now = cfgs != null && !cfgs.isEmpty();
                    long t = System.currentTimeMillis();
                    if (now && !micInUse && t - lastMic > 60000) { lastMic = t; alert(c, 102, c.getString(R.string.guard_mic)); }
                    micInUse = now;
                }
            };
            try { am.registerAudioRecordingCallback(micCb, h); } catch (Exception e) { micCb = null; }
        }
    }

    static synchronized void stop(Context ctx) {
        Context c = ctx.getApplicationContext();
        CameraManager cm = (CameraManager) c.getSystemService(Context.CAMERA_SERVICE);
        if (cm != null && camCb != null) try { cm.unregisterAvailabilityCallback(camCb); } catch (Exception ignored) { }
        AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
        if (am != null && micCb != null) try { am.unregisterAudioRecordingCallback(micCb); } catch (Exception ignored) { }
        camCb = null; micCb = null; camsInUse.clear(); micInUse = false;
    }

    private static void channel(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        if (nm != null) nm.createNotificationChannel(new NotificationChannel(CH, c.getString(R.string.guard_title), NotificationManager.IMPORTANCE_HIGH));
    }

    private static void alert(Context c, int id, String text) {
        try {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            if (nm == null) return;
            PendingIntent pi = PendingIntent.getActivity(c, 0, new Intent(c, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
            Notification n = new Notification.Builder(c, CH).setSmallIcon(R.mipmap.ic_launcher).setContentTitle(c.getString(R.string.guard_title))
                .setContentText(text).setStyle(new Notification.BigTextStyle().bigText(text)).setContentIntent(pi).setAutoCancel(true).build();
            nm.notify(id, n);
        } catch (Exception ignored) { }   // no notification permission: stay silent
    }
}
