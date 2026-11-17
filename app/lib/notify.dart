// Phone reminders. Everything is scheduled on the phone itself (nothing is sent from a server), for the next 14 days,
// and re-planned every time the app opens or the plan or your reminder settings change.

import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

class Reminder {
  final DateTime at;
  final String title;
  final String body;
  const Reminder(this.at, this.title, this.body);
}

class Notifier {
  static final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();
  static bool _ready = false;

  /// Last result in plain words, shown in Profile > Reminders.
  static String status = 'Reminders have not been set up yet.';

  static const NotificationDetails _details = NotificationDetails(
    android: AndroidNotificationDetails(
      'coach',
      'Coach reminders',
      channelDescription: 'Workouts, mobility, kegels, meals, water, sleep and race reminders',
      importance: Importance.high,
      priority: Priority.high,
    ),
  );

  static Future<bool> init() async {
    if (_ready) return true;
    try {
      tzdata.initializeTimeZones();
      await _plugin.initialize(settings: const InitializationSettings(android: AndroidInitializationSettings('@mipmap/ic_launcher')));
      _ready = true;
    } catch (e) {
      status = 'Reminders are not available on this device ($e).';
    }
    return _ready;
  }

  /// Ask Android (13 and newer) for permission to show notifications. Returns true when allowed.
  static Future<bool> requestPermission() async {
    if (!await init()) return false;
    try {
      final android = _plugin.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      final ok = await android?.requestNotificationsPermission();
      if (ok == false) status = 'Notifications are blocked for EnduraForge. Allow them in the phone settings (Apps > EnduraForge > Notifications).';
      return ok ?? true;
    } catch (e) {
      status = 'Could not ask for notification permission ($e).';
      return false;
    }
  }

  /// Replace every pending reminder with [items] (only those still in the future are kept).
  static Future<int> schedule(List<Reminder> items) async {
    if (!await init()) return 0;
    var n = 0;
    try {
      await _plugin.cancelAll();
      final now = DateTime.now();
      final future = items.where((r) => r.at.isAfter(now)).toList()..sort((a, b) => a.at.compareTo(b.at));
      for (final r in future.take(400)) {
        await _plugin.zonedSchedule(
          id: 1000 + n,
          title: r.title,
          body: r.body,
          scheduledDate: tz.TZDateTime.from(r.at, tz.UTC),
          notificationDetails: _details,
          androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
        );
        n++;
      }
      status = n == 0 ? 'No reminders are switched on.' : '$n reminders are set for the next 14 days. They refresh every time you open the app.';
    } catch (e) {
      status = 'Could not set reminders ($e).';
    }
    return n;
  }

  static Future<void> cancelAll() async {
    if (!await init()) return;
    try {
      await _plugin.cancelAll();
      status = 'All reminders are off.';
    } catch (_) {}
  }

  static Future<bool> test() async {
    if (!await requestPermission()) return false;
    try {
      await _plugin.show(id: 1, title: 'EnduraForge reminders work', body: 'You will be reminded about workouts, mobility, kegels and more.', notificationDetails: _details);
      return true;
    } catch (e) {
      status = 'Could not show a test reminder ($e).';
      return false;
    }
  }
}
