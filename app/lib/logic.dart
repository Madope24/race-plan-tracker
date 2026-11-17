// Goal, mini-goal and weekly-review calculations. Mirrors server/app/logic.py.
import 'util.dart';

typedef Logs = Map<String, Map<String, dynamic>>;

double? wavg(Logs days, String atIso) {
  final at = dateOf(atIso);
  final lo = at.subtract(const Duration(days: 7));
  final vals = <double>[];
  days.forEach((iso, d) {
    final w = asNum(d['weight']);
    final t = dateOf(iso);
    if (w != null && t.isAfter(lo) && !t.isAfter(at)) vals.add(w);
  });
  if (vals.isEmpty) return null;
  return round1(vals.reduce((a, b) => a + b) / vals.length);
}

String? lastWeighDate(Logs days) {
  String? best;
  days.forEach((iso, d) {
    if (asNum(d['weight']) != null && (best == null || iso.compareTo(best!) > 0)) best = iso;
  });
  return best;
}

double? currentWeight(Logs days) {
  final last = lastWeighDate(days);
  return last == null ? null : wavg(days, last);
}

double? maxOf(Logs days, String field, {String? upto}) {
  double? best;
  days.forEach((iso, d) {
    if (upto != null && iso.compareTo(upto) > 0) return;
    final v = asNum(d[field]);
    if (v != null && v > 0 && (best == null || v > best!)) best = v;
  });
  return best;
}

double? plannedWeight(Map<String, dynamic> plan, String iso) {
  for (final raw in asList(plan['days'])) {
    final d = asMap(raw);
    if (d['date'] == iso) return asNum(d['target_weight']);
  }
  return null;
}

List<Map<String, dynamic>> weekly(Map<String, dynamic> plan, Logs days) {
  final byWeek = <int, List<Map<String, dynamic>>>{};
  for (final raw in asList(plan['days'])) {
    final d = asMap(raw);
    final w = (d['week'] as num).toInt();
    byWeek.putIfAbsent(w, () => <Map<String, dynamic>>[]).add(d);
  }
  final keys = byWeek.keys.toList()..sort();
  final out = <Map<String, dynamic>>[];
  double? prevAvg;
  for (final w in keys) {
    final pds = byWeek[w]!;
    final weights = <double>[];
    final sleeps = <double>[];
    final kcals = <double>[];
    var planned = 0, done = 0, protHit = 0, protDays = 0;
    double run = 0, swim = 0, bike = 0, tgtSum = 0;
    for (final pd in pds) {
      final log = days[asStr(pd['date'])] ?? <String, dynamic>{};
      final hasAm = pd['am'] != null || pd['race'] != null;
      final hasPm = pd['pm'] != null;
      if (hasAm) planned++;
      if (hasPm) planned++;
      if (hasAm && log['am_done'] == true) done++;
      if (hasPm && log['pm_done'] == true) done++;
      final wt = asNum(log['weight']);
      if (wt != null) weights.add(wt);
      final sl = asNum(log['sleep_h']);
      if (sl != null) sleeps.add(sl);
      final kc = asNum(log['kcal']);
      if (kc != null) kcals.add(kc);
      final pr = asNum(log['protein']);
      if (pr != null) {
        protDays++;
        if (pr >= (asNum(pd['protein']) ?? 160)) protHit++;
      }
      run += asNum(log['run_km']) ?? 0;
      swim += asNum(log['swim_m']) ?? 0;
      bike += asNum(log['bike_km']) ?? 0;
      tgtSum += asNum(pd['target_weight']) ?? 0;
    }
    final avgW = weights.isEmpty ? null : round1(weights.reduce((a, b) => a + b) / weights.length);
    final tgt = round1(tgtSum / pds.length);
    final avgSleep = sleeps.isEmpty ? null : round1(sleeps.reduce((a, b) => a + b) / sleeps.length);
    final gap = avgW == null ? null : round1(avgW - tgt);
    final adherence = planned == 0 ? null : done / planned;
    final g = gap ?? 0;
    String status;
    if (avgW == null) {
      status = done == 0 ? '' : ((adherence ?? 0) >= 0.8 ? 'Training on track' : 'Train more consistently');
    } else if (g > 1) {
      status = 'BEHIND: apply the catch-up rule';
    } else if (g < -1.5) {
      status = 'TOO FAST: eat 150 kcal more';
    } else if ((adherence ?? 0) < 0.8) {
      status = 'Weight OK, adherence low';
    } else {
      status = 'ON TRACK';
    }
    out.add(<String, dynamic>{
      'week': w,
      'start': asStr(asMap(asList(plan['weeks'])[w - 1])['start']),
      'phase': asStr(pds.first['phase']),
      'avg_weight': avgW,
      'target_weight': tgt,
      'gap': gap,
      'change': (avgW != null && prevAvg != null) ? round1(avgW - prevAvg) : null,
      'planned': planned,
      'done': done,
      'adherence': adherence,
      'run_km': round1(run),
      'swim_m': swim.roundToDouble(),
      'bike_km': round1(bike),
      'avg_sleep': avgSleep,
      'sleep_ok': avgSleep == null ? null : avgSleep >= 7.5,
      'protein_hit': protHit,
      'protein_days': protDays,
      'avg_kcal': kcals.isEmpty ? null : (kcals.reduce((a, b) => a + b) / kcals.length).roundToDouble(),
      'status': status,
    });
    if (avgW != null) prevAvg = avgW;
  }
  return out;
}

