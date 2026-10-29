import 'dart:async';

import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models.dart';
import '../widgets/charts.dart';
import '../widgets/common.dart';
import '../widgets/sync_button.dart';
import 'reminders_screen.dart';
import 'session_screen.dart';
import 'settings_screen.dart';

/// Dashboard. Rebuilds whenever the state changes (every sync, every log) and ticks each minute
/// so "synced X min ago" stays true.
class HomeScreen extends StatefulWidget {
  final VoidCallback onOpenWorkouts;
  const HomeScreen({super.key, required this.onOpenWorkouts});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Timer? _tick;

  @override
  void initState() {
    super.initState();
    _tick = Timer.periodic(const Duration(minutes: 1), (_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _tick?.cancel();
    super.dispose();
  }

  void _open(Session s) => Navigator.push(context, MaterialPageRoute(builder: (_) => SessionScreen(sessionId: s.id)));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Race Plan', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            tooltip: 'Reminders',
            icon: const Icon(Icons.notifications_none),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RemindersScreen())),
          ),
          const SyncButton(),
          const SettingsButton(),
        ],
      ),
      body: ListenableBuilder(
        listenable: appState,
        builder: (context, _) {
          if (!appState.configured || (!appState.hasData && appState.dashboard == null)) {
            return _ConnectPrompt(syncing: appState.syncing, error: appState.lastError, configured: appState.configured);
          }
          return RefreshIndicator(
            onRefresh: appState.sync,
            child: _content(context),
          );
        },
      ),
    );
  }

  Widget _content(BuildContext context) {
    final d = appState.dashboard ?? {};
    final theme = Theme.of(context);
    final today = d['today'] as String? ?? isoDate(DateTime.now());
    final todays = appState.sessionsOn(today).where((s) => s.isTraining).toList();
    final next = appState.sessionById(d['next_session_id'] as int?);
    final sessions = Map<String, dynamic>.from(d['sessions'] as Map? ?? {});
    final week = Map<String, dynamic>.from(d['this_week'] as Map? ?? {});
    final weight = Map<String, dynamic>.from(d['weight'] as Map? ?? {});
    final habits = Map<String, dynamic>.from(d['habits_7d'] as Map? ?? {});
    final completion = ((sessions['completion_to_date'] as num?) ?? 0).toDouble();
    final currentWeek = (d['current_week'] as int?) ?? 0;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
      children: [
        _HeroCard(dashboard: d),
        if (d['is_fast_day'] == true)
          Card(
            color: theme.colorScheme.tertiaryContainer,
            margin: const EdgeInsets.only(top: 12),
            child: ListTile(
              leading: Icon(Icons.nightlight_round, color: theme.colorScheme.onTertiaryContainer),
              title: const Text('Fast day', style: TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('No training while fasting. Break the fast at ${d['fast_until'] ?? '18:50'}, train about an hour later.'),
            ),
          ),

        SectionTitle("Today's workouts", trailing: TextButton(onPressed: widget.onOpenWorkouts, child: const Text('Full plan'))),
        if (todays.isEmpty)
          Card(
            child: ListTile(
              leading: const TypeIcon('Rest'),
              title: Text(d['plan_started'] == false ? 'Plan starts ${fmtDate(d['start_date'] as String? ?? today, 'EEEE d MMMM')}' : 'Rest day'),
              subtitle: next == null ? null : Text('Next: ${next.shortTitle} · ${fmtDate(next.date)}'),
              onTap: next == null ? null : () => _open(next),
            ),
          )
        else
          ...todays.map((s) => SessionTile(session: s, onTap: () => _open(s))),

        if (d['decision_last_week'] != null || d['decision_this_week'] != null) ...[
          const SectionTitle('Training decision'),
          _DecisionCard(
            decision: Map<String, dynamic>.from((d['decision_last_week'] ?? d['decision_this_week']) as Map),
            isLastWeek: d['decision_last_week'] != null,
          ),
        ],

        const SectionTitle('Progress'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(children: [
              SizedBox(
                width: 84,
                height: 84,
                child: Stack(alignment: Alignment.center, children: [
                  SizedBox(
                    width: 84,
                    height: 84,
                    child: CircularProgressIndicator(
                      value: completion,
                      strokeWidth: 9,
                      backgroundColor: theme.colorScheme.surfaceContainerHighest,
                      strokeCap: StrokeCap.round,
                    ),
                  ),
                  Text('${(completion * 100).round()}%', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                ]),
              ),
              const SizedBox(width: 18),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('Sessions completed', style: theme.textTheme.labelLarge),
                  Text('${sessions['done_to_date'] ?? 0} of ${sessions['planned_to_date'] ?? 0} so far',
                      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  Text('${sessions['done_total'] ?? 0} / ${sessions['total'] ?? 0} in the whole plan', style: theme.textTheme.bodySmall),
                  const SizedBox(height: 8),
                  Row(children: [
                    const Icon(Icons.local_fire_department, color: Color(0xFFE07A1F), size: 20),
                    const SizedBox(width: 4),
                    Text('${d['streak_days'] ?? 0}-day streak', style: theme.textTheme.titleSmall),
                  ]),
                ]),
              ),
            ]),
          ),
        ),
        const SizedBox(height: 10),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          childAspectRatio: 1.45,
          children: [
            StatCard(
              icon: Icons.monitor_weight_outlined,
              label: 'Weight (7-day average)',
              value: weight['latest'] == null ? '–' : '${fmtNum(weight['latest'] as num)} kg',
              sub: weight['latest'] == null
                  ? 'Weigh in each morning in Track'
                  : '${((weight['lost'] as num?) ?? 0) >= 0 ? '−' : '+'}${fmtNum(((weight['lost'] as num?) ?? 0).abs())} kg since start',
              color: const Color(0xFFE07A1F),
            ),
            StatCard(
              icon: Icons.calendar_view_week,
              label: 'This week',
              value: '${week['done'] ?? 0}/${week['planned'] ?? 0}',
              sub: 'Week $currentWeek · ${d['phase'] ?? ''}',
            ),
            StatCard(
              icon: Icons.directions_run,
              label: 'Run this week',
              value: '${fmtNum(week['run_min_done'] as num?)} min',
              sub: 'of ${fmtNum(week['run_min_planned'] as num?)} min · longest ${fmtNum(d['longest_run_min'] as num?)} min',
              color: TypeStyle.of('Run').color,
            ),
            StatCard(
              icon: Icons.pool,
              label: 'Swim this week',
              value: '${fmtNum(week['swim_m_done'] as num?)} m',
              sub: 'of ${fmtNum(week['swim_m_planned'] as num?)} m · non-stop ${fmtNum(d['longest_swim_m'] as num?)} m',
              color: TypeStyle.of('Swim').color,
            ),
          ],
        ),

        const SectionTitle('Race outlook'),
        _TestCard(test: d['test'] == null ? null : Map<String, dynamic>.from(d['test'] as Map), raceDate: d['race_date'] as String?),

        const SectionTitle('Weight'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: WeightChart(
              series: [for (final p in (d['weight_series'] as List? ?? [])) Map<String, dynamic>.from(p as Map)],
            ),
          ),
        ),

        const SectionTitle('Weekly completion'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: WeeklyBars(
              weeks: [for (final w in (d['weekly_completion'] as List? ?? [])) Map<String, dynamic>.from(w as Map)],
              currentWeek: currentWeek,
            ),
          ),
        ),

        const SectionTitle('Last 7 days'),
        Row(children: [
          Expanded(child: _MiniStat(icon: Icons.bedtime_outlined, value: '${fmtNum(habits['sleep_hours'] as num?)} h', label: 'Sleep')),
          const SizedBox(width: 8),
          Expanded(child: _MiniStat(icon: Icons.bolt_outlined, value: '${fmtNum(habits['energy'] as num?)}/5', label: 'Energy')),
          const SizedBox(width: 8),
          Expanded(child: _MiniStat(icon: Icons.favorite_border, value: '${fmtNum(habits['resting_hr'] as num?)}', label: 'Resting pulse')),
        ]),

        const SizedBox(height: 18),
        Center(
          child: Text(
            appState.pendingCount > 0
                ? '${appState.pendingCount} change(s) waiting to sync · last sync ${timeAgo(appState.lastSync)}'
                : 'Synced ${timeAgo(appState.lastSync)} · auto-sync every 4 minutes',
            style: theme.textTheme.bodySmall,
          ),
        ),
        if (appState.lastError != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Center(
              child: Text(appState.lastError!, textAlign: TextAlign.center, style: TextStyle(color: theme.colorScheme.error, fontSize: 12)),
            ),
          ),
      ],
    );
  }
}

