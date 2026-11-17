import 'package:flutter/material.dart';

import 'coach.dart' as coach;
import 'exercise_detail.dart';
import 'sheets.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';
import 'workout_screen.dart';

String paceText(double? minPerKm) {
  if (minPerKm == null || minPerKm <= 0) return '-';
  var m = minPerKm.floor();
  var s = ((minPerKm - m) * 60).round();
  if (s == 60) {
    m += 1;
    s = 0;
  }
  return '$m:${two(s)} per km';
}

String clockText(double minutes) {
  final h = (minutes / 60).floor();
  final m = (minutes % 60).round();
  return h > 0 ? '$h h ${two(m)}' : '$m min';
}

/// Home: the race target, then today's workouts listed top to bottom, exercise by exercise.
class HomeScreen extends StatelessWidget {
  final AppState st;
  final VoidCallback onOpenTraining;
  final VoidCallback onOpenNutrition;
  const HomeScreen({super.key, required this.st, required this.onOpenTraining, required this.onOpenNutrition});

  String _greeting() {
    final h = DateTime.now().hour;
    final name = asStr(st.profile['name']);
    final g = h < 12 ? 'Good morning' : (h < 17 ? 'Good afternoon' : 'Good evening');
    return name.isEmpty ? g : '$g, $name';
  }

