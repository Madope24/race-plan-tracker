import 'package:flutter/material.dart';

import 'state.dart';
import 'ui.dart';
import 'util.dart';

String fmtVal(double? v, String unit) {
  if (v == null) return '-';
  if (unit.startsWith('%')) return fmtPct(v);
  return '${fmtNum(v)} $unit';
}

/// SMART goals, their mini goals, and your baselines.
class GoalsScreen extends StatelessWidget {
  final AppState st;
  const GoalsScreen({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    final defs = {for (final g in asList(st.plan['goals']).map(asMap)) asStr(g['id']): g};
    final goals = st.goals();
    final minis = st.minis();
    final hit = minis.where((m) => m['status'] == 'Hit').length;
    final due = minis.where((m) => m['status'] == 'Due this week' || m['status'] == 'Overdue: log it').toList();
    return ListView(
      padding: const EdgeInsets.only(bottom: 24),
      children: [
        Section(
          title: 'Mini goals',
          subtitle: '$hit of ${minis.length} hit. ${due.length} need your attention this week.',
          children: [
            for (final m in due)
              ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: Text(asStr(m['text'])),
                subtitle: Text('${asStr(m['goal'])} · due ${prettyDate(asStr(m['due']))}'),
                trailing: Pill(asStr(m['status']), color: statusColor(asStr(m['status']))),
                onTap: () => _openGoal(context, defs[asStr(m['goal'])]!),
              ),
          ],
        ),
        for (final g in goals)
          Card(
            margin: const EdgeInsets.fromLTRB(12, 5, 12, 5),
            elevation: 0,
            child: InkWell(
              borderRadius: BorderRadius.circular(12),
              onTap: () => _openGoal(context, defs[asStr(g['id'])]!),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Row(children: [
                    Expanded(
                        child: Text('${asStr(g['id'])}: ${asStr(g['name'])}', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: C.navy))),
                    Pill(asStr(g['status']), color: statusColor(asStr(g['status']))),
                  ]),
                  const SizedBox(height: 8),
                  Bar(g['progress'] as double?, color: statusColor(asStr(g['status'])) == C.mut ? C.teal : statusColor(asStr(g['status']))),
                  const SizedBox(height: 6),
                  Text(
                      'Now ${fmtVal(g['current'] as double?, asStr(defs[asStr(g['id'])]!['unit']))} · target ${fmtVal(g['target'] as double?, asStr(defs[asStr(g['id'])]!['unit']))} · ${prettyDate(asStr(defs[asStr(g['id'])]!['deadline']), year: true)} (${asStr(g['days_left'])} days)',
                      style: TextStyle(color: C.mut, fontSize: 13)),
                ]),
              ),
            ),
          ),
        BaselinesCard(st: st),
      ],
    );
  }

  void _openGoal(BuildContext context, Map<String, dynamic> def) {
    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => GoalPage(st: st, def: def)));
  }
}

class BaselinesCard extends StatelessWidget {
  final AppState st;
  const BaselinesCard({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    return Section(
      title: 'Your baselines',
      subtitle: 'Enter these in week 1. Some mini goals are set from them (waist, push-ups).',
      children: [
        for (final b in asList(st.plan['baselines']).map(asMap))
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: NumField(
              key: ValueKey('base-${b['key']}'),
              label: '${asStr(b['label'])} · ${asStr(b['when'])}',
              value: st.results['base:${b['key']}'],
              onChanged: (v) => st.setResult('base:${b['key']}', v),
            ),
          ),
      ],
    );
  }
}

class GoalPage extends StatelessWidget {
  final AppState st;
  final Map<String, dynamic> def;
  const GoalPage({super.key, required this.st, required this.def});

  @override
  Widget build(BuildContext context) {
    final id = asStr(def['id']);
    final manualGoal = def['auto'] == 'manual' || def['auto'] == 'race';
    return Scaffold(
      appBar: AppBar(title: Text(id)),
      body: ListenableBuilder(
        listenable: st,
        builder: (context, _) {
          final g = st.goals().firstWhere((x) => x['id'] == id);
          final unit = asStr(def['unit']);
          return ListView(padding: const EdgeInsets.only(bottom: 24), children: [
            Section(title: asStr(def['name']), trailing: Pill(asStr(g['status']), color: statusColor(asStr(g['status']))), children: [
              Bar(g['progress'] as double?),
              const SizedBox(height: 8),
              KV('Now', fmtVal(g['current'] as double?, unit)),
              KV('Target', fmtVal(g['target'] as double?, unit)),
              if (def['auto'] == 'race')
                KV('Longest run so far', g['longest_run_km'] == null ? '-' : '${fmtNum(g['longest_run_km'] as double?)} km of ${fmtNum(asNum(def['distance_km']))} km')
              else
                KV('Baseline', fmtVal(g['baseline'] as double?, unit)),
              KV('Deadline', '${prettyDate(asStr(def['deadline']), year: true)} (${asStr(g['days_left'])} days left)'),
            ]),
            Section(title: 'SMART', children: [
              Para('Specific', asStr(def['specific'])),
              Para('Measurable', asStr(def['measurable'])),
              Para('Achievable', asStr(def['achievable'])),
              Para('Relevant', asStr(def['relevant'])),
              Para('Time-bound', prettyDate(asStr(def['deadline']), year: true)),
            ]),
            if (manualGoal)
              Section(
                title: 'Your result',
                subtitle: def['auto'] == 'race'
                    ? 'Your race time in minutes (for example 1 h 52 = 112). Until race day, progress shows your longest run against the race distance.'
                    : 'Race or test time in minutes (or reps for push-ups).',
                children: [
                  NumField(key: ValueKey('goal-$id'), label: 'Result', suffix: unit == 'km' ? 'min' : unit, value: st.results['goal:$id'],
                      onChanged: (v) => st.setResult('goal:$id', v)),
                ],
              ),
            Section(title: 'Mini goals', subtitle: 'Checkpoints on the way. Values from your daily log fill in by themselves.', children: [
              for (final m in st.minis(goalId: id)) MiniTile(st: st, m: m),
            ]),
          ]);
        },
      ),
    );
  }
}

class MiniTile extends StatelessWidget {
  final AppState st;
  final Map<String, dynamic> m;
  const MiniTile({super.key, required this.st, required this.m});

  @override
  Widget build(BuildContext context) {
    final unit = asStr(m['unit']);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(child: Text(asStr(m['text']), style: const TextStyle(fontWeight: FontWeight.w600))),
          Pill(asStr(m['status']), color: statusColor(asStr(m['status']))),
        ]),
        Text(
            'Due ${prettyDate(asStr(m['due']), year: true)} · target ${fmtVal(m['target'] as double?, unit)} · actual ${fmtVal(m['actual'] as double?, unit)}',
            style: TextStyle(color: C.mut, fontSize: 13)),
        const SizedBox(height: 6),
        NumField(
          key: ValueKey('mini-${m['id']}'),
          label: m['from_log'] != null ? 'Override the logged value (optional)' : 'Your result',
          suffix: unit,
          value: st.results['mini:${m['id']}'],
          onChanged: (v) => st.setResult('mini:${m['id']}', v),
        ),
      ]),
    );
  }
}
