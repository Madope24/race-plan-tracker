// Garmin Connect "Activities.csv" import, on the phone (works offline). Mirrors server/app/engine/garmin.py.
// Missing values ("--") stay missing: nothing is invented.

import 'util.dart';

List<List<String>> parseCsv(String text) {
  final rows = <List<String>>[];
  var row = <String>[];
  final cell = StringBuffer();
  var quoted = false;
  final s = text.startsWith('﻿') ? text.substring(1) : text;
  for (var i = 0; i < s.length; i++) {
    final ch = s[i];
    if (quoted) {
      if (ch == '"') {
        if (i + 1 < s.length && s[i + 1] == '"') {
          cell.write('"');
          i++;
        } else {
          quoted = false;
        }
      } else {
        cell.write(ch);
      }
    } else if (ch == '"') {
      quoted = true;
    } else if (ch == ',') {
      row.add(cell.toString());
      cell.clear();
    } else if (ch == '\n' || ch == '\r') {
      if (ch == '\r' && i + 1 < s.length && s[i + 1] == '\n') i++;
      row.add(cell.toString());
      cell.clear();
      if (row.any((c) => c.isNotEmpty)) rows.add(row);
      row = <String>[];
    } else {
      cell.write(ch);
    }
  }
  if (cell.isNotEmpty || row.isNotEmpty) {
    row.add(cell.toString());
    if (row.any((c) => c.isNotEmpty)) rows.add(row);
  }
  return rows;
}

double? _num(String? v) {
  if (v == null) return null;
  final t = v.replaceAll(',', '').trim();
  if (t.isEmpty || t == '--') return null;
  return double.tryParse(t);
}

double? _secs(String? v) {
  if (v == null || v.trim().isEmpty || v.trim() == '--') return null;
  var s = 0.0;
  for (final p in v.trim().split(':')) {
    final x = double.tryParse(p);
    if (x == null) return null;
    s = s * 60 + x;
  }
  return s;
}

String kindOf(String t) {
  final l = t.toLowerCase();
  if (l.contains('swim')) return 'swim';
  if (l.contains('run')) return 'run';
  if (l.contains('walk')) return 'walk';
  if (l.contains('cycl') || l.contains('bik') || l.contains('ride')) return 'bike';
  if (l.contains('strength')) return 'strength';
  return 'other';
}

List<Map<String, dynamic>> parseGarmin(String text) {
  final rows = parseCsv(text);
  if (rows.length < 2) return [];
  final head = rows.first.map((h) => h.trim()).toList();
  final out = <Map<String, dynamic>>[];
  // Garmin's CSV has no unit. Steps x stride length gives the real distance: about 1.6 x the Distance column means miles.
  var mi = 0, km = 0;
  for (final r in rows.skip(1)) {
    double? g(String name) {
      final i = head.indexOf(name);
      return (i >= 0 && i < r.length) ? _num(r[i]) : null;
    }

    final d = g('Distance'), steps = g('Steps'), stride = g('Avg Stride Length');
    if (d == null || d <= 0 || steps == null || stride == null) continue;
    final ratio = steps * stride / 1000 / d;
    if (ratio >= 1.35 && ratio <= 1.95) mi++;
    if (ratio >= 0.8 && ratio <= 1.25) km++;
  }
  final miles = mi > km;
  final k = miles ? 1.609344 : 1.0;
  for (final r in rows.skip(1)) {
    String? f(String name) {
      final i = head.indexOf(name);
      return (i >= 0 && i < r.length) ? r[i] : null;
    }

    final start = (f('Date') ?? '').trim();
    if (start.length < 10) continue;
    final k = kindOf(f('Activity Type') ?? '');
    final dist = _num(f('Distance'));
    final a = <String, dynamic>{
      'id': 'garmin-${start.replaceAll(' ', 'T')}-$k',
      'source': 'garmin_csv',
      'type': k,
      'garmin_type': f('Activity Type'),
      'title': f('Title') ?? '',
      'start': start,
      'date': start.substring(0, 10),
      'duration_s': _secs(f('Time')),
      'moving_s': _secs(f('Moving Time')),
      'avg_hr': _num(f('Avg HR')),
      'max_hr': _num(f('Max HR')),
      'calories': _num(f('Calories')),
    };
    if (k == 'swim') {
      a['distance_m'] = dist;
      a['pace_100m_s'] = _secs(f('Avg Pace'));
      a['strokes'] = _num(f('Total Strokes'));
      a['swolf'] = _num(f('Avg. Swolf'));
      a['stroke_rate'] = _num(f('Avg Stroke Rate'));
    } else {
      final pace = _secs(f('Avg Pace')), best = _secs(f('Best Pace'));
      a['distance_km'] = dist == null ? null : (dist * k * 100).roundToDouble() / 100;
      a['recorded_unit'] = miles ? 'mi' : 'km';
      a['pace_s_km'] = pace == null ? null : (pace / k).roundToDouble();
      a['best_pace_s_km'] = best == null ? null : (best / k).roundToDouble();
      a['cadence'] = _num(f('Avg Run Cadence'));
    }
    a.removeWhere((key, v) => v == null);
    out.add(a);
  }
  out.sort((a, b) => asStr(a['start']).compareTo(asStr(b['start'])));
  return out;
}
