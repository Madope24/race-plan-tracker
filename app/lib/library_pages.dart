import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'exercise_detail.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

/// Coach and reference pages: running, swimming, cycling, strength, HYROX, mobility, pelvic floor, sleep, Tanzania.
class Pages {
  final AppState st;
  Pages(this.st);

  Map<String, dynamic> get p => st.plan;
  List<Map<String, dynamic>> _l(String k) => asList(p[k]).map(asMap).toList();

  Widget _routine(String code) {
    final w = _l('warmups').firstWhere((x) => x['code'] == code, orElse: () => <String, dynamic>{});
    if (w.isEmpty) return const SizedBox.shrink();
    return Section(title: asStr(w['title']), subtitle: 'Tap any move for how to do it.', children: [for (final i in asList(w['items']).map(asMap)) RoutineItem(st: st, item: i)]);
  }

  List<Widget> _weekTable(String field, String unit, String title, {String Function(num)? fmt}) {
    final ws = _l('weeks').where((w) => w[field] != null).toList();
    return [
      Section(title: title, children: [
        BarChart(values: ws.map((w) => (asNum(w[field]) ?? 0.0).toDouble()).toList(), labels: ws.map((w) => 'W${asStr(w['week'])}').toList(), unit: unit),
        const SizedBox(height: 8),
        for (final w in ws)
          KV('Week ${asStr(w['week'])} · ${prettyDate(asStr(w['start']))}',
              '${fmt != null ? fmt(asNum(w[field])!) : '${fmtNum(asNum(w[field]))} $unit'} · ${asStr(w['type'])}'),
      ]),
    ];
  }

  List<Widget> running() {
    final hr = asNum(asMap(st.effective('profile'))['max_hr']) ?? 194;
    final b = asMap(st.effective('baseline'));
    return [
      Section(title: 'How your running is built', children: [
        Para('Aerobic first', 'Most runs are easy: you can talk in full sentences. Speed work is short and controlled. Mileage grows by at most 1.5 to 2 km on the long run per week, with an easier week every 4th week.'),
        Para('Run-walk is training', 'Walk breaks keep the effort easy and let you go further. They are planned into long runs and races.'),
        Para('Your race targets', '10 km on 5 December under 1 h 40 (10:00 per km) and the Kilimanjaro half on 7 February under 3 h (8:32 per km). These are race-day goals: only the race-pace practice runs use them. Everything else is run by effort.'),
        Para('Heat', 'In Dar you run 30 to 60 s per km slower at the same effort. Start before 06:30 and go by effort and heart rate.'),
      ]),
      Section(title: 'Heart-rate guide', subtitle: 'From a maximum of ${hr.round()} bpm. Update it in Profile if a test or race shows higher.', children: [
        KV('Easy / long', '${(hr * 0.67).round()} to ${(hr * 0.75).round()} bpm'),
        KV('Steady', '${(hr * 0.75).round()} to ${(hr * 0.82).round()} bpm'),
        KV('Hard intervals', '${(hr * 0.82).round()} to ${(hr * 0.89).round()} bpm'),
      ]),
      Section(title: 'Your baseline', subtitle: 'From Activities.csv and your logs', children: [
        KV('Longest run', '${fmtNum(asNum(b['long_run_km']))} km (${prettyDate(asStr(b['long_run_date']))})'),
        KV('Average pace', '${fmtNum(asNum(b['run_pace_min_km']))} min/km, walking included'),
        KV('Fastest pace seen', '${fmtNum(asNum(b['run_best_pace_min_km']))} min/km'),
        KV('Average heart rate', '${fmtNum(asNum(b['run_avg_hr']), dp: 0)} bpm'),
      ]),
      ..._weekTable('long_run_km', 'km', 'Long-run progression'),
      _rules('Avoiding running injuries', 'running', C.accent),
      _stopSigns(),
      _routine('W-RUN'),
      _routine('C-RUN'),
      _routine('KNEE'),
    ];
  }

