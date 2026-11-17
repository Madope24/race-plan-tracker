import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:enduraforge/logic.dart';
import 'package:enduraforge/util.dart';

void main() {
  final plan = asMap(jsonDecode(File('assets/plan.json').readAsStringSync()));

  Map<String, dynamic> goal(String id) => asList(plan['goals']).map(asMap).firstWhere((g) => g['id'] == id);

  test('plan covers 27 Oct 2026 to the 70.3 on 22 Aug 2027', () {
    expect(plan['start'], '2026-10-27');
    expect(plan['end'], '2027-08-22');
    expect(asList(plan['days']).length, 300);
  });

  test('7-day average and goal status', () {
    final Logs days = {};
    var w = 87.5;
    for (var i = 0; i < 14; i++) {
      w -= 0.12;
      days[addDays('2026-10-27', i)] = {'weight': round1(w), 'sleep_h': 7.8, 'protein': 165.0, 'am_done': true, 'pm_done': true};
    }
    days['2026-10-31']!['run_km'] = 7.0;
    final weeks = weekly(plan, days);
    expect(weeks.first['planned'] as int, greaterThan(0));
    final g1 = goalStatus(plan, goal('Goal 1'), days, <String, double?>{}, weeks, '2026-11-09');
    expect(g1['status'], 'On track');
    final m = asList(plan['mini_goals']).map(asMap).firstWhere((x) => x['text'] == 'Long run 6 km');
    expect(miniStatus(plan, m, days, <String, double?>{}, '2026-11-09')['status'], 'Hit');
    final g2 = goalStatus(plan, goal('Goal 2'), days, <String, double?>{}, weeks, '2026-11-09');
    expect(g2['status'], 'In progress');
    expect(g2['progress'], 0.7);
    final done = goalStatus(plan, goal('Goal 2'), days, <String, double?>{'goal:Goal 2': 112}, weeks, '2026-12-05');
    expect(done['status'], 'Achieved');
  });

  test('baseline-based mini goal targets', () {
    final m = asList(plan['mini_goals']).map(asMap).firstWhere((x) => x['text'] == 'Push-ups: baseline + 5');
    expect(miniTarget(plan, m, <String, double?>{'base:pushups': 12}), 17);
  });
}
