import 'package:flutter/material.dart';

import 'goals_screen.dart';
import 'library_pages.dart';
import 'notify.dart';
import 'state.dart';
import 'ui.dart';
import 'util.dart';

const kEquipment = ['Pool', 'Loaded backpack', 'Jerrycans', 'Water bottles', 'Sturdy chair', 'Bed or sofa', 'Resistance band', 'Dumbbells',
  'Kettlebell', 'Gym access', 'Bike', 'Bike trainer or spin bike', 'Heart-rate watch', 'Open water nearby'];

Future<String?> pickDate(BuildContext context, String? current) async {
  final init = (current != null && current.isNotEmpty) ? dateOf(current) : DateTime.now();
  final d = await showDatePicker(context: context, initialDate: init, firstDate: DateTime(2026, 1, 1), lastDate: DateTime(2028, 12, 31));
  return d == null ? null : isoOf(DateTime.utc(d.year, d.month, d.day));
}

/// Profile: athlete details, race calendar, goals, equipment, preferences, fasting, notifications, integrations, privacy.
class ProfileScreen extends StatelessWidget {
  final AppState st;
  const ProfileScreen({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    final p = st.profile;
    final pref = asMap(st.effective('preferences'));
    final fast = asMap(st.effective('fasting'));
    final ram = st.effective('ramadan');
    void open(Widget w) => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => w));
    return ListView(padding: const EdgeInsets.only(bottom: 28), children: [
      Section(title: asStr(p['name']).isEmpty ? 'Athlete' : asStr(p['name']), subtitle: '${asStr(p['location'])} · plan ${prettyDate(st.startIso, year: true)} to ${prettyDate(st.endIso, year: true)}', children: [
        KV('Age, sex, height', '${asStr(p['age'])} · ${asStr(p['sex'])} · ${asStr(p['height_cm'])} cm'),
        KV('Weight goal', '${asStr(p['start_weight'])} kg to ${asStr(p['goal_weight'])} kg by ${prettyDate(asStr(p['goal_weight_date']), year: true)}'),
        KV('Max heart rate', '${asStr(p['max_hr'])} bpm'),
        const SizedBox(height: 6),
        OutlinedButton.icon(onPressed: () => open(_AthletePage(st: st)), icon: const Icon(Icons.edit), label: const Text('Edit athlete details')),
      ]),
      Section(
        title: 'Race calendar',
        subtitle: 'Add, edit or remove races. The whole plan (phases, tapers, recovery) is rebuilt around them.',
        trailing: IconButton(icon: Icon(Icons.add_circle, color: C.accent), onPressed: () => open(RaceEditor(st: st, race: null))),
        children: [
          for (final r in st.races..sort((a, b) => (asStr(a['date']).isEmpty ? '9999' : asStr(a['date'])).compareTo(asStr(b['date']).isEmpty ? '9999' : asStr(b['date']))))
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(asStr(r['type']) == 'run' ? Icons.directions_run : (asStr(r['type']) == 'hyrox' ? Icons.bolt : Icons.pool), color: C.accent),
              title: Text(asStr(r['name']), style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
              subtitle: Text(
                  '${asStr(r['date']).isEmpty ? 'Date not set' : prettyDate(asStr(r['date']), year: true)} · priority ${asStr(r['priority'])}${asNum(r['target_min']) != null ? ' · target ${asNum(r['target_min'])!.round()} min' : ''}',
                  style: TextStyle(color: C.mut, fontSize: 12.5)),
              trailing: Icon(Icons.chevron_right, color: C.mut),
              onTap: () => open(RaceEditor(st: st, race: r)),
            ),
          if (st.planPending) Text('Changes are applied by the server at the next sync.', style: TextStyle(color: C.warn, fontSize: 12.5)),
        ],
      ),
      Section(title: 'Goals and baselines', children: [
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.flag, color: C.accent),
          title: Text('SMART goals and mini goals', style: TextStyle(color: C.text)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => open(Scaffold(appBar: AppBar(title: const Text('Goals')), body: ListenableBuilder(listenable: st, builder: (_, __) => GoalsScreen(st: st)))),
        ),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.speed, color: C.accent),
          title: Text('Training baseline', style: TextStyle(color: C.text)),
          subtitle: Text('Longest run, pace and swim used to size your sessions', style: TextStyle(color: C.mut, fontSize: 12.5)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => open(_BaselinePage(st: st)),
        ),
      ]),
      Section(title: 'Equipment', subtitle: 'Sessions have a home version; tell the coach what else you have.', children: [
        Wrap(spacing: 6, runSpacing: 6, children: [
          for (final e in kEquipment)
            FilterChip(
              label: Text(e),
              selected: asList(st.effective('equipment')).contains(e),
              onSelected: (on) {
                final l = asList(st.effective('equipment')).map(asStr).toList();
                if (on) {
                  l.add(e);
                } else {
                  l.remove(e);
                }
                st.setConfig('equipment', l);
              },
            ),
        ]),
      ]),
      Section(title: 'Training preferences', children: [
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: Text('Two sessions a day where the plan allows', style: TextStyle(color: C.text)),
          subtitle: Text('Never on fasting days. Off = one session a day, keeping the most important one.', style: TextStyle(color: C.mut, fontSize: 12.5)),
          value: pref['two_sessions'] != false,
          onChanged: (v) => st.setSectionField('preferences', 'two_sessions', v),
        ),
        KV('Runs', 'Mornings only'),
        KV('Swims', 'Evenings only, never on a run day'),
        _dateRow(context, 'Cycling starts', asStr(st.effective('bike_start')), (d) => st.setConfig('bike_start', d)),
        _dateRow(context, '1,500 m swim test', asStr(st.effective('swim_test')), (d) => st.setConfig('swim_test', d)),
      ]),
      Section(title: 'Fasting', subtitle: 'Fasting days get only an easy walk and mobility after breaking the fast.', children: [
        Wrap(spacing: 6, children: [
          for (final d in kWeekdays)
            FilterChip(
              label: Text(d),
              selected: asList(fast['weekdays']).contains(d),
              onSelected: (on) {
                final l = asList(fast['weekdays']).map(asStr).toList();
                if (on) {
                  l.add(d);
                } else {
                  l.remove(d);
                }
                l.sort((a, b) => kWeekdays.indexOf(a).compareTo(kWeekdays.indexOf(b)));
                st.setSectionField('fasting', 'weekdays', l);
              },
            ),
        ]),
        const SizedBox(height: 10),
        TextBox(key: const ValueKey('fast-break'), label: 'Break the fast at (HH:MM)', value: asStr(fast['break_time']), onChanged: (t) {
          if (RegExp(r'^\d{2}:\d{2}$').hasMatch(t)) st.setSectionField('fasting', 'break_time', t);
        }),
        const SizedBox(height: 6),
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: Text('Ramadan', style: TextStyle(color: C.text)),
          subtitle: Text(ram == null ? 'Off' : 'Expected ${prettyDate(asStr(asMap(ram)['start']), year: true)} to ${prettyDate(asStr(asMap(ram)['end']), year: true)}. Adjust after the moon sighting.',
              style: TextStyle(color: C.mut, fontSize: 12.5)),
          value: ram != null,
          onChanged: (v) => st.setConfig('ramadan', v ? <String, dynamic>{'start': '2027-02-08', 'end': '2027-03-09'} : null),
        ),
        if (ram != null) ...[
          _dateRow(context, 'Ramadan starts', asStr(asMap(ram)['start']), (d) => st.setConfig('ramadan', {...asMap(ram), 'start': d})),
          _dateRow(context, 'Ramadan ends', asStr(asMap(ram)['end']), (d) => st.setConfig('ramadan', {...asMap(ram), 'end': d})),
        ],
      ]),
      Section(
        title: 'Reminders',
        subtitle: Notifier.status,
        trailing: Switch(
          value: st.remindersAllowed,
          onChanged: (v) async {
            if (v) {
              final ok = await st.enableReminders();
              if (context.mounted && !ok) showMsg(context, 'Notifications are blocked. Allow them in the phone settings.');
            } else {
              await st.disableReminders();
            }
          },
        ),
        children: [
          for (final n in const [
            ['workouts', 'Workouts (morning and evening)'], ['checkin', 'Morning check-in'], ['mobility', 'Mobility and knee care'], ['kegels', 'Kegels (days without strength)'],
            ['sleep', 'Bedtime'], ['races', 'Race countdown (7, 3 and 1 days before)'], ['meals', 'Meals'], ['supps', 'Supplements'], ['water', 'Water (every 2 hours)'],
          ])
            SwitchListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              title: Text(n[1], style: TextStyle(color: C.text)),
              value: st.notifyOn(n[0]),
              onChanged: st.remindersAllowed ? (v) => st.setNotify(n[0], v) : null,
            ),
          const SizedBox(height: 6),
          for (final t in const [['checkin', 'Check-in'], ['workout_am', 'Morning workout'], ['mobility', 'Mobility'], ['workout_pm', 'Evening workout'], ['kegels', 'Kegels'], ['sleep', 'Bedtime']])
            ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              title: Text('${t[1]} reminder at', style: TextStyle(color: C.text)),
              trailing: Text(st.reminderTime(t[0]), style: TextStyle(color: C.accent, fontWeight: FontWeight.w700, fontSize: 15)),
              onTap: () async {
                final cur = st.reminderTime(t[0]).split(':');
                final picked = await showTimePicker(
                    context: context, initialTime: TimeOfDay(hour: int.tryParse(cur.first) ?? 6, minute: cur.length > 1 ? (int.tryParse(cur[1]) ?? 0) : 0));
                if (picked != null) st.setReminderTime(t[0], '${two(picked.hour)}:${two(picked.minute)}');
              },
            ),
          Row(children: [
            OutlinedButton.icon(
              icon: const Icon(Icons.notifications_active),
              label: const Text('Send a test reminder'),
              onPressed: () async {
                final ok = await Notifier.test();
                if (context.mounted) showMsg(context, ok ? 'Sent. Check your notification bar.' : Notifier.status);
              },
            ),
          ]),
          Text('Reminders are set on this phone for the next 14 days and refresh each time you open the app. Timing can be a few minutes late when the phone is saving battery.',
              style: TextStyle(color: C.mut, fontSize: 12.5)),
        ],
      ),
      _injurySection(context),
      Section(title: 'Integrations', children: [
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.watch, color: C.accent),
          title: Text('Import Garmin Activities.csv', style: TextStyle(color: C.text)),
          subtitle: Text('${st.activities.length} activities saved', style: TextStyle(color: C.mut, fontSize: 12.5)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => open(_ImportPage(st: st)),
        ),
        Text('Strava, Google Health Connect and Apple Health connect through separate adapters on the server; they are documented integration points and not required.',
            style: TextStyle(color: C.mut, fontSize: 12.5)),
      ]),
      Section(title: 'App', children: [
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          title: Text('Dark mode', style: TextStyle(color: C.text)),
          value: st.darkMode,
          onChanged: st.setDark,
        ),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.cloud_sync, color: C.accent),
          title: Text('Server and sync', style: TextStyle(color: C.text)),
          subtitle: Text(st.syncNote, style: TextStyle(color: C.mut, fontSize: 12.5)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => open(ServerPage(st: st)),
        ),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.lock_outline, color: C.accent),
          title: Text('Privacy and your data', style: TextStyle(color: C.text)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => open(DataPage(st: st)),
        ),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.bedtime_outlined, color: C.accent),
          title: Text('Sleep and recovery guide', style: TextStyle(color: C.text)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => pushPage(context, 'Sleep and recovery', st, Pages(st).sleep),
        ),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Icon(Icons.wb_sunny_outlined, color: C.accent),
          title: Text('Training in Tanzania', style: TextStyle(color: C.text)),
          trailing: Icon(Icons.chevron_right, color: C.mut),
          onTap: () => pushPage(context, 'Training in Tanzania', st, Pages(st).tanzania),
        ),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text('EnduraForge · plan engine ${asStr(st.plan['engine'])} · plan ${asStr(st.plan['version'])}', style: TextStyle(color: C.mut, fontSize: 12)),
        ),
      ]),
    ]);
  }

  Widget _injurySection(BuildContext context) {
    final inj = st.effective('injury');
    if (inj == null) {
      return Section(title: 'Injuries and niggles', subtitle: 'None active.', children: [
        OutlinedButton(
          onPressed: () => st.setConfig('injury', <String, dynamic>{'area': 'knee', 'since': todayIso(), 'until': addDays(todayIso(), 14), 'note': 'Reported in the app.'}),
          child: const Text('Report a knee niggle (2 weeks of knee care)'),
        ),
      ]);
    }
    final m = asMap(inj);
    return Section(
      title: 'Knee care is on',
      subtitle: '${asStr(m['note'])} Active from ${prettyDate(asStr(m['since']))} to ${prettyDate(asStr(m['until']), year: true)}.',
      accent: C.warn,
      children: [
        Text('While it is on: the long run is held, no sprints or hills, knee-friendly strength exercises, and a daily knee routine.', style: TextStyle(color: C.text, height: 1.35)),
        const SizedBox(height: 8),
        Wrap(spacing: 8, runSpacing: 6, children: [
          OutlinedButton(onPressed: () => st.setConfig('injury', <String, dynamic>{...m, 'until': addDays(asStr(m['until']), 7)}), child: const Text('Extend 1 week')),
          OutlinedButton(
            onPressed: () {
              st.setConfig('injury', null);
              showMsg(context, 'Knee care will switch off when the plan is rebuilt at the next sync.');
            },
            child: const Text('It has settled: switch off'),
          ),
        ]),
      ],
    );
  }

  Widget _dateRow(BuildContext context, String label, String value, ValueChanged<String> onPick) {
    return ListTile(
      dense: true,
      contentPadding: EdgeInsets.zero,
      title: Text(label, style: TextStyle(color: C.text)),
      subtitle: Text(value.isEmpty ? 'Not set' : prettyDate(value, year: true), style: TextStyle(color: C.mut)),
      trailing: Icon(Icons.edit_calendar, color: C.mut),
      onTap: () async {
        final d = await pickDate(context, value);
        if (d != null) onPick(d);
      },
    );
  }
}

