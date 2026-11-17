import 'package:flutter/material.dart';

import 'day_view.dart';
import 'library_pages.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

/// Training: the week as a vertical list of days, each with its sessions; tap a day for every exercise.
class TrainingScreen extends StatefulWidget {
  final AppState st;
  const TrainingScreen({super.key, required this.st});

  @override
  State<TrainingScreen> createState() => _TrainingScreenState();
}

class _TrainingScreenState extends State<TrainingScreen> {
  late String monday = _monday(widget.st.currentIso);

  String _monday(String d) => addDays(d, -(dateOf(d).weekday - 1));

  void _openDay(String iso) {
    final st = widget.st;
    Navigator.of(context).push(MaterialPageRoute<void>(
        builder: (_) => Scaffold(
              appBar: AppBar(title: Text(prettyDate(iso, year: true))),
              body: ListenableBuilder(listenable: st, builder: (context, _) => ListView(padding: const EdgeInsets.only(bottom: 28), children: [DayView(st: st, iso: iso)])),
            )));
  }

  @override
  Widget build(BuildContext context) {
    final st = widget.st;
    final pages = Pages(st);
    final week = [for (var i = 0; i < 7; i++) addDays(monday, i)];
    final inPlan = week.where(st.hasDay).toList();
    final wk = inPlan.isEmpty ? <String, dynamic>{} : asMap(asList(st.plan['weeks']).map(asMap).firstWhere((w) => w['week'] == st.planDay(inPlan.first)['week'], orElse: () => <String, dynamic>{}));
    void go(String title, List<Widget> Function() body) => pushPage(context, title, st, body);
    final coaches = <List<Object>>[
      ['Running', Icons.directions_run, C.accent, () => go('Running coach', pages.running)],
      ['Swimming', Icons.pool, C.swim, () => go('Swimming coach', pages.swimming)],
      ['Cycling', Icons.directions_bike, C.bike, () => go('Cycling', pages.cycling)],
      ['Strength', Icons.fitness_center, C.teal, () => go('Strength', () => pages.strength(context))],
      ['HYROX', Icons.bolt, C.hyrox, () => go('HYROX', pages.hyrox)],
      ['Mobility', Icons.self_improvement, C.mut, () => go('Mobility', pages.mobility)],
      ['Pelvic floor', Icons.favorite_border, C.mut, () => go('Pelvic floor', pages.pelvic)],
      ['Library', Icons.menu_book, C.mut, () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => LibraryPage(st: st)))],
      ['Full plan', Icons.calendar_view_month, C.mut, () => go('Full plan', () => pages.fullPlan((d) {
            Navigator.of(context).pop();
            setState(() => monday = _monday(d));
            _openDay(d);
          }))],
    ];
    return ListView(padding: const EdgeInsets.only(bottom: 28), children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(6, 2, 6, 0),
        child: Row(children: [
          IconButton(
              icon: const Icon(Icons.chevron_left),
              onPressed: st.hasDay(addDays(monday, -1)) ? () => setState(() => monday = addDays(monday, -7)) : null),
          Expanded(
            child: Column(children: [
              Text('Week of ${prettyDate(monday)}', style: TextStyle(color: C.text, fontWeight: FontWeight.w800, fontSize: 16)),
              if (wk.isNotEmpty) Text('Week ${asStr(wk['week'])} · ${asStr(wk['phase'])} · ${asStr(wk['type'])}', textAlign: TextAlign.center, style: TextStyle(color: C.mut, fontSize: 12.5)),
            ]),
          ),
          IconButton(
              icon: const Icon(Icons.chevron_right),
              onPressed: st.hasDay(addDays(monday, 7)) ? () => setState(() => monday = addDays(monday, 7)) : null),
        ]),
      ),
      if (monday != _monday(st.currentIso))
        Center(child: TextButton(onPressed: () => setState(() => monday = _monday(st.currentIso)), child: const Text('Back to this week'))),
      for (final d in week)
        if (st.hasDay(d)) _dayCard(d),
      if (inPlan.isEmpty) const EmptyState(Icons.event_busy, 'Outside the plan', 'Choose another week.'),
      Padding(
        padding: const EdgeInsets.fromLTRB(18, 14, 18, 6),
        child: Text('COACHES AND GUIDES', style: TextStyle(color: C.mut, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1)),
      ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.25,
          children: [
            for (final c in coaches)
              InkWell(
                borderRadius: BorderRadius.circular(14),
                onTap: c[3] as VoidCallback,
                child: Container(
                  decoration: BoxDecoration(color: C.card, borderRadius: BorderRadius.circular(14), border: Border.all(color: C.line)),
                  child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                    Icon(c[1] as IconData, color: c[2] as Color),
                    const SizedBox(height: 6),
                    Text(c[0] as String, style: TextStyle(color: C.text, fontWeight: FontWeight.w600, fontSize: 13)),
                  ]),
                ),
              ),
          ],
        ),
      ),
    ]);
  }

  /// One day: the date on the left, its sessions stacked top to bottom on the right.
  Widget _dayCard(String d) {
    final st = widget.st;
    final pd = st.planDay(d);
    final today = d == todayIso();
    final items = st.todaySessions(d);
    final date = dateOf(d);
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 5, 14, 5),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => _openDay(d),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: C.card,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: today ? C.accent : C.line, width: today ? 1.6 : 1),
          ),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            SizedBox(
              width: 50,
              child: Column(children: [
                Text(kWeekdays[date.weekday - 1].toUpperCase(), style: TextStyle(color: today ? C.accent : C.mut, fontSize: 11.5, fontWeight: FontWeight.w800)),
                Text('${date.day}', style: TextStyle(color: C.text, fontSize: 24, fontWeight: FontWeight.w800, height: 1.1)),
                if (today) Text('today', style: TextStyle(color: C.accent, fontSize: 10.5)),
              ]),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                if (pd['race'] != null)
                  Padding(padding: const EdgeInsets.only(bottom: 4), child: Text(asStr(pd['race']), style: TextStyle(color: C.bad, fontWeight: FontWeight.w800))),
                for (final s in items) _sessionLine(s),
                if (items.isEmpty) Text('Rest day', style: TextStyle(color: C.mut)),
                if (pd['fasting'] == true && pd['race'] == null) Padding(padding: const EdgeInsets.only(top: 2), child: Pill('fasting', color: C.warn)),
              ]),
            ),
            Icon(Icons.chevron_right, color: C.mut),
          ]),
        ),
      ),
    );
  }

  Widget _sessionLine(Map<String, dynamic> s) {
    final ses = asMap(s['session']);
    final disc = asStr(asMap(ses['meta'])['discipline']);
    final done = s['done'] == true;
    final slot = asStr(s['slot']);
    final adj = asMap(s['adjust']);
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(done ? Icons.check_circle : disciplineIcon(disc), size: 18, color: done ? C.ok : C.discipline(disc)),
        const SizedBox(width: 8),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(asStr(ses['name']), style: TextStyle(color: C.text, fontWeight: FontWeight.w600, fontSize: 14)),
            Text(
                '${slot == 'am' ? 'Morning' : (slot == 'pm' ? 'Evening' : 'Moved here')}${asStr(adj['action']).isNotEmpty && adj['action'] != 'as planned' ? ' · coach: ${asStr(adj['action'])}' : ''}${s['skipped'] == true ? ' · skipped' : ''}',
                style: TextStyle(color: C.mut, fontSize: 12)),
            Text(asStr(ses['summary']), maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: C.mut, fontSize: 12.5, height: 1.3)),
          ]),
        ),
      ]),
    );
  }
}
