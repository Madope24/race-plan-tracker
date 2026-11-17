import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'coach.dart' as coach;
import 'goals_screen.dart';
import 'logic.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

/// Progress: running, swimming, cycling, strength, body weight, consistency and recovery, from your logs and imported activities.
class ProgressScreen extends StatelessWidget {
  final AppState st;
  const ProgressScreen({super.key, required this.st});

  /// Per-day value: the log wins, otherwise the imported activities for that date.
  double _day(String iso, String logKey, String actType, String actKey, {double factor = 1}) {
    final v = asNum(st.log(iso)[logKey]);
    if (v != null) return v;
    var t = 0.0;
    for (final a in st.activities.values) {
      if (a['type'] == actType && a['date'] == iso) t += (asNum(a[actKey]) ?? 0.0) * factor;
    }
    return t;
  }

  @override
  Widget build(BuildContext context) {
    final today = todayIso();
    final allWeeks = asList(st.plan['weeks']).map(asMap).where((w) => asStr(w['start']).compareTo(today) <= 0).toList();
    final weeks = allWeeks.length > 16 ? allWeeks.sublist(allWeeks.length - 16) : allWeeks;
    final labels = weeks.map((w) => 'W${asStr(w['week'])}').toList();
    List<double> perWeek(double Function(String) f) => [
          for (final w in weeks) [for (var i = 0; i < 7; i++) addDays(asStr(w['start']), i)].fold<double>(0, (a, d) => a + f(d)),
        ];
    final runKm = perWeek((d) => _day(d, 'run_km', 'run', 'distance_km'));
    final swimM = perWeek((d) => _day(d, 'swim_m', 'swim', 'distance_m'));
    final bikeKm = perWeek((d) => _day(d, 'bike_km', 'bike', 'distance_km'));
    final review = {for (final w in st.weeks) asStr(w['week']): w};
    final adherence = [for (final w in weeks) ((review[asStr(w['week'])]?['adherence'] as double?) ?? 0.0) * 100];
    final weight = [for (final w in weeks) review[asStr(w['week'])]?['avg_weight'] as double?];
    final target = [for (final w in weeks) review[asStr(w['week'])]?['target_weight'] as double?];
    final sleep = [for (final w in weeks) review[asStr(w['week'])]?['avg_sleep'] as double?];

    // runs: pace and longest
    final runs = <Map<String, Object>>[];
    for (final a in st.activitiesOf('run')) {
      final km = asNum(a['distance_km']);
      final s = asNum(a['duration_s']);
      if (km != null && km > 0 && s != null) runs.add({'date': asStr(a['date']), 'km': km, 'pace': s / 60 / km});
    }
    st.days.forEach((iso, l) {
      final km = asNum(l['run_km']), m = asNum(l['run_min']);
      if (km != null && km > 0 && m != null && !runs.any((r) => r['date'] == iso)) runs.add({'date': iso, 'km': km, 'pace': m / km});
    });
    runs.sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));
    final longestLog = maxOf(st.days, 'run_km') ?? 0.0;
    final longestAct = st.activitiesOf('run').fold<double>(0, (a, x) => math.max(a, asNum(x['distance_km']) ?? 0.0));
    final longest = math.max(longestLog, longestAct);

    // swims: continuous record, SWOLF
    final cont = maxOf(st.days, 'swim_cont_m');
    final swolf = <Map<String, Object>>[];
    for (final a in st.activitiesOf('swim')) {
      final s = asNum(a['swolf']);
      if (s != null) swolf.add({'date': asStr(a['date']), 'v': s});
    }
    st.days.forEach((iso, l) {
      final s = asNum(l['swolf']);
      if (s != null && !swolf.any((x) => x['date'] == iso)) swolf.add({'date': iso, 'v': s});
    });
    swolf.sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));

    // strength: best set per exercise per day
    final byEx = <String, Map<String, double>>{};
    st.days.forEach((iso, l) {
      asMap(l['sets']).forEach((id, lst) {
        for (final s in asList(lst).map(asMap)) {
          final ex = asStr(s['ex']);
          if (ex.isEmpty) continue;
          final kg = asNum(s['kg']) ?? 0.0, reps = asNum(s['reps']) ?? 0.0;
          final score = kg > 0 ? kg * (1 + reps / 30) : reps;    // estimated 1-rep max (Epley), or reps for bodyweight
          final m = byEx.putIfAbsent(ex, () => <String, double>{});
          m[iso] = math.max(m[iso] ?? 0.0, score);
        }
      });
    });
    final topEx = byEx.keys.toList()..sort((a, b) => byEx[b]!.length.compareTo(byEx[a]!.length));

    // recovery: readiness over the last 28 days
    final last28 = [for (var i = 27; i >= 0; i--) addDays(today, -i)];
    final ready = [for (final d in last28) asNum(coach.readiness(st.days, d)['score'])];

    final races = st.races.where((r) => asStr(r['date']).isNotEmpty).toList()..sort((a, b) => asStr(a['date']).compareTo(asStr(b['date'])));
    final cur = currentWeight(st.days);
    final t = asMap(st.plan['targets']);
    return ListView(padding: const EdgeInsets.only(bottom: 28), children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(14, 6, 14, 0),
        child: TileRow([
          StatTile('Longest run', '${fmtNum(longest)} km', icon: Icons.directions_run, color: C.accent),
          StatTile('Non-stop swim', cont == null ? '-' : '${fmtNum(cont, dp: 0)} m', icon: Icons.pool, color: C.swim),
          StatTile('Weight', cur == null ? '-' : '${fmtNum(cur)} kg', sub: 'goal ${fmtNum(asNum(t['goal_weight']))}', icon: Icons.monitor_weight, color: C.teal),
        ]),
      ),
      Section(title: 'Goals', subtitle: 'SMART goals and mini goals', trailing: Icon(Icons.chevron_right, color: C.mut), children: [
        for (final g in st.goals().take(4))
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Expanded(child: Text(asStr(g['name']), style: TextStyle(color: C.text, fontSize: 13.5))),
                Pill(asStr(g['status']), color: statusColor(asStr(g['status']))),
              ]),
              const SizedBox(height: 4),
              Bar(g['progress'] as double?, color: C.teal),
            ]),
          ),
        FilledButton.tonal(
          onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(
              builder: (_) => Scaffold(appBar: AppBar(title: const Text('Goals')), body: ListenableBuilder(listenable: st, builder: (_, __) => GoalsScreen(st: st))))),
          child: const Text('All goals and mini goals'),
        ),
      ]),
      Section(title: 'Race countdown', children: [
        for (final r in races)
          KV(asStr(r['name']),
              '${math.max(0, daysBetween(today, asStr(r['date'])))} days · ${prettyDate(asStr(r['date']), year: true)}${asStr(r['priority']) == 'C' ? ' (optional)' : ''}'),
      ]),
      Section(title: 'Running distance per week', children: [BarChart(values: runKm, labels: labels, unit: ' km', color: C.accent)]),
      Section(title: 'Average running pace', subtitle: 'Minutes per km, lower is faster. Walk breaks included.', children: [
        LineChart(values: runs.map((r) => r['pace'] as double).toList(), labels: runs.map((r) => prettyDate(r['date'] as String).substring(4)).toList(),
            color: C.accent, invert: true, fmt: (v) => fmtNum(v)),
      ]),
      Section(title: 'Swimming distance per week', children: [BarChart(values: swimM, labels: labels, unit: ' m', color: C.swim)]),
      Section(title: 'SWOLF', subtitle: 'Time plus strokes per length: lower means more efficient.', children: [
        LineChart(values: swolf.map((x) => x['v'] as double).toList(), labels: swolf.map((x) => prettyDate(x['date'] as String).substring(4)).toList(), color: C.swim, invert: true),
      ]),
      Section(title: 'Cycling distance per week', children: [BarChart(values: bikeKm, labels: labels, unit: ' km', color: C.bike)]),
      Section(title: 'Strength progression', subtitle: 'Estimated 1-rep max from your best set each session (reps for bodyweight exercises).', children: [
        if (topEx.isEmpty) Text('Log sets in a strength workout to see progress.', style: TextStyle(color: C.mut)),
        for (final ex in topEx.take(4)) ...[
          Text(ex, style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
          LineChart(
            values: (byEx[ex]!.keys.toList()..sort()).map((d) => byEx[ex]![d]).toList(),
            labels: (byEx[ex]!.keys.toList()..sort()).map((d) => prettyDate(d).substring(4)).toList(),
            color: C.teal,
            height: 120,
          ),
          const SizedBox(height: 8),
        ],
      ]),
      Section(title: 'Body weight', subtitle: 'Weekly average (orange) against the target line (grey)', children: [
        LineChart(values: weight, target: target, labels: labels, color: C.accent),
      ]),
      Section(title: 'Training consistency', subtitle: 'Planned sessions done each week (%)', children: [BarChart(values: adherence, labels: labels, unit: '%', color: C.ok)]),
      Section(title: 'Recovery', subtitle: 'Average sleep per week, and readiness over the last 28 days', children: [
        LineChart(values: sleep, labels: labels, color: C.swim, height: 120),
        const SizedBox(height: 10),
        LineChart(values: ready, labels: last28.map((d) => prettyDate(d).substring(4)).toList(), color: C.ok, height: 120),
      ]),
      Section(title: 'Weekly review', subtitle: asStr(st.plan['weekly_rule']), children: [
        for (final w in st.weeks.where((w) => asStr(w['start']).compareTo(today) <= 0).toList().reversed.take(8)) _week(w),
      ]),
    ]);
  }

  Widget _week(Map<String, dynamic> w) {
    final status = asStr(w['status']);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(child: Text('Week ${asStr(w['week'])} · ${prettyDate(asStr(w['start']))}', style: TextStyle(fontWeight: FontWeight.w700, color: C.text))),
          if (status.isNotEmpty) Pill(status, color: statusColor(status)),
        ]),
        Text(
          'Weight ${fmtNum(w['avg_weight'] as double?)} vs target ${fmtNum(w['target_weight'] as double?)} kg · '
          'sessions ${asStr(w['done'])}/${asStr(w['planned'])} (${fmtPct(w['adherence'] as double?)}) · '
          'run ${fmtNum(w['run_km'] as double?)} km · swim ${fmtNum(w['swim_m'] as double?, dp: 0)} m · bike ${fmtNum(w['bike_km'] as double?)} km · '
          'sleep ${fmtNum(w['avg_sleep'] as double?)} h',
          style: TextStyle(color: C.mut, fontSize: 13, height: 1.35),
        ),
      ]),
    );
  }
}