class _AthletePage extends StatelessWidget {
  final AppState st;
  const _AthletePage({required this.st});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Athlete details')),
      body: ListenableBuilder(
        listenable: st,
        builder: (context, _) {
          final p = st.profile;
          Widget numBox(String k, String label, String sfx) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: NumField(key: ValueKey('p-$k'), label: label, suffix: sfx, value: asNum(p[k]), onChanged: (v) => st.setProfileField(k, v)),
              );
          Widget txt(String k, String label, {int lines = 1}) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: TextBox(key: ValueKey('p-$k'), label: label, value: asStr(p[k]), lines: lines, onChanged: (v) => st.setProfileField(k, v)),
              );
          return ListView(padding: const EdgeInsets.all(16), children: [
            txt('name', 'Name'),
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: SegmentedButton<String>(
                segments: const [ButtonSegment(value: 'male', label: Text('Male')), ButtonSegment(value: 'female', label: Text('Female'))],
                selected: {asStr(p['sex']).isEmpty ? 'male' : asStr(p['sex'])},
                onSelectionChanged: (s) => st.setProfileField('sex', s.first),
              ),
            ),
            numBox('age', 'Age', 'years'),
            numBox('height_cm', 'Height', 'cm'),
            numBox('start_weight', 'Starting weight', 'kg'),
            numBox('goal_weight', 'Target weight', 'kg'),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Target weight date', style: TextStyle(color: C.text)),
              subtitle: Text(prettyDate(asStr(p['goal_weight_date']), year: true), style: TextStyle(color: C.mut)),
              trailing: const Icon(Icons.edit_calendar),
              onTap: () async {
                final d = await pickDate(context, asStr(p['goal_weight_date']));
                if (d != null) st.setProfileField('goal_weight_date', d);
              },
            ),
            numBox('end_weight', 'Weight by the end of the plan', 'kg'),
            numBox('max_hr', 'Maximum heart rate', 'bpm'),
            numBox('sleep_h', 'Usual sleep', 'h'),
            numBox('hours_per_week', 'Training hours available per week', 'h'),
            txt('experience', 'Training experience (running, swimming, cycling)', lines: 2),
            txt('injuries', 'Previous injuries', lines: 2),
            txt('medical', 'Medical considerations', lines: 2),
            txt('allergies', 'Food allergies', lines: 2),
            txt('diet', 'Dietary preferences', lines: 2),
            Text('Changes rebuild the plan on the server at the next sync.', style: TextStyle(color: C.mut)),
          ]);
        },
      ),
    );
  }
}

