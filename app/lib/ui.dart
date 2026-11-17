import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'util.dart';

/// EnduraForge palette. Dark ("forge") is the default; light is optional. Colours are getters so the whole app
/// switches when the theme changes.
class C {
  static bool dark = true;

  static Color get bg => dark ? const Color(0xFF0D1014) : const Color(0xFFF4F6F8);
  static Color get card => dark ? const Color(0xFF161B21) : const Color(0xFFFFFFFF);
  static Color get card2 => dark ? const Color(0xFF1E252D) : const Color(0xFFEEF1F4);
  static Color get line => dark ? const Color(0xFF2A323C) : const Color(0xFFE1E6EB);
  static Color get text => dark ? const Color(0xFFE8EDF2) : const Color(0xFF14202B);
  static Color get navy => text;
  static Color get mut => dark ? const Color(0xFF8C99A6) : const Color(0xFF5F6B78);
  static Color get accent => dark ? const Color(0xFFFF7A3D) : const Color(0xFFE2601F);
  static Color get teal => dark ? const Color(0xFF2EC4B6) : const Color(0xFF0F8C80);
  static Color get ok => dark ? const Color(0xFF3DDC84) : const Color(0xFF2E7D32);
  static Color get warn => dark ? const Color(0xFFF5B841) : const Color(0xFFB26A00);
  static Color get bad => dark ? const Color(0xFFFF5C5C) : const Color(0xFFC62828);
  static Color get swim => dark ? const Color(0xFF4DA3FF) : const Color(0xFF1565C0);
  static Color get bike => dark ? const Color(0xFFB07CFF) : const Color(0xFF6A3FC4);
  static Color get hyrox => dark ? const Color(0xFFFFD34D) : const Color(0xFF9A7400);

  static Color discipline(String d) {
    switch (d) {
      case 'run':
        return accent;
      case 'swim':
        return swim;
      case 'bike':
      case 'brick':
        return bike;
      case 'strength':
        return teal;
      case 'hyrox':
        return hyrox;
      case 'race':
        return bad;
      default:
        return mut;
    }
  }
}

IconData disciplineIcon(String d) {
  switch (d) {
    case 'run':
      return Icons.directions_run;
    case 'swim':
      return Icons.pool;
    case 'bike':
      return Icons.directions_bike;
    case 'brick':
      return Icons.merge_type;
    case 'strength':
      return Icons.fitness_center;
    case 'hyrox':
      return Icons.bolt;
    case 'race':
      return Icons.emoji_events;
    default:
      return Icons.self_improvement;
  }
}

ThemeData buildTheme(bool dark) {
  C.dark = dark;
  final scheme = ColorScheme.fromSeed(seedColor: C.accent, brightness: dark ? Brightness.dark : Brightness.light).copyWith(
    primary: C.accent,
    secondary: C.teal,
    surface: C.card,
    error: C.bad,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: C.bg,
    canvasColor: C.bg,
    cardColor: C.card,
    dividerColor: C.line,
    appBarTheme: AppBarTheme(backgroundColor: C.bg, foregroundColor: C.text, elevation: 0, scrolledUnderElevation: 0,
        titleTextStyle: TextStyle(color: C.text, fontSize: 20, fontWeight: FontWeight.w800, letterSpacing: -0.3)),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: C.card,
      indicatorColor: C.accent.withOpacity(0.18),
      height: 66,
      labelTextStyle: WidgetStatePropertyAll(TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: C.text)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: C.card2,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: C.line)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: C.line)),
      isDense: true,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(backgroundColor: C.accent, foregroundColor: Colors.white, minimumSize: const Size(48, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)), textStyle: const TextStyle(fontWeight: FontWeight.w700)),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(foregroundColor: C.text, minimumSize: const Size(48, 48), side: BorderSide(color: C.line),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
    ),
    chipTheme: ChipThemeData(backgroundColor: C.card2, selectedColor: C.accent.withOpacity(0.25), side: BorderSide(color: C.line),
        labelStyle: TextStyle(color: C.text)),
    pageTransitionsTheme: const PageTransitionsTheme(builders: {
      TargetPlatform.android: FadeUpwardsPageTransitionsBuilder(),
      TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
    }),
    textTheme: (dark ? ThemeData.dark() : ThemeData.light()).textTheme.apply(bodyColor: C.text, displayColor: C.text),
  );
}

Color statusColor(String s) {
  if (s == 'Achieved' || s == 'Hit' || s == 'ON TRACK' || s == 'On track' || s == 'green') return C.ok;
  if (s.startsWith('BEHIND') || s == 'Behind' || s == 'Missed' || s.startsWith('TOO FAST') || s == 'red') return C.bad;
  if (s.startsWith('Overdue') || s == 'Due this week' || s.contains('adherence') || s == 'Log the result' || s == 'amber') return C.warn;
  return C.mut;
}

