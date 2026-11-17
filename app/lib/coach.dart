// Deterministic daily coach. Mirrors server/app/engine/coach.py so the phone gives the same answer offline.
// Rules: never change the plan on one number alone; only ever make a session easier; persistent pain stops
// progression; strength progression changes one variable at a time.

import 'logic.dart' show Logs;
import 'util.dart';

const Map<String, List<String>> kPainAreas = {
  'knee': ['squat', 'lunge', 'split squat', 'step-up', 'wall sit', 'thruster', 'run'],
  'shin': ['run', 'calf', 'jump', 'burpee'],
  'calf or achilles': ['calf', 'run', 'jump', 'burpee'],
  'foot': ['run', 'calf', 'jump', 'burpee'],
  'hip': ['squat', 'lunge', 'deadlift', 'bridge', 'thrust', 'swing', 'run'],
  'hamstring': ['deadlift', 'good morning', 'nordic', 'hamstring', 'bridge', 'swing', 'run'],
  'lower back': ['deadlift', 'good morning', 'row', 'swing', 'carry', 'thruster', 'squat'],
  'shoulder': ['press', 'push-up', 'raise', 'dip', 'row', 'swim', 'pike', 'y-t-w', 'thruster'],
  'elbow or wrist': ['curl', 'push-up', 'dip', 'extension', 'row'],
  'other': [],
};

double _median(List<double> v) {
  final s = [...v]..sort();
  final n = s.length;
  return n.isOdd ? s[n ~/ 2] : (s[n ~/ 2 - 1] + s[n ~/ 2]) / 2;
}

String _g(double v) => fmtNum(v, dp: 1);

Map<String, dynamic> readiness(Logs days, String iso) {
  final log = days[iso] ?? <String, dynamic>{};
  final past = days.entries.where((e) {
    final age = daysBetween(e.key, iso);
    return age > 0 && age < 15;
  }).map((e) => e.value).toList();
  final rhrs = past.map((d) => asNum(d['rhr'])).whereType<double>().toList();
  final hrvs = past.map((d) => asNum(d['hrv'])).whereType<double>().toList();
  final signals = <List<Object>>[];
  final sh = asNum(log['sleep_h']), sq = asNum(log['sleep_q']), so = asNum(log['soreness']), en = asNum(log['energy']);
  final stv = asNum(log['stress']), rhr = asNum(log['rhr']), hrv = asNum(log['hrv']);
  if (sh != null) {
    if (sh < 6) {
      signals.add(['Short sleep (${_g(sh)} h)', 2]);
    } else if (sh < 7) {
      signals.add(['Sleep under 7 h (${_g(sh)} h)', 1]);
    }
  }
  if (sq != null && sq <= 2) signals.add(['Poor sleep quality', 1]);
  if (so != null) {
    if (so >= 4) {
      signals.add(['Heavy muscle soreness', 2]);
    } else if (so >= 3) {
      signals.add(['Moderate soreness', 1]);
    }
  }
  if (en != null && en <= 2) signals.add(['Low energy', 1]);
  if (stv != null && stv >= 4) signals.add(['High stress', 1]);
  if (rhr != null && rhrs.length >= 3) {
    final base = _median(rhrs);
    if (rhr >= base + 7) {
      signals.add(['Resting heart rate ${(rhr - base).round()} bpm above your normal', 2]);
    } else if (rhr >= base + 4) {
      signals.add(['Resting heart rate ${(rhr - base).round()} bpm above your normal', 1]);
    }
  }
  if (hrv != null && hrvs.length >= 3 && hrv <= _median(hrvs) * 0.85) signals.add(['HRV well below your normal', 1]);
  if (log['pain_today'] == true) signals.add(['Pain reported today', 2]);
  final pts = signals.fold<int>(0, (a, s) => a + (s[1] as int));
  final n = signals.length;
  final checked = ['sleep_h', 'sleep_q', 'soreness', 'energy', 'stress', 'rhr', 'hrv'].any((k) => log[k] != null);
  final level = (n >= 3 && pts >= 5) ? 'red' : ((n >= 2 && pts >= 3) ? 'amber' : 'green');
  var msg = {
    'green': checked ? 'Ready: train as planned.' : 'Do the morning check-in so the coach can adjust today if needed.',
    'amber': 'Take it easier today: the hard parts of today\'s sessions are reduced.',
    'red': 'Recovery day: today\'s demanding sessions are swapped for easy movement and mobility.',
  }[level]!;
  if (level == 'green' && n == 1) {
    msg = 'Mostly ready. One sign to watch (${(signals[0][0] as String).toLowerCase()}): train as planned but keep easy parts truly easy.';
  }
  return {
    'level': level,
    'score': checked ? (100 - pts * 12).clamp(0, 100) : null,
    'signals': signals.map((s) => s[0] as String).toList(),
    'message': msg,
    'checked_in': checked,
  };
}