double? _goalCurrent(Map<String, dynamic> g, Logs days, Map<String, double?> results, List<Map<String, dynamic>> weeks) {
  final auto = asStr(g['auto']);
  final manual = results['goal:${g['id']}'];
  switch (auto) {
    case 'race':
      return manual;
    case 'wavg':
      return currentWeight(days);
    case 'maxrun':
      return manual ?? maxOf(days, 'run_km');
    case 'maxswim':
      return maxOf(days, 'swim_cont_m');
    case 'maxbike':
      return maxOf(days, 'bike_km');
    case 'sleep':
      {
        final ws = weeks.where((w) => w['avg_sleep'] != null).toList();
        if (ws.isEmpty) return null;
        return ws.where((w) => w['sleep_ok'] == true).length / ws.length;
      }
    case 'protein':
      {
        var tot = 0;
        var hit = 0;
        for (final w in weeks) {
          tot += (w['protein_days'] as int);
          hit += (w['protein_hit'] as int);
        }
        return tot == 0 ? null : hit / tot;
      }
    default:
      return manual;
  }
}

double? _goalBaseline(Map<String, dynamic> g, Map<String, double?> results) {
  final b = asNum(g['baseline']);
  if (b != null) return b;
  if (g['id'] == 'Goal 6') return results['base:swim'];
  if (g['id'] == 'Goal 8') return results['base:pushups'];
  return null;
}

