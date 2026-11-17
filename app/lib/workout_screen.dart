import 'dart:async';

import 'package:flutter/material.dart';

import 'exercise_detail.dart';
import 'sheets.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

/// Guided workout: one step at a time, with the instructions, set logging, a rest timer, pause, skip and finish.
class WorkoutScreen extends StatefulWidget {
  final AppState st;
  final String iso;
  final String slot;
  final Map<String, dynamic> session;
  final Map<String, dynamic>? adjust;
  const WorkoutScreen({super.key, required this.st, required this.iso, required this.slot, required this.session, this.adjust});

  @override
  State<WorkoutScreen> createState() => _WorkoutScreenState();
}

int restSeconds(String rest) {
  final m = RegExp(r'(\d+)\s*(s|min)').firstMatch(rest);
  if (m == null) return 0;
  final v = int.parse(m.group(1)!);
  return m.group(2) == 'min' ? v * 60 : v;
}

class _WorkoutScreenState extends State<WorkoutScreen> {
  int step = 0;
  int elapsed = 0;
  bool paused = false;
  int restLeft = 0;
  Timer? _tick;

  List<Map<String, dynamic>> get rows => asList(widget.session['rows']).map(asMap).toList();

  @override
  void initState() {
    super.initState();
    final firstOpen = rows.indexWhere((r) => !widget.st.isDone(widget.iso, asStr(r['id'])));
    step = firstOpen < 0 ? 0 : firstOpen;
    _tick = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || paused) return;
      setState(() {
        elapsed++;
        if (restLeft > 0) restLeft--;
      });
    });
  }

  @override
  void dispose() {
    _tick?.cancel();
    super.dispose();
  }

  String _clock(int s) => '${two(s ~/ 60)}:${two(s % 60)}';

  void _next({bool mark = true}) {
    final r = rows[step];
    if (mark && !widget.st.isDone(widget.iso, asStr(r['id']))) widget.st.toggleDone(widget.iso, asStr(r['id']));
    if (step < rows.length - 1) {
      setState(() => step++);
    } else {
      _finish();
    }
  }

  Future<void> _finish() async {
    final st = widget.st;
    await showSheet(context, (ctx) => FeedbackSheet(st: st, iso: widget.iso, slot: widget.slot, session: widget.session, minutes: (elapsed / 60).round()));
    if (widget.slot == 'extra') {
      final id = '${asStr(widget.session['key'])}:done';
      if (!st.isDone(widget.iso, id)) st.toggleDone(widget.iso, id);
    }
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final st = widget.st;
    final r = rows[step];
    final disc = asStr(asMap(widget.session['meta'])['discipline']);
    final col = C.discipline(disc);
    final lib = st.libraryFor(r);
    final canLog = widget.session['strength'] == true && ['Main', 'Accessory', 'Core', 'Station'].contains(r['block']);
    final sets = r['sets'];
    final reps = asStr(r['reps']);
    final rest = asStr(r['rest']);
    final adj = widget.adjust;
    return Scaffold(
      appBar: AppBar(
        title: Text(asStr(widget.session['name']), overflow: TextOverflow.ellipsis),
        actions: [
          Center(child: Text(_clock(elapsed), style: TextStyle(fontWeight: FontWeight.w800, color: paused ? C.warn : C.text, fontSize: 16))),
          IconButton(
            tooltip: paused ? 'Resume' : 'Pause',
            icon: Icon(paused ? Icons.play_arrow : Icons.pause),
            onPressed: () => setState(() => paused = !paused),
          ),
        ],
      ),
      body: ListenableBuilder(
        listenable: st,
        builder: (context, _) => ListView(padding: const EdgeInsets.only(bottom: 120), children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Bar((step + 1) / rows.length, color: col, height: 6),
              const SizedBox(height: 6),
              Text('Step ${step + 1} of ${rows.length} · ${asStr(r['block'])}', style: TextStyle(color: C.mut)),
            ]),
          ),
          if (adj != null && asStr(adj['note']).isNotEmpty)
            Section(title: adj['action'] == 'as planned' ? 'Coach note' : 'Coach: ${asStr(adj['action'])} today', accent: C.warn, children: [
              Text(asStr(adj['note']), style: TextStyle(color: C.text, height: 1.35)),
            ]),
          Section(
            title: asStr(r['ex']),
            accent: col,
            subtitle: [
              if (sets is num && sets > 1) '$sets sets x $reps' else if (reps.isNotEmpty) reps,
              if (rest.isNotEmpty) 'rest $rest',
            ].join(' · '),
            children: [
              if (asStr(r['note']).isNotEmpty) Text(asStr(r['note']), style: TextStyle(color: C.text, height: 1.4)),
              if (lib != null) ...[
                const SizedBox(height: 10),
                ExerciseDetail(lib: lib, showName: false),
              ],
            ],
          ),
          if (canLog) _SetPanel(key: ValueKey('sp-${asStr(r['id'])}'), st: st, iso: widget.iso, row: r, onSetSaved: () => setState(() => restLeft = restSeconds(rest))),
          if (restLeft > 0)
            Section(title: 'Rest', accent: C.teal, children: [
              Row(children: [
                Text(_clock(restLeft), style: TextStyle(fontSize: 34, fontWeight: FontWeight.w800, color: C.teal)),
                const Spacer(),
                OutlinedButton(onPressed: () => setState(() => restLeft = 0), child: const Text('Skip rest')),
              ]),
            ]),
          Section(title: 'Coming up', children: [
            for (var i = step + 1; i < rows.length && i <= step + 4; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text('${asStr(rows[i]['ex'])}  ${rows[i]['sets'] is num && (rows[i]['sets'] as num) > 1 ? '${rows[i]['sets']} x ' : ''}${asStr(rows[i]['reps'])}',
                    style: TextStyle(color: C.mut)),
              ),
            if (step >= rows.length - 1) Text('Last step. Finish to record how it went.', style: TextStyle(color: C.mut)),
          ]),
        ]),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
          child: Row(children: [
            IconButton.outlined(onPressed: step > 0 ? () => setState(() => step--) : null, icon: const Icon(Icons.chevron_left)),
            const SizedBox(width: 8),
            OutlinedButton(onPressed: () => _next(mark: false), child: const Text('Skip')),
            const SizedBox(width: 8),
            Expanded(
              child: FilledButton(
                onPressed: () => _next(),
                child: Text(step < rows.length - 1 ? 'Done, next' : 'Finish workout'),
              ),
            ),
          ]),
        ),
      ),
    );
  }
}

