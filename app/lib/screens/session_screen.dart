import 'dart:async';

import 'package:flutter/material.dart';

import '../app_state.dart';
import '../models.dart';
import '../widgets/common.dart';

/// One workout: what to do, a workout timer with rest timers, and the log form.
class SessionScreen extends StatefulWidget {
  final int sessionId;
  const SessionScreen({super.key, required this.sessionId});

  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  late Session session;

  // workout timer
  final _watch = Stopwatch();
  Timer? _ticker;
  int _restLeft = 0;
  Timer? _restTimer;

  // log form
  String _status = 'done';
  final _minutes = TextEditingController();
  final _distance = TextEditingController();
  final _notes = TextEditingController();
  double _effort = 4;

  @override
  void initState() {
    super.initState();
    session = appState.sessionById(widget.sessionId)!;
    final log = session.log;
    if (log != null) {
      _status = log.status;
      if (log.durationMin != null) _minutes.text = fmtNum(log.durationMin, decimals: 1);
      if (log.actual != null) _distance.text = fmtNum(log.actual, decimals: 2);
      _notes.text = log.notes ?? '';
      _effort = (log.effort ?? 4).toDouble();
    } else {
      if (session.unit == 'min' && session.planned > 0) _minutes.text = fmtNum(session.planned);
      if (session.unit != 'min' && session.planned > 0) _distance.text = fmtNum(session.planned, decimals: 2);
    }
  }

  @override
  void dispose() {
    _ticker?.cancel();
    _restTimer?.cancel();
    _minutes.dispose();
    _distance.dispose();
    _notes.dispose();
    super.dispose();
  }

  void _toggleWatch() {
    setState(() {
      if (_watch.isRunning) {
        _watch.stop();
        _ticker?.cancel();
      } else {
        _watch.start();
        _ticker = Timer.periodic(const Duration(seconds: 1), (_) => setState(() {}));
      }
    });
  }

  void _resetWatch() => setState(() {
        _watch
          ..stop()
          ..reset();
        _ticker?.cancel();
      });

