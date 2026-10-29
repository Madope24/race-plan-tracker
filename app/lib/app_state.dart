import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';
import 'models.dart';

/// Single shared state for the whole app.
final appState = AppState();

/// Holds everything the app shows and keeps it in step with the server.
///
/// How syncing works:
///  * Every change is saved on the phone first, then queued for the server.
///  * A sync pushes the queue, then pulls the full state (plan, logs, habits, check-ins, dashboard).
///  * Syncs run every 4 minutes while the app is open, when the app comes back to the foreground,
///    a few seconds after any change, on pull-to-refresh, and from "Sync now".
///  * If the phone is offline, changes wait in the queue and go out on the next successful sync.
class AppState extends ChangeNotifier {
  static const syncInterval = Duration(minutes: 4);
  static const defaultServerUrl = 'http://164.68.97.148:7070';

  static const _kServer = 'server_url';
  static const _kToken = 'api_token';
  static const _kCache = 'sync_cache_v1';
  static const _kReference = 'reference_cache_v1';
  static const _kQueue = 'pending_queue_v1';
  static const _kLastSync = 'last_sync';

  late SharedPreferences _prefs;

  String serverUrl = defaultServerUrl;
  String token = '';

  List<Session> sessions = [];
  Map<String, Habit> habits = {};
  List<Checkin> checkins = [];
  Map<String, dynamic>? dashboard;
  Map<String, dynamic>? reference;

  List<PendingChange> _queue = [];
  DateTime? lastSync;
  bool syncing = false;
  String? lastError;
  bool online = true;

  Timer? _autoTimer;
  Timer? _debounce;
  Future<void>? _running;

  bool get configured => serverUrl.isNotEmpty && token.isNotEmpty;
  int get pendingCount => _queue.length;
  bool get hasData => sessions.isNotEmpty;

  ApiClient get _api => ApiClient(serverUrl, token);

  // ---------------- startup & persistence ----------------
  Future<void> load() async {
    _prefs = await SharedPreferences.getInstance();
    serverUrl = _prefs.getString(_kServer) ?? defaultServerUrl;
    token = _prefs.getString(_kToken) ?? '';
    final last = _prefs.getString(_kLastSync);
    lastSync = last == null ? null : DateTime.tryParse(last);

    final cache = _prefs.getString(_kCache);
    if (cache != null) {
      try {
        _applySync(jsonDecode(cache) as Map<String, dynamic>);
      } catch (_) {}
    }
    final ref = _prefs.getString(_kReference);
    if (ref != null) {
      try {
        reference = jsonDecode(ref) as Map<String, dynamic>;
      } catch (_) {}
    }
    final q = _prefs.getString(_kQueue);
    if (q != null) {
      try {
        _queue = (jsonDecode(q) as List).map((e) => PendingChange.fromJson(Map<String, dynamic>.from(e as Map))).toList();
      } catch (_) {}
    }
    notifyListeners();
  }

  Future<void> saveSettings(String url, String newToken) async {
    serverUrl = url.trim().replaceAll(RegExp(r'/+$'), '');
    token = newToken.trim();
    await _prefs.setString(_kServer, serverUrl);
    await _prefs.setString(_kToken, token);
    notifyListeners();
    await sync();
  }

  Future<String> testConnection(String url, String testToken) => ApiClient(url, testToken.trim()).testConnection();

  Future<void> _saveQueue() => _prefs.setString(_kQueue, jsonEncode(_queue.map((e) => e.toJson()).toList()));

  Future<void> _saveLocalCache() => _prefs.setString(
        _kCache,
        jsonEncode({
          'sessions': sessions.map((s) => s.toJson()).toList(),
          'habits': habits.values.map((h) => h.toJson()).toList(),
          'checkins': checkins.map((c) => c.toJson()).toList(),
          'dashboard': dashboard,
        }),
      );

  void _applySync(Map<String, dynamic> j) {
    sessions = (j['sessions'] as List).map((e) => Session.fromJson(Map<String, dynamic>.from(e as Map))).toList();
    habits = {
      for (final e in (j['habits'] as List? ?? []))
        (e as Map)['date'] as String: Habit.fromJson(Map<String, dynamic>.from(e)),
    };
    checkins = (j['checkins'] as List? ?? []).map((e) => Checkin.fromJson(Map<String, dynamic>.from(e as Map))).toList();
    final d = j['dashboard'];
    dashboard = d == null ? null : Map<String, dynamic>.from(d as Map);
  }