class _SetPanel extends StatefulWidget {
  final AppState st;
  final String iso;
  final Map<String, dynamic> row;
  final VoidCallback onSetSaved;
  const _SetPanel({super.key, required this.st, required this.iso, required this.row, required this.onSetSaved});

  @override
  State<_SetPanel> createState() => _SetPanelState();
}

class _SetPanelState extends State<_SetPanel> {
  late List<Map<String, dynamic>> sets;

  @override
  void initState() {
    super.initState();
    sets = widget.st.setsFor(widget.iso, asStr(widget.row['id']));
    final n = widget.row['sets'] is num ? (widget.row['sets'] as num).toInt() : 3;
    while (sets.length < n) {
      sets.add(<String, dynamic>{'kg': null, 'reps': null, 'rpe': null});
    }
  }

  void _save() {
    final clean = sets.where((x) => x['kg'] != null || x['reps'] != null).toList();
    widget.st.saveSets(widget.iso, asStr(widget.row['id']), asStr(widget.row['ex']), clean);
  }

  @override
  Widget build(BuildContext context) {
    final sug = widget.st.progressionFor(asStr(widget.row['ex']), asStr(widget.row['reps']), widget.iso);
    return Section(title: 'Log your sets', subtitle: 'Load in kg (bodyweight = 0), reps, and effort (RPE 1 to 10).', children: [
      Container(
        padding: const EdgeInsets.all(10),
        margin: const EdgeInsets.only(bottom: 10),
        decoration: BoxDecoration(color: C.card2, borderRadius: BorderRadius.circular(10)),
        child: Row(children: [
          Icon(Icons.trending_up, color: sug['action'] == 'hold' ? C.warn : C.teal, size: 18),
          const SizedBox(width: 8),
          Expanded(child: Text(asStr(sug['text']), style: TextStyle(color: C.text, fontSize: 13))),
        ]),
      ),
      for (var i = 0; i < sets.length; i++)
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(children: [
            SizedBox(width: 44, child: Text('Set ${i + 1}', style: TextStyle(color: C.mut))),
            Expanded(child: NumField(key: ValueKey('kg-$i'), label: 'kg', value: asNum(sets[i]['kg']), onChanged: (v) => sets[i]['kg'] = v)),
            const SizedBox(width: 6),
            Expanded(child: NumField(key: ValueKey('reps-$i'), label: 'Reps', value: asNum(sets[i]['reps']), onChanged: (v) => sets[i]['reps'] = v)),
            const SizedBox(width: 6),
            Expanded(child: NumField(key: ValueKey('rpe-$i'), label: 'RPE', value: asNum(sets[i]['rpe']), onChanged: (v) => sets[i]['rpe'] = v)),
            IconButton(
              tooltip: 'Save set and start rest',
              icon: Icon(Icons.check_circle, color: C.ok),
              onPressed: () {
                _save();
                widget.onSetSaved();
              },
            ),
          ]),
        ),
      Row(children: [
        TextButton.icon(onPressed: () => setState(() => sets.add(<String, dynamic>{'kg': null, 'reps': null, 'rpe': null})), icon: const Icon(Icons.add), label: const Text('Add set')),
        const Spacer(),
        TextButton(onPressed: _save, child: const Text('Save all')),
      ]),
    ]);
  }
}
