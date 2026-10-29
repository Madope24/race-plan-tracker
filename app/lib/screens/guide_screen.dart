import 'package:flutter/material.dart';

import '../app_state.dart';
import '../widgets/sync_button.dart';

IconData _guideIcon(String? id) {
  switch (id) {
    case 'strength':
      return Icons.fitness_center;
    case 'mobility':
      return Icons.self_improvement;
    case 'nutrition':
      return Icons.restaurant;
    case 'race':
      return Icons.emoji_events_outlined;
    case 'swim':
      return Icons.pool;
    case 'meals':
      return Icons.restaurant_menu;
    case 'fuel':
      return Icons.local_drink_outlined;
    case 'rules':
      return Icons.rule;
    default:
      return Icons.flag_outlined;
  }
}

/// Reference library: exercises, mobility routines, nutrition, race week, goals and rules.
class GuideScreen extends StatelessWidget {
  const GuideScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Guide'), actions: const [SyncButton(), SettingsButton()]),
      body: ListenableBuilder(
        listenable: appState,
        builder: (context, _) {
          final guides = (appState.reference?['guides'] as List?) ?? [];
          if (guides.isEmpty) {
            return const Center(child: Text('The guide downloads with your first sync.'));
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              for (final g in guides)
                Card(
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    leading: CircleAvatar(child: Icon(_guideIcon((g as Map)['id'] as String?))),
                    title: Text(g['title'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('${(g['sections'] as List).length} sections'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => GuideDetailScreen(guide: Map<String, dynamic>.from(g))),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class GuideDetailScreen extends StatelessWidget {
  final Map<String, dynamic> guide;
  const GuideDetailScreen({super.key, required this.guide});

  @override
  Widget build(BuildContext context) {
    final sections = guide['sections'] as List;
    return Scaffold(
      appBar: AppBar(title: Text(guide['title'] as String)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 24),
        children: [
          for (var i = 0; i < sections.length; i++)
            Card(
              clipBehavior: Clip.antiAlias,
              child: ExpansionTile(
                initiallyExpanded: i == 0,
                title: Text((sections[i] as Map)['title'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
                childrenPadding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                children: [for (final row in (sections[i]['rows'] as List)) _RowCard(row as List)],
              ),
            ),
        ],
      ),
    );
  }
}

/// One table row from the plan, shown as a small card: first value is the heading, the rest are labelled lines.
class _RowCard extends StatelessWidget {
  final List cells;
  const _RowCard(this.cells);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final first = cells.first as Map;
    final rest = cells.skip(1).cast<Map>().toList();
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(first['value'] as String, style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
        for (final c in rest) ...[
          const SizedBox(height: 4),
          if ((c['label'] as String).isNotEmpty)
            Text.rich(TextSpan(children: [
              TextSpan(text: '${c['label']}: ', style: TextStyle(fontWeight: FontWeight.w600, color: theme.colorScheme.primary)),
              TextSpan(text: c['value'] as String),
            ]))
          else
            Text(c['value'] as String),
        ],
      ]),
    );
  }
}