class Section extends StatelessWidget {
  final String title;
  final String? subtitle;
  final List<Widget> children;
  final Widget? trailing;
  final Color? accent;
  const Section({super.key, required this.title, this.subtitle, required this.children, this.trailing, this.accent});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(14, 6, 14, 6),
      decoration: BoxDecoration(
        color: C.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: C.line),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: accent == null ? null : BoxDecoration(border: Border(left: BorderSide(color: accent!, width: 4))),
          padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(child: Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: C.text, letterSpacing: -0.2))),
                if (trailing != null) trailing!,
              ]),
              if (subtitle != null && subtitle!.isNotEmpty)
                Padding(padding: const EdgeInsets.only(top: 2), child: Text(subtitle!, style: TextStyle(color: C.mut, fontSize: 13, height: 1.3))),
              const SizedBox(height: 8),
              ...children,
            ],
          ),
        ),
      ),
    );
  }
}

class Pill extends StatelessWidget {
  final String text;
  final Color? color;
  const Pill(this.text, {super.key, this.color});

  @override
  Widget build(BuildContext context) {
    final c = color ?? C.teal;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
      decoration: BoxDecoration(color: c.withOpacity(0.16), borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: TextStyle(color: c, fontWeight: FontWeight.w700, fontSize: 12)),
    );
  }
}

class KV extends StatelessWidget {
  final String k;
  final String v;
  const KV(this.k, this.v, {super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SizedBox(width: 130, child: Text(k, style: TextStyle(color: C.mut, fontSize: 13))),
        Expanded(child: Text(v, style: TextStyle(fontSize: 14, color: C.text))),
      ]),
    );
  }
}

class Bar extends StatelessWidget {
  final double? value;
  final Color? color;
  final double height;
  const Bar(this.value, {super.key, this.color, this.height = 8});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(6),
      child: LinearProgressIndicator(
          value: (value ?? 0).clamp(0.0, 1.0).toDouble(), minHeight: height, backgroundColor: C.card2, color: color ?? C.accent),
    );
  }
}

class Para extends StatelessWidget {
  final String title;
  final String body;
  final String? extra;
  const Para(this.title, this.body, {super.key, this.extra});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (title.isNotEmpty) Text(title, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: C.text)),
        if (body.isNotEmpty) Text(body, style: TextStyle(fontSize: 14, height: 1.38, color: C.text)),
        if (extra != null && extra!.isNotEmpty) Text(extra!, style: TextStyle(fontSize: 13, color: C.mut, height: 1.35)),
      ]),
    );
  }
}

/// A big number with a label, for dashboards.
class StatTile extends StatelessWidget {
  final String label;
  final String value;
  final String? sub;
  final Color? color;
  final IconData? icon;
  const StatTile(this.label, this.value, {super.key, this.sub, this.color, this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: C.card2, borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          if (icon != null) Icon(icon, size: 16, color: color ?? C.mut),
          if (icon != null) const SizedBox(width: 5),
          Expanded(child: Text(label, style: TextStyle(color: C.mut, fontSize: 12), overflow: TextOverflow.ellipsis)),
        ]),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(color: color ?? C.text, fontSize: 22, fontWeight: FontWeight.w800, letterSpacing: -0.5)),
        if (sub != null) Text(sub!, style: TextStyle(color: C.mut, fontSize: 11.5)),
      ]),
    );
  }
}

/// Two or three tiles in a row.
class TileRow extends StatelessWidget {
  final List<Widget> tiles;
  const TileRow(this.tiles, {super.key});

  @override
  Widget build(BuildContext context) {
    final out = <Widget>[];
    for (var i = 0; i < tiles.length; i++) {
      if (i > 0) out.add(const SizedBox(width: 8));
      out.add(Expanded(child: tiles[i]));
    }
    return Padding(padding: const EdgeInsets.only(bottom: 8), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: out));
  }
}

/// Circular progress ring with a centred label.
class Ring extends StatelessWidget {
  final double? value;
  final String label;
  final String? sub;
  final Color? color;
  final double size;
  const Ring({super.key, required this.value, required this.label, this.sub, this.color, this.size = 86});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _RingPainter((value ?? 0).clamp(0.0, 1.0).toDouble(), color ?? C.accent, C.card2),
        child: Center(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text(label, style: TextStyle(fontSize: size / 4.6, fontWeight: FontWeight.w800, color: C.text)),
            if (sub != null) Text(sub!, style: TextStyle(fontSize: 10.5, color: C.mut)),
          ]),
        ),
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final double v;
  final Color c;
  final Color bg;
  _RingPainter(this.v, this.c, this.bg);

  @override
  void paint(Canvas canvas, Size size) {
    final r = math.min(size.width, size.height) / 2 - 5;
    final center = Offset(size.width / 2, size.height / 2);
    final p = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round
      ..color = bg;
    canvas.drawCircle(center, r, p);
    p.color = c;
    canvas.drawArc(Rect.fromCircle(center: center, radius: r), -math.pi / 2, 2 * math.pi * v, false, p);
  }

  @override
  bool shouldRepaint(covariant _RingPainter old) => old.v != v || old.c != c;
}

