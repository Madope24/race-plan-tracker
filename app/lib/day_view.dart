import 'package:flutter/material.dart';

import 'exercise_detail.dart';
import 'logic.dart';
import 'sheets.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';
import 'workout_screen.dart';

/// One day of the plan: sessions with every exercise, warm-ups, kegels, targets and the log.
class DayView extends StatelessWidget {
  final AppState st;
  final String iso;
  const DayView({super.key, required this.st, required this.iso});

  @override
  Widget build(BuildContext context) {
    final pd = st.planDay(iso);
    final race = pd['race'];
    final sessions = st.todaySessions(iso);
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(18, 4, 18, 4),
        child: Text('${prettyDate(iso, year: true)} · Week ${asStr(pd['week'])} · ${asStr(pd['week_type']).isEmpty ? '' : '${asStr(pd['week_type'])} week'}',
            style: TextStyle(color: C.mut, fontSize: 13)),
      ),
      if (race != null) Section(title: asStr(race), accent: C.bad, subtitle: 'Race day. The plan for the day is below.', children: const []),
      if (pd['ramadan'] == true)
        Section(title: 'Ramadan', accent: C.warn, children: [
          Text('One light session today, timed around suhoor and iftar. Drink well between iftar and suhoor.', style: TextStyle(color: C.text)),
        ]),
      for (final s in sessions) SessionCard(st: st, iso: iso, item: s),
      if (sessions.isEmpty) Section(title: 'Rest day', children: [Text('Walk, stretch and sleep well.', style: TextStyle(color: C.mut))]),
      if (asStr(pd['warmup']).isNotEmpty)
        Section(title: 'Warm-up stretches', children: [
          for (final line in asStr(pd['warmup']).split('\n'))
            Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(line, style: TextStyle(height: 1.35, color: C.text))),
        ]),
      if (asList(pd['mobility']).isNotEmpty)
        Section(title: 'Mobility', subtitle: pd['knee_care'] == true ? 'Morning routine plus knee care' : 'Morning routine', children: [
          for (final w in asList(st.plan['warmups']).map(asMap).where((w) => asList(pd['mobility']).contains(w['code'])))
          ...[
            Padding(
              padding: const EdgeInsets.only(top: 6, bottom: 2),
              child: Text(asStr(w['title']).toUpperCase(), style: TextStyle(color: C.swim, fontSize: 11.5, fontWeight: FontWeight.w800, letterSpacing: 0.8)),
            ),
            for (final i in asList(w['items']).map(asMap)) RoutineItem(st: st, item: i),
          ],
        ]),
      Section(title: 'Kegels', children: [Text(asStr(pd['kegels']).replaceAll('; ', '\n'), style: TextStyle(height: 1.4, color: C.text))]),
      _logCard(context),
    ]);
  }

  Widget _logCard(BuildContext context) {
    final log = st.log(iso);
    final avg = wavg(st.days, iso);
    Widget numBox(String key, String label, {String? suffix}) =>
        NumField(key: ValueKey('$iso-$key'), label: label, suffix: suffix, value: asNum(log[key]), onChanged: (v) => st.setField(iso, key, v));
    Widget pair(Widget a, Widget b) => Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Row(children: [Expanded(child: a), const SizedBox(width: 10), Expanded(child: b)]),
        );
    return Section(
      title: 'Log this day',
      subtitle: 'Saved on your phone as you type and synced when signed in. 7-day average: ${avg == null ? '-' : '${fmtNum(avg)} kg'}.',
      children: [
        pair(numBox('weight', 'Weight', suffix: 'kg'), numBox('waist', 'Waist', suffix: 'cm')),
        pair(numBox('run_km', 'Run', suffix: 'km'), numBox('run_min', 'Run time', suffix: 'min')),
        pair(numBox('swim_m', 'Swim total', suffix: 'm'), numBox('swim_cont_m', 'Longest non-stop', suffix: 'm')),
        pair(numBox('bike_km', 'Bike', suffix: 'km'), numBox('bike_min', 'Bike time', suffix: 'min')),
        SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: Text('Kegels done', style: TextStyle(color: C.text)),
            value: log['kegels'] == true,
            onChanged: (v) => st.setField(iso, 'kegels', v)),
        SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: Text('Mobility done', style: TextStyle(color: C.text)),
            value: log['mobility'] == true,
            onChanged: (v) => st.setField(iso, 'mobility', v)),
        TextBox(key: ValueKey('$iso-notes'), label: 'Notes (how you felt, PBs)', value: asStr(log['notes']), lines: 3, onChanged: (t) => st.setField(iso, 'notes', t)),
      ],
    );
  }
}

/// A session with all its rows: warm-up stretches, exercises with sets/reps/rest, kegel finisher, cool-down.
class SessionCard extends StatelessWidget {
  final AppState st;
  final String iso;
  final Map<String, dynamic> item;
  const SessionCard({super.key, required this.st, required this.iso, required this.item});

