import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models.dart';
import '../widgets/common.dart';
import '../widgets/sync_button.dart';

/// The 2-minute daily log and the weekly check-in (plan section 14).
class TrackScreen extends StatelessWidget {
  const TrackScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Track'),
          actions: const [SyncButton(), SettingsButton()],
          bottom: const TabBar(tabs: [
            Tab(icon: Icon(Icons.today), text: 'Daily log'),
            Tab(icon: Icon(Icons.fact_check_outlined), text: 'Weekly check-in'),
          ]),
        ),
        body: const TabBarView(children: [DailyLogTab(), CheckinsTab()]),
      ),
    );
  }
}

// ---------------- Daily log ----------------
class DailyLogTab extends StatefulWidget {
  const DailyLogTab({super.key});

  @override
  State<DailyLogTab> createState() => _DailyLogTabState();
}

class _DailyLogTabState extends State<DailyLogTab> {
  DateTime _day = DateTime.now();
  late Habit _h;
  final _weight = TextEditingController();
  final _pulse = TextEditingController();
  final _painWhere = TextEditingController();
  final _protein = TextEditingController();
  final _notes = TextEditingController();
  bool _dirty = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    for (final c in [_weight, _pulse, _painWhere, _protein, _notes]) {
      c.dispose();
    }
    super.dispose();
  }

  void _load() {
    final saved = appState.habitFor(isoDate(_day));
    _h = Habit.fromJson(saved.toJson()); // edit a copy; nothing changes until Save
    _weight.text = _h.weight == null ? '' : fmtNum(_h.weight, decimals: 1);
    _pulse.text = _h.restingHr?.toString() ?? '';
    _painWhere.text = _h.painWhere ?? '';
    _protein.text = _h.proteinG?.toString() ?? '';
    _notes.text = _h.notes ?? '';
    _dirty = false;
  }

  void _shift(int days) {
    final next = _day.add(Duration(days: days));
    if (next.isAfter(DateTime.now())) return;
    setState(() {
      _day = next;
      _load();
    });
  }

  void _edit(VoidCallback f) => setState(() {
        f();
        _dirty = true;
      });

  String? _trim(TextEditingController c) => c.text.trim().isEmpty ? null : c.text.trim();

  void _save() {
    _h.weight = double.tryParse(_weight.text.trim().replaceAll(',', '.'));
    _h.restingHr = int.tryParse(_pulse.text.trim());
    _h.painWhere = _trim(_painWhere);
    _h.proteinG = int.tryParse(_protein.text.trim());
    _h.notes = _trim(_notes);
    appState.saveHabit(_h);
    setState(() => _dirty = false);
    final warn = (_h.pain ?? 0) >= 4 || (_h.warningSigns ?? false);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(warn
          ? 'Saved. Pain of 4+ or warning signs: rest from running and check the plan rules (Guide → Weekly rules).'
          : 'Daily log saved'),
      duration: Duration(seconds: warn ? 6 : 2),
    ));
  }

  Widget _scale(String label, int? value, int min, int max, ValueChanged<int> onPick, {String? hint}) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(child: Text(label, style: theme.textTheme.titleSmall)),
          if (hint != null) Text(hint, style: theme.textTheme.bodySmall),
        ]),
        const SizedBox(height: 4),
        Wrap(spacing: 6, runSpacing: 6, children: [
          for (var i = min; i <= max; i++)
            ChoiceChip(
              label: Text('$i'),
              selected: value == i,
              visualDensity: VisualDensity.compact,
              onSelected: (_) => onPick(i),
            ),
        ]),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isToday = isoDate(_day) == isoDate(DateTime.now());
    final fastDay = _day.weekday == DateTime.monday || _day.weekday == DateTime.thursday;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      children: [
        Row(children: [
          IconButton(onPressed: () => _shift(-1), icon: const Icon(Icons.chevron_left)),
          Expanded(
            child: Column(children: [
              Text(isToday ? 'Today' : fmtDate(isoDate(_day), 'EEEE'),
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              Text(fmtDate(isoDate(_day), 'd MMMM yyyy') + (fastDay ? ' · fast day' : '')),
            ]),
          ),
          IconButton(onPressed: isToday ? null : () => _shift(1), icon: const Icon(Icons.chevron_right)),
        ]),
        const SizedBox(height: 8),

        // Morning
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Morning', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Row(children: [
                Expanded(
                  child: TextField(
                    controller: _weight,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    onChanged: (_) => setState(() => _dirty = true),
                    decoration: const InputDecoration(
                      labelText: 'Weight (kg)',
                      helperText: 'After the toilet, before food',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _pulse,
                    keyboardType: TextInputType.number,
                    onChanged: (_) => setState(() => _dirty = true),
                    decoration: const InputDecoration(
                      labelText: 'Resting pulse',
                      helperText: '60 s, lying still (optional)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ]),
              const SizedBox(height: 8),
              ValueStepper(label: 'Sleep', value: _h.sleepHours, step: 0.5, max: 14, unit: 'h', onChanged: (v) => _edit(() => _h.sleepHours = v)),
              _scale('Sleep quality', _h.sleepQuality, 1, 5, (v) => _edit(() => _h.sleepQuality = v), hint: '1 poor · 5 great'),
            ]),
          ),
        ),

        // Body
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Body', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              _scale('Muscle soreness', _h.soreness, 0, 10, (v) => _edit(() => _h.soreness = v), hint: '0 none · 10 severe'),
              _scale('Pain', _h.pain, 0, 10, (v) => _edit(() => _h.pain = v), hint: '4+ = stop running'),
              if ((_h.pain ?? 0) > 0)
                TextField(
                  controller: _painWhere,
                  onChanged: (_) => setState(() => _dirty = true),
                  decoration: const InputDecoration(labelText: 'Where does it hurt?', border: OutlineInputBorder()),
                ),
            ]),
          ),
        ),

        // Mind
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('How you feel', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              _scale('Energy', _h.energy, 1, 5, (v) => _edit(() => _h.energy = v)),
              _scale('Mood', _h.mood, 1, 5, (v) => _edit(() => _h.mood = v)),
              _scale('Motivation', _h.motivation, 1, 5, (v) => _edit(() => _h.motivation = v)),
            ]),
          ),
        ),

        // Food
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Food and water', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              _scale('Ate to plan', _h.nutrition, 1, 5, (v) => _edit(() => _h.nutrition = v), hint: '1 off plan · 5 on plan'),
              const SizedBox(height: 6),
              TextField(
                controller: _protein,
                keyboardType: TextInputType.number,
                onChanged: (_) => setState(() => _dirty = true),
                decoration: InputDecoration(
                  labelText: 'Protein (g, optional)',
                  helperText: 'Target about ${fastDay ? 125 : 140} g',
                  border: const OutlineInputBorder(),
                ),
              ),
              ValueStepper(label: 'Water', value: _h.waterLitres, step: 0.25, max: 8, unit: 'L', onChanged: (v) => _edit(() => _h.waterLitres = v)),
            ]),
          ),
        ),

        // Fast day
        if (fastDay)
          Card(
            color: theme.colorScheme.tertiaryContainer,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Dry fast', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Fast kept until 18:50'),
                  value: _h.fastKept ?? false,
                  onChanged: (v) => _edit(() => _h.fastKept = v),
                ),
                _scale('How well you coped', _h.fastTolerance, 1, 5, (v) => _edit(() => _h.fastTolerance = v), hint: '1 badly · 5 easily'),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Warning signs'),
                  subtitle: const Text('Dizziness, fainting, confusion, racing heart, very dark or no urine'),
                  value: _h.warningSigns ?? false,
                  onChanged: (v) => _edit(() => _h.warningSigns = v),
                ),
              ]),
            ),
          ),

        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _notes,
              maxLines: 2,
              onChanged: (_) => setState(() => _dirty = true),
              decoration: const InputDecoration(labelText: 'Notes', border: OutlineInputBorder()),
            ),
          ),
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
          onPressed: _dirty ? _save : null,
          icon: const Icon(Icons.save_alt),
          label: Text(_dirty ? 'Save daily log' : 'Saved'),
        ),
      ],
    );
  }
}

