import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import 'api.dart';
import 'coach.dart' as coach;
import 'garmin.dart';
import 'logic.dart';
import 'notify.dart';
import 'util.dart';

const String kDefaultServer = 'http://164.68.97.148:8090';

/// Everything the app knows. Works fully offline; syncs to the server when you are signed in.
/// The plan is generated on the server from your settings (races, fasting, Ramadan...). The phone keeps the last
/// plan it received, so it always works offline; settings changed offline are sent at the next sync.
class AppState extends ChangeNotifier {
  AppState._(this.plan, this.prefs);

  Map<String, dynamic> plan;
  final SharedPreferences prefs;

  final Logs days = <String, Map<String, dynamic>>{};
  final Map<String, String> dayUpdated = <String, String>{};
  final Map<String, double?> results = <String, double?>{};
  final Map<String, String> resultUpdated = <String, String>{};
  final Set<String> outbox = <String>{};
  final Map<String, Map<String, dynamic>> activities = <String, Map<String, dynamic>>{};
  final Set<String> activityOutbox = <String>{};

  /// Settings you changed (sent to the server as your config). Empty = the starting config.
  Map<String, dynamic> custom = <String, dynamic>{};
  String? customUpdated;
  bool planPending = false;     // settings changed, waiting for the server to rebuild the plan

  String serverUrl = kDefaultServer;
  String? token;
  String? email;
  String? lastSync;
  String syncNote = 'Not signed in: everything is saved on this phone.';
  bool syncing = false;
  bool darkMode = true;
  Map<String, dynamic> notify = <String, dynamic>{};
  Timer? _syncTimer;

  final Map<String, int> _dayIndex = <String, int>{};

  static Future<AppState> load() async {
    final prefs = await SharedPreferences.getInstance();
    Map<String, dynamic>? cached;
    try {
      final c = prefs.getString('plan_cache');
      if (c != null) cached = asMap(jsonDecode(c));
    } catch (_) {}
    final asset = asMap(jsonDecode(await rootBundle.loadString('assets/plan.json')));
    // A plan cached from the server is only used while it comes from the same plan engine as this app version.
    // After an app update the bundled plan wins until the (updated) server sends a new one.
    if (cached != null && asStr(cached['engine']) != asStr(asset['engine'])) {
      cached = null;
      await prefs.remove('plan_cache');
    }
    final st = AppState._(cached ?? asset, prefs);
    st._index();
    st._restore();
    // The watch history that ships with the plan: add it, and correct earlier copies (they were stored in miles).
    var seeded = false;
    for (final a in asList(st.plan['seed_activities']).map(asMap)) {
      final id = asStr(a['id']);
      final mine = st.activities[id];
      if (mine == null || asNum(mine['distance_km']) != asNum(a['distance_km'])) {
        st.activities[id] = Map<String, dynamic>.from(a);
        st.activityOutbox.add(id);
        seeded = true;
      }
    }
    if (seeded) await st._save();
    return st;
  }

  void _index() {
    _dayIndex.clear();
    final ds = asList(plan['days']);
    for (var i = 0; i < ds.length; i++) {
      _dayIndex[asStr(asMap(ds[i])['date'])] = i;
    }
  }

  void _restore() {
    try {
      asMap(jsonDecode(prefs.getString('days') ?? '{}')).forEach((k, v) => days[k] = Map<String, dynamic>.from(asMap(v)));
      asMap(jsonDecode(prefs.getString('dayUpdated') ?? '{}')).forEach((k, v) => dayUpdated[k] = asStr(v));
      asMap(jsonDecode(prefs.getString('results') ?? '{}')).forEach((k, v) => results[k] = asNum(v));
      asMap(jsonDecode(prefs.getString('resultUpdated') ?? '{}')).forEach((k, v) => resultUpdated[k] = asStr(v));
      for (final o in asList(jsonDecode(prefs.getString('outbox') ?? '[]'))) {
        outbox.add(asStr(o));
      }
      asMap(jsonDecode(prefs.getString('activities') ?? '{}')).forEach((k, v) => activities[k] = Map<String, dynamic>.from(asMap(v)));
      for (final o in asList(jsonDecode(prefs.getString('activityOutbox') ?? '[]'))) {
        activityOutbox.add(asStr(o));
      }
      custom = Map<String, dynamic>.from(asMap(jsonDecode(prefs.getString('custom') ?? '{}')));
      notify = Map<String, dynamic>.from(asMap(jsonDecode(prefs.getString('notify') ?? '{}')));
    } catch (_) {}
    customUpdated = prefs.getString('customUpdated');
    planPending = prefs.getBool('planPending') ?? false;
    serverUrl = prefs.getString('serverUrl') ?? kDefaultServer;
    token = prefs.getString('token');
    email = prefs.getString('email');
    lastSync = prefs.getString('lastSync');
    darkMode = prefs.getBool('dark') ?? true;
    if (token != null) syncNote = 'Signed in as $email.';
  }