class _BaselinePage extends StatelessWidget {
  final AppState st;
  const _BaselinePage({required this.st});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Training baseline')),
      body: ListenableBuilder(
        listenable: st,
        builder: (context, _) {
          final b = asMap(st.effective('baseline'));
          Widget numBox(String k, String label, String sfx) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: NumField(key: ValueKey('b-$k'), label: label, suffix: sfx, value: asNum(b[k]), onChanged: (v) => st.setSectionField('baseline', k, v)),
              );
          final bases = asList(st.plan['baselines']).map(asMap).toList();
          return ListView(padding: const EdgeInsets.all(16), children: [
            Text('Used to size your long runs and swims. Imported from Activities.csv; change it when you have new numbers.', style: TextStyle(color: C.mut)),
            const SizedBox(height: 12),
            numBox('long_run_km', 'Longest recent run', 'km'),
            numBox('run_pace_min_km', 'Average run pace (walking included)', 'min/km'),
            numBox('run_avg_hr', 'Average run heart rate', 'bpm'),
            numBox('swim_cont_m', 'Longest non-stop swim', 'm'),
            numBox('swim_pace_100m', 'Swim pace', 'min/100 m'),
            numBox('swim_swolf', 'Average SWOLF', ''),
            const Divider(height: 28),
            Text('Test results', style: TextStyle(color: C.text, fontWeight: FontWeight.w700, fontSize: 16)),
            const SizedBox(height: 8),
            for (final x in bases)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: NumField(
                  key: ValueKey('base-${asStr(x['key'])}'),
                  label: '${asStr(x['label'])} · ${asStr(x['when'])}',
                  value: st.results['base:${asStr(x['key'])}'],
                  onChanged: (v) => st.setResult('base:${asStr(x['key'])}', v),
                ),
              ),
          ]);
        },
      ),
    );
  }
}

