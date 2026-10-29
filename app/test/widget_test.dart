import 'package:flutter_test/flutter_test.dart';
import 'package:race_plan_tracker/models.dart';
import 'package:race_plan_tracker/widgets/common.dart';

void main() {
  test('session parses and formats planned amount', () {
    final s = Session.fromJson({
      'id': 1,
      'date': '2026-11-03',
      'week': 1,
      'day': 'Tuesday',
      'phase': 'Base',
      'time_slot': 'Morning',
      'type': 'Run',
      'title': 'Easy run 3 km',
      'details': 'Easy run 3 km. Run 3 minutes, walk 1 minute.',
      'planned': 3,
      'unit': 'km',
      'log': {'status': 'done', 'actual': 3.2, 'effort': 4, 'updated_at': '2026-11-03T05:00:00Z'},
    });
    expect(s.plannedLabel, '3 km');
    expect(s.log!.counts, isTrue);
    expect(s.isFastDay, isFalse);
  });

  test('detail text splits into readable lines', () {
    final lines = detailLines('Warm-up: 5 minutes. Exercises: Push-ups — 3 sets of 8; Pike push-ups — 3 sets of 5. Rest 60 seconds.');
    expect(lines.length, greaterThanOrEqualTo(4));
    expect(lines.first, 'Warm-up:');
  });
}