// ---------------- Weekly check-in ----------------
class CheckinsTab extends StatelessWidget {
  const CheckinsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: appState,
      builder: (context, _) {
        if (appState.checkins.isEmpty) {
          return const Center(child: Text('Check-ins appear here after the first sync.'));
        }
        final series = {
          for (final p in (appState.dashboard?['weight_series'] as List? ?? []))
            (p as Map)['week'] as int: (p['actual'] as num?)?.toDouble(),
        };
        return ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
          children: [
            Card(
              color: Theme.of(context).colorScheme.secondaryContainer,
              child: const ListTile(
                leading: Icon(Icons.info_outline),
                title: Text('Every Sunday evening'),
                subtitle: Text('Waist at the navel, your longest non-stop swim, and the 5 km test time in test weeks (4, 8, 11). '
                    'Weight comes from your daily log.'),
              ),
            ),
            for (final c in appState.checkins.where((c) => c.week <= 14)) _CheckinCard(c, series[c.week]),
          ],
        );
      },
    );
  }
}

class _CheckinCard extends StatelessWidget {
  final Checkin c;
  final double? avgWeight;
  const _CheckinCard(this.c, this.avgWeight);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final parts = <String>[
      if (avgWeight != null) '${fmtNum(avgWeight)} kg avg (range ${fmtNum(c.stretchWeight)}–${fmtNum(c.targetWeight)})',
      if (avgWeight == null) 'Expected ${fmtNum(c.stretchWeight)}–${fmtNum(c.targetWeight)} kg',
      if (c.waist != null) 'waist ${fmtNum(c.waist)} cm',
      if (c.swimNonstopActual != null) 'swim ${fmtNum(c.swimNonstopActual)} m',
      if (c.tt5kMin != null) '5 km ${fmtNum(c.tt5kMin)} min',
    ];
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        leading: CircleAvatar(
          backgroundColor: c.logged ? theme.colorScheme.primary : theme.colorScheme.surfaceContainerHighest,
          foregroundColor: c.logged ? theme.colorScheme.onPrimary : theme.colorScheme.onSurfaceVariant,
          child: Text('${c.week}'),
        ),
        title: Text('${c.label} · from ${fmtDate(c.date, 'd MMM')}${c.testWeek ? ' · 5 km test' : ''}',
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(parts.join(' · ')),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          showDragHandle: true,
          builder: (_) => CheckinForm(checkin: c),
        ),
      ),
    );
  }
}

