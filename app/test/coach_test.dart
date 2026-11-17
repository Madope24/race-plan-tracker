import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:enduraforge/exercise_detail.dart';
import 'package:enduraforge/coach.dart';
import 'package:enduraforge/garmin.dart';
import 'package:enduraforge/logic.dart' show Logs;
import 'package:enduraforge/util.dart';

void main() {
  final plan = asMap(jsonDecode(File('assets/plan.json').readAsStringSync()));
  final sessions = asMap(plan['sessions']);

  test('one bad metric alone never changes the plan', () {
    final Logs d = {'2026-11-10': {'sleep_h': 5.0}};
    expect(readiness(d, '2026-11-10')['level'], 'green');
  });

  test('poor sleep plus sore legs reduces the hard session', () {
    final Logs d = {'2026-11-10': {'sleep_h': 5.5, 'soreness': 4.0}};
    final r = readiness(d, '2026-11-10');
    expect(r['level'], 'amber');
    expect(adjust(asMap(sessions['3-RUN-I']), 'amber', <String>[])!['action'], 'reduce');
  });

  test('persistent pain pauses progression and swaps runs', () {
    final Logs d = {
      '2026-11-08': {'pm_fb': {'pain': true, 'pain_area': 'knee'}},
      '2026-11-10': {'pain_areas': ['knee']},
    };
    final pain = persistentPain(d, '2026-11-11');
    expect(pain, ['knee']);
    expect(progression([{'date': 'a', 'sets': [{'kg': 10, 'reps': 12}]}], '10 to 12', painBlocked: true)['action'], 'hold');
    expect(adjust(asMap(sessions['3-RUN-L']), 'green', pain)!['action'], 'swap');
  });

  test('progression changes one variable at a time', () {
    final hit = [
      {'date': 'a', 'sets': List.filled(3, {'kg': 12, 'reps': 12, 'rpe': 8})}
    ];
    final p = progression(hit, '10 to 12');
    expect(p['action'], 'add_load');
    expect(p['kg'], 14.0);
    expect(progression([{'date': 'a', 'sets': List.filled(3, {'kg': 0, 'reps': 12})}], '10 to 12')['action'], 'add_reps');
  });

  test('Thursday is the only fast day; runs mornings, swims evenings', () {
    for (final raw in asList(plan['days'])) {
      final d = asMap(raw);
      final am = d['am'] == null ? '' : asStr(asMap(sessions[d['am']])['code']);
      final pm = d['pm'] == null ? '' : asStr(asMap(sessions[d['pm']])['code']);
      if (d['weekday'] == 'Thu' && d['race'] == null && d['ramadan'] != true) expect([am, pm].where((c) => c.isNotEmpty).toList(), ['FAST'], reason: asStr(d['date']));
      if (d['weekday'] == 'Mon') expect(d['fasting'] == true, isFalse, reason: asStr(d['date']));
      expect(pm.startsWith('RUN'), isFalse, reason: asStr(d['date']));
      expect(am.startsWith('SWIM'), isFalse, reason: asStr(d['date']));
    }
  });

  test('every day has mobility and kegels; knee care before the 10 km', () {
    for (final raw in asList(plan['days'])) {
      final d = asMap(raw);
      expect(asList(d['mobility']), isNotEmpty, reason: asStr(d['date']));
      expect(asStr(d['kegels']), isNotEmpty, reason: asStr(d['date']));
    }
    final dec1 = asMap(asList(plan['days']).map(asMap).firstWhere((d) => d['date'] == '2026-12-01'));
    expect(dec1['knee_care'], isTrue);
  });

  test('Garmin CSV in miles is converted to kilometres', () {
    final csv = File('../server/app/engine/data/Activities.csv').readAsStringSync();
    final acts = parseGarmin(csv);
    expect(acts.length, 7);
    final swim = acts.firstWhere((a) => a['type'] == 'swim');
    expect(swim['distance_m'], 854);
    expect(swim.containsKey('avg_hr'), isFalse);
    final run = acts.lastWhere((a) => a['type'] == 'run');
    expect(run['distance_km'], 8.01);
    expect(run['pace_s_km'], 638);
  });

  test('swim drills and warm-up moves open full instructions', () {
    final lib = {for (final e in asList(plan['library']).map(asMap)) asStr(e['name']): e};
    for (final s in sessions.values.map(asMap)) {
      for (final r in asList(s['rows']).map(asMap)) {
        if (r['block'] == 'Drills' || r['block'] == 'Warm-up on the pool deck' || r['block'] == 'Cool-down stretch') {
          final e = lib[asStr(r['lib'])];
          expect(e, isNotNull, reason: asStr(r['ex']));
          expect(howSteps(asStr(e!['how'])).length, greaterThan(1), reason: asStr(r['ex']));
        }
      }
    }
    expect(howSteps('1) Stand tall. 2) Reach up. 3) Lower slowly.'), ['Stand tall.', 'Reach up.', 'Lower slowly.']);
  });
}