class _ImportPage extends StatefulWidget {
  final AppState st;
  const _ImportPage({required this.st});

  @override
  State<_ImportPage> createState() => _ImportPageState();
}

class _ImportPageState extends State<_ImportPage> {
  final c = TextEditingController();

  @override
  void dispose() {
    c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Import from Garmin')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        Text('In Garmin Connect on the web: Activities > All activities > Export CSV. Open the file, copy everything and paste it here. '
            'Duplicates are ignored. Missing values stay empty: nothing is invented.', style: TextStyle(color: C.mut, height: 1.4)),
        const SizedBox(height: 12),
        TextField(controller: c, maxLines: 10, decoration: const InputDecoration(hintText: 'Activity Type,Date,Favorite,Title,Distance,...')),
        const SizedBox(height: 12),
        FilledButton.icon(
          icon: const Icon(Icons.download),
          label: const Text('Import'),
          onPressed: () {
            final n = widget.st.importGarmin(c.text);
            showMsg(context, n == 0 ? 'Nothing new found.' : 'Imported $n new activities.');
            if (n > 0) c.clear();
          },
        ),
        const SizedBox(height: 16),
        for (final a in (widget.st.activities.values.toList()..sort((x, y) => asStr(y['start']).compareTo(asStr(x['start'])))).take(30))
          ListTile(
            dense: true,
            contentPadding: EdgeInsets.zero,
            title: Text('${asStr(a['title']).isEmpty ? asStr(a['type']) : asStr(a['title'])} · ${prettyDate(asStr(a['date']))}', style: TextStyle(color: C.text)),
            subtitle: Text(
                a['type'] == 'swim'
                    ? '${fmtNum(asNum(a['distance_m']), dp: 0)} m · SWOLF ${fmtNum(asNum(a['swolf']), dp: 0)} · ${fmtNum(asNum(a['strokes']), dp: 0)} strokes'
                    : '${fmtNum(asNum(a['distance_km']))} km · HR ${fmtNum(asNum(a['avg_hr']), dp: 0)} avg / ${fmtNum(asNum(a['max_hr']), dp: 0)} max',
                style: TextStyle(color: C.mut)),
          ),
      ]),
    );
  }
}

