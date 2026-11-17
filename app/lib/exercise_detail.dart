import 'package:flutter/material.dart';

import 'sheets.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

/// Splits library text written as "1) first 2) second" into separate steps.
List<String> howSteps(String how) {
  final parts = how.split(RegExp(r'(?:^|\s)\d+\)\s')).map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
  return parts.isEmpty ? [how] : parts;
}

/// Splits "A. B; C." into short lines for bullet lists.
List<String> bulletLines(String text) =>
    text.split(RegExp(r'(?<=[.;])\s+')).map((s) => s.trim().replaceAll(RegExp(r'[;]$'), '')).where((s) => s.isNotEmpty).toList();

/// Every detail of one exercise, stacked top to bottom: what it is, why, set-up, numbered steps,
/// breathing, cues, mistakes, easier and harder versions, and the dose.
class ExerciseDetail extends StatelessWidget {
  final Map<String, dynamic> lib;
  final Map<String, dynamic>? row;
  final bool showName;
  const ExerciseDetail({super.key, required this.lib, this.row, this.showName = true});

  @override
  Widget build(BuildContext context) {
    final steps = howSteps(asStr(lib['how']));
    final r = row;
    final today = r == null
        ? ''
        : [
            if (r['sets'] is num && (r['sets'] as num) > 1) '${r['sets']} x ${asStr(r['reps'])}' else if (asStr(r['reps']).isNotEmpty) asStr(r['reps']),
            if (asStr(r['rest']).isNotEmpty) 'rest ${asStr(r['rest'])}',
          ].join(' · ');
    final dose = asStr(lib['dose']).isNotEmpty
        ? asStr(lib['dose'])
        : (lib['sets'] != null ? '${asStr(lib['sets'])} sets x ${asStr(lib['reps'])}, rest ${asStr(lib['rest'])}' : '');
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      if (showName) Text(asStr(lib['name']), style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: C.text)),
      if (asStr(lib['also']).isNotEmpty) Text('Also called: ${asStr(lib['also'])}', style: TextStyle(color: C.mut)),
      const SizedBox(height: 8),
      _fact('Type', asStr(lib['cat'])),
      _fact('Level', asStr(lib['difficulty'])),
      _fact('Equipment', asStr(lib['equipment'])),
      _fact('Works', asStr(lib['muscles'])),
      if (today.isNotEmpty) _fact('Today', today),
      const SizedBox(height: 6),
      if (r != null && asStr(r['note']).isNotEmpty) _block('Coach note for today', asStr(r['note']), color: C.accent),
      if (asStr(lib['purpose']).isNotEmpty) _block('Why it matters', asStr(lib['purpose'])),
      if (asStr(lib['setup']).isNotEmpty) _block('Set-up', asStr(lib['setup'])),
      _heading('How to do it'),
      for (var i = 0; i < steps.length; i++)
        Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
              width: 22,
              height: 22,
              alignment: Alignment.center,
              margin: const EdgeInsets.only(right: 8, top: 1),
              decoration: BoxDecoration(color: C.accent.withOpacity(0.15), shape: BoxShape.circle),
              child: Text('${i + 1}', style: TextStyle(color: C.accent, fontWeight: FontWeight.w800, fontSize: 12)),
            ),
            Expanded(child: Text(steps[i], style: TextStyle(color: C.text, height: 1.4, fontSize: 14))),
          ]),
        ),
      const SizedBox(height: 6),
      if (asStr(lib['breathing']).isNotEmpty) _block('Breathing', asStr(lib['breathing'])),
      if (asStr(lib['cues']).isNotEmpty) _block('Coaching cues', asStr(lib['cues'])),
      if (asStr(lib['mistakes']).isNotEmpty) ...[
        _heading('Common mistakes'),
        for (final m in bulletLines(asStr(lib['mistakes']))) _bullet(m, C.bad),
        const SizedBox(height: 6),
      ],
      if (asStr(lib['easier']).isNotEmpty) _block('Easier version', asStr(lib['easier'])),
      if (asStr(lib['harder']).isNotEmpty) _block('Harder version', asStr(lib['harder'])),
      if (dose.isNotEmpty) _block('Typical dose', dose),
    ]);
  }

  Widget _heading(String t) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Text(t, style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14, color: C.text)),
      );

  Widget _block(String title, String body, {Color? color}) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _heading(title),
          Text(body, style: TextStyle(color: color ?? C.text, height: 1.4, fontSize: 14)),
        ]),
      );

  Widget _fact(String k, String v) => v.isEmpty
      ? const SizedBox.shrink()
      : Padding(
          padding: const EdgeInsets.only(bottom: 3),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            SizedBox(width: 92, child: Text(k, style: TextStyle(color: C.mut, fontSize: 13))),
            Expanded(child: Text(v, style: TextStyle(color: C.text, fontSize: 13.5, fontWeight: FontWeight.w600))),
          ]),
        );

  Widget _bullet(String t, Color dot) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Padding(padding: const EdgeInsets.only(top: 7, right: 8), child: Icon(Icons.circle, size: 6, color: dot)),
          Expanded(child: Text(t, style: TextStyle(color: C.text, height: 1.4, fontSize: 14))),
        ]),
      );
}

/// Opens the full, vertical instructions for an exercise in a bottom sheet.
Future<void> showExercise(BuildContext context, Map<String, dynamic> lib, {Map<String, dynamic>? row}) {
  return showSheet(context, (ctx) => ExerciseDetail(lib: lib, row: row));
}

/// One line of a routine (warm-up, mobility, knee or shoulder care): name and amount; tap for the full how-to.
class RoutineItem extends StatelessWidget {
  final AppState st;
  final Map<String, dynamic> item;
  final Color? color;
  const RoutineItem({super.key, required this.st, required this.item, this.color});

  @override
  Widget build(BuildContext context) {
    final lib = st.libraryFor({'ex': item['name'], 'lib': item['lib']});
    return InkWell(
      onTap: lib == null ? null : () => showExercise(context, lib, row: {'reps': item['amount'], 'sets': 1}),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(asStr(item['name']), style: TextStyle(color: C.text, fontSize: 14, fontWeight: FontWeight.w600)),
              Text(asStr(item['amount']), style: TextStyle(color: color ?? C.accent, fontSize: 13, fontWeight: FontWeight.w700)),
            ]),
          ),
          if (lib != null) Icon(Icons.chevron_right, size: 20, color: C.mut),
        ]),
      ),
    );
  }
}

/// A rule with its explanation, for the injury-prevention lists.
class RuleTile extends StatelessWidget {
  final int n;
  final String rule;
  final String detail;
  final Color color;
  const RuleTile(this.n, this.rule, this.detail, {super.key, required this.color});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            width: 24,
            height: 24,
            alignment: Alignment.center,
            margin: const EdgeInsets.only(right: 10, top: 1),
            decoration: BoxDecoration(color: color.withOpacity(0.15), shape: BoxShape.circle),
            child: Text('$n', style: TextStyle(color: color, fontWeight: FontWeight.w800, fontSize: 12)),
          ),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(rule, style: TextStyle(color: C.text, fontWeight: FontWeight.w700, fontSize: 14)),
              Text(detail, style: TextStyle(color: C.text, height: 1.38, fontSize: 13.5)),
            ]),
          ),
        ]),
      );
}
