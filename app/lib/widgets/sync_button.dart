import 'package:flutter/material.dart';

import '../app_state.dart';
import '../screens/settings_screen.dart';
import 'common.dart';

/// App-bar sync indicator: spinning while syncing, cloud-off when offline, badge with waiting changes.
class SyncButton extends StatelessWidget {
  const SyncButton({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: appState,
      builder: (context, _) {
        final s = appState;
        Widget icon;
        if (s.syncing) {
          icon = const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2));
        } else if (!s.configured) {
          icon = const Icon(Icons.cloud_queue);
        } else if (!s.online || s.lastError != null) {
          icon = Icon(Icons.cloud_off, color: Theme.of(context).colorScheme.error);
        } else {
          icon = const Icon(Icons.cloud_done);
        }
        if (s.pendingCount > 0) {
          icon = Badge(label: Text('${s.pendingCount}'), child: icon);
        }
        return IconButton(
          tooltip: 'Synced ${timeAgo(s.lastSync)}',
          icon: icon,
          onPressed: () {
            if (!s.configured) {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen()));
              return;
            }
            s.sync();
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Syncing with your server…'), duration: Duration(seconds: 1)));
          },
        );
      },
    );
  }
}

class SettingsButton extends StatelessWidget {
  const SettingsButton({super.key});

  @override
  Widget build(BuildContext context) => IconButton(
        tooltip: 'Settings',
        icon: const Icon(Icons.settings_outlined),
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
      );
}