/// Simple bar chart (weekly totals).
class BarChart extends StatelessWidget {
  final List<double> values;
  final List<String> labels;
  final Color? color;
  final String unit;
  final double height;
  const BarChart({super.key, required this.values, required this.labels, this.color, this.unit = '', this.height = 150});

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty || values.every((v) => v == 0)) {
      return Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text('No data yet.', style: TextStyle(color: C.mut)));
    }
    return SizedBox(height: height, child: CustomPaint(painter: _BarPainter(values, labels, color ?? C.accent, unit), size: Size.infinite));
  }
}

class _BarPainter extends CustomPainter {
  final List<double> v;
  final List<String> l;
  final Color c;
  final String unit;
  _BarPainter(this.v, this.l, this.c, this.unit);

  @override
  void paint(Canvas canvas, Size size) {
    final mx = v.reduce(math.max);
    final bottom = 16.0;
    final top = 14.0;
    final h = size.height - bottom - top;
    final slot = size.width / v.length;
    final bw = math.max(3.0, slot * 0.62);
    final tp = TextPainter(textDirection: TextDirection.ltr);
    final paint = Paint()..color = c;
    for (var i = 0; i < v.length; i++) {
      final bh = mx <= 0 ? 0.0 : h * v[i] / mx;
      final x = slot * i + (slot - bw) / 2;
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(x, top + h - bh, bw, bh), const Radius.circular(3)), paint);
      if (i == v.length - 1 || v[i] == mx) {
        tp.text = TextSpan(text: '${fmtNum(v[i])}$unit', style: TextStyle(fontSize: 10, color: C.text));
        tp.layout();
        tp.paint(canvas, Offset(math.min(size.width - tp.width, math.max(0.0, x + bw / 2 - tp.width / 2)), top + h - bh - 13));
      }
      if (l.length == v.length && (i % math.max(1, (v.length / 6).ceil()) == 0)) {
        tp.text = TextSpan(text: l[i], style: TextStyle(fontSize: 9.5, color: C.mut));
        tp.layout();
        tp.paint(canvas, Offset(math.max(0.0, x + bw / 2 - tp.width / 2), size.height - bottom + 3));
      }
    }
  }

  @override
  bool shouldRepaint(covariant _BarPainter old) => true;
}

/// Line chart with an optional target line (both lists the same length; nulls are gaps).
class LineChart extends StatelessWidget {
  final List<double?> values;
  final List<double?>? target;
  final List<String> labels;
  final Color? color;
  final double height;
  final bool invert;
  final String Function(double)? fmt;
  const LineChart({super.key, required this.values, this.target, required this.labels, this.color, this.height = 170, this.invert = false, this.fmt});

  @override
  Widget build(BuildContext context) {
    if (values.where((v) => v != null).length < 2) {
      return Padding(padding: const EdgeInsets.symmetric(vertical: 12), child: Text('Log at least two values to see a trend.', style: TextStyle(color: C.mut)));
    }
    return SizedBox(height: height, child: CustomPaint(painter: _LinePainter(values, target, labels, color ?? C.accent, invert, fmt), size: Size.infinite));
  }
}

class _LinePainter extends CustomPainter {
  final List<double?> v;
  final List<double?>? t;
  final List<String> l;
  final Color c;
  final bool invert;
  final String Function(double)? fmt;
  _LinePainter(this.v, this.t, this.l, this.c, this.invert, this.fmt);

