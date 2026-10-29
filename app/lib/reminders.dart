import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest_all.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

import 'app_state.dart';
import 'models.dart';
import 'widgets/common.dart';

/// Workout reminders, scheduled on the phone in advance for every remaining day of the plan.
///
/// They live in Android's alarm system, so they fire when the app is closed, the phone is offline,
/// or after a reboot. Whenever the plan or your logs change, the whole set is rebuilt, so a workout
/// you've already logged stops reminding you.
///
/// Per day (only on days with training):
///   * Morning summary with the weigh-in prompt: your chosen time (default 05:00); 04:10 on fast days (before suhoor)
///   * One reminder per workout, timed by its slot (Morning 05:30, Afternoon 16:15, Any time 16:30,
///     Evening 17:30, After iftar 19:40, Before bed 21:30)
///   * 22:00 nudge if a run, swim or strength session from that day still isn't logged
class ReminderSettings {
  bool enabled;
  int summaryMinutes; // minutes after midnight
  bool perWorkout;
  bool logNudge;
  bool weighIn;

  ReminderSettings({
    this.enabled = true,
    this.summaryMinutes = 5 * 60,
    this.perWorkout = true,
    this.logNudge = true,
    this.weighIn = true,
  });

  factory ReminderSettings.fromJson(Map<String, dynamic> j) => ReminderSettings(
        enabled: j['enabled'] as bool? ?? true,
        summaryMinutes: j['summaryMinutes'] as int? ?? 5 * 60,
        perWorkout: j['perWorkout'] as bool? ?? true,
        logNudge: j['logNudge'] as bool? ?? true,
        weighIn: j['weighIn'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        'enabled': enabled,
        'summaryMinutes': summaryMinutes,
        'perWorkout': perWorkout,
        'logNudge': logNudge,
        'weighIn': weighIn,
      };

  TimeOfDay get summaryTime => TimeOfDay(hour: summaryMinutes ~/ 60, minute: summaryMinutes % 60);
}

/// When each kind of workout gets its reminder.
const slotReminderTimes = <String, int>{
  'Morning': 5 * 60 + 30,
  'Afternoon': 16 * 60 + 15,
  'Any time': 16 * 60 + 30,
  'Evening': 17 * 60 + 30,
  'After iftar': 19 * 60 + 40, // fast breaks 18:50, train ~20:00
  'Before bed': 21 * 60 + 30,
};
const logNudgeMinutes = 22 * 60;
const fastDaySummaryMinutes = 4 * 60 + 10; // before suhoor

int? slotMinutes(String timeSlot) {
  for (final e in slotReminderTimes.entries) {
    if (timeSlot.startsWith(e.key)) return e.value;
  }
  return null;
}

String hhmm(int minutes) => '${(minutes ~/ 60).toString().padLeft(2, '0')}:${(minutes % 60).toString().padLeft(2, '0')}';

String _emoji(String type) => const {'Run': '🏃', 'Swim': '🏊', 'Strength': '🏋️', 'Mobility': '🧘'}[type] ?? '📋';

class ReminderService {
  ReminderService._();
  static final ReminderService instance = ReminderService._();

  static const _kSettings = 'reminder_settings_v1';
  static const _zone = 'Africa/Dar_es_Salaam';
  // ID ranges: sessions use their own id (1–999); the rest are offset.
  static const _summaryBase = 10000, _nudgeBase = 20000, _testId = 99999;

  final _plugin = FlutterLocalNotificationsPlugin();
  late SharedPreferences _prefs;
  ReminderSettings settings = ReminderSettings();
  GlobalKey<NavigatorState>? navigatorKey;
  void Function(int sessionId)? onOpenSession;

  String? _lastSignature;
  Timer? _debounce;
  bool _ready = false;
  bool? permissionGranted;
  bool? exactAllowed;
  int scheduledCount = 0;

  static const _workoutChannel = AndroidNotificationDetails(
    'workouts',
    'Workout reminders',
    channelDescription: 'A reminder before each planned workout',
    importance: Importance.high,
    priority: Priority.high,
    category: AndroidNotificationCategory.reminder,
  );
  static const _dailyChannel = AndroidNotificationDetails(
    'daily',
    'Daily plan',
    channelDescription: "Morning summary of the day's workouts, log and weigh-in reminders",
    importance: Importance.defaultImportance,
    priority: Priority.defaultPriority,
    category: AndroidNotificationCategory.reminder,
  );

