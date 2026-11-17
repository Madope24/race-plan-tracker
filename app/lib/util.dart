// Small helpers for reading JSON safely and formatting dates and numbers.

Map<String, dynamic> asMap(Object? v) {
  if (v is Map<String, dynamic>) return v;
  if (v is Map) return Map<String, dynamic>.from(v);
  return <String, dynamic>{};
}

List<dynamic> asList(Object? v) => v is List ? v : const <dynamic>[];

String asStr(Object? v) => v == null ? '' : v.toString();

double? asNum(Object? v) {
  if (v is bool) return null;
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v.trim());
  return null;
}

String two(int n) => n.toString().padLeft(2, '0');

String isoOf(DateTime d) => '${d.year.toString().padLeft(4, '0')}-${two(d.month)}-${two(d.day)}';

/// Dates are handled in UTC so that day arithmetic never shifts.
DateTime dateOf(String iso) {
  final p = iso.split('-');
  return DateTime.utc(int.parse(p[0]), int.parse(p[1]), int.parse(p[2]));
}

String todayIso() {
  final n = DateTime.now();
  return isoOf(DateTime.utc(n.year, n.month, n.day));
}

int daysBetween(String a, String b) => dateOf(b).difference(dateOf(a)).inDays;

String addDays(String iso, int n) => isoOf(dateOf(iso).add(Duration(days: n)));

const List<String> kWeekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const List<String> kMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

String prettyDate(String iso, {bool year = false}) {
  if (iso.isEmpty) return '';
  final d = dateOf(iso);
  final s = '${kWeekdays[d.weekday - 1]} ${d.day} ${kMonths[d.month - 1]}';
  return year ? '$s ${d.year}' : s;
}

double round1(double v) => (v * 10).roundToDouble() / 10;

String fmtNum(double? v, {int dp = 1}) {
  if (v == null) return '-';
  if (dp == 0) return v.round().toString();
  final s = v.toStringAsFixed(dp);
  return s.endsWith('.0') ? s.substring(0, s.length - 2) : s;
}

String fmtPct(double? v) => v == null ? '-' : '${(v * 100).round()}%';

String nowIso() => DateTime.now().toUtc().toIso8601String();