List<String> persistentPain(Logs days, String iso) {
  final c7 = <String, int>{};
  final c14 = <String, int>{};
  days.forEach((k, d) {
    final age = daysBetween(k, iso);
    if (age < 0 || age >= 14) return;
    final areas = asList(d['pain_areas']).map(asStr).toSet();
    if ((asNum(d['knee_pain']) ?? 0.0) >= 3) areas.add('knee');
    for (final fb in ['am_fb', 'pm_fb']) {
      final f = asMap(d[fb]);
      if (f['pain'] == true && asStr(f['pain_area']).isNotEmpty) areas.add(asStr(f['pain_area']));
    }
    for (final a in areas) {
      c14[a] = (c14[a] ?? 0) + 1;
      if (age < 7) c7[a] = (c7[a] ?? 0) + 1;
    }
  });
  return c14.keys.where((a) => (c7[a] ?? 0) >= 2 || c14[a]! >= 3).toList()..sort();
}

List<String> loadsArea(String exercise, List<String> areas) {
  final e = exercise.toLowerCase();
  return areas.where((a) => (kPainAreas[a] ?? const <String>[]).any((w) => e.contains(w))).toList();
}

/// What to do with a planned session today. Only ever makes it easier.
Map<String, dynamic>? adjust(Map<String, dynamic> session, String level, List<String> pain, {bool fastingToday = false}) {
  if (session.isEmpty) return null;
  final meta = asMap(session['meta']);
  final disc = asStr(meta['discipline']);
  final code = asStr(session['code']);
  final hard = meta['hard'] == true;
  final out = <String, dynamic>{'key': session['key'], 'name': session['name'], 'action': 'as planned', 'note': ''};
  if (['FAST', 'REST', 'MOB', 'RACE'].contains(code)) return out;
  if (fastingToday) {
    out['action'] = 'swap';
    out['note'] = 'You marked today as a fasting day: only an easy walk and mobility after breaking the fast. No demanding session.';
    return out;
  }
  final runPain = pain.where((a) => (kPainAreas[a] ?? const <String>[]).contains('run')).toList();
  if (['run', 'brick', 'hyrox'].contains(disc) && runPain.isNotEmpty) {
    out['action'] = 'swap';
    out['note'] = 'Persistent ${runPain.join(', ')} pain: replace this run with an easy swim or a 30 min walk if pain-free, and book a physiotherapist or doctor assessment.';
    return out;
  }
  if (level == 'red' && (hard || ['run', 'strength', 'hyrox', 'brick', 'bike'].contains(disc))) {
    out['action'] = 'swap';
    out['note'] = 'Recovery day: 20 to 30 min easy walk or an easy swim, plus the mobility routine and kegels. The session is not made up later.';
  } else if (level == 'amber' && hard) {
    out['action'] = 'reduce';
    out['note'] = disc == 'strength'
        ? 'One set fewer on every exercise, same load, effort no more than 7 out of 10. Keep the kegel finisher.'
        : disc == 'swim'
            ? 'Swim the drills and an easy continuous swim; skip the faster repeats.'
            : 'Cut the main set by a third and keep the effort at 6 out of 10 or less (easy heart rate).';
  } else if (level == 'amber') {
    out['note'] = 'Keep it truly easy today.';
  }
  if (pain.isNotEmpty && disc == 'strength' && out['action'] == 'as planned') {
    out['note'] = '${asStr(out['note'])} Persistent ${pain.join(', ')} pain: do not add load to exercises that hurt; skip any that cause pain.'.trim();
  }
  return out;
}

List<int>? repRange(String reps) {
  final nums = RegExp(r'\d+').allMatches(reps).map((m) => int.parse(m.group(0)!)).toList();
  if (nums.isEmpty || reps.contains(' s') || reps.replaceAll('min', '').contains('m')) return null;
  return [nums[0], nums.length > 1 ? nums[1] : nums[0]];
}