  Future<void> _save() async {
    await prefs.setString('days', jsonEncode(days));
    await prefs.setString('dayUpdated', jsonEncode(dayUpdated));
    await prefs.setString('results', jsonEncode(results));
    await prefs.setString('resultUpdated', jsonEncode(resultUpdated));
    await prefs.setString('outbox', jsonEncode(outbox.toList()));
    await prefs.setString('activities', jsonEncode(activities));
    await prefs.setString('activityOutbox', jsonEncode(activityOutbox.toList()));
    await prefs.setString('custom', jsonEncode(custom));
    if (customUpdated != null) await prefs.setString('customUpdated', customUpdated!);
    await prefs.setBool('planPending', planPending);
    await prefs.setString('notify', jsonEncode(notify));
  }

  // ---------------------------------------------------------------- plan access
  String get startIso => asStr(plan['start']);
  String get endIso => asStr(plan['end']);
  List<dynamic> get planDays => asList(plan['days']);
  Map<String, dynamic> get config => asMap(plan['config']);
  Map<String, dynamic> get profile => asMap(effective('profile'));

  /// A config section with your unsynced edits applied on top.
  Object? effective(String section) {
    final base = config[section];
    final mine = custom[section];
    if (mine == null) return base;
    if (base is Map && mine is Map) return <String, dynamic>{...asMap(base), ...asMap(mine)};
    return mine;
  }

  List<Map<String, dynamic>> get races => asList(effective('races')).map((r) => Map<String, dynamic>.from(asMap(r))).toList();

  String clampIso(String iso) {
    if (iso.compareTo(startIso) < 0) return startIso;
    if (iso.compareTo(endIso) > 0) return endIso;
    return iso;
  }

  String get currentIso => clampIso(todayIso());
  bool hasDay(String iso) => _dayIndex.containsKey(iso);
  Map<String, dynamic> planDay(String iso) => asMap(planDays[_dayIndex[iso] ?? 0]);
  Map<String, dynamic> session(String? key) => key == null ? <String, dynamic>{} : asMap(asMap(plan['sessions'])[key]);
  Map<String, dynamic> log(String iso) => days[iso] ?? <String, dynamic>{};

  /// The library entry that explains a session row (rows carry a 'lib' link when the name differs).
  Map<String, dynamic>? libraryFor(Map<String, dynamic> row) {
    final l = asStr(row['lib']);
    return libraryEntry(l.isNotEmpty ? l : asStr(row['ex']));
  }

  Map<String, dynamic>? libraryEntry(String name) {
    for (final raw in asList(plan['library'])) {
      final e = asMap(raw);
      if (e['name'] == name) return e;
    }
    return null;
  }

  /// The next dated A or B race on or after today.
  Map<String, dynamic>? get nextRace {
    final t = todayIso();
    final rs = races.where((r) => asStr(r['date']).isNotEmpty && asStr(r['date']).compareTo(t) >= 0 && asStr(r['priority']) != 'C').toList()
      ..sort((a, b) => asStr(a['date']).compareTo(asStr(b['date'])));
    return rs.isEmpty ? null : rs.first;
  }

  // ---------------------------------------------------------------- editing a day
  void _snapshot(String iso, Map<String, dynamic> d) {
    // keep what was planned at the time, so later plan changes never rewrite history
    if (d['planned'] != null || !hasDay(iso)) return;
    final pd = planDay(iso);
    final p = <String, dynamic>{};
    if (pd['am'] != null) p['am'] = asStr(session(asStr(pd['am']))['name']);
    if (pd['pm'] != null) p['pm'] = asStr(session(asStr(pd['pm']))['name']);
    if (pd['race'] != null) p['race'] = asStr(pd['race']);
    if (p.isNotEmpty) d['planned'] = p;
  }