  // ---------------- auto sync ----------------
  void startAutoSync() {
    _autoTimer?.cancel();
    _autoTimer = Timer.periodic(syncInterval, (_) => sync());
    sync();
  }

  void stopAutoSync() {
    _autoTimer?.cancel();
    _autoTimer = null;
  }

  void _syncSoon() {
    _debounce?.cancel();
    _debounce = Timer(const Duration(seconds: 3), sync);
  }

  /// Push queued changes, then pull the latest state. Safe to call at any time; overlapping calls share one run.
  Future<void> sync() {
    if (!configured) return Future.value();
    return _running ??= _doSync().whenComplete(() => _running = null);
  }

  Future<void> _doSync() async {
    syncing = true;
    notifyListeners();
    final api = _api;
    try {
      // 1. Push
      while (_queue.isNotEmpty) {
        final change = _queue.first;
        try {
          if (change.method == 'DELETE') {
            await api.delete(change.path);
          } else {
            await api.put(change.path, change.body);
          }
        } on ApiException catch (e) {
          if (!e.permanent) rethrow;
          lastError = 'A change was rejected and dropped: ${e.message}';
        }
        _queue.removeAt(0);
        await _saveQueue();
      }

      // 2. Pull (only when nothing is waiting, so the server never overwrites unsent changes)
      final data = await api.get('/api/sync') as Map<String, dynamic>;
      _applySync(data);
      await _prefs.setString(_kCache, jsonEncode(data));

      final version = data['reference_version'];
      if (reference == null || reference!['version'] != version) {
        reference = await api.get('/api/reference') as Map<String, dynamic>;
        await _prefs.setString(_kReference, jsonEncode(reference));
      }

      lastSync = DateTime.now();
      await _prefs.setString(_kLastSync, lastSync!.toIso8601String());
      online = true;
      if (lastError != null && !lastError!.startsWith('A change')) lastError = null;
    } on ApiException catch (e) {
      online = true;
      lastError = e.toString();
    } catch (e) {
      online = false;
      lastError = 'Offline — changes are saved on your phone and will sync automatically.';
    } finally {
      syncing = false;
      notifyListeners();
    }
  }

  void _enqueue(PendingChange change) {
    // Keep only the newest change per item.
    _queue.removeWhere((c) => c.path == change.path);
    _queue.add(change);
    _saveQueue();
    _saveLocalCache();
    notifyListeners();
    _syncSoon();
  }

  // ---------------- writes ----------------
  void logSession(Session s, SessionLog log) {
    s.log = log;
    _enqueue(PendingChange('PUT', '/api/sessions/${s.id}/log', log.toJson()));
  }

  void clearSessionLog(Session s) {
    s.log = null;
    _enqueue(PendingChange('DELETE', '/api/sessions/${s.id}/log', null));
  }

  void saveHabit(Habit h) {
    h.updatedAt = nowUtcIso();
    habits[h.date] = h;
    _enqueue(PendingChange('PUT', '/api/habits/${h.date}', h.toBody()));
  }

  void saveCheckin(Checkin c) {
    c.updatedAt = nowUtcIso();
    final i = checkins.indexWhere((x) => x.week == c.week);
    if (i >= 0) checkins[i] = c;
    _enqueue(PendingChange('PUT', '/api/checkins/${c.week}', c.toBody()));
  }

  // ---------------- queries ----------------
  List<Session> sessionsOn(String date) => sessions.where((s) => s.date == date).toList();

  List<Session> sessionsInWeek(int week) => sessions.where((s) => s.week == week).toList();

  Session? sessionById(int? id) {
    if (id == null) return null;
    for (final s in sessions) {
      if (s.id == id) return s;
    }
    return null;
  }

  Habit habitFor(String date) => habits[date] ?? Habit(date: date);

  /// Current plan week from the server (week 0 = the start-up days before 2 November).
  int get currentWeek {
    final w = dashboard?['current_week'];
    if (w is int && weeks.contains(w)) return w;
    return weeks.isEmpty ? 0 : weeks.first;
  }

  /// Every week number in the plan, in order (0–14).
  List<int> get weeks => (sessions.map((s) => s.week).toSet().toList()..sort());

  Checkin? checkinFor(int week) {
    for (final c in checkins) {
      if (c.week == week) return c;
    }
    return null;
  }

  @override
  void dispose() {
    _autoTimer?.cancel();
    _debounce?.cancel();
    super.dispose();
  }
}
