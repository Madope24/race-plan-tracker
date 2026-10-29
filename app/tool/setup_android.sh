#!/usr/bin/env bash
# Generates the Android project files (first run only) and applies the app's Android settings:
#   - internet access and plain-http access to your server
#   - everything scheduled workout reminders need (flutter_local_notifications):
#     notification, boot and exact-alarm permissions, the scheduling receivers, and core library desugaring
# Safe to run again: it never overwrites your Dart code and only adds what is missing.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f android/app/src/main/AndroidManifest.xml ]; then
  flutter create --platforms=android --org com.samatope --project-name race_plan_tracker .
fi

python3 - <<'PY'
import os, re

# ---------- AndroidManifest.xml ----------
path = "android/app/src/main/AndroidManifest.xml"
m = open(path).read()

permissions = [
    '<uses-permission android:name="android.permission.INTERNET"/>',
    '<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>',
    '<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>',
    '<uses-permission android:name="android.permission.VIBRATE"/>',
    # Exact reminder times: asked for on Android 12, granted automatically on Android 13+
    '<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" android:maxSdkVersion="32"/>',
    '<uses-permission android:name="android.permission.USE_EXACT_ALARM"/>',
]
missing = [p for p in permissions if re.search(r'android:name="([^"]+)"', p).group(1) not in m]
if missing:
    m = m.replace("<application", "\n    ".join(missing) + "\n    <application", 1)

# Plain http:// to reach http://SERVER_IP:7070. Remove once you only use HTTPS.
if "usesCleartextTraffic" not in m:
    m = m.replace("<application", '<application android:usesCleartextTraffic="true"', 1)

m = m.replace('android:label="race_plan_tracker"', 'android:label="Race Plan"')

receivers = '''        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>
'''
if "ScheduledNotificationReceiver" not in m:
    m = m.replace("</application>", receivers + "    </application>", 1)
open(path, "w").write(m)

# ---------- app/build.gradle(.kts): core library desugaring ----------
groovy, kts = "android/app/build.gradle", "android/app/build.gradle.kts"
if os.path.exists(kts):
    g, path = open(kts).read(), kts
    enable, multidex = "isCoreLibraryDesugaringEnabled = true", "multiDexEnabled = true"
    deps = '''
dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")
    implementation("androidx.window:window:1.0.0")
    implementation("androidx.window:window-java:1.0.0")
}
'''
else:
    g, path = open(groovy).read(), groovy
    enable, multidex = "coreLibraryDesugaringEnabled = true", "multiDexEnabled = true"
    deps = '''
dependencies {
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
    implementation 'androidx.window:window:1.0.0'
    implementation 'androidx.window:window-java:1.0.0'
}
'''
if "oreLibraryDesugaringEnabled" not in g:
    g = re.sub(r"compileOptions\s*\{", lambda x: x.group(0) + "\n        " + enable, g, count=1)
if "multiDexEnabled" not in g:
    g = re.sub(r"defaultConfig\s*\{", lambda x: x.group(0) + "\n        " + multidex, g, count=1)
if "desugar_jdk_libs" not in g:
    g = g.rstrip() + "\n" + deps
open(path, "w").write(g)
print("Patched", path)
PY

echo "Android project ready:"
grep -E 'permission|usesCleartextTraffic|android:label|ScheduledNotification' android/app/src/main/AndroidManifest.xml
grep -nE 'esugar|multiDex' android/app/build.gradle* || true