  List<Widget> swimming() => [
        Section(title: 'Swimming programme', subtitle: 'Evenings only, never on a run day', children: [
          Para('Phase 1: November', 'Technique, breathing every 3 strokes, longer non-stop swims, efficient stroke mechanics.'),
          Para('Phase 2: December to January', 'Structured intervals (100 m and 200 m repeats), aerobic endurance, stroke efficiency (count strokes per length).'),
          Para('Phase 3: February to March', 'Longer endurance swims, pacing, and the 1,500 m non-stop test after Ramadan. Then open-water skills for the triathlons.'),
          Para('What to log', 'Distance, time, longest non-stop swim, strokes and SWOLF from your watch. Pace per 100 m comes from distance and time.'),
          Para('Open water', 'Calm water near the shore, with a buddy and a bright tow-float, before sunset. Never alone.'),
        ]),
        Section(
          title: 'Swim drills',
          subtitle: 'Two drills in every technique swim, rotating week by week. Each one in full: why, set-up, steps, breathing, cues, mistakes, easier and harder.',
          children: [
            for (final n in asList(p['swim_drills']).map(asStr))
              if (st.libraryEntry(n) != null)
                ExpansionTile(
                    shape: const Border(),
                    collapsedShape: const Border(),
                    tilePadding: EdgeInsets.zero,
                    title: Text(n, style: TextStyle(color: C.text, fontWeight: FontWeight.w700)),
                    subtitle: Text('${asStr(st.libraryEntry(n)!['muscles'])} · ${asStr(st.libraryEntry(n)!['dose'])}', style: TextStyle(color: C.mut, fontSize: 12.5)),
                    childrenPadding: const EdgeInsets.only(bottom: 10),
                    children: [ExerciseDetail(lib: st.libraryEntry(n)!, showName: false)],
                ),
          ],
        ),
        _rules('Avoiding swimming injuries', 'swimming', C.swim),
        _routine('SHOULDER'),
        ..._weekTable('swim_cont_m', 'm', 'Friday non-stop swim progression'),
        _routine('W-SWIM'),
        _routine('C-SWIM'),
        _stopSigns(),
      ];

  Widget _rules(String title, String key, Color color) {
    final rules = asList(asMap(p['injury_prevention'])[key]).map(asMap).toList();
    if (rules.isEmpty) return const SizedBox.shrink();
    return Section(title: title, children: [
      for (var i = 0; i < rules.length; i++) RuleTile(i + 1, asStr(rules[i]['rule']), asStr(rules[i]['detail']), color: color),
    ]);
  }

