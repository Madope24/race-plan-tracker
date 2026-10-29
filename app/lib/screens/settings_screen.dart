import 'package:flutter/material.dart';

import '../app_state.dart';
import '../widgets/common.dart';
import 'reminders_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final TextEditingController _url = TextEditingController(text: appState.serverUrl);
  late final TextEditingController _token = TextEditingController(text: appState.token);
  bool _hide = true;
  bool _testing = false;
  String? _result;

  @override
  void dispose() {
    _url.dispose();
    _token.dispose();
    super.dispose();
  }

  Future<void> _test() async {
    setState(() {
      _testing = true;
      _result = null;
    });
    final r = await appState.testConnection(_url.text, _token.text);
    if (!mounted) return;
    setState(() {
      _testing = false;
      _result = r == 'ok' ? '✅ Connected — server and token are correct.' : '⚠️ $r';
    });
  }

  Future<void> _save() async {
    final messenger = ScaffoldMessenger.of(context);
    await appState.saveSettings(_url.text, _token.text);
    messenger.showSnackBar(SnackBar(content: Text(appState.lastError ?? 'Saved and synced')));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListenableBuilder(
        listenable: appState,
        builder: (context, _) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Server', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(
              controller: _url,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: 'Server address',
                helperText: 'e.g. http://164.68.97.148:7070 or https://your-domain:773',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _token,
              obscureText: _hide,
              decoration: InputDecoration(
                labelText: 'API token',
                helperText: 'The API_TOKEN from the .env file on your server',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(_hide ? Icons.visibility : Icons.visibility_off),
                  onPressed: () => setState(() => _hide = !_hide),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _testing ? null : _test,
                  icon: _testing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.network_check),
                  label: const Text('Test'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(child: FilledButton.icon(onPressed: _save, icon: const Icon(Icons.save), label: const Text('Save'))),
            ]),
            if (_result != null) Padding(padding: const EdgeInsets.only(top: 12), child: Text(_result!)),
            const Divider(height: 40),
            Card(
              margin: EdgeInsets.zero,
              child: ListTile(
                leading: const Icon(Icons.notifications_active_outlined),
                title: const Text('Workout reminders'),
                subtitle: const Text('Daily plan, before each workout, log and weigh-in reminders'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RemindersScreen())),
              ),
            ),
            const Divider(height: 40),
            Text('Sync', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.schedule),
              title: const Text('Automatic sync every 4 minutes'),
              subtitle: const Text('While the app is open, plus whenever you open it and a few seconds after every change.'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.history),
              title: Text('Last sync: ${timeAgo(appState.lastSync)}'),
              subtitle: Text(appState.pendingCount == 0
                  ? 'Everything is on the server'
                  : '${appState.pendingCount} change(s) waiting — they upload on the next successful sync'),
            ),
            if (appState.lastError != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(Icons.error_outline, color: theme.colorScheme.error),
                title: Text(appState.lastError!),
              ),
            const SizedBox(height: 8),
            FilledButton.tonalIcon(
              onPressed: appState.syncing || !appState.configured ? null : appState.sync,
              icon: appState.syncing
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.sync),
              label: Text(appState.syncing ? 'Syncing…' : 'Sync now'),
            ),
          ],
        ),
      ),
    );
  }
}