class _HeroCard extends StatelessWidget {
  final Map<String, dynamic> dashboard;
  const _HeroCard({required this.dashboard});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final week = (dashboard['current_week'] as int?) ?? 0;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: LinearGradient(colors: [scheme.primary, scheme.tertiary], begin: Alignment.topLeft, end: Alignment.bottomRight),
      ),
      child: Row(children: [
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(week == 0 ? 'Week 0 · start-up days' : 'Week $week of 14 · ${dashboard['phase'] ?? ''}',
                style: TextStyle(color: scheme.onPrimary.withOpacity(0.85), fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            Text('Half marathon', style: TextStyle(color: scheme.onPrimary, fontSize: 22, fontWeight: FontWeight.bold)),
            Text(
              dashboard['race_date'] == null ? '' : fmtDate(dashboard['race_date'] as String, 'EEEE d MMMM yyyy'),
              style: TextStyle(color: scheme.onPrimary.withOpacity(0.85)),
            ),
          ]),
        ),
        Column(children: [
          Text('${dashboard['days_to_race'] ?? '–'}',
              style: TextStyle(color: scheme.onPrimary, fontSize: 44, fontWeight: FontWeight.w900, height: 1)),
          Text('days to go', style: TextStyle(color: scheme.onPrimary.withOpacity(0.85))),
        ]),
      ]),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  const _MiniStat({required this.icon, required this.value, required this.label});

  @override
  Widget build(BuildContext context) => Card(
        margin: EdgeInsets.zero,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Column(children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            Text(label, style: Theme.of(context).textTheme.bodySmall),
          ]),
        ),
      );
}