  Widget _stopSigns() {
    final ip = asMap(p['injury_prevention']);
    if (ip.isEmpty) return const SizedBox.shrink();
    return Section(title: 'Stop and get it checked', accent: C.bad, children: [
      for (final t in asList(ip['stop_signs']).map(asStr))
        Padding(
          padding: const EdgeInsets.only(bottom: 5),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Padding(padding: const EdgeInsets.only(top: 2, right: 8), child: Icon(Icons.warning_amber_rounded, size: 18, color: C.bad)),
            Expanded(child: Text(t, style: TextStyle(color: C.text, height: 1.35))),
          ]),
        ),
      const SizedBox(height: 4),
      Text(asStr(ip['stop_action']), style: TextStyle(color: C.text, height: 1.38, fontWeight: FontWeight.w600)),
    ]);
  }

  List<Widget> cycling() {
    final ck = asMap(p['bike_checklists']);
    final start = asStr(st.effective('bike_start'));
    return [
      Section(title: 'Cycling', subtitle: 'Starts ${prettyDate(start, year: true)}, after Ramadan. Nothing on a bike before that.', children: [
        Para('Before the bike starts', 'Strength (single-leg work, hamstrings, core), running and swimming build the engine and the hips you need on the bike.'),
        Para('From March', 'Easy rides and bike handling first, cadence drills (80 to 95 turns a minute), then tempo, hills, long rides and bike-run bricks. The long ride grows about 15 min a week toward 3 h 15 for the 90 km 70.3 bike.'),
        Para('Fuelling', 'Rides over 75 min: eat and drink from 30 min. Build from 30 g carbs an hour to 60 to 90 g by July.'),
      ]),
      ..._weekTable('ride_min', 'min', 'Long-ride progression'),
      Section(title: 'Equipment checklist', children: [for (final i in asList(ck['equipment'])) Text('□ ${asStr(i)}', style: TextStyle(color: C.text, height: 1.6))]),
      Section(title: 'Before every ride', children: [for (final i in asList(ck['before_every_ride'])) Text('□ ${asStr(i)}', style: TextStyle(color: C.text, height: 1.6))]),
      Section(title: 'Maintenance', children: [
        Para('Weekly', asList(ck['weekly']).map(asStr).join('; ')),
        Para('Monthly', asList(ck['monthly']).map(asStr).join('; ')),
      ]),
      _routine('W-BIKE'),
      _routine('C-BIKE'),
    ];
  }

  List<Widget> strength(BuildContext context) => [
        Section(title: 'Strength is a priority', children: [
          Para('Focus', 'Legs, hamstrings, glutes, quads, calves, shoulders, arms, core, lower back and pelvic floor. Three sessions a week in most phases, two at lower volume in the 70.3 build.'),
          Para('Progressive overload', 'Log load, reps and effort (RPE). When every set reaches the top of the rep range at RPE 8 or less with no pain, the app suggests +1 to 2.5 kg OR +1 to 2 reps. Never both, never everything at once.'),
          Para('When it is hard', 'Missed reps or RPE 9.5+: repeat the load. Missed twice: drop about 10%. Pain reported on several days: progression stops for exercises that load that area.'),
          Para('Every session', 'Warm-up stretches, the main work, a kegel finisher and a cool-down stretch.'),
        ]),
        Section(title: 'Exercise library', subtitle: '${asList(p['library']).length} exercises with sets, reps, rest, how-to, breathing, mistakes, easier and harder versions', children: [
          FilledButton.icon(
              onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => LibraryPage(st: st))),
              icon: const Icon(Icons.search),
              label: const Text('Open the library')),
        ]),
        _routine('W-STR'),
        _routine('C-STR'),
      ];

  List<Widget> hyrox() {
    final h = asMap(p['hyrox']);
    final div = asMap(h['divisions']);
    return [
      Section(title: 'HYROX', subtitle: asStr(h['format']), children: [Text(asStr(h['gym_note']), style: TextStyle(color: C.mut))]),
      for (final s in asList(h['stations']).map(asMap))
        Section(title: '${asStr(s['name'])}: ${asStr(s['race'])}', accent: C.hyrox, children: [
          Para('Trains', asStr(s['trains'])),
          Para('Technique', asStr(s['cue'])),
          Para('At a gym', asStr(s['gym'])),
          Para('At home', asStr(s['home'])),
        ]),
      Section(title: 'Division standards', subtitle: 'Singles. Check the current HYROX rulebook before race day.', children: [
        for (final e in div.entries)
          Para(e.key, asMap(e.value).entries.map((x) => '${x.key.replaceAll('_', ' ')}: ${asStr(x.value)}').join(' · ')),
      ]),
      Section(title: 'Skills', children: [for (final s in asList(h['skills']).map(asMap)) Para(asStr(s['skill']), asStr(s['how']))]),
    ];
  }

  List<Widget> mobility() => [
        for (final r in _l('mobility_routines')) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 0),
            child: Text('${asStr(r['title'])}: ${asStr(r['when'])}', style: TextStyle(color: C.mut, fontSize: 12.5)),
          ),
          _routine(asStr(r['code'])),
        ],
        Section(title: 'Mobility library', children: [for (final m in _l('mobility')) Para('${asStr(m['name'])} (${asStr(m['area'])})', asStr(m['how']), extra: asStr(m['dose']))]),
      ];

  List<Widget> pelvic() {
    final pf = asMap(p['pelvic']);
    return [
      Section(title: 'Pelvic floor', children: [Text(asStr(pf['intro']), style: TextStyle(color: C.text, height: 1.4))]),
      Section(title: 'Find the right muscles', children: [for (final s in asList(pf['find'])) Para('', '· ${asStr(s)}')]),
      Section(title: 'The drills', children: [for (final d in asList(pf['drills'])) Para(asStr(asList(d)[0]), asStr(asList(d)[1]), extra: asStr(asList(d)[2]))]),
      Section(title: 'Progression', subtitle: 'Move up only with good technique and full relaxation', children: [
        for (final d in asList(pf['levels'])) Para(asStr(asList(d)[0]), asStr(asList(d)[1]), extra: asStr(asList(d)[2])),
      ]),
      Section(title: 'Rules', accent: C.warn, children: [for (final s in asList(pf['rules'])) Para('', '· ${asStr(s)}')]),
      for (final k in _l('kegels'))
        Section(title: 'Kegel finisher: ${asStr(k['name'])}', children: [
          for (final i in asList(k['items']).map(asMap)) Para('${asStr(i['name'])}: ${asStr(i['sets'])} x ${asStr(i['reps'])}', asStr(i['how'])),
        ]),
    ];
  }

  List<Widget> sleep() => [
        Section(title: 'Why sleep matters', children: [
          Text('Muscle repair, fat loss, endurance adaptations and hormone balance all happen mostly during sleep. Short sleep raises hunger, '
              'lowers training quality and slows recovery. The coach looks at your sleep together with soreness, energy, stress and resting heart rate, never alone.',
              style: TextStyle(color: C.text, height: 1.4)),
        ]),
        Section(title: 'Daily routine', children: [for (final s in _l('sleep')) Para(asStr(s['time']), asStr(s['what']), extra: asStr(s['why']))]),
        Section(title: 'Bedroom', children: [for (final s in _l('bedroom')) Para(asStr(s['area']), asStr(s['what']))]),
        Section(title: 'Recovery', children: [for (final s in _l('recovery')) Para(asStr(s['tool']), asStr(s['how']), extra: asStr(s['when']))]),
      ];

  List<Widget> tanzania() => [
        for (final t in _l('tanzania')) Section(title: asStr(t['factor']), children: [Para('', asStr(t['meaning'])), Para('What to do', asStr(t['todo']))]),
      ];

  List<Widget> fullPlan(void Function(String) open) {
    final byWeek = <int, List<Map<String, dynamic>>>{};
    for (final d in st.planDays.map(asMap)) {
      byWeek.putIfAbsent((d['week'] as num).toInt(), () => <Map<String, dynamic>>[]).add(d);
    }
    return [
      for (final ph in _l('phases'))
        Section(title: asStr(ph['name']), subtitle: 'Weeks ${asStr(ph['first_week'])} to ${asStr(ph['last_week'])}', children: [
          Text(asStr(ph['purpose']), style: TextStyle(height: 1.35, color: C.text)),
        ]),
      for (final w in _l('weeks'))
        Section(title: 'Week ${asStr(w['week'])} · ${prettyDate(asStr(w['start']))}', subtitle: '${asStr(w['phase'])} · ${asStr(w['type'])}', children: [
          for (final d in byWeek[(w['week'] as num).toInt()] ?? <Map<String, dynamic>>[])
            InkWell(
              onTap: () => open(asStr(d['date'])),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  SizedBox(width: 92, child: Text(prettyDate(asStr(d['date'])), style: TextStyle(color: C.mut, fontSize: 13))),
                  Expanded(
                    child: Text(
                        d['race'] != null
                            ? asStr(d['race'])
                            : [d['am'], d['pm']].where((k) => k != null).map((k) => asStr(st.session(asStr(k))['name'])).join(' + '),
                        style: TextStyle(color: C.text, fontSize: 13)),
                  ),
                ]),
              ),
            ),
        ]),
    ];
  }
}

