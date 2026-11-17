import 'package:flutter/material.dart';

import 'coach.dart' show kPainAreas;
import 'state.dart';
import 'ui.dart';
import 'util.dart';

Future<void> showSheet(BuildContext context, Widget Function(BuildContext) builder) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: C.card,
    shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
    builder: (ctx) => Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom),
      child: DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.85,
        maxChildSize: 0.95,
        builder: (ctx, scroll) => ListView(controller: scroll, padding: const EdgeInsets.fromLTRB(18, 10, 18, 28), children: [
          Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: C.line, borderRadius: BorderRadius.circular(4)))),
          const SizedBox(height: 12),
          builder(ctx),
        ]),
      ),
    ),
  );
}

/// Morning check-in: sleep, soreness, energy, stress, resting heart rate, HRV, weight, pain.
class CheckInSheet extends StatelessWidget {
  final AppState st;
  final String iso;
  const CheckInSheet({super.key, required this.st, required this.iso});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: st,
      builder: (context, _) {
        final l = st.log(iso);
        int? i(String k) => asNum(l[k])?.round();
        Widget n(String k, String label, String suffix) =>
            NumField(key: ValueKey('ci-$iso-$k'), label: label, suffix: suffix, value: asNum(l[k]), onChanged: (v) => st.setField(iso, k, v));
        final areas = asList(l['pain_areas']).map(asStr).toSet();
        final r = st.readiness(iso);
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Morning check-in', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: C.text)),
          Text('30 seconds. The coach only changes today\'s plan when several signs agree.', style: TextStyle(color: C.mut)),
          const SizedBox(height: 14),
          Row(children: [Expanded(child: n('sleep_h', 'Sleep last night', 'h')), const SizedBox(width: 10), Expanded(child: n('rhr', 'Resting heart rate', 'bpm'))]),
          const SizedBox(height: 10),
          Row(children: [Expanded(child: n('weight', 'Weight', 'kg')), const SizedBox(width: 10), Expanded(child: n('hrv', 'HRV (if your watch has it)', 'ms'))]),
          const SizedBox(height: 14),
          Scale5(label: 'Sleep quality', value: i('sleep_q'), low: 'poor', high: 'great', onChanged: (v) => st.setField(iso, 'sleep_q', v)),
          Scale5(label: 'Muscle soreness', value: i('soreness'), low: 'none', high: 'very sore', onChanged: (v) => st.setField(iso, 'soreness', v)),
          Scale5(label: 'Energy', value: i('energy'), low: 'flat', high: 'full', onChanged: (v) => st.setField(iso, 'energy', v)),
          Scale5(label: 'Stress', value: i('stress'), low: 'calm', high: 'very high', onChanged: (v) => st.setField(iso, 'stress', v)),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: Text('Any pain today?', style: TextStyle(color: C.text)),
            subtitle: Text('Joint, tendon or sharp pain, not normal muscle soreness', style: TextStyle(color: C.mut)),
            value: l['pain_today'] == true,
            onChanged: (v) => st.setFields(iso, {'pain_today': v ? true : null, if (!v) 'pain_areas': null}),
          ),
          if (l['pain_today'] == true)
            Wrap(spacing: 6, runSpacing: 6, children: [
              for (final a in kPainAreas.keys)
                FilterChip(label: Text(a), selected: areas.contains(a), onSelected: (_) => st.toggleInList(iso, 'pain_areas', a)),
            ]),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: statusColor(asStr(r['level'])).withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
            child: Text(asStr(r['message']), style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
          ),
          const SizedBox(height: 12),
          FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Done')),
        ]);
      },
    );
  }
}

/// After a workout: completed? how hard? pain? energy? notes, plus the numbers for that discipline.
class FeedbackSheet extends StatefulWidget {
  final AppState st;
  final String iso;
  final String slot;
  final Map<String, dynamic> session;
  final int? minutes;
  const FeedbackSheet({super.key, required this.st, required this.iso, required this.slot, required this.session, this.minutes});

  @override
  State<FeedbackSheet> createState() => _FeedbackSheetState();
}

class _FeedbackSheetState extends State<FeedbackSheet> {
  late Map<String, dynamic> fb = Map<String, dynamic>.from(asMap(widget.st.log(widget.iso)['${widget.slot}_fb']));