Map<String, dynamic> goalStatus(Map<String, dynamic> plan, Map<String, dynamic> g, Logs days, Map<String, double?> results,
    List<Map<String, dynamic>> weeks, String today) {
  final cur = _goalCurrent(g, days, results, weeks);
  final base = _goalBaseline(g, results);
  final tgt = asNum(g['target']) ?? 0;
  final lower = g['better'] == 'Lower';
  final manual = results['goal:${g['id']}'];
  bool met;
  double? prog;
  double? longest;
  final isRace = g['auto'] == 'race';
  if (isRace) {
    longest = maxOf(days, 'run_km');
    met = manual != null && manual <= tgt;
    if (manual != null) {
      prog = met ? 1.0 : tgt / manual;
    } else {
      final dist = asNum(g['distance_km']) ?? 10;
      prog = longest == null ? null : (longest / dist).clamp(0.0, 1.0).toDouble();
    }
  } else {
    met = cur != null && (lower ? cur <= tgt : cur >= tgt);
    if (cur == null) {
      prog = null;
    } else if (base != null && base != tgt) {
      final raw = lower ? (base - cur) / (base - tgt) : (cur - base) / (tgt - base);
      prog = raw.clamp(0.0, 1.0).toDouble();
    } else if (lower) {
      prog = cur <= tgt ? 1.0 : tgt / cur;
    } else {
      prog = tgt == 0 ? null : (cur / tgt).clamp(0.0, 1.0).toDouble();
    }
  }
  final deadline = asStr(g['deadline']);
  String status;
  if (met) {
    status = 'Achieved';
  } else if (today.compareTo(deadline) > 0) {
    status = cur == null ? 'Log the result' : 'Missed';
  } else if (isRace && manual == null) {
    status = longest != null ? 'In progress' : 'Not started';
  } else if (cur == null) {
    status = 'Not started';
  } else if (g['auto'] == 'wavg') {
    final last = lastWeighDate(days);
    final pw = last == null ? null : plannedWeight(plan, last);
    status = (pw == null || cur <= pw + 0.5) ? 'On track' : 'Behind';
  } else {
    status = 'In progress';
  }
  final left = daysBetween(today, deadline);
  return <String, dynamic>{
    'id': g['id'],
    'name': g['name'],
    'current': cur,
    'baseline': base,
    'target': tgt,
    'progress': prog,
    'status': status,
    'days_left': left < 0 ? 0 : left,
    'longest_run_km': longest,
  };
}

double? miniTarget(Map<String, dynamic> plan, Map<String, dynamic> m, Map<String, double?> results) {
  final rule = asMap(m['rule']);
  if (rule.isEmpty) return asNum(m['target']);
  final r = asStr(rule['rule']);
  if (r == 'weight_line') {
    final t = asMap(plan['targets']);
    final sw = asNum(t['start_weight'])!;
    final gw = asNum(t['goal_weight'])!;
    final span = daysBetween(asStr(t['start_date']), asStr(t['goal_date']));
    final el = daysBetween(asStr(t['start_date']), asStr(m['due']));
    return round1(sw - (sw - gw) * el / span);
  }
  final b = results['base:${rule['base']}'];
  if (r == 'baseline_add') return b == null ? null : b + (asNum(rule['add']) ?? 0);
  if (r == 'double_or_30') return b == null ? 30 : (b < 15 ? b * 2 : 30);
  return asNum(m['target']);
}

Map<String, dynamic> miniStatus(Map<String, dynamic> plan, Map<String, dynamic> m, Logs days, Map<String, double?> results, String today) {
  final due = asStr(m['due']);
  final manual = results['mini:${m['id']}'];
  double? auto;
  switch (asStr(m['auto'])) {
    case 'wavg':
      auto = wavg(days, due);
      break;
    case 'maxrun':
      auto = maxOf(days, 'run_km', upto: due);
      break;
    case 'maxswim':
      auto = maxOf(days, 'swim_cont_m', upto: due);
      break;
    case 'maxbike':
      auto = maxOf(days, 'bike_km', upto: due);
      break;
  }
  final actual = manual ?? auto;
  final tgt = miniTarget(plan, m, results);
  final lower = m['better'] == 'Lower';
  final left = daysBetween(today, due);
  String status;
  if (actual == null) {
    status = left < 0 ? 'Overdue: log it' : (left <= 7 ? 'Due this week' : 'Upcoming');
  } else if (tgt == null) {
    status = 'Logged';
  } else if (lower ? actual <= tgt : actual >= tgt) {
    status = 'Hit';
  } else {
    status = left < 0 ? 'Missed' : 'In progress';
  }
  return <String, dynamic>{
    'id': m['id'],
    'goal': m['goal'],
    'due': due,
    'text': m['text'],
    'unit': m['unit'],
    'target': tgt,
    'from_log': auto,
    'result': manual,
    'actual': actual,
    'status': status,
    'days_left': left < 0 ? 0 : left,
  };
}