class LibraryPage extends StatefulWidget {
  final AppState st;
  const LibraryPage({super.key, required this.st});

  @override
  State<LibraryPage> createState() => _LibraryPageState();
}

class _LibraryPageState extends State<LibraryPage> {
  String q = '';
  String cat = 'All';

  @override
  Widget build(BuildContext context) {
    final lib = asList(widget.st.plan['library']).map(asMap).toList();
    final cats = ['All', ...{for (final e in lib) asStr(e['cat'])}];
    final all = lib.where((e) {
      final t = '${asStr(e['name'])} ${asStr(e['also'])} ${asStr(e['cat'])} ${asStr(e['muscles'])}'.toLowerCase();
      return (q.isEmpty || t.contains(q.toLowerCase())) && (cat == 'All' || e['cat'] == cat);
    }).toList();
    return Scaffold(
      appBar: AppBar(title: const Text('Exercise library')),
      body: ListView(padding: const EdgeInsets.only(bottom: 24), children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(14, 6, 14, 6),
          child: TextField(
            decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Search: hamstrings, shoulders, kegel...'),
            onChanged: (t) => setState(() => q = t),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Wrap(spacing: 6, runSpacing: 4, children: [
            for (final c in cats) ChoiceChip(label: Text(c), selected: cat == c, onSelected: (_) => setState(() => cat = c)),
          ]),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
          child: Text('${all.length} exercises. Tap one to open its full instructions.', style: TextStyle(color: C.mut, fontSize: 12.5)),
        ),
        for (final e in all)
          Container(
            margin: const EdgeInsets.fromLTRB(12, 0, 12, 8),
            decoration: BoxDecoration(color: C.card, borderRadius: BorderRadius.circular(14), border: Border.all(color: C.line)),
            child: Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                key: PageStorageKey(asStr(e['name'])),
                title: Text(asStr(e['name']), style: TextStyle(color: C.text, fontWeight: FontWeight.w700)),
                subtitle: Text('${asStr(e['cat'])} · ${asStr(e['muscles'])}', style: TextStyle(color: C.mut, fontSize: 12.5)),
                childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                children: [ExerciseDetail(lib: e, showName: false)],
              ),
            ),
          ),
        if (all.isEmpty) const EmptyState(Icons.search_off, 'No exercises found', 'Try another word or category.'),
      ]),
    );
  }
}

class ServerPage extends StatefulWidget {
  final AppState st;
  const ServerPage({super.key, required this.st});

  @override
  State<ServerPage> createState() => _ServerPageState();
}