  @override
  void paint(Canvas canvas, Size size) {
    final all = [...v.whereType<double>(), ...(t ?? const <double?>[]).whereType<double>()];
    var lo = all.reduce(math.min);
    var hi = all.reduce(math.max);
    if (hi - lo < 1e-6) {
      hi += 1;
      lo -= 1;
    }
    final pad = (hi - lo) * 0.1;
    lo -= pad;
    hi += pad;
    const left = 34.0, bottom = 16.0, top = 6.0;
    final w = size.width - left - 4;
    final h = size.height - bottom - top;
    final n = math.max(2, v.length);
    double x(int i) => left + w * i / (n - 1);
    double y(double val) {
      final f = (val - lo) / (hi - lo);
      return top + h * (invert ? f : 1 - f);
    }

    final grid = Paint()
      ..color = C.line
      ..strokeWidth = 1;
    final tp = TextPainter(textDirection: TextDirection.ltr);
    for (var k = 0; k <= 3; k++) {
      final val = lo + (hi - lo) * k / 3;
      canvas.drawLine(Offset(left, y(val)), Offset(left + w, y(val)), grid);
      tp.text = TextSpan(text: fmt != null ? fmt!(val) : fmtNum(val), style: TextStyle(fontSize: 9.5, color: C.mut));
      tp.layout();
      tp.paint(canvas, Offset(0, y(val) - 6));
    }
    void line(List<double?> s, Paint p) {
      final path = Path();
      var started = false;
      for (var i = 0; i < s.length; i++) {
        final val = s[i];
        if (val == null) continue;
        if (!started) {
          path.moveTo(x(i), y(val));
          started = true;
        } else {
          path.lineTo(x(i), y(val));
        }
      }
      canvas.drawPath(path, p);
    }

    if (t != null) {
      line(t!, Paint()
        ..color = C.mut
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5);
    }
    line(v, Paint()
      ..color = c
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5);
    final dot = Paint()..color = c;
    for (var i = 0; i < v.length; i++) {
      final val = v[i];
      if (val != null) canvas.drawCircle(Offset(x(i), y(val)), 2.6, dot);
    }
    final step = math.max(1, (l.length / 5).ceil());
    for (var i = 0; i < l.length; i += step) {
      tp.text = TextSpan(text: l[i], style: TextStyle(fontSize: 9.5, color: C.mut));
      tp.layout();
      tp.paint(canvas, Offset(math.min(size.width - tp.width, math.max(left, x(i) - tp.width / 2)), size.height - bottom + 3));
    }
  }

  @override
  bool shouldRepaint(covariant _LinePainter old) => true;
}

/// A number box that saves as you type. Re-created per day via its key.
class NumField extends StatefulWidget {
  final String label;
  final double? value;
  final String? suffix;
  final ValueChanged<double?> onChanged;
  const NumField({super.key, required this.label, required this.value, required this.onChanged, this.suffix});

  @override
  State<NumField> createState() => _NumFieldState();
}

class _NumFieldState extends State<NumField> {
  late final TextEditingController _c = TextEditingController(text: widget.value == null ? '' : fmtNum(widget.value, dp: 2));

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: _c,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(labelText: widget.label, suffixText: widget.suffix),
      onChanged: (t) {
        final v = double.tryParse(t.replaceAll(',', '.').trim());
        if (t.trim().isEmpty || v != null) widget.onChanged(v);
      },
    );
  }
}

/// A text box that saves as you type.
class TextBox extends StatefulWidget {
  final String label;
  final String value;
  final int lines;
  final ValueChanged<String> onChanged;
  const TextBox({super.key, required this.label, required this.value, required this.onChanged, this.lines = 1});

  @override
  State<TextBox> createState() => _TextBoxState();
}

class _TextBoxState extends State<TextBox> {
  late final TextEditingController _c = TextEditingController(text: widget.value);

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(controller: _c, maxLines: widget.lines, decoration: InputDecoration(labelText: widget.label), onChanged: widget.onChanged);
  }
}

/// 1 to 5 picker.
class Scale5 extends StatelessWidget {
  final String label;
  final int? value;
  final String low;
  final String high;
  final ValueChanged<int?> onChanged;
  const Scale5({super.key, required this.label, required this.value, required this.onChanged, this.low = '', this.high = ''});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text(label, style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
          const Spacer(),
          if (low.isNotEmpty) Text('1 = $low · 5 = $high', style: TextStyle(color: C.mut, fontSize: 11.5)),
        ]),
        const SizedBox(height: 4),
        Row(children: [
          for (var i = 1; i <= 5; i++)
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(right: 6),
                child: ChoiceChip(
                  label: SizedBox(width: double.infinity, child: Text('$i', textAlign: TextAlign.center)),
                  selected: value == i,
                  showCheckmark: false,
                  onSelected: (sel) => onChanged(sel ? i : null),
                ),
              ),
            ),
        ]),
      ]),
    );
  }
}

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String body;
  const EmptyState(this.icon, this.title, this.body, {super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(28),
      child: Column(children: [
        Icon(icon, size: 44, color: C.mut),
        const SizedBox(height: 10),
        Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: C.text)),
        const SizedBox(height: 4),
        Text(body, textAlign: TextAlign.center, style: TextStyle(color: C.mut)),
      ]),
    );
  }
}

void showMsg(BuildContext context, String text) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
}

/// Push a simple page with a list of widgets that rebuilds when [listenable] changes.
void pushPage(BuildContext context, String title, Listenable listenable, List<Widget> Function() body) {
  Navigator.of(context).push(MaterialPageRoute<void>(
      builder: (_) => Scaffold(
            appBar: AppBar(title: Text(title)),
            body: ListenableBuilder(listenable: listenable, builder: (context, _) => ListView(padding: const EdgeInsets.only(bottom: 28), children: body())),
          )));
}