  @override
  Widget build(BuildContext context) {
    final iso = st.currentIso;
    final pd = st.planDay(iso);
    final l = st.log(iso);
    final r = st.readiness(iso);
    final sessions = st.todaySessions(iso);
    final pain = st.pain(iso);
    final warn = coach.runLoadWarning(st.days, iso);
    final race = st.nextRace;
    final open = sessions.where((s) => s['done'] != true && s['skipped'] != true).toList();
    return ListView(padding: const EdgeInsets.only(bottom: 28), children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 6),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(prettyDate(todayIso(), year: true).toUpperCase(), style: TextStyle(color: C.mut, fontSize: 12, letterSpacing: 1.1, fontWeight: FontWeight.w700)),
          const SizedBox(height: 2),
          Text(_greeting(), style: TextStyle(color: C.text, fontSize: 26, fontWeight: FontWeight.w800, letterSpacing: -0.6)),
          Text('Week ${asStr(pd['week'])} · ${asStr(pd['phase'])}${pd['fasting'] == true ? ' · fasting day' : ''}', style: TextStyle(color: C.mut)),
        ]),
      ),
      if (st.planPending)
        Section(title: 'Plan update waiting', accent: C.warn, children: [
          Text(
              st.token == null
                  ? 'Your settings changed. Sign in (Profile > Server and sync) so the server can rebuild your plan.'
                  : 'Your settings changed. The new plan arrives at the next sync.',
              style: TextStyle(color: C.text)),
        ]),
      if (st.notify['asked'] != true)
        Section(title: 'Turn on reminders', accent: C.teal, subtitle: 'Workouts, mobility, kegels, bedtime and race countdowns. You choose which in Profile.', children: [
          Row(children: [
            FilledButton.icon(
              icon: const Icon(Icons.notifications_active),
              label: const Text('Turn on'),
              onPressed: () async {
                final ok = await st.enableReminders();
                if (context.mounted) showMsg(context, ok ? 'Reminders are on.' : 'Notifications are blocked. Allow them in the phone settings.');
              },
            ),
            const SizedBox(width: 8),
            TextButton(onPressed: () => st.disableReminders(), child: const Text('Not now')),
          ]),
        ]),
      if (race != null) _raceCard(race),
      if (pd['knee_care'] == true) _kneeCard(context, iso, l),
      _readinessCard(context, iso, r),
      if (pain.isNotEmpty)
        Section(title: 'Pain check', accent: C.bad, children: [
          Text(
              'You reported ${pain.join(', ')} pain on several days. Progression is paused for exercises that load it. '
              'Please see a physiotherapist or doctor if it does not settle within a week, or straight away if it is sharp, swollen or getting worse.',
              style: TextStyle(color: C.text, height: 1.35)),
        ]),
      if (warn != null) Section(title: 'Training load', accent: C.warn, children: [Text(warn, style: TextStyle(color: C.text))]),
      Padding(
        padding: const EdgeInsets.fromLTRB(18, 12, 18, 2),
        child: Text('TODAY\'S WORKOUTS', style: TextStyle(color: C.mut, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1)),
      ),
      if (open.isNotEmpty)
        Padding(
          padding: const EdgeInsets.fromLTRB(14, 6, 14, 4),
          child: FilledButton.icon(
            style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(56)),
            icon: const Icon(Icons.play_arrow_rounded, size: 28),
            label: Text('Start: ${asStr(asMap(open.first['session'])['name'])}', overflow: TextOverflow.ellipsis),
            onPressed: () => _start(context, iso, open.first),
          ),
        ),
      for (final s in sessions) _sessionList(context, iso, s),
      if (sessions.isEmpty)
        Section(title: 'No session today', children: [Text('Rest, walk and stretch. Recovery is part of the programme.', style: TextStyle(color: C.mut))]),
      _mobilityCard(iso, pd, l),
      _kegelCard(iso, pd, l),
      Padding(
        padding: const EdgeInsets.fromLTRB(14, 6, 14, 0),
        child: TileRow([
          StatTile('Streak', '${st.streak(iso)}', sub: 'days with training done', icon: Icons.local_fire_department, color: C.accent),
          StatTile('Sleep', asNum(l['sleep_h']) == null ? '-' : '${fmtNum(asNum(l['sleep_h']))} h', sub: 'target 7 to 9 h', icon: Icons.bedtime, color: C.swim),
        ]),
      ),
      _waterCard(iso, pd, l),
      _foodCard(iso, pd, l),
      if (pd['fasting'] != true)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: SwitchListTile(
            title: Text('I am fasting today', style: TextStyle(color: C.text)),
            subtitle: Text('Swaps demanding sessions for a walk and mobility', style: TextStyle(color: C.mut, fontSize: 12.5)),
            value: l['fasting'] == true,
            onChanged: (v) => st.setField(iso, 'fasting', v ? true : null),
          ),
        ),
    ]);
  }

  // ---------------------------------------------------------------- race target
  Widget _raceCard(Map<String, dynamic> race) {
    final left = daysBetween(todayIso(), asStr(race['date']));
    final t = asNum(race['target_min']);
    final km = asNum(race['run_km']);
    final isRun = asStr(race['type']) == 'run' && km != null && km > 0;
    final longest = st.longestRun;
    final longKm = longest == null ? 0.0 : longest['km'] as double;
    final nowPace = longest == null ? null : longest['pace'] as double?;
    final double? targetPace = (isRun && t != null) ? t / km! : null;
    return Section(
      title: 'Target: ${asStr(race['name'])}',
      accent: C.accent,
      subtitle: prettyDate(asStr(race['date']), year: true),
      trailing: Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
        Text('$left', style: TextStyle(fontSize: 30, fontWeight: FontWeight.w900, color: C.accent, height: 1)),
        Text(left == 1 ? 'day to go' : 'days to go', style: TextStyle(color: C.mut, fontSize: 11.5)),
      ]),
      children: [
        if (t != null)
          TileRow([
            StatTile('Finish under', clockText(t), icon: Icons.flag, color: C.accent),
            if (targetPace != null) StatTile('Target pace', paceText(targetPace).replaceAll(' per km', ''), sub: 'min per km', icon: Icons.speed, color: C.teal),
          ]),
        if (isRun) ...[
          Text('Longest run so far: ${fmtNum(longKm)} of ${fmtNum(km)} km${longest == null ? '' : ' (${prettyDate(asStr(longest['date']))})'}',
              style: TextStyle(color: C.text, fontSize: 13.5)),
          const SizedBox(height: 5),
          Bar(longKm / km!, color: C.accent),
          if (nowPace != null && targetPace != null) ...[
            const SizedBox(height: 8),
            Text(
                nowPace <= targetPace
                    ? 'Your pace on that run was ${paceText(nowPace)}: already at target pace. Now hold it for the full distance.'
                    : 'Your pace on that run was ${paceText(nowPace)}. To hit the target you need ${paceText(targetPace)}: ${((nowPace - targetPace) * 60).round()} s per km faster.',
                style: TextStyle(color: C.mut, fontSize: 13, height: 1.35)),
          ],
        ],
        if (asStr(race['note']).isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text(asStr(race['note']), style: TextStyle(color: C.mut, fontSize: 12.5))),
      ],
    );
  }

  // ---------------------------------------------------------------- knee care
  Widget _kneeCard(BuildContext context, String iso, Map<String, dynamic> l) {
    final inj = asMap(st.plan['injury']);
    final score = asNum(l['knee_pain']);
    return Section(
      title: 'Knee care is on',
      accent: C.warn,
      subtitle: 'Long run held, no sprints or hills, knee-friendly strength, knee routine every day.',
      children: [
        Text('How is the knee today? ${score == null ? 'Tap a number' : '${score.round()} out of 10'}', style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        Wrap(spacing: 6, runSpacing: 6, children: [
          for (var i = 0; i <= 6; i++)
            ChoiceChip(
              label: Text(i == 6 ? '6+' : '$i'),
              selected: score != null && (i == 6 ? score >= 6 : score.round() == i),
              showCheckmark: false,
              onSelected: (_) => st.setKnee(iso, i.toDouble()),
            ),
        ]),
        const SizedBox(height: 8),
        Text(
            score == null
                ? '0 = nothing, 1 to 2 = a small pinch that does not grow, 3 or more = pain that changes how you move.'
                : score >= 3
                    ? 'Do not run today. Walk or swim instead, do the knee routine, and book a physiotherapist or doctor if it is like this on a second day.'
                    : 'Fine to train. Keep to flat ground and stop if it reaches 3.',
            style: TextStyle(color: score != null && score >= 3 ? C.bad : C.mut, fontSize: 13, height: 1.35)),
        Theme(
          data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
          child: ExpansionTile(
            tilePadding: EdgeInsets.zero,
            title: Text('What to do about it', style: TextStyle(color: C.accent, fontWeight: FontWeight.w600, fontSize: 13.5)),
            children: [for (final a in asList(inj['advice'])) Para('', '· ${asStr(a)}')],
          ),
        ),
      ],
    );
  }

  Widget _readinessCard(BuildContext context, String iso, Map<String, dynamic> r) {
    final level = asStr(r['level']);
    final score = asNum(r['score']);
    final col = statusColor(level);
    return Section(title: 'Readiness', children: [
      Row(children: [
        Ring(value: score == null ? 0 : score / 100, label: score == null ? '?' : '${score.round()}', sub: score == null ? 'check in' : level, color: col, size: 78),
        const SizedBox(width: 14),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(asStr(r['message']), style: TextStyle(color: C.text, fontWeight: FontWeight.w600, height: 1.3)),
            for (final s in asList(r['signals'])) Text('· ${asStr(s)}', style: TextStyle(color: C.mut, fontSize: 12.5)),
          ]),
        ),
      ]),
      const SizedBox(height: 8),
      Align(
        alignment: Alignment.centerLeft,
        child: OutlinedButton.icon(
          icon: const Icon(Icons.favorite_border),
          label: Text(r['checked_in'] == true ? 'Edit check-in' : 'Morning check-in'),
          onPressed: () => showSheet(context, (ctx) => CheckInSheet(st: st, iso: iso)),
        ),
      ),
    ]);
  }

  void _start(BuildContext context, String iso, Map<String, dynamic> s) {
    Navigator.of(context).push(MaterialPageRoute<void>(
        builder: (_) => WorkoutScreen(st: st, iso: iso, slot: asStr(s['slot']), session: asMap(s['session']), adjust: s['adjust'] == null ? null : asMap(s['adjust']))));
  }

  // ---------------------------------------------------------------- a workout, every step listed top to bottom
  Widget _sessionList(BuildContext context, String iso, Map<String, dynamic> s) {
    final ses = asMap(s['session']);
    final disc = asStr(asMap(ses['meta'])['discipline']);
    final col = C.discipline(disc);
    final adj = asMap(s['adjust']);
    final action = asStr(adj['action']);
    final done = s['done'] == true;
    final skipped = s['skipped'] == true;
    final rows = asList(ses['rows']).map(asMap).toList();
    final ticked = rows.where((r) => st.isDone(iso, asStr(r['id']))).length;
    final lines = <Widget>[];
    var block = '';
    for (final r in rows) {
      final b = asStr(r['block']);
      if (b != block) {
        block = b;
        lines.add(Padding(
          padding: const EdgeInsets.only(top: 10, bottom: 2),
          child: Text(b.toUpperCase(), style: TextStyle(color: col, fontSize: 11.5, fontWeight: FontWeight.w800, letterSpacing: 0.8)),
        ));
      }
      lines.add(_rowLine(context, iso, r));
    }
    return Section(
      title: asStr(ses['name']),
      subtitle: '${asStr(s['when'])} · $ticked of ${rows.length} done${skipped ? ' · skipped' : ''}',
      accent: col,
      trailing: done ? Icon(Icons.check_circle, color: C.ok) : Icon(disciplineIcon(disc), color: col),
      children: [
        if (asStr(adj['note']).isNotEmpty)
          Container(
            padding: const EdgeInsets.all(10),
            margin: const EdgeInsets.only(bottom: 4),
            decoration: BoxDecoration(color: (action == 'as planned' ? C.teal : C.warn).withOpacity(0.13), borderRadius: BorderRadius.circular(10)),
            child: Text('${action == 'as planned' ? 'Coach' : 'Coach says $action'}: ${asStr(adj['note'])}', style: TextStyle(color: C.text, fontSize: 13)),
          ),
        ...lines,
        const SizedBox(height: 10),
        Wrap(spacing: 8, runSpacing: 6, children: [
          if (!done) FilledButton.icon(onPressed: () => _start(context, iso, s), icon: const Icon(Icons.play_arrow), label: const Text('Start guided')),
          OutlinedButton(
            onPressed: () => showSheet(context, (ctx) => FeedbackSheet(st: st, iso: iso, slot: asStr(s['slot']), session: ses)),
            child: Text(done ? 'Edit feedback' : 'Mark done'),
          ),
        ]),
      ],
    );
  }

  Widget _rowLine(BuildContext context, String iso, Map<String, dynamic> r) {
    final id = asStr(r['id']);
    final sets = r['sets'];
    final reps = asStr(r['reps']);
    final rest = asStr(r['rest']);
    final amount = [
      if (sets is num && sets > 1) '$sets x $reps' else if (reps.isNotEmpty) reps,
      if (rest.isNotEmpty) 'rest $rest',
    ].join(' · ');
    final lib = st.libraryFor(r);
    final ticked = st.isDone(iso, id);
    return InkWell(
      onTap: lib == null ? null : () => showExercise(context, lib, row: r),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          SizedBox(width: 36, height: 36, child: Checkbox(value: ticked, onChanged: (_) => st.toggleDone(iso, id))),
          const SizedBox(width: 4),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(top: 7),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(asStr(r['ex']),
                    style: TextStyle(color: ticked ? C.mut : C.text, fontSize: 14, fontWeight: FontWeight.w600, decoration: ticked ? TextDecoration.lineThrough : null)),
                if (amount.isNotEmpty) Text(amount, style: TextStyle(color: C.accent, fontSize: 13, fontWeight: FontWeight.w700)),
              ]),
            ),
          ),
          if (lib != null) Padding(padding: const EdgeInsets.only(top: 8), child: Icon(Icons.chevron_right, size: 20, color: C.mut)),
        ]),
      ),
    );
  }

  // ---------------------------------------------------------------- mobility and kegels
  Widget _mobilityCard(String iso, Map<String, dynamic> pd, Map<String, dynamic> l) {
    final codes = asList(pd['mobility']).map(asStr).toList();
    final routines = asList(st.plan['warmups']).map(asMap).where((w) => codes.contains(asStr(w['code']))).toList();
    if (routines.isEmpty) return const SizedBox.shrink();
    final done = l['mobility'] == true;
    return Section(
      title: 'Mobility',
      subtitle: [
        'Morning routine (7 min)',
        if (pd['knee_care'] == true) 'knee care (8 min)',
        if (codes.contains('SHOULDER')) 'shoulder care before the swim (6 min)',
      ].join(' + ') + '. Tap any move for how to do it.',
      accent: C.swim,
      trailing: Checkbox(value: done, onChanged: (v) => st.setField(iso, 'mobility', v == true ? true : null)),
      children: [
        for (final w in routines) ...[
          Padding(
            padding: const EdgeInsets.only(top: 6, bottom: 2),
            child: Text(asStr(w['title']).toUpperCase(), style: TextStyle(color: C.swim, fontSize: 11.5, fontWeight: FontWeight.w800, letterSpacing: 0.8)),
          ),
          for (final i in asList(w['items']).map(asMap)) RoutineItem(st: st, item: i),
        ],
      ],
    );
  }

  Widget _kegelCard(String iso, Map<String, dynamic> pd, Map<String, dynamic> l) {
    final parts = asStr(pd['kegels']).split(': ');
    final head = parts.first;
    final items = parts.length > 1 ? parts.sublist(1).join(': ').split('; ') : <String>[];
    return Section(
      title: 'Kegels',
      subtitle: head,
      accent: C.teal,
      trailing: Checkbox(value: l['kegels'] == true, onChanged: (v) => st.setField(iso, 'kegels', v == true ? true : null)),
      children: [
        for (final i in items) Padding(padding: const EdgeInsets.symmetric(vertical: 3), child: Text(i, style: TextStyle(color: C.text, fontSize: 14))),
        Text('Relax fully between squeezes. Never hold your breath.', style: TextStyle(color: C.mut, fontSize: 12.5)),
      ],
    );
  }

  Widget _waterCard(String iso, Map<String, dynamic> pd, Map<String, dynamic> l) {
    final target = asNum(pd['water_l']) ?? 3.5;
    final w = asNum(l['water']) ?? 0.0;
    return Section(title: 'Hydration', subtitle: pd['fasting'] == true ? 'Fasting day: drink after breaking the fast, slowly' : null, children: [
      Row(children: [
        Text('${fmtNum(w)} / ${fmtNum(target)} L', style: TextStyle(color: C.text, fontSize: 18, fontWeight: FontWeight.w800)),
        const Spacer(),
        OutlinedButton(onPressed: () => st.addWater(iso, 0.25), child: const Text('+250 ml')),
        const SizedBox(width: 6),
        OutlinedButton(onPressed: () => st.addWater(iso, 0.5), child: const Text('+500 ml')),
      ]),
      const SizedBox(height: 8),
      Bar(w / target, color: C.swim),
    ]);
  }

  Widget _foodCard(String iso, Map<String, dynamic> pd, Map<String, dynamic> l) {
    final k = asNum(l['kcal']) ?? 0.0;
    final p = asNum(l['protein']) ?? 0.0;
    final kt = asNum(pd['kcal']) ?? 1.0;
    final pt = asNum(pd['protein']) ?? 1.0;
    return Section(
      title: 'Nutrition',
      subtitle: pd['fasting'] == true ? 'Fasting: eat after ${asStr(asMap(st.effective('fasting'))['break_time'])}' : 'No breakfast. Tap meals as you eat them.',
      trailing: TextButton(onPressed: onOpenNutrition, child: const Text('Meals')),
      children: [
        Row(children: [
          Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Calories ${k.round()} / ${kt.round()}', style: TextStyle(color: C.text, fontSize: 13)),
            const SizedBox(height: 4),
            Bar(k / kt, color: C.accent),
          ])),
          const SizedBox(width: 12),
          Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Protein ${p.round()} / ${pt.round()} g', style: TextStyle(color: C.text, fontSize: 13)),
            const SizedBox(height: 4),
            Bar(p / pt, color: C.teal),
          ])),
        ]),
      ],
    );
  }
}