class _ConnectPrompt extends StatelessWidget {
  final bool syncing;
  final bool configured;
  final String? error;
  const _ConnectPrompt({required this.syncing, required this.configured, this.error});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.cloud_sync_outlined, size: 72, color: theme.colorScheme.primary),
          const SizedBox(height: 16),
          Text(configured ? 'Loading your plan…' : 'Connect to your server', style: theme.textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(
            configured
                ? (error ?? 'Fetching your 14-week plan from the server.')
                : 'Enter your server address and API token once. After that everything syncs automatically every 4 minutes.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          if (syncing)
            const CircularProgressIndicator()
          else
            FilledButton.icon(
              icon: Icon(configured ? Icons.refresh : Icons.settings),
              label: Text(configured ? 'Try again' : 'Open settings'),
              onPressed: () => configured
                  ? appState.sync()
                  : Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
            ),
          if (configured && !syncing)
            TextButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
              child: const Text('Check settings'),
            ),
        ]),
      ),
    );
  }
}

/// The Sunday rule (plan section 14): green = progress, amber = repeat the week, red = step back.
class _DecisionCard extends StatelessWidget {
  final Map<String, dynamic> decision;
  final bool isLastWeek;
  const _DecisionCard({required this.decision, required this.isLastWeek});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final status = decision['status'] as String? ?? 'green';
    final color = status == 'red'
        ? const Color(0xFFD64545)
        : status == 'amber'
            ? const Color(0xFFE0A21F)
            : const Color(0xFF2E9E5B);
    final label = status == 'red' ? 'Step back' : status == 'amber' ? 'Repeat the week' : 'Progress';
    final reasons = (decision['reasons'] as List? ?? []).cast<String>();
    final completion = ((decision['completion'] as num?) ?? 0) * 100;
    return Card(
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border(left: BorderSide(color: color, width: 6)),
        ),
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Icon(status == 'green' ? Icons.trending_up : status == 'amber' ? Icons.replay : Icons.trending_down, color: color),
            const SizedBox(width: 8),
            Expanded(
              child: Text('$label · week ${decision['week']}${isLastWeek ? '' : ' so far'}',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            ),
          ]),
          const SizedBox(height: 6),
          Text(decision['action'] as String? ?? ''),
          if (reasons.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text('Because ${reasons.join('; ')}.', style: theme.textTheme.bodySmall),
          ],
          const SizedBox(height: 6),
          Text(
            '${completion.round()}% done'
            '${decision['avg_run_rpe'] != null ? ' · runs RPE ${fmtNum(decision['avg_run_rpe'] as num)}' : ''}'
            '${decision['avg_sleep'] != null ? ' · sleep ${fmtNum(decision['avg_sleep'] as num)} h' : ''}'
            '${decision['max_pain'] != null ? ' · max pain ${decision['max_pain']}/10' : ''}',
            style: theme.textTheme.bodySmall,
          ),
        ]),
      ),
    );
  }
}

/// Latest 5 km test → projected finish and suggested race plan.
class _TestCard extends StatelessWidget {
  final Map<String, dynamic>? test;
  final String? raceDate;
  const _TestCard({required this.test, required this.raceDate});

  String _hm(num minutes) {
    final m = minutes.round();
    return '${m ~/ 60}:${(m % 60).toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (test == null) {
      return const Card(
        child: ListTile(
          leading: Icon(Icons.timer_outlined),
          title: Text('No 5 km test yet'),
          subtitle: Text('Tests on Fri 27 Nov, Fri 25 Dec and Tue 12 Jan. Log the time in Track → Weekly check-in.'),
        ),
      );
    }
    final t = test!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Race plan: ${t['plan']}', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text('From your week ${t['week']} test: 5 km in ${fmtNum(t['test_min'] as num)} min.'),
              Text('Projected finish on the Kilimanjaro course: about ${_hm(t['course_min'] as num)} '
                  '(flat course ${_hm(t['flat_min'] as num)}). Cut-off 12:30.', style: theme.textTheme.bodySmall),
            ]),
          ),
          const Icon(Icons.flag_outlined, size: 32),
        ]),
      ),
    );
  }
}