  @override
  void initState() {
    super.initState();
    fb['done'] ??= 'yes';
    if (widget.minutes != null && widget.minutes! > 0) fb['minutes'] = widget.minutes!.toDouble();
  }

  @override
  Widget build(BuildContext context) {
    final st = widget.st;
    final iso = widget.iso;
    final disc = asStr(asMap(widget.session['meta'])['discipline']);
    final l = st.log(iso);
    Widget n(String k, String label, String suffix) =>
        NumField(key: ValueKey('fb-$iso-$k'), label: label, suffix: suffix, value: asNum(l[k]), onChanged: (v) => st.setField(iso, k, v));
    final rpe = asNum(fb['rpe']) ?? 6;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('How did it go?', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: C.text)),
      Text(asStr(widget.session['name']), style: TextStyle(color: C.mut)),
      const SizedBox(height: 14),
      Text('Did you complete it?', style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
      const SizedBox(height: 6),
      SegmentedButton<String>(
        segments: const [
          ButtonSegment(value: 'yes', label: Text('Yes')),
          ButtonSegment(value: 'partly', label: Text('Partly')),
          ButtonSegment(value: 'no', label: Text('No')),
        ],
        selected: {asStr(fb['done'])},
        onSelectionChanged: (s) => setState(() => fb['done'] = s.first),
      ),
      const SizedBox(height: 14),
      Text('How hard was it? ${rpe.round()} out of 10', style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
      Slider(value: rpe, min: 1, max: 10, divisions: 9, label: '${rpe.round()}', onChanged: (v) => setState(() => fb['rpe'] = v.roundToDouble())),
      Scale5(label: 'Energy', value: asNum(fb['energy'])?.round(), low: 'flat', high: 'full', onChanged: (v) => setState(() => fb['energy'] = v?.toDouble())),
      SwitchListTile(
        contentPadding: EdgeInsets.zero,
        title: Text('Any pain?', style: TextStyle(color: C.text)),
        value: fb['pain'] == true,
        onChanged: (v) => setState(() {
          fb['pain'] = v;
          if (!v) fb.remove('pain_area');
        }),
      ),
      if (fb['pain'] == true)
        Wrap(spacing: 6, runSpacing: 6, children: [
          for (final a in kPainAreas.keys) ChoiceChip(label: Text(a), selected: fb['pain_area'] == a, onSelected: (_) => setState(() => fb['pain_area'] = a)),
        ]),
      const SizedBox(height: 12),
      if (disc == 'run' || disc == 'brick' || disc == 'race') ...[
        Row(children: [Expanded(child: n('run_km', 'Run distance', 'km')), const SizedBox(width: 10), Expanded(child: n('run_hr', 'Average heart rate', 'bpm'))]),
        const SizedBox(height: 10),
      ],
      if (disc == 'swim') ...[
        Row(children: [Expanded(child: n('swim_m', 'Swim total', 'm')), const SizedBox(width: 10), Expanded(child: n('swim_cont_m', 'Longest non-stop', 'm'))]),
        const SizedBox(height: 10),
        Row(children: [Expanded(child: n('swolf', 'Average SWOLF', '')), const SizedBox(width: 10), Expanded(child: n('swim_strokes', 'Total strokes', ''))]),
        const SizedBox(height: 10),
      ],
      if (disc == 'bike' || disc == 'brick') ...[
        Row(children: [Expanded(child: n('bike_km', 'Ride distance', 'km')), const SizedBox(width: 10), Expanded(child: n('bike_min', 'Ride time', 'min'))]),
        const SizedBox(height: 10),
      ],
      TextBox(key: ValueKey('fbn-$iso-${widget.slot}'), label: 'Notes (optional)', value: asStr(fb['notes']), lines: 2, onChanged: (t) => fb['notes'] = t),
      const SizedBox(height: 14),
      FilledButton(
        onPressed: () {
          fb.removeWhere((k, v) => v == null || (v is String && v.isEmpty));
          st.setFeedback(iso, widget.slot == 'extra' ? 'pm' : widget.slot, fb);
          if (fb['pain'] == true) {
            final p = st.pain(iso);
            if (p.isNotEmpty) {
              showMsg(context, 'Pain in the ${p.join(', ')} on several days: progression is paused for exercises that load it. Please get it checked.');
            }
          }
          Navigator.pop(context);
        },
        child: const Text('Save'),
      ),
    ]);
  }
}