/// history: logged sessions for one exercise, newest last: [{'date':..,'sets':[{'kg':..,'reps':..,'rpe':..}]}]
Map<String, dynamic> progression(List<Map<String, dynamic>> history, String reps, {bool painBlocked = false}) {
  final rr = repRange(reps);
  if (painBlocked) {
    return {'action': 'hold', 'text': 'Hold: you reported persistent pain in an area this exercise loads. Keep the load, skip it if it hurts, and get it assessed.'};
  }
  if (history.isEmpty) {
    return {'action': 'start', 'text': 'First time: choose a load where the last 2 reps feel hard but clean (effort 7 out of 10). Log it.'};
  }
  if (rr == null) return {'action': 'repeat', 'text': 'Timed or distance exercise: add 5 s (or a few metres) once every set feels controlled.'};
  final last = asList(history.last['sets']).map(asMap).where((s) => asNum(s['reps']) != null).toList();
  if (last.isEmpty) return {'action': 'repeat', 'text': 'Log reps for each set to get a suggestion.'};
  final lo = rr[0], hi = rr[1];
  final done = last.map((s) => asNum(s['reps'])!).toList();
  final rpes = last.map((s) => asNum(s['rpe'])).whereType<double>().toList();
  final kg = last.map((s) => asNum(s['kg']) ?? 0.0).fold<double>(0, (a, b) => b > a ? b : a);
  final avgRpe = rpes.isEmpty ? null : rpes.reduce((a, b) => a + b) / rpes.length;
  final minDone = done.reduce((a, b) => a < b ? a : b);
  if (minDone < lo || (avgRpe != null && avgRpe >= 9.5)) {
    final missedTwice = history.length >= 2 && asList(history[history.length - 2]['sets']).map(asMap).any((s) => (asNum(s['reps']) ?? 0.0) < lo);
    if (missedTwice && kg > 0) {
      final r = (kg * 0.9 * 2).round() / 2;
      return {'action': 'reduce', 'kg': r, 'text': 'Missed reps two sessions in a row: drop to ${fmtNum(r)} kg and rebuild.'};
    }
    return {'action': 'repeat', 'kg': kg, 'text': 'Repeat ${fmtNum(kg)} kg and aim for $lo to $hi clean reps on every set.'};
  }
  if (minDone >= hi && (avgRpe == null || avgRpe <= 8)) {
    if (kg > 0) {
      final inc = kg < 10 ? 1.0 : (kg < 40 ? 2.0 : 2.5);
      return {
        'action': 'add_load',
        'kg': kg + inc,
        'text': 'Every set hit $hi reps: add ${fmtNum(inc)} kg (to ${fmtNum(kg + inc)} kg) and start again at $lo reps. Do not change anything else.'
      };
    }
    return {'action': 'add_reps', 'text': 'Every set hit $hi reps with bodyweight: add 1 to 2 reps per set, OR move to the harder version. Not both.'};
  }
  return {'action': 'repeat', 'kg': kg, 'text': 'Same load (${fmtNum(kg)} kg). Add a rep where you can until every set reaches $hi.'};
}

String? runLoadWarning(Logs days, String iso) {
  double weekKm(int k) {
    final a = addDays(iso, -7 * (k + 1));
    var t = 0.0;
    days.forEach((d, log) {
      if (d.compareTo(a) > 0 && d.compareTo(addDays(a, 7)) <= 0) t += asNum(log['run_km']) ?? 0.0;
    });
    return t;
  }

  final now = weekKm(0);
  final avg = (weekKm(1) + weekKm(2) + weekKm(3)) / 3;
  if (avg >= 5 && now > avg * 1.3) {
    return 'Your running this week (${now.round()} km) is more than 30% above your recent average (${avg.round()} km). Keep the rest of the week easy.';
  }
  return null;
}

int streak(List<dynamic> planDays, Logs days, String iso) {
  var n = 0;
  final pds = planDays.map(asMap).where((d) => asStr(d['date']).compareTo(iso) <= 0).toList().reversed;
  for (final pd in pds) {
    if (pd['am'] == null && pd['pm'] == null) continue;
    final log = days[asStr(pd['date'])] ?? <String, dynamic>{};
    final done = (pd['am'] != null && log['am_done'] == true) || (pd['pm'] != null && log['pm_done'] == true);
    if (done) {
      n++;
    } else if (pd['date'] == iso) {
      continue;
    } else {
      break;
    }
  }
  return n;
}
