import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models.dart';
import '../widgets/common.dart';
import '../widgets/sync_button.dart';
import 'session_screen.dart';

/// Week-by-week plan: pick a week, see each day's workouts, tap one to train and log it.
class WorkoutsScreen extends StatefulWidget {
  const WorkoutsScreen({super.key});

  @override
  State<WorkoutsScreen> createState() => _WorkoutsScreenState();
}

class _WorkoutsScreenState extends State<WorkoutsScreen> {
  int? _week;
  final _chips = ScrollController();

  @override
  void dispose() {
    _chips.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Workouts'), actions: const [SyncButton(), SettingsButton()]),
      body: ListenableBuilder(
        listenable: appState,
        builder: (context, _) {
          if (!appState.hasData) {
            return const Center(child: Text('Your plan appears here after the first sync.'));
          }
          final week = _week ?? appState.currentWeek;
          final sessions = appState.sessionsInWeek(week);
          final byDate = <String, List<Session>>{};
          for (final s in sessions) {
            byDate.putIfAbsent(s.date, () => []).add(s);
          }
          final training = sessions.where((s) => s.isTraining).toList();
          final done = training.where((s) => s.log?.counts ?? false).length;
          // Runs are planned in minutes (the race itself is in km and is left out of the minutes total).
          double sum(String type) =>
              training.where((s) => s.type == type && s.unit != 'km').fold(0.0, (a, s) => a + s.planned);
          final today = isoDate(DateTime.now());

          return Column(children: [
            SizedBox(
              height: 56,
              child: ListView.separated(
                controller: _chips,
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                itemCount: appState.weeks.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (context, i) {
                  final w = appState.weeks[i];
                  final wTraining = appState.sessionsInWeek(w).where((s) => s.isTraining);
                  final complete = wTraining.isNotEmpty && wTraining.every((s) => s.log?.counts ?? false);
                  return ChoiceChip(
                    label: Text('Week $w'),
                    avatar: complete ? const Icon(Icons.check, size: 16) : null,
                    selected: w == week,
                    onSelected: (_) => setState(() => _week = w),
                  );
                },
              ),
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: appState.sync,
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text('Week $week · ${sessions.isEmpty ? '' : sessions.first.phase}',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          LinearProgressIndicator(
                            value: training.isEmpty ? 0 : done / training.length,
                            minHeight: 8,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          const SizedBox(height: 8),
                          Text('$done of ${training.length} sessions done · '
                              'run ${fmtNum(sum('Run'))} min · swim ${fmtNum(sum('Swim'))} m'),
                        ]),
                      ),
                    ),
                    for (final entry in byDate.entries) ...[
                      Padding(
                        padding: const EdgeInsets.fromLTRB(4, 16, 4, 4),
                        child: Row(children: [
                          Text(fmtDate(entry.key, 'EEEE d MMM'),
                              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: entry.key == today ? Theme.of(context).colorScheme.primary : null,
                                  )),
                          if (entry.key == today) ...[
                            const SizedBox(width: 8),
                            const _Pill('TODAY'),
                          ],
                          if (entry.value.first.isFastDay) ...[
                            const SizedBox(width: 8),
                            const _Pill('FAST DAY', icon: Icons.nightlight_round),
                          ],
                        ]),
                      ),
                      ...entry.value.map((s) => SessionTile(
                            session: s,
                            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => SessionScreen(sessionId: s.id))),
                          )),
                    ],
                  ],
                ),
              ),
            ),
          ]);
        },
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final String text;
  final IconData? icon;
  const _Pill(this.text, {this.icon});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: scheme.secondaryContainer, borderRadius: BorderRadius.circular(20)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        if (icon != null) ...[Icon(icon, size: 12, color: scheme.onSecondaryContainer), const SizedBox(width: 4)],
        Text(text, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: scheme.onSecondaryContainer)),
      ]),
    );
  }
}