class CheckinForm extends StatefulWidget {
  final Checkin checkin;
  const CheckinForm({super.key, required this.checkin});

  @override
  State<CheckinForm> createState() => _CheckinFormState();
}

class _CheckinFormState extends State<CheckinForm> {
  late final TextEditingController _waist, _run, _swim, _tt, _notes;
  int? _energy;

  @override
  void initState() {
    super.initState();
    final c = widget.checkin;
    String t(double? v) => v == null ? '' : fmtNum(v, decimals: 2);
    _waist = TextEditingController(text: t(c.waist));
    _run = TextEditingController(text: t(c.longRunActual));
    _swim = TextEditingController(text: t(c.swimNonstopActual));
    _tt = TextEditingController(text: t(c.tt5kMin));
    _notes = TextEditingController(text: c.notes ?? '');
    _energy = c.energy;
  }

  @override
  void dispose() {
    for (final c in [_waist, _run, _swim, _tt, _notes]) {
      c.dispose();
    }
    super.dispose();
  }

  double? _p(TextEditingController c) => double.tryParse(c.text.trim().replaceAll(',', '.'));

  Widget _field(TextEditingController c, String label, String? hint) => Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: TextField(
          controller: c,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(labelText: label, helperText: hint, border: const OutlineInputBorder()),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final c = widget.checkin;
    return Padding(
      padding: EdgeInsets.fromLTRB(20, 0, 20, MediaQuery.of(context).viewInsets.bottom + 20),
      child: SingleChildScrollView(
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('${c.label} check-in', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          Text('Week starting ${fmtDate(c.date, 'EEEE d MMMM')}'),
          const SizedBox(height: 16),
          _field(_waist, 'Waist (cm)', 'At the navel, relaxed, after breathing out'),
          _field(_run, 'Long session done (minutes)', c.plannedLongRun == null ? null : 'Planned ${fmtNum(c.plannedLongRun)} min'),
          _field(_swim, 'Longest non-stop swim (m)', c.plannedSwim == null ? null : 'Planned ${fmtNum(c.plannedSwim)} m continuous'),
          _field(_tt, '5 km test (minutes, e.g. 47.5)', c.testWeek ? 'Test week: this sets your race plan' : 'Only if you ran a test this week'),
          Text('Energy this week', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 6),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            for (var i = 1; i <= 5; i++)
              ChoiceChip(label: Text('$i'), selected: _energy == i, onSelected: (_) => setState(() => _energy = i)),
          ]),
          const SizedBox(height: 12),
          TextField(controller: _notes, maxLines: 2, decoration: const InputDecoration(labelText: 'Notes', border: OutlineInputBorder())),
          const SizedBox(height: 16),
          FilledButton.icon(
            style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
            icon: const Icon(Icons.save_alt),
            label: const Text('Save check-in'),
            onPressed: () {
              final updated = Checkin.fromJson(c.toJson())
                ..waist = _p(_waist)
                ..longRunActual = _p(_run)
                ..swimNonstopActual = _p(_swim)
                ..tt5kMin = _p(_tt)
                ..energy = _energy
                ..notes = _notes.text.trim().isEmpty ? null : _notes.text.trim();
              final messenger = ScaffoldMessenger.of(context);
              appState.saveCheckin(updated);
              Navigator.pop(context);
              messenger.showSnackBar(const SnackBar(content: Text('Check-in saved — the dashboard updates on the next sync')));
            },
          ),
        ]),
      ),
    );
  }
}