  void _write(String iso, Map<String, dynamic> d) {
    _snapshot(iso, d);
    days[iso] = d;
    dayUpdated[iso] = nowIso();
    outbox.add('day:$iso');
    _changed();
  }

  void setField(String iso, String key, Object? value) {
    final d = Map<String, dynamic>.from(log(iso));
    if (value == null || (value is String && value.isEmpty)) {
      d.remove(key);
    } else {
      d[key] = value;
    }
    _write(iso, d);
  }

  void setFields(String iso, Map<String, Object?> values) {
    final d = Map<String, dynamic>.from(log(iso));
    values.forEach((k, v) {
      if (v == null) {
        d.remove(k);
      } else {
        d[k] = v;
      }
    });
    _write(iso, d);
  }

  void toggleDone(String iso, String id) {
    final d = Map<String, dynamic>.from(log(iso));
    final done = asList(d['done']).map(asStr).toSet();
    if (!done.remove(id)) done.add(id);
    d['done'] = done.toList()..sort();
    _write(iso, d);
  }

  bool isDone(String iso, String id) => asList(log(iso)['done']).contains(id);

  List<Map<String, dynamic>> setsFor(String iso, String id) =>
      asList(asMap(log(iso)['sets'])[id]).map((e) => Map<String, dynamic>.from(asMap(e))).toList();

  void saveSets(String iso, String id, String exercise, List<Map<String, dynamic>> sets) {
    final d = Map<String, dynamic>.from(log(iso));
    final all = Map<String, dynamic>.from(asMap(d['sets']));
    if (sets.isEmpty) {
      all.remove(id);
    } else {
      all[id] = sets.map((s) => <String, dynamic>{...s, 'ex': exercise}).toList();
    }
    d['sets'] = all;
    _write(iso, d);
  }

  void addWater(String iso, double litres) {
    final cur = asNum(log(iso)['water']) ?? 0.0;
    setField(iso, 'water', round1((cur + litres).clamp(0, 20).toDouble()));
  }

  void toggleInList(String iso, String field, String value) {
    final d = Map<String, dynamic>.from(log(iso));
    final l = asList(d[field]).map(asStr).toList();
    if (!l.remove(value)) l.add(value);
    if (l.isEmpty) {
      d.remove(field);
    } else {
      d[field] = l;
    }
    _write(iso, d);
  }

  /// Tick a planned meal as eaten: the day's food totals are recalculated from the ticked meals.
  void toggleMeal(String iso, String meal) {
    toggleInList(iso, 'meals_eaten', meal);
    final eaten = asList(log(iso)['meals_eaten']).map(asStr).toSet();
    var k = 0.0, p = 0.0, c = 0.0, f = 0.0;
    for (final m in mealsFor(iso)) {
      if (!eaten.contains(asStr(m['meal']))) continue;
      final t = asMap(m['totals']);
      k += asNum(t['kcal']) ?? 0.0;
      p += asNum(t['p']) ?? 0.0;
      c += asNum(t['c']) ?? 0.0;
      f += asNum(t['f']) ?? 0.0;
    }
    setFields(iso, {
      'kcal': eaten.isEmpty ? null : k.roundToDouble(),
      'protein': eaten.isEmpty ? null : p.roundToDouble(),
      'carbs': eaten.isEmpty ? null : c.roundToDouble(),
      'fat': eaten.isEmpty ? null : f.roundToDouble(),
    });
  }

  List<Map<String, dynamic>> mealsFor(String iso) {
    final pd = planDay(iso);
    final mp = asMap(asMap(asMap(asMap(plan['nutrition'])['meal_plans'])[asStr(pd['meal_plan'])])[asStr(pd['weekday'])]);
    return asList(mp['meals']).map(asMap).toList();
  }

  void setFeedback(String iso, String slot, Map<String, dynamic> fb) {
    final d = Map<String, dynamic>.from(log(iso));
    d['${slot}_fb'] = fb;
    if (fb['done'] == 'yes' || fb['done'] == 'partly') d['${slot}_done'] = true;
    if (fb['done'] == 'no') d['skip_$slot'] = true;
    _write(iso, d);
  }