class _ServerPageState extends State<ServerPage> {
  late final TextEditingController url = TextEditingController(text: widget.st.serverUrl);
  late final TextEditingController mail = TextEditingController(text: widget.st.email ?? '');
  final TextEditingController pw = TextEditingController();
  bool busy = false;

  @override
  void dispose() {
    url.dispose();
    mail.dispose();
    pw.dispose();
    super.dispose();
  }

  Future<void> _go(bool register) async {
    setState(() => busy = true);
    final err = await widget.st.signIn(url.text, mail.text, pw.text, register: register);
    if (!mounted) return;
    setState(() => busy = false);
    showMsg(context, err ?? 'Signed in. Your data is syncing.');
  }

  @override
  Widget build(BuildContext context) {
    final st = widget.st;
    return Scaffold(
      appBar: AppBar(title: const Text('Server and sync')),
      body: ListenableBuilder(
        listenable: st,
        builder: (context, _) => ListView(padding: const EdgeInsets.symmetric(vertical: 8), children: [
          Section(title: 'Status', children: [
            Text(st.syncNote, style: TextStyle(color: C.text)),
            const SizedBox(height: 6),
            Text('${st.outbox.length + st.activityOutbox.length} change(s) waiting to be sent. Plan ${asStr(st.plan['version'])}.', style: TextStyle(color: C.mut)),
          ]),
          if (st.token == null)
            Section(
              title: 'Sign in',
              subtitle: 'Optional. The app works fully offline. Sign in to back up to your server and to rebuild the plan when you change races or settings.',
              children: [
                TextField(controller: url, decoration: const InputDecoration(labelText: 'Server address')),
                const SizedBox(height: 10),
                TextField(controller: mail, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email')),
                const SizedBox(height: 10),
                TextField(controller: pw, obscureText: true, decoration: const InputDecoration(labelText: 'Password (8+ characters)')),
                const SizedBox(height: 12),
                Row(children: [
                  FilledButton(onPressed: busy ? null : () => _go(false), child: const Text('Sign in')),
                  const SizedBox(width: 10),
                  OutlinedButton(onPressed: busy ? null : () => _go(true), child: const Text('Create account')),
                ]),
                const SizedBox(height: 8),
                Text('First time: Create account. The server allows only the first account by default.', style: TextStyle(color: C.mut, fontSize: 12.5)),
              ],
            )
          else
            Section(title: 'Signed in as ${st.email}', subtitle: st.serverUrl, children: [
              Row(children: [
                FilledButton.icon(onPressed: st.syncing ? null : () => st.sync(), icon: const Icon(Icons.sync), label: const Text('Sync now')),
                const SizedBox(width: 10),
                OutlinedButton(onPressed: () => st.signOut(), child: const Text('Sign out')),
              ]),
            ]),
        ]),
      ),
    );
  }
}

class DataPage extends StatelessWidget {
  final AppState st;
  const DataPage({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your data and privacy')),
      body: ListView(padding: const EdgeInsets.symmetric(vertical: 8), children: [
        Section(title: 'Where your data lives', children: [
          Text('On this phone, and on your own server if you sign in. Nothing is sent to any other company. No external fitness platform is required.',
              style: TextStyle(color: C.text, height: 1.4)),
        ]),
        Section(title: 'Export', subtitle: 'Copies your daily log as CSV. Paste it into Excel, Google Sheets or an email.', children: [
          FilledButton.icon(
            icon: const Icon(Icons.copy),
            label: const Text('Copy my log as CSV'),
            onPressed: () async {
              final csv = await st.exportCsv();
              await Clipboard.setData(ClipboardData(text: csv));
              if (context.mounted) showMsg(context, 'Copied ${csv.split('\n').length - 1} days.');
            },
          ),
        ]),
        Section(title: 'On this phone', children: [
          Text('${st.days.length} days, ${st.results.length} results and ${st.activities.length} activities.', style: TextStyle(color: C.text)),
        ]),
        Section(title: 'Erase this phone', subtitle: 'Deletes the log on this phone only. If you are signed in, sign out first so the server copy is untouched.', children: [
          OutlinedButton(
            style: OutlinedButton.styleFrom(foregroundColor: C.bad),
            onPressed: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Erase everything on this phone?'),
                  content: const Text('This cannot be undone.'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                    TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Erase')),
                  ],
                ),
              );
              if (ok == true) {
                await st.resetAll();
                if (context.mounted) showMsg(context, 'Erased.');
              }
            },
            child: const Text('Erase my log'),
          ),
        ]),
      ]),
    );
  }
}
