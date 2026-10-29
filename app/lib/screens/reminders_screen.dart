import 'package:flutter/material.dart';

import '../reminders.dart';

class RemindersScreen extends StatefulWidget {
  const RemindersScreen({super.key});

  @override
  State<RemindersScreen> createState() => _RemindersScreenState();
}

class _RemindersScreenState extends State<RemindersScreen> {
  final r = ReminderService.instance;
  late ReminderSettings s = ReminderSettings.fromJson(r.settings.toJson());
  int? _pending;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    try {
      await r.refreshPermissionState();
      final n = await r.pendingCount();
      if (mounted) setState(() => _pending = n);
    } catch (_) {}
  }

  Future<void> _save(ReminderSettings next) async {
    setState(() {
      s = next;
      _busy = true;
    });
    try {
      await r.saveSettings(next);
    } finally {
      await _refresh();
      if (mounted) setState(() => _busy = false);
    }
  }

  ReminderSettings _copy() => ReminderSettings.fromJson(s.toJson());

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final blocked = r.permissionGranted == false;
    return Scaffold(
      appBar: AppBar(title: const Text('Reminders')),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          if (blocked)
            Card(
              margin: const EdgeInsets.fromLTRB(16, 8, 16, 8),
              color: theme.colorScheme.errorContainer,
              child: ListTile(
                leading: Icon(Icons.notifications_off, color: theme.colorScheme.onErrorContainer),
                title: const Text('Notifications are blocked'),
                subtitle: const Text('Allow them so your reminders can appear.'),
                trailing: TextButton(
                  onPressed: () async {
                    await r.requestPermissions();
                    await _refresh();
                  },
                  child: const Text('Allow'),
                ),
              ),
            ),
          SwitchListTile(
            secondary: const Icon(Icons.notifications_active_outlined),
            title: const Text('Workout reminders', style: TextStyle(fontWeight: FontWeight.w600)),
            subtitle: const Text('Scheduled on your phone for every remaining day of the plan. They arrive even with the app closed or offline.'),
            value: s.enabled,
            onChanged: _busy ? null : (v) => _save(_copy()..enabled = v),
          ),
          const Divider(),
          ListTile(
            enabled: s.enabled,
            leading: const Icon(Icons.wb_twilight),
            title: const Text("Today's plan"),
            subtitle: const Text('Summary of the day’s workouts (fast days at 04:10, before suhoor)'),
            trailing: Text(hhmm(s.summaryMinutes), style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            onTap: !s.enabled || _busy
                ? null
                : () async {
                    final t = await showTimePicker(context: context, initialTime: s.summaryTime);
                    if (t != null) await _save(_copy()..summaryMinutes = t.hour * 60 + t.minute);
                  },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.alarm),
            title: const Text('Before each workout'),
            subtitle: Text('Morning ${hhmm(slotReminderTimes['Morning']!)} · Afternoon ${hhmm(slotReminderTimes['Afternoon']!)} · Any time ${hhmm(slotReminderTimes['Any time']!)} · '
                'Evening ${hhmm(slotReminderTimes['Evening']!)} · After iftar ${hhmm(slotReminderTimes['After iftar']!)} · '
                'Before bed ${hhmm(slotReminderTimes['Before bed']!)}'),
            value: s.perWorkout,
            onChanged: !s.enabled || _busy ? null : (v) => _save(_copy()..perWorkout = v),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.fact_check_outlined),
            title: const Text('Log reminder'),
            subtitle: Text('${hhmm(logNudgeMinutes)} if a workout from that day isn’t logged yet'),
            value: s.logNudge,
            onChanged: !s.enabled || _busy ? null : (v) => _save(_copy()..logNudge = v),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.monitor_weight_outlined),
            title: const Text('Weigh-in prompt'),
            subtitle: Text('In the morning summary; fast days at ${hhmm(fastDaySummaryMinutes)}, before suhoor'),
            value: s.weighIn,
            onChanged: !s.enabled || _busy ? null : (v) => _save(_copy()..weighIn = v),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.event_available),
            title: Text(_pending == null ? 'Checking scheduled reminders…' : '$_pending reminders scheduled ahead'),
            subtitle: const Text('Logging a workout cancels its reminders. The list rebuilds after every sync.'),
          ),
          ListTile(
            leading: Icon(r.exactAllowed == false ? Icons.timer_off_outlined : Icons.timer_outlined),
            title: Text(r.exactAllowed == false ? 'Approximate timing' : 'Exact timing'),
            subtitle: Text(r.exactAllowed == false
                ? 'Android may deliver reminders a few minutes late. Tap to allow exact alarms.'
                : 'Reminders arrive on the minute.'),
            onTap: r.exactAllowed == false
                ? () async {
                    await r.requestPermissions();
                    await _refresh();
                  }
                : null,
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: OutlinedButton.icon(
              onPressed: () => r.sendTest(),
              icon: const Icon(Icons.notifications),
              label: const Text('Send a test notification'),
            ),
          ),
        ],
      ),
    );
  }
}