  /// Move a missed session to another day (the original is marked skipped; history is kept).
  void reschedule(String fromIso, String slot, String toIso) {
    final key = asStr(planDay(fromIso)[slot]);
    if (key.isEmpty) return;
    setField(fromIso, 'skip_$slot', true);
    final d = Map<String, dynamic>.from(log(toIso));
    final extra = asList(d['extra']).map(asStr).toList();
    if (!extra.contains(key) && extra.length < 4) extra.add(key);
    d['extra'] = extra;
    _write(toIso, d);
  }

  void removeExtra(String iso, String key) {
    final d = Map<String, dynamic>.from(log(iso));
    final extra = asList(d['extra']).map(asStr).toList()..remove(key);
    if (extra.isEmpty) {
      d.remove('extra');
    } else {
      d['extra'] = extra;
    }
    _write(iso, d);
  }

  void setResult(String key, double? value) {
    results[key] = value;
    resultUpdated[key] = nowIso();
    outbox.add('res:$key');
    _changed();
  }

  void _changed() {
    _save();
    notifyListeners();
    if (token != null) {
      _syncTimer?.cancel();
      _syncTimer = Timer(const Duration(seconds: 4), () => sync());
    }
  }

  // ---------------------------------------------------------------- settings (config)
  void setConfig(String section, Object? value) {
    custom[section] = value;
    customUpdated = nowIso();
    planPending = true;
    outbox.add('cfg');
    _changed();
  }

  void setProfileField(String key, Object? value) {
    final p = Map<String, dynamic>.from(asMap(custom['profile']));
    p[key] = value;
    setConfig('profile', p);
  }

  void setSectionField(String section, String key, Object? value) {
    final p = Map<String, dynamic>.from(asMap(custom[section] ?? config[section]));
    p[key] = value;
    setConfig(section, p);
  }

  void saveRace(Map<String, dynamic> race) {
    final rs = races;
    final i = rs.indexWhere((r) => r['id'] == race['id']);
    if (i >= 0) {
      rs[i] = race;
    } else {
      rs.add(race);
    }
    setConfig('races', rs);
  }

  void deleteRace(String id) => setConfig('races', races.where((r) => r['id'] != id).toList());

  void setDark(bool v) {
    darkMode = v;
    prefs.setBool('dark', v);
    notifyListeners();
  }

  // ---------------------------------------------------------------- reminders
  static const Map<String, bool> kNotifyDefaults = {
    'workouts': true, 'checkin': true, 'mobility': true, 'kegels': true, 'sleep': true, 'races': true,
    'meals': false, 'supps': false, 'water': false,
  };

  bool notifyOn(String key) => notify[key] is bool ? notify[key] as bool : (kNotifyDefaults[key] ?? false);
  bool get remindersAllowed => notify['allowed'] == true;

  void setNotify(String key, bool v) {
    notify[key] = v;
    _save();
    notifyListeners();
    refreshReminders();
  }

  String reminderTime(String key) {
    final mine = asStr(asMap(notify['times'])[key]);
    return mine.isNotEmpty ? mine : asStr(asMap(effective('reminders'))[key]);
  }

  void setReminderTime(String key, String hhmm) {
    final t = Map<String, dynamic>.from(asMap(notify['times']));
    t[key] = hhmm;
    notify['times'] = t;
    _save();
    notifyListeners();
    refreshReminders();
  }

  /// Ask for permission (first time) and switch reminders on.
  Future<bool> enableReminders() async {
    final ok = await Notifier.requestPermission();
    notify['allowed'] = ok;
    notify['asked'] = true;
    await _save();
    await refreshReminders();
    notifyListeners();
    return ok;
  }

  Future<void> disableReminders() async {
    notify['allowed'] = false;
    notify['asked'] = true;
    await _save();
    await Notifier.cancelAll();
    notifyListeners();
  }

  DateTime? _at(String iso, String hhmm, {int addMin = 0}) {
    final p = hhmm.split(':');
    if (p.length != 2) return null;
    final h = int.tryParse(p[0]), m = int.tryParse(p[1]);
    if (h == null || m == null) return null;
    final d = dateOf(iso);
    return DateTime(d.year, d.month, d.day, h, m).add(Duration(minutes: addMin));
  }

