"""Run after `flutter create`: allows HTTP to your server, names the app, and sets up phone reminders
(notification permission, boot receiver, library desugaring that the notifications plugin needs)."""
import pathlib
import re
import sys

m = pathlib.Path('android/app/src/main/AndroidManifest.xml')
if not m.exists():
    sys.exit('android/ not found: run flutter create first')
s = m.read_text()
for perm in ('INTERNET', 'POST_NOTIFICATIONS', 'RECEIVE_BOOT_COMPLETED'):
    if f'android.permission.{perm}' not in s:
        s = s.replace('<application', f'<uses-permission android:name="android.permission.{perm}"/>\n    <application', 1)
if 'usesCleartextTraffic' not in s:
    s = s.replace('<application', '<application\n        android:usesCleartextTraffic="true"', 1)
s = re.sub(r'android:label="[^"]*"', 'android:label="EnduraForge"', s, count=1)
RECEIVERS = """        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>
"""
if 'ScheduledNotificationReceiver' not in s:
    s = s.replace('    </application>', RECEIVERS + '    </application>', 1)
m.write_text(s)
print('AndroidManifest patched: permissions, cleartext HTTP, label, reminder receivers')

# keep the launcher icon in release builds: it is the notification icon
raw = pathlib.Path('android/app/src/main/res/raw')
raw.mkdir(parents=True, exist_ok=True)
(raw / 'keep.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources xmlns:tools="http://schemas.android.com/tools" tools:keep="@mipmap/ic_launcher" />\n')

# core library desugaring (required by flutter_local_notifications)
kts = pathlib.Path('android/app/build.gradle.kts')
groovy = pathlib.Path('android/app/build.gradle')
if kts.exists():
    g = kts.read_text()
    if 'isCoreLibraryDesugaringEnabled' not in g:
        g, n = re.subn(r'compileOptions\s*\{', 'compileOptions {\n        isCoreLibraryDesugaringEnabled = true', g, count=1)
        if n == 0:
            sys.exit('compileOptions block not found in build.gradle.kts')
    if 'multiDexEnabled' not in g:
        g = re.sub(r'defaultConfig\s*\{', 'defaultConfig {\n        multiDexEnabled = true', g, count=1)
    if 'desugar_jdk_libs' not in g:
        g += '\ndependencies {\n    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n}\n'
    kts.write_text(g)
    print('build.gradle.kts patched: desugaring on')
elif groovy.exists():
    g = groovy.read_text()
    if 'coreLibraryDesugaringEnabled' not in g:
        g, n = re.subn(r'compileOptions\s*\{', 'compileOptions {\n        coreLibraryDesugaringEnabled true', g, count=1)
        if n == 0:
            sys.exit('compileOptions block not found in build.gradle')
    if 'multiDexEnabled' not in g:
        g = re.sub(r'defaultConfig\s*\{', 'defaultConfig {\n        multiDexEnabled true', g, count=1)
    if 'desugar_jdk_libs' not in g:
        g += "\ndependencies {\n    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'\n}\n"
    groovy.write_text(g)
    print('build.gradle patched: desugaring on')
else:
    sys.exit('android/app/build.gradle(.kts) not found')