  AndroidFlutterLocalNotificationsPlugin? get _android =>
      _plugin.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    final raw = _prefs.getString(_kSettings);
    if (raw != null) {
      try {
        settings = ReminderSettings.fromJson(jsonDecode(raw) as Map<String, dynamic>);
      } catch (_) {}
    }
    tzdata.initializeTimeZones();
    tz.setLocalLocation(tz.getLocation(_zone));
    await _plugin.initialize(
      const InitializationSettings(android: AndroidInitializationSettings('@mipmap/ic_launcher')),
      onDidReceiveNotificationResponse: (r) => _handleTap(r.payload),
    );
    _ready = true;
    appState.addListener(_onStateChanged);
  }

  /// Call after the first frame: opens the workout if the app was launched by tapping a reminder.
  Future<void> handleLaunch() async {
    final details = await _plugin.getNotificationAppLaunchDetails();
    if (details?.didNotificationLaunchApp ?? false) {
      _handleTap(details!.notificationResponse?.payload);
    }
  }

  void _handleTap(String? payload) {
    if (payload == null || !payload.startsWith('session:')) return;
    final id = int.tryParse(payload.substring(8));
    if (id != null) onOpenSession?.call(id);
  }

  /// Asks Android for notification permission (Android 13+) and exact alarms (Android 12+).
  Future<void> requestPermissions() async {
    final android = _android;
    if (android == null) return;
    permissionGranted = await android.requestNotificationsPermission() ?? await android.areNotificationsEnabled();
    exactAllowed = await android.canScheduleExactNotifications();
    if (exactAllowed == false) {
      await android.requestExactAlarmsPermission();
      exactAllowed = await android.canScheduleExactNotifications();
    }
    _lastSignature = null;
    await reschedule();
  }

  Future<void> refreshPermissionState() async {
    final android = _android;
    if (android == null) return;
    permissionGranted = await android.areNotificationsEnabled();
    exactAllowed = await android.canScheduleExactNotifications();
  }

  Future<void> saveSettings(ReminderSettings s) async {
    settings = s;
    await _prefs.setString(_kSettings, jsonEncode(s.toJson()));
    _lastSignature = null;
    await reschedule();
  }

  void _onStateChanged() {
    _debounce?.cancel();
    _debounce = Timer(const Duration(seconds: 2), reschedule);
  }

  /// What the schedule depends on. If it hasn't changed, nothing is rebuilt (syncs every 4 minutes stay cheap).
  String _signature(List<Session> sessions) {
    final today = isoDate(DateTime.now());
    final b = StringBuffer('${jsonEncode(settings.toJson())}|$today|$exactAllowed|');
    for (final s in sessions) {
      if (s.date.compareTo(today) >= 0) b.write('${s.id}:${s.date}:${s.timeSlot}:${s.log?.status ?? '-'};');
    }
    return b.toString();
  }

  Future<void>? _job;
  bool _again = false;

  /// Rebuilds every future reminder from the current plan and logs. Calls that arrive mid-rebuild
  /// are folded into one more pass afterwards, so two rebuilds never interleave.
  Future<void> reschedule() async {
    if (_job != null) {
      _again = true;
      return _job;
    }
    _job = _rebuild();
    try {
      await _job;
    } finally {
      _job = null;
    }
    if (_again) {
      _again = false;
      await reschedule();
    }
  }