  String _short(String t, [int n = 110]) => t.length <= n ? t : '${t.substring(0, n - 1)}...';

  /// Every reminder for the next 14 days, from the plan and your switches.
  List<Reminder> buildReminders() {
    final out = <Reminder>[];
    void add(String iso, String hhmm, String title, String body, {int addMin = 0}) {
      final at = _at(iso, hhmm, addMin: addMin);
      if (at != null) out.add(Reminder(at, title, body));
    }

    final breakTime = asStr(asMap(effective('fasting'))['break_time']).isEmpty ? '18:50' : asStr(asMap(effective('fasting'))['break_time']);
    final today = todayIso();
    for (var i = 0; i < 14; i++) {
      final iso = addDays(today, i);
      if (!hasDay(iso)) continue;
      final pd = planDay(iso);
      final fasting = pd['fasting'] == true;
      final am = session(pd['am'] == null ? null : asStr(pd['am']));
      final pm = session(pd['pm'] == null ? null : asStr(pd['pm']));
      if (notifyOn('checkin')) add(iso, reminderTime('checkin'), 'Morning check-in', 'Sleep, soreness, energy${pd['knee_care'] == true ? ', knee' : ''}: 30 seconds before you train.');
      if (notifyOn('workouts')) {
        if (am.isNotEmpty) add(iso, reminderTime('workout_am'), asStr(am['name']), _short(asStr(am['summary'])));
        if (pm.isNotEmpty) {
          if (fasting) {
            add(iso, breakTime, asStr(pm['name']), _short(asStr(pm['summary'])), addMin: 40);
          } else {
            add(iso, reminderTime('workout_pm'), asStr(pm['name']), _short(asStr(pm['summary'])));
          }
        }
      }
      if (notifyOn('mobility')) {
        add(iso, reminderTime('mobility'), pd['knee_care'] == true ? 'Mobility and knee care: 15 min' : 'Morning mobility: 7 min',
            pd['knee_care'] == true ? 'Morning routine, then straight-leg raises, side-lying leg raises, bridges and stretches.' : 'Hips, ankles, spine and shoulders.');
      }
      final strength = am['strength'] == true || pm['strength'] == true;
      if (notifyOn('kegels') && !strength) add(iso, reminderTime('kegels'), 'Kegels: 5 minutes', 'Slow holds, quick squeezes, relaxation breathing. Relax fully between squeezes.');
      if (notifyOn('meals')) {
        for (final m in mealsFor(iso)) {
          add(iso, asStr(m['time']), '${asStr(m['meal'])} time', _short(asList(m['items']).map(asMap).map((x) => '${asStr(x['grams'])} g ${asStr(x['food'])}').join(', ')), addMin: -10);
        }
      }
      if (notifyOn('supps')) add(iso, fasting ? breakTime : reminderTime('supplements'), 'Supplements', 'Tick what you take in Nutrition.', addMin: fasting ? 80 : 0);
      if (notifyOn('water')) {
        if (fasting) {
          add(iso, breakTime, 'Break your fast', 'Water first: 500 ml slowly, then dates and a light meal.');
        } else {
          final every = (asNum(asMap(effective('reminders'))['water_every_h']) ?? 2.0).round().clamp(1, 6).toInt();
          for (var h = 9; h <= 17; h += every) {
            add(iso, '${two(h)}:00', 'Water', 'A glass now. Target ${fmtNum(asNum(pd['water_l']))} L today.');
          }
        }
      }
      if (notifyOn('sleep')) {
        final tomorrow = addDays(iso, 1);
        final next = hasDay(tomorrow) ? session(planDay(tomorrow)['am'] == null ? null : asStr(planDay(tomorrow)['am'])) : <String, dynamic>{};
        add(iso, reminderTime('sleep'), 'Wind down: lights out by 22:00', next.isEmpty ? 'Sleep is training too: 7 to 9 hours.' : 'Tomorrow morning: ${asStr(next['name'])}. Lay out your kit.');
      }
    }
    if (notifyOn('races')) {
      for (final r in races) {
        final date = asStr(r['date']);
        if (date.isEmpty || asStr(r['priority']) == 'C') continue;
        for (final before in [7, 3, 1]) {
          final t = asNum(r['target_min']);
          add(addDays(date, -before), '09:00', '${asStr(r['name'])} in $before day${before == 1 ? '' : 's'}',
              t == null ? 'Check the race plan in Training.' : 'Target: under ${(t / 60).floor()} h ${two((t % 60).round())}. Check the race plan in Training.');
        }
      }
    }
    return out;
  }