  @override
  Widget build(BuildContext context) {
    final s = asMap(item['session']);
    final rows = asList(s['rows']).map(asMap).toList();
    final ticked = rows.where((r) => st.isDone(iso, asStr(r['id']))).length;
    final disc = asStr(asMap(s['meta'])['discipline']);
    final adj = asMap(item['adjust']);
    final slot = asStr(item['slot']);
    final done = item['done'] == true;
    return Section(
      title: asStr(s['name']),
      accent: C.discipline(disc),
      subtitle: '${asStr(item['when'])} · $ticked of ${rows.length} steps done${item['skipped'] == true ? ' · skipped' : ''}',
      trailing: done ? Icon(Icons.check_circle, color: C.ok) : Icon(disciplineIcon(disc), color: C.discipline(disc)),
      children: [
        Text(asStr(s['summary']), style: TextStyle(height: 1.35, color: C.text)),
        if (asStr(adj['note']).isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('Coach: ${asStr(adj['note'])}', style: TextStyle(color: C.warn, fontSize: 13)),
          ),
        const SizedBox(height: 8),
        Wrap(spacing: 8, runSpacing: 6, children: [
          FilledButton.icon(
            onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(
                builder: (_) => WorkoutScreen(st: st, iso: iso, slot: slot, session: s, adjust: adj.isEmpty ? null : adj))),
            icon: const Icon(Icons.play_arrow),
            label: Text(done ? 'Open' : 'Start'),
          ),
          OutlinedButton(
              onPressed: () => showSheet(context, (ctx) => FeedbackSheet(st: st, iso: iso, slot: slot, session: s)), child: Text(done ? 'Feedback' : 'Mark done')),
          if (slot != 'extra' && !done)
            OutlinedButton(onPressed: () => _move(context, slot), child: const Text('Move')),
          if (slot == 'extra') OutlinedButton(onPressed: () => st.removeExtra(iso, asStr(s['key'])), child: const Text('Remove')),
        ]),
        Theme(
          data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
          child: ExpansionTile(
            tilePadding: EdgeInsets.zero,
            initiallyExpanded: true,
            title: Text('Every exercise, set and rep (${rows.length})', style: TextStyle(fontWeight: FontWeight.w600, color: C.accent)),
            children: [for (final r in rows) _row(context, s, r)],
          ),
        ),
      ],
    );
  }

  Future<void> _move(BuildContext context, String slot) async {
    final options = [for (var i = 1; i <= 6; i++) addDays(iso, i)].where((d) => st.hasDay(d) && st.planDay(d)['fasting'] != true).toList();
    final to = await showDialog<String>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Move this session to'),
        children: [
          for (final d in options)
            SimpleDialogOption(
              onPressed: () => Navigator.pop(ctx, d),
              child: Text('${prettyDate(d)}  (${[st.planDay(d)['am'], st.planDay(d)['pm']].where((k) => k != null).map((k) => asStr(st.session(asStr(k))['name'])).join(' + ')})'),
            ),
        ],
      ),
    );
    if (to != null) {
      st.reschedule(iso, slot, to);
      if (context.mounted) showMsg(context, 'Moved to ${prettyDate(to)}. Avoid stacking two hard sessions on one day.');
    }
  }

  static const _stretchBlocks = {'Warm-up', 'Warm-up on the pool deck', 'Cool-down stretch', 'Cool-down in the water', 'Mobility', 'Hydration', 'Progress', 'Warm-up in the water'};

  /// One exercise, stacked vertically: tick box and name, today's amount, the coach note, then the full how-to.
  Widget _row(BuildContext context, Map<String, dynamic> s, Map<String, dynamic> r) {
    final id = asStr(r['id']);
    final sets = r['sets'];
    final reps = asStr(r['reps']);
    final block = asStr(r['block']);
    final amount = [
      if (sets is num && sets > 1) '$sets x $reps' else if (reps.isNotEmpty) reps,
      if (asStr(r['rest']).isNotEmpty) 'rest ${asStr(r['rest'])}',
    ].join(' · ');
    final logged = st.setsFor(iso, id);
    final lib = st.libraryFor(r);
    final ticked = st.isDone(iso, id);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.fromLTRB(2, 4, 10, 6),
      decoration: BoxDecoration(color: C.card2, borderRadius: BorderRadius.circular(12), border: Border.all(color: C.line)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Checkbox(value: ticked, onChanged: (_) => st.toggleDone(iso, id)),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(block.toUpperCase(), style: TextStyle(color: C.mut, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.6)),
                Text(asStr(r['ex']),
                    style: TextStyle(
                        fontWeight: FontWeight.w700, fontSize: 15, color: ticked ? C.mut : C.text, decoration: ticked ? TextDecoration.lineThrough : null)),
                if (amount.isNotEmpty) Text(amount, style: TextStyle(color: C.accent, fontWeight: FontWeight.w700, fontSize: 13.5)),
                if (asStr(r['note']).isNotEmpty)
                  Padding(padding: const EdgeInsets.only(top: 3), child: Text(asStr(r['note']), style: TextStyle(fontSize: 13, height: 1.35, color: C.mut))),
                if (logged.isNotEmpty)
                  Text('Logged: ${logged.map((x) => '${fmtNum(asNum(x['kg']))} kg x ${fmtNum(asNum(x['reps']), dp: 0)}').join(', ')}',
                      style: TextStyle(fontSize: 12.5, color: C.teal)),
              ]),
            ),
          ),
        ]),
        if (lib != null)
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              tilePadding: const EdgeInsets.only(left: 48),
              childrenPadding: const EdgeInsets.fromLTRB(48, 0, 0, 6),
              initiallyExpanded: !_stretchBlocks.contains(block),
              dense: true,
              title: Text('How to do it: full details', style: TextStyle(color: C.accent, fontWeight: FontWeight.w600, fontSize: 13.5)),
              children: [ExerciseDetail(lib: lib, showName: false)],
            ),
          ),
      ]),
    );
  }
}