  void _startRest(int seconds) {
    _restTimer?.cancel();
    setState(() => _restLeft = seconds);
    _restTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      setState(() => _restLeft--);
      if (_restLeft <= 0) {
        t.cancel();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Rest over — next set!')));
        }
      }
    });
  }

  String _clock(Duration d) {
    final h = d.inHours;
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return h > 0 ? '$h:$m:$s' : '$m:$s';
  }

  /// Runs log distance in km (optional), swims in metres; strength and mobility log minutes only.
  String? get _distanceLabel {
    if (session.type == 'Run') return 'Distance (km, optional)';
    if (session.type == 'Swim') return 'Distance swum (m)';
    return null;
  }

  double? _num(TextEditingController c) => double.tryParse(c.text.trim().replaceAll(',', '.'));

  void _save({String? quickStatus}) {
    final status = quickStatus ?? _status;
    final timed = _watch.elapsed.inSeconds >= 60 ? double.parse((_watch.elapsed.inSeconds / 60).toStringAsFixed(1)) : null;
    final skipped = status == 'skipped';
    appState.logSession(
      session,
      SessionLog(
        status: status,
        actual: skipped || _distanceLabel == null ? null : _num(_distance),
        effort: skipped ? null : _effort.round(),
        durationMin: skipped ? null : (timed ?? _num(_minutes)),
        notes: _notes.text.trim().isEmpty ? null : _notes.text.trim(),
      ),
    );
    _watch.stop();
    _ticker?.cancel();
    _restTimer?.cancel();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(status == 'skipped' ? 'Marked as skipped' : 'Workout logged 💪 Syncing…'),
    ));
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final style = TypeStyle.of(session.type);
    final lines = detailLines(session.details);

    return Scaffold(
      appBar: AppBar(title: Text(session.type)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(color: style.color.withOpacity(0.12), borderRadius: BorderRadius.circular(20)),
            child: Row(children: [
              TypeIcon(session.type, size: 56),
              const SizedBox(width: 14),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(session.shortTitle, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text('${fmtDate(session.date, 'EEEE d MMM')} · ${session.timeSlot}'),
                  const SizedBox(height: 6),
                  Wrap(spacing: 6, runSpacing: 6, children: [
                    if (session.plannedLabel.isNotEmpty) Chip(label: Text(session.plannedLabel), visualDensity: VisualDensity.compact),
                    Chip(label: Text('Week ${session.week} · ${session.phase}'), visualDensity: VisualDensity.compact),
                    if (session.isFastDay) const Chip(label: Text('Fast day'), avatar: Icon(Icons.nightlight_round, size: 16), visualDensity: VisualDensity.compact),
                  ]),
                ]),
              ),
            ]),
          ),

          if (session.isTraining) ...[
            const SectionTitle('Workout timer'),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(children: [
                  Text(_clock(_watch.elapsed),
                      style: theme.textTheme.displayMedium?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                    FilledButton.icon(
                      onPressed: _toggleWatch,
                      icon: Icon(_watch.isRunning ? Icons.pause : Icons.play_arrow),
                      label: Text(_watch.isRunning ? 'Pause' : (_watch.elapsed == Duration.zero ? 'Start' : 'Resume')),
                    ),
                    const SizedBox(width: 10),
                    OutlinedButton(onPressed: _resetWatch, child: const Text('Reset')),
                  ]),
                  if (session.type == 'Strength' || session.type == 'Swim') ...[
                    const Divider(height: 28),
                    Text(_restLeft > 0 ? 'Rest: $_restLeft s' : 'Rest timer', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Wrap(spacing: 8, children: [
                      for (final s in session.type == 'Swim' ? [15, 20, 30] : [60, 90, 120])
                        ActionChip(label: Text('${s}s'), avatar: const Icon(Icons.timer_outlined, size: 18), onPressed: () => _startRest(s)),
                      if (_restLeft > 0)
                        ActionChip(
                          label: const Text('Stop'),
                          onPressed: () {
                            _restTimer?.cancel();
                            setState(() => _restLeft = 0);
                          },
                        ),
                    ]),
                  ],
                ]),
              ),
            ),
          ],

          const SectionTitle('What to do'),
          Card(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final l in lines)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 5),
                      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 7, right: 10),
                          child: Container(width: 6, height: 6, decoration: BoxDecoration(color: style.color, shape: BoxShape.circle)),
                        ),
                        Expanded(
                          child: Text(
                            l,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontWeight: l.endsWith(':') || l.startsWith('FAST DAY') || l.startsWith('WEEK') ? FontWeight.bold : null,
                              height: 1.35,
                            ),
                          ),
                        ),
                      ]),
                    ),
                ],
              ),
            ),
          ),

          if (session.isTraining) ...[
            SectionTitle(session.log == null ? 'Log this workout' : 'Your log',
                trailing: session.log == null ? null : StatusIcon(session.log)),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(value: 'done', label: Text('Done'), icon: Icon(Icons.check)),
                      ButtonSegment(value: 'partial', label: Text('Partial'), icon: Icon(Icons.timelapse)),
                      ButtonSegment(value: 'skipped', label: Text('Skipped'), icon: Icon(Icons.close)),
                    ],
                    selected: {_status},
                    onSelectionChanged: (v) => setState(() => _status = v.first),
                  ),
                  if (_status != 'skipped') ...[
                    const SizedBox(height: 16),
                    Row(children: [
                      Expanded(
                        child: TextField(
                          controller: _minutes,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: InputDecoration(
                            labelText: 'Minutes',
                            helperText: _watch.elapsed.inSeconds >= 60 ? 'Timer time is used' : null,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ),
                      if (_distanceLabel != null) ...[
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _distance,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            decoration: InputDecoration(labelText: _distanceLabel, border: const OutlineInputBorder()),
                          ),
                        ),
                      ],
                    ]),
                    const SizedBox(height: 16),
                    Text('Effort: ${_effort.round()} / 10 — ${_effortWord(_effort.round())}', style: theme.textTheme.titleSmall),
                    Slider(
                      value: _effort,
                      min: 1,
                      max: 10,
                      divisions: 9,
                      label: '${_effort.round()}',
                      onChanged: (v) => setState(() => _effort = v),
                    ),
                  ],
                  const SizedBox(height: 8),
                  TextField(
                    controller: _notes,
                    maxLines: 3,
                    decoration: const InputDecoration(labelText: 'Notes (how it felt, pain, weather…)', border: OutlineInputBorder()),
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                    onPressed: _save,
                    icon: const Icon(Icons.save_alt),
                    label: Text(session.log == null ? 'Save workout' : 'Update log'),
                  ),
                  if (session.log != null)
                    TextButton(
                      onPressed: () {
                        appState.clearSessionLog(session);
                        Navigator.pop(context);
                      },
                      child: const Text('Clear log'),
                    ),
                ]),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _effortWord(int e) {
    if (e <= 2) return 'very easy';
    if (e <= 4) return 'easy, can chat';
    if (e <= 6) return 'steady';
    if (e <= 8) return 'hard';
    return 'all-out';
  }
}