  Future<void> refreshReminders() async {
    if (!remindersAllowed) return;
    await Notifier.schedule(buildReminders());
    notifyListeners();
  }

  // ---------------------------------------------------------------- running numbers for the race target card
  /// Every run known to the app: logged runs first, then watch imports for days without a log.
  List<Map<String, dynamic>> allRuns() {
    final out = <Map<String, dynamic>>[];
    final seen = <String>{};
    days.forEach((iso, l) {
      final km = asNum(l['run_km']);
      if (km != null && km > 0) {
        final min = asNum(l['run_min']);
        out.add({'date': iso, 'km': km, 'pace': (min != null && min > 0) ? min / km : null});
        seen.add(iso);
      }
    });
    for (final a in activitiesOf('run')) {
      final km = asNum(a['distance_km']), s = asNum(a['duration_s']);
      if (km == null || km <= 0 || seen.contains(asStr(a['date']))) continue;
      out.add({'date': asStr(a['date']), 'km': km, 'pace': s == null ? null : s / 60 / km});
    }
    out.sort((a, b) => asStr(a['date']).compareTo(asStr(b['date'])));
    return out;
  }

  Map<String, dynamic>? get longestRun {
    Map<String, dynamic>? best;
    for (final r in allRuns()) {
      if (best == null || (r['km'] as double) > (best['km'] as double)) best = r;
    }
    return best;
  }

  /// Knee score for today, 0 (nothing) to 10. A score of 3 or more also counts as pain for the coach.
  void setKnee(String iso, double? score) {
    final l = log(iso);
    final areas = asList(l['pain_areas']).map(asStr).toSet();
    if (score != null && score >= 3) {
      areas.add('knee');
    } else {
      areas.remove('knee');
    }
    setFields(iso, {
      'knee_pain': score,
      'pain_today': areas.isNotEmpty ? true : null,
      'pain_areas': areas.isEmpty ? null : areas.toList(),
    });
  }

  // ---------------------------------------------------------------- activities
  int importGarmin(String csv) {
    final acts = parseGarmin(csv);
    var added = 0;
    for (final a in acts) {
      final id = asStr(a['id']);
      if (!activities.containsKey(id)) added++;
      activities[id] = a;
      activityOutbox.add(id);
    }
    _changed();
    return added;
  }

  List<Map<String, dynamic>> activitiesOf(String type) =>
      activities.values.where((a) => a['type'] == type).toList()..sort((a, b) => asStr(a['start']).compareTo(asStr(b['start'])));

  // ---------------------------------------------------------------- calculations
  List<Map<String, dynamic>> get weeks => weekly(plan, days);

  List<Map<String, dynamic>> goals() {
    final ws = weeks;
    final t = todayIso();
    return asList(plan['goals']).map((g) => goalStatus(plan, asMap(g), days, results, ws, t)).toList();
  }

  List<Map<String, dynamic>> minis({String? goalId}) {
    final t = todayIso();
    return asList(plan['mini_goals'])
        .map(asMap)
        .where((m) => goalId == null || m['goal'] == goalId)
        .map((m) => miniStatus(plan, m, days, results, t))
        .toList();
  }

  Map<String, dynamic> readiness(String iso) => coach.readiness(days, iso);
  List<String> pain(String iso) => coach.persistentPain(days, iso);
  int streak(String iso) => coach.streak(planDays, days, iso);