/// Add or edit a race.
class RaceEditor extends StatefulWidget {
  final AppState st;
  final Map<String, dynamic>? race;
  const RaceEditor({super.key, required this.st, required this.race});

  @override
  State<RaceEditor> createState() => _RaceEditorState();
}

class _RaceEditorState extends State<RaceEditor> {
  late Map<String, dynamic> r = Map<String, dynamic>.from(widget.race ??
      <String, dynamic>{'id': 'r${DateTime.now().millisecondsSinceEpoch}', 'name': '', 'type': 'run', 'priority': 'B', 'date': null});

  Widget _num(String k, String label, String sfx) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: NumField(key: ValueKey('race-$k'), label: label, suffix: sfx, value: asNum(r[k]), onChanged: (v) => r[k] = v),
      );

  @override
  Widget build(BuildContext context) {
    final type = asStr(r['type']);
    return Scaffold(
      appBar: AppBar(title: Text(widget.race == null ? 'Add a race' : 'Edit race')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        TextBox(key: const ValueKey('race-name'), label: 'Name', value: asStr(r['name']), onChanged: (t) => r['name'] = t),
        const SizedBox(height: 12),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: 'run', label: Text('Run')),
            ButtonSegment(value: 'hyrox', label: Text('HYROX')),
            ButtonSegment(value: 'triathlon', label: Text('Triathlon')),
          ],
          selected: {type},
          onSelectionChanged: (s) => setState(() => r['type'] = s.first),
        ),
        const SizedBox(height: 12),
        ListTile(
          contentPadding: EdgeInsets.zero,
          title: Text('Date', style: TextStyle(color: C.text)),
          subtitle: Text(asStr(r['date']).isEmpty ? 'Not set (it will not shape the plan)' : prettyDate(asStr(r['date']), year: true), style: TextStyle(color: C.mut)),
          trailing: const Icon(Icons.edit_calendar),
          onTap: () async {
            final d = await pickDate(context, asStr(r['date']));
            if (d != null) setState(() => r['date'] = d);
          },
        ),
        Text('Priority', style: TextStyle(color: C.text, fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: 'A', label: Text('A: goal')),
            ButtonSegment(value: 'B', label: Text('B: tune-up')),
            ButtonSegment(value: 'C', label: Text('C: optional')),
          ],
          selected: {asStr(r['priority']).isEmpty ? 'A' : asStr(r['priority'])},
          onSelectionChanged: (s) => setState(() => r['priority'] = s.first),
        ),
        const SizedBox(height: 14),
        if (type == 'run') _num('run_km', 'Distance', 'km'),
        if (type == 'triathlon') ...[_num('swim_m', 'Swim', 'm'), _num('bike_km', 'Bike', 'km'), _num('run_km', 'Run', 'km')],
        if (type == 'hyrox')
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: DropdownButtonFormField<String>(
              value: asStr(r['division']).isEmpty ? 'Men Open' : asStr(r['division']),
              decoration: const InputDecoration(labelText: 'Division'),
              items: [for (final d in const ['Men Open', 'Men Pro', 'Women Open', 'Women Pro']) DropdownMenuItem(value: d, child: Text(d))],
              onChanged: (v) => r['division'] = v,
            ),
          ),
        _num('target_min', 'Target finish time', 'min'),
        TextBox(key: const ValueKey('race-note'), label: 'Note', value: asStr(r['note']), onChanged: (t) => r['note'] = t),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: () {
            if (asStr(r['name']).trim().isEmpty) {
              showMsg(context, 'Give the race a name.');
              return;
            }
            r.removeWhere((k, v) => v == null && k != 'date');
            widget.st.saveRace(r);
            Navigator.pop(context);
            showMsg(context, 'Saved. The plan is rebuilt around it at the next sync.');
          },
          child: const Text('Save race'),
        ),
        if (widget.race != null) ...[
          const SizedBox(height: 8),
          OutlinedButton(
            style: OutlinedButton.styleFrom(foregroundColor: C.bad),
            onPressed: () {
              widget.st.deleteRace(asStr(r['id']));
              Navigator.pop(context);
            },
            child: const Text('Remove race'),
          ),
        ],
      ]),
    );
  }
}
