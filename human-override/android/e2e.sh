#!/bin/bash
# Human Override (c) 2026 Amghar Said - end-to-end test on an Android emulator (run by the CI workflow).
set -u
PKG=xyz.geopolcoins.humanoverride
adb install -r "$1" || exit 1
adb shell appops set $PKG ACTIVATE_VPN allow          # same as the user tapping "OK" on the VPN dialog
adb shell am start -n $PKG/.MainActivity; sleep 6
tap() {   # tap the first element whose text contains $1
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null; adb pull /sdcard/ui.xml /tmp/ui.xml >/dev/null
  python3 - "$1" <<'PY'
import re, sys, subprocess
x = open('/tmp/ui.xml', encoding='utf-8').read()
for m in re.finditer(r'<node [^>]*text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', x):
    if sys.argv[1].lower() in m.group(1).lower():
        a, b, c, d = map(int, m.groups()[1:]); subprocess.run(['adb', 'shell', 'input', 'tap', str((a + c) // 2), str((b + d) // 2)]); print('tapped', m.group(1)); break
else: print('not found', sys.argv[1]); sys.exit(1)
PY
}
look() { adb shell "ping -c 1 -W 3 $1 2>&1" | head -1; }
echo "== before"; for h in chatgpt.com www.google.com; do echo "$h: $(look $h)"; done
tap "I agree" || exit 1; sleep 2
tap "AI ALLOWED" || exit 1; sleep 6
adb shell uiautomator dump /sdcard/ui.xml >/dev/null; adb pull /sdcard/ui.xml /tmp/ui.xml >/dev/null
grep -qi "AI BLOCKED" /tmp/ui.xml && echo "UI: AI BLOCKED shown" || { echo "FAIL: button did not switch"; exit 1; }
echo "== while blocking"; fail=0
for h in chatgpt.com claude.ai gemini.google.com chat.openai.com chat.com duck.ai chatgpt-com.translate.goog lmarena.ai; do r=$(look $h); echo "$h: $r"; echo "$r" | grep -qi "unknown host" || { echo "FAIL: $h not blocked"; fail=1; }; done
for h in www.google.com example.org wikipedia.org; do r=$(look $h); echo "$h: $r"; echo "$r" | grep -qi "unknown host" && { echo "FAIL: $h wrongly blocked"; fail=1; }; done
adb shell "dumpsys connectivity | grep -i 'VPN' | head -3"
echo "== camera guard (informative: needs an emulated camera)"
adb shell am start -n $PKG/.MainActivity; sleep 2
for i in 1 2 3 4; do adb shell input swipe 500 1600 500 500 300; sleep 1; done
if tap "Warn me when"; then sleep 2
  adb shell am start -a android.media.action.STILL_IMAGE_CAMERA >/dev/null 2>&1; sleep 8
  adb shell dumpsys notification --noredact 2>/dev/null | grep -qi "camera is being used" && echo "guard: camera notification shown" || echo "WARN: no camera notification (emulator may have no camera)"
  adb shell input keyevent KEYCODE_HOME
else echo "WARN: guard switch not found"; fi
exit $fail