  /// Planned sessions for a day with the coach's adjustment, plus any rescheduled sessions.
  List<Map<String, dynamic>> todaySessions(String iso) {
    final pd = planDay(iso);
    final l = log(iso);
    final r = readiness(iso);
    final p = pain(iso);
    final fastToggle = l['fasting'] == true && pd['fasting'] != true;
    final out = <Map<String, dynamic>>[];
    for (final slot in ['am', 'pm']) {
      final key = pd[slot];
      if (key == null) continue;
      final s = session(asStr(key));
      out.add({
        'slot': slot,
        'session': s,
        'when': asStr(pd['when_$slot']),
        'adjust': coach.adjust(s, asStr(r['level']), p, fastingToday: fastToggle),
        'done': l['${slot}_done'] == true,
        'skipped': l['skip_$slot'] == true,
      });
    }
    for (final k in asList(l['extra']).map(asStr)) {
      final s = session(k);
      if (s.isEmpty) continue;
      out.add({'slot': 'extra', 'session': s, 'when': 'Moved here', 'adjust': coach.adjust(s, asStr(r['level']), p), 'done': isDone(iso, '$k:done'), 'skipped': false});
    }
    return out;
  }

  Map<String, dynamic> progressionFor(String exercise, String reps, String beforeIso) {
    final hist = <Map<String, dynamic>>[];
    final keys = days.keys.where((k) => k.compareTo(beforeIso) < 0).toList()..sort();
    for (final iso in keys) {
      asMap(days[iso]!['sets']).forEach((id, lst) {
        final sets = asList(lst).map(asMap).toList();
        var name = sets.isNotEmpty ? asStr(sets.first['ex']) : '';
        if (name.isEmpty) {
          final parts = id.split(':');
          final rows = asList(session(parts.first)['rows']);
          final i = parts.length > 1 ? int.tryParse(parts[1]) : null;
          if (i != null && i < rows.length) name = asStr(asMap(rows[i])['ex']);
        }
        if (name == exercise) hist.add({'date': iso, 'sets': sets});
      });
    }
    final blocked = coach.loadsArea(exercise, pain(beforeIso)).isNotEmpty;
    return coach.progression(hist, reps, painBlocked: blocked);
  }

  // ---------------------------------------------------------------- server
  Api get _api => Api(serverUrl, token: token);

  Future<String?> signIn(String url, String mail, String password, {bool register = false}) async {
    serverUrl = url.trim().isEmpty ? kDefaultServer : url.trim();
    await prefs.setString('serverUrl', serverUrl);
    try {
      final r = await Api(serverUrl).login(mail.trim(), password, register: register);
      token = asStr(r['token']);
      email = asStr(r['email']);
      await prefs.setString('token', token!);
      await prefs.setString('email', email!);
      lastSync = null;
      await prefs.remove('lastSync');
      for (final k in days.keys) {
        outbox.add('day:$k');
      }
      for (final k in results.keys) {
        outbox.add('res:$k');
      }
      activityOutbox.addAll(activities.keys);
      if (custom.isNotEmpty) outbox.add('cfg');
      await _save();
      notifyListeners();
      await sync();
      return null;
    } on ApiException catch (e) {
      return e.message;
    }
  }

  Future<void> signOut() async {
    token = null;
    email = null;
    lastSync = null;
    await prefs.remove('token');
    await prefs.remove('email');
    await prefs.remove('lastSync');
    syncNote = 'Signed out. Your data stays on this phone.';
    notifyListeners();
  }

  void _setPlan(Map<String, dynamic> p, String text) {
    plan = p;
    _index();
    prefs.setString('plan_cache', text);
  }

