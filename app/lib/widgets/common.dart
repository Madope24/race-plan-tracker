import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models.dart';

/// Colour and icon for each workout type — used everywhere so the app reads at a glance.
class TypeStyle {
  final Color color;
  final IconData icon;
  const TypeStyle(this.color, this.icon);

  static TypeStyle of(String type) {
    switch (type) {
      case 'Run':
        return const TypeStyle(Color(0xFF2E9E5B), Icons.directions_run);
      case 'Swim':
        return const TypeStyle(Color(0xFF2D7DD2), Icons.pool);
      case 'Strength':
        return const TypeStyle(Color(0xFFE07A1F), Icons.fitness_center);
      case 'Mobility':
        return const TypeStyle(Color(0xFF8A5CD1), Icons.self_improvement);
      default:
        return const TypeStyle(Color(0xFF8A8A8A), Icons.hotel);
    }
  }
}

String fmtDate(String iso, [String pattern = 'EEE d MMM']) => DateFormat(pattern).format(DateTime.parse(iso));

String isoDate(DateTime d) => DateFormat('yyyy-MM-dd').format(d);

String fmtNum(num? v, {int decimals = 1}) {
  if (v == null) return '–';
  if (v == v.roundToDouble()) return v.toStringAsFixed(0);
  return v.toStringAsFixed(decimals);
}

String timeAgo(DateTime? t) {
  if (t == null) return 'never';
  final d = DateTime.now().difference(t);
  if (d.inSeconds < 60) return 'just now';
  if (d.inMinutes < 60) return '${d.inMinutes} min ago';
  if (d.inHours < 24) return '${d.inHours} h ago';
  return DateFormat('d MMM HH:mm').format(t);
}

class TypeIcon extends StatelessWidget {
  final String type;
  final double size;
  const TypeIcon(this.type, {super.key, this.size = 44});

  @override
  Widget build(BuildContext context) {
    final s = TypeStyle.of(type);
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(color: s.color.withOpacity(0.15), borderRadius: BorderRadius.circular(size / 3.2)),
      child: Icon(s.icon, color: s.color, size: size * 0.55),
    );
  }
}

class StatusIcon extends StatelessWidget {
  final SessionLog? log;
  const StatusIcon(this.log, {super.key});

  @override
  Widget build(BuildContext context) {
    final muted = Theme.of(context).colorScheme.outline;
    switch (log?.status) {
      case 'done':
        return const Icon(Icons.check_circle, color: Color(0xFF2E9E5B), size: 28);
      case 'partial':
        return const Icon(Icons.timelapse, color: Color(0xFFE0A21F), size: 28);
      case 'skipped':
        return Icon(Icons.cancel, color: Colors.red.shade300, size: 28);
      default:
        return Icon(Icons.radio_button_unchecked, color: muted, size: 28);
    }
  }
}

/// The workout row used on Home and in Workouts.
class SessionTile extends StatelessWidget {
  final Session session;
  final VoidCallback onTap;
  const SessionTile({super.key, required this.session, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final s = session;
    final sub = [s.timeSlot, if (s.plannedLabel.isNotEmpty) s.plannedLabel].join(' · ');
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        leading: TypeIcon(s.type),
        title: Text(s.shortTitle, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(sub),
        trailing: StatusIcon(s.log),
        onTap: onTap,
      ),
    );
  }
}

class StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final String? sub;
  final Color? color;
  const StatCard({super.key, required this.icon, required this.label, required this.value, this.sub, this.color});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final c = color ?? theme.colorScheme.primary;
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, size: 18, color: c),
              const SizedBox(width: 6),
              Expanded(child: Text(label, style: theme.textTheme.labelMedium, overflow: TextOverflow.ellipsis)),
            ]),
            const SizedBox(height: 8),
            Text(value, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            if (sub != null) Text(sub!, style: theme.textTheme.bodySmall, maxLines: 1, overflow: TextOverflow.ellipsis),
          ],
        ),
      ),
    );
  }
}

class SectionTitle extends StatelessWidget {
  final String text;
  final Widget? trailing;
  const SectionTitle(this.text, {super.key, this.trailing});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(4, 20, 4, 8),
        child: Row(children: [
          Expanded(child: Text(text, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold))),
          if (trailing != null) trailing!,
        ]),
      );
}

/// − value + control for quick logging (water, sleep, servings…)
class ValueStepper extends StatelessWidget {
  final String label;
  final double? value;
  final double step;
  final double max;
  final String unit;
  final ValueChanged<double?> onChanged;
  const ValueStepper({
    super.key,
    required this.label,
    required this.value,
    required this.step,
    required this.unit,
    required this.onChanged,
    this.max = 9999,
  });

  @override
  Widget build(BuildContext context) {
    final v = value ?? 0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(children: [
        Expanded(child: Text(label, style: Theme.of(context).textTheme.bodyLarge)),
        IconButton.filledTonal(
          onPressed: v <= 0 ? null : () => onChanged((v - step).clamp(0, max).toDouble()),
          icon: const Icon(Icons.remove),
        ),
        SizedBox(
          width: 84,
          child: Text(
            value == null ? '–' : '${fmtNum(v, decimals: 2)} $unit',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
        ),
        IconButton.filledTonal(
          onPressed: v >= max ? null : () => onChanged((v + step).clamp(0, max).toDouble()),
          icon: const Icon(Icons.add),
        ),
      ]),
    );
  }
}

/// Splits the long plan text into readable lines.
List<String> detailLines(String text) => text
    .replaceAll(' sheet', ' guide') // the plan text was written for the Excel workbook
    .replaceAllMapped(RegExp(r'([.;:])\s+(?=[A-Z0-9])'), (m) => '${m[1]}\n')
    .split('\n')
    .map((l) => l.trim().replaceAll(RegExp(r';$'), ''))
    .where((l) => l.isNotEmpty)
    .toList();