  Future<void> _rebuild() async {
    if (!_ready) return;
    final sessions = appState.sessions;
    final sig = _signature(sessions);
    if (sig == _lastSignature) return;
    _lastSignature = sig;

    await _plugin.cancelAll();
    scheduledCount = 0;
    if (!settings.enabled || sessions.isEmpty) return;

    final android = _android;
    exactAllowed ??= await android?.canScheduleExactNotifications();
    final mode = (exactAllowed ?? false) ? AndroidScheduleMode.exactAllowWhileIdle : AndroidScheduleMode.inexactAllowWhileIdle;
    final now = tz.TZDateTime.now(tz.local);

    final byDate = <String, List<Session>>{};
    for (final s in sessions) {
      if (s.isTraining) byDate.putIfAbsent(s.date, () => []).add(s);
    }
    final dates = byDate.keys.toList()..sort();

    Future<void> at(int id, String date, int minutes, String title, String body, AndroidNotificationDetails channel, String? payload) async {
      final d = DateTime.parse(date);
      final when = tz.TZDateTime(tz.local, d.year, d.month, d.day, minutes ~/ 60, minutes % 60);
      if (!when.isAfter(now)) return;
      await _plugin.zonedSchedule(
        id,
        title,
        body,
        when,
        NotificationDetails(android: channel),
        androidScheduleMode: mode,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        payload: payload,
      );
      scheduledCount++;
    }

    for (var i = 0; i < dates.length; i++) {
      final date = dates[i];
      final day = byDate[date]!;
      final open = day.where((s) => s.log == null).toList();
      final fast = day.first.isFastDay;

      // Morning summary (with the weigh-in prompt)
      if (open.isNotEmpty) {
        final list = open.map((s) => '${_emoji(s.type)} ${s.shortTitle} (${s.timeSlot.split(' (').first.toLowerCase()})').join('\n');
        final weigh = settings.weighIn ? (fast ? '⚖️ Weigh in now, before suhoor.\n' : '⚖️ Weigh in after the toilet, then log it in Track.\n') : '';
        await at(
          _summaryBase + i,
          date,
          fast ? fastDaySummaryMinutes : settings.summaryMinutes,
          fast ? "Today's plan · dry-fast day 🌙" : "Today's plan 💪",
          fast ? '$weigh$list\nNo exercise while fasting. Break the fast at 18:50, drink 500 ml first.' : '$weigh$list',
          _dailyChannel,
          'session:${open.first.id}',
        );
      }

      // One reminder per workout
      if (settings.perWorkout) {
        for (final s in open) {
          final m = slotMinutes(s.timeSlot);
          if (m == null) continue;
          await at(s.id, date, m, '${_emoji(s.type)} ${s.shortTitle}', _workoutBody(s), _workoutChannel, 'session:${s.id}');
        }
      }

      // Evening nudge to log (runs, swims and strength only; fast-day walks don't need one)
      final mainOpen = open.where((s) => s.type != 'Mobility').toList();
      if (settings.logNudge && mainOpen.isNotEmpty) {
        await at(
          _nudgeBase + i,
          date,
          logNudgeMinutes,
          'Log today\'s training ✅',
          '${mainOpen.length} workout${mainOpen.length == 1 ? '' : 's'} not logged yet: ${mainOpen.map((s) => s.shortTitle).join(', ')}',
          _dailyChannel,
          'session:${mainOpen.first.id}',
        );
      }
    }

  }

  String _workoutBody(Session s) {
    final when = s.timeSlot;
    final amount = s.plannedLabel.isEmpty ? '' : '${s.plannedLabel} · ';
    String tip;
    switch (s.type) {
      case 'Run':
        tip = 'Banana + 300–400 ml water now (400 ml after a fast day), warm-up drills, then go at first light.';
        break;
      case 'Swim':
        tip = s.isFastDay ? 'Break the fast lightly first. Pre-swim mobility poolside.' : 'Pre-swim mobility poolside, 5 minutes.';
        break;
      case 'Strength':
        tip = 'Warm up 5 minutes, then the exercises and the pelvic-floor finisher. Stop each set with 2–3 reps left.';
        break;
      case 'Mobility':
        tip = s.isFastDay
            ? 'Only after you have broken the fast and drunk 500 ml. Easy walk, then mobility and slow breathing.'
            : 'Easy walk and mobility.';
        break;
      default:
        tip = 'Rest and recover.';
    }
    return '$amount$when. $tip Tap to open.';
  }

  Future<void> sendTest() async {
    await _plugin.show(
      _testId,
      '🏃 Reminders are working',
      'You will get your daily plan at ${hhmm(settings.summaryMinutes)} and a reminder before each workout.',
      const NotificationDetails(android: _workoutChannel),
    );
  }

  Future<int> pendingCount() async => (await _plugin.pendingNotificationRequests()).length;
}