  Future<void> sync() async {
    if (token == null || syncing) return;
    syncing = true;
    syncNote = 'Syncing...';
    notifyListeners();
    final api = _api;
    try {
      if (outbox.contains('cfg')) {
        await api.putConfig(custom, customUpdated ?? nowIso());
        outbox.remove('cfg');
      }
      for (final item in outbox.toList()) {
        if (item.startsWith('day:')) {
          final iso = item.substring(4);
          await api.putDay(iso, log(iso), dayUpdated[iso] ?? nowIso());
        } else if (item.startsWith('res:')) {
          final key = item.substring(4);
          await api.putResult(key, results[key], resultUpdated[key] ?? nowIso());
        }
        outbox.remove(item);
      }
      if (activityOutbox.isNotEmpty) {
        final ids = activityOutbox.toList();
        for (var i = 0; i < ids.length; i += 200) {
          final chunk = ids.sublist(i, i + 200 > ids.length ? ids.length : i + 200);
          await api.putActivities(chunk.map((id) => activities[id]).whereType<Map<String, dynamic>>().toList());
        }
        activityOutbox.clear();
      }
      final r = await api.sync(lastSync);
      for (final raw in asList(r['days'])) {
        final d = asMap(raw);
        final iso = asStr(d['date']);
        final theirs = asStr(d['updated_at']);
        final mine = dayUpdated[iso];
        if (mine == null || DateTime.parse(theirs).isAfter(DateTime.parse(mine))) {
          days[iso] = Map<String, dynamic>.from(asMap(d['data']));
          dayUpdated[iso] = theirs;
        }
      }
      for (final raw in asList(r['results'])) {
        final d = asMap(raw);
        final key = asStr(d['key']);
        final theirs = asStr(d['updated_at']);
        final mine = resultUpdated[key];
        if (mine == null || DateTime.parse(theirs).isAfter(DateTime.parse(mine))) {
          results[key] = asNum(d['value']);
          resultUpdated[key] = theirs;
        }
      }
      for (final raw in asList(r['activities'])) {
        final a = Map<String, dynamic>.from(asMap(raw));
        activities[asStr(a['id'])] = a;
      }
      final cfg = asMap(r['config']);
      if (cfg.isNotEmpty) {
        final theirs = asStr(cfg['updated_at']);
        if (customUpdated == null || DateTime.parse(theirs).isAfter(DateTime.parse(customUpdated!))) {
          custom = Map<String, dynamic>.from(asMap(cfg['config']));
          customUpdated = theirs;
        }
      }
      if (asStr(r['plan_version']).isNotEmpty && r['plan_version'] != plan['version']) {
        final res = await api.plan();
        _setPlan(asMap(jsonDecode(res)), res);
        refreshReminders();
      }
      planPending = false;
      lastSync = asStr(r['server_time']);
      await prefs.setString('lastSync', lastSync!);
      syncNote = 'Synced ${prettyDate(todayIso())} at ${_clock()} as $email.';
    } on ApiException catch (e) {
      if (e.status == 401) {
        syncNote = '${e.message} (Profile > Server and sync).';
      } else if (e.status == 422) {
        syncNote = 'The server rejected a change: ${e.message}';
        outbox.remove('cfg');
      } else {
        syncNote = 'Not synced: ${e.message} Your changes are kept and will be sent later.';
      }
    } catch (e) {
      syncNote = 'Not synced: $e';
    }
    syncing = false;
    await _save();
    notifyListeners();
  }

  String _clock() {
    final n = DateTime.now();
    return '${two(n.hour)}:${two(n.minute)}';
  }

  Future<String> exportCsv() async {
    final cols = ['date', 'week', 'planned_am', 'planned_pm', 'target_weight', 'weight', 'waist', 'sleep_h', 'sleep_q', 'soreness', 'energy',
        'stress', 'rhr', 'am_done', 'pm_done', 'run_km', 'swim_m', 'swim_cont_m', 'swolf', 'bike_km', 'kcal', 'protein', 'carbs', 'fat',
        'water', 'supps', 'kegels', 'fasting', 'notes'];
    final sb = StringBuffer(cols.join(','));
    final keys = days.keys.toList()..sort();
    for (final iso in keys) {
      final d = days[iso]!;
      final pd = hasDay(iso) ? planDay(iso) : <String, dynamic>{};
      final planned = asMap(d['planned']);
      final row = <String>[iso, asStr(pd['week']), asStr(planned['am']), asStr(planned['pm']), asStr(pd['target_weight'])];
      for (final c in cols.sublist(5)) {
        var v = asStr(d[c]).replaceAll('"', "'");
        if (v.isNotEmpty && '=+-@'.contains(v[0])) v = "'$v";
        row.add(v.contains(',') || v.contains('\n') ? '"$v"' : v);
      }
      sb.write('\n${row.join(',')}');
    }
    return sb.toString();
  }

  Future<void> resetAll() async {
    days.clear();
    dayUpdated.clear();
    results.clear();
    resultUpdated.clear();
    outbox.clear();
    activities.clear();
    activityOutbox.clear();
    await _save();
    notifyListeners();
  }
}
