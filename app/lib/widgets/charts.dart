import 'package:flutter/material.dart';

/// Weight chart: the expected healthy range (0.3 and 0.5 kg a week) and your weekly average weight.
class WeightChart extends StatelessWidget {
  final List<Map<String, dynamic>> series;
  const WeightChart({super.key, required this.series});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(children: [
      SizedBox(
        height: 190,
        child: CustomPaint(
          size: Size.infinite,
          painter: _WeightPainter(
            series: series,
            target: scheme.primary,
            stretch: scheme.tertiary,
            actual: const Color(0xFFE07A1F),
            grid: scheme.outlineVariant,
            text: scheme.onSurfaceVariant,
          ),
        ),
      ),
      const SizedBox(height: 8),
      Wrap(spacing: 16, children: [
        _Legend(color: scheme.primary, label: '0.3 kg/week'),
        _Legend(color: scheme.tertiary, label: '0.5 kg/week', dashed: true),
        const _Legend(color: Color(0xFFE07A1F), label: 'You (weekly average)'),
      ]),
    ]);
  }
}

class _Legend extends StatelessWidget {
  final Color color;
  final String label;
  final bool dashed;
  const _Legend({required this.color, required this.label, this.dashed = false});

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        Container(width: 16, height: 3, color: dashed ? color.withOpacity(0.5) : color),
        const SizedBox(width: 6),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ]);
}

double? _num(dynamic v) => v == null ? null : (v as num).toDouble();

class _WeightPainter extends CustomPainter {
  final List<Map<String, dynamic>> series;
  final Color target, stretch, actual, grid, text;
  _WeightPainter({
    required this.series,
    required this.target,
    required this.stretch,
    required this.actual,
    required this.grid,
    required this.text,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (series.isEmpty) return;
    final values = <double>[];
    for (final p in series) {
      for (final k in ['target', 'stretch', 'actual']) {
        final v = _num(p[k]);
        if (v != null) values.add(v);
      }
    }
    if (values.isEmpty) return;
    var minY = values.reduce((a, b) => a < b ? a : b).floorToDouble() - 1;
    var maxY = values.reduce((a, b) => a > b ? a : b).ceilToDouble() + 1;
    if (maxY - minY < 4) maxY = minY + 4;

    const left = 34.0, bottom = 20.0, top = 6.0, right = 8.0;
    final w = size.width - left - right;
    final h = size.height - top - bottom;
    final n = series.length;
    double x(int i) => left + (n == 1 ? w / 2 : w * i / (n - 1));
    double y(double v) => top + h * (1 - (v - minY) / (maxY - minY));

    final gridPaint = Paint()
      ..color = grid
      ..strokeWidth = 1;
    final step = ((maxY - minY) / 4).ceilToDouble();
    for (var v = minY; v <= maxY; v += step) {
      canvas.drawLine(Offset(left, y(v)), Offset(size.width - right, y(v)), gridPaint);
      _label(canvas, v.toStringAsFixed(0), Offset(0, y(v) - 7));
    }
    for (var i = 0; i < n; i += 2) {
      _label(canvas, i == n - 1 ? 'End' : 'W${series[i]['week']}', Offset(x(i) - 9, size.height - 15));
    }

    void line(String key, Color c, {bool dashed = false, bool dots = false}) {
      final pts = <Offset>[];
      for (var i = 0; i < n; i++) {
        final v = _num(series[i][key]);
        if (v != null) pts.add(Offset(x(i), y(v)));
      }
      if (pts.isEmpty) return;
      final paint = Paint()
        ..color = c
        ..strokeWidth = dots ? 3 : 2
        ..style = PaintingStyle.stroke;
      for (var i = 0; i < pts.length - 1; i++) {
        if (dashed) {
          _dash(canvas, pts[i], pts[i + 1], paint);
        } else {
          canvas.drawLine(pts[i], pts[i + 1], paint);
        }
      }
      if (dots) {
        final dot = Paint()..color = c;
        for (final p in pts) {
          canvas.drawCircle(p, 4.5, dot);
        }
      }
    }

    line('target', target);
    line('stretch', stretch.withOpacity(0.6), dashed: true);
    line('actual', actual, dots: true);
  }

  void _dash(Canvas canvas, Offset a, Offset b, Paint p) {
    final total = (b - a).distance;
    final dir = (b - a) / total;
    var d = 0.0;
    while (d < total) {
      final end = (d + 5).clamp(0, total).toDouble();
      canvas.drawLine(a + dir * d, a + dir * end, p);
      d += 9;
    }
  }

  void _label(Canvas canvas, String s, Offset at) {
    final tp = TextPainter(
      text: TextSpan(text: s, style: TextStyle(color: text, fontSize: 10)),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, at);
  }

  @override
  bool shouldRepaint(covariant _WeightPainter old) => old.series != series;
}

/// One small bar per week: how many sessions you completed.
class WeeklyBars extends StatelessWidget {
  final List<Map<String, dynamic>> weeks;
  final int currentWeek;
  const WeeklyBars({super.key, required this.weeks, required this.currentWeek});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SizedBox(
      height: 110,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          for (final w in weeks)
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 2),
                child: Column(mainAxisAlignment: MainAxisAlignment.end, children: [
                  Expanded(
                    child: LayoutBuilder(builder: (context, c) {
                      final planned = (w['planned'] as num).toDouble();
                      final done = (w['done'] as num).toDouble();
                      final ratio = planned == 0 ? 0.0 : (done / planned).clamp(0.0, 1.0);
                      return Stack(alignment: Alignment.bottomCenter, children: [
                        Container(
                          decoration: BoxDecoration(
                            color: scheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(4),
                            border: w['week'] == currentWeek ? Border.all(color: scheme.primary, width: 1.5) : null,
                          ),
                        ),
                        Container(
                          height: c.maxHeight * ratio,
                          decoration: BoxDecoration(
                            color: ratio >= 0.85 ? const Color(0xFF2E9E5B) : scheme.primary,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ]);
                    }),
                  ),
                  const SizedBox(height: 4),
                  Text('${w['week']}', style: Theme.of(context).textTheme.labelSmall),
                ]),
              ),
            ),
        ],
      ),
    );
  }
}
