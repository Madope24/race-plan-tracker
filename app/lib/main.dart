import 'package:flutter/material.dart';

import 'home_screen.dart';
import 'nutrition_screen.dart';
import 'profile_screen.dart';
import 'progress_screen.dart';
import 'state.dart';
import 'training_screen.dart';
import 'ui.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final st = await AppState.load();
  runApp(EnduraForgeApp(st: st));
  st.refreshReminders();
  st.sync();
}

class EnduraForgeApp extends StatelessWidget {
  final AppState st;
  const EnduraForgeApp({super.key, required this.st});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: st,
      builder: (context, _) => MaterialApp(
        title: 'EnduraForge',
        debugShowCheckedModeBanner: false,
        theme: buildTheme(st.darkMode),
        home: HomeShell(st: st),
      ),
    );
  }
}

class HomeShell extends StatefulWidget {
  final AppState st;
  const HomeShell({super.key, required this.st});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int tab = 0;

  @override
  Widget build(BuildContext context) {
    final st = widget.st;
    final pages = <Widget>[
      HomeScreen(st: st, onOpenTraining: () => setState(() => tab = 1), onOpenNutrition: () => setState(() => tab = 2)),
      TrainingScreen(st: st),
      NutritionScreen(st: st),
      ProgressScreen(st: st),
      ProfileScreen(st: st),
    ];
    const titles = ['EnduraForge', 'Training', 'Nutrition', 'Progress', 'Profile'];
    return Scaffold(
      appBar: AppBar(
        title: Text(titles[tab]),
        actions: [
          if (st.token != null)
            IconButton(
              tooltip: st.syncNote,
              icon: st.syncing
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                  : Icon(st.outbox.isEmpty && st.activityOutbox.isEmpty ? Icons.cloud_done_outlined : Icons.cloud_upload_outlined,
                      color: st.syncNote.startsWith('Not synced') ? C.warn : null),
              onPressed: () => st.sync(),
            )
          else
            Padding(padding: const EdgeInsets.only(right: 12), child: Icon(Icons.cloud_off_outlined, color: C.mut, size: 20)),
        ],
      ),
      body: SafeArea(child: AnimatedSwitcher(duration: const Duration(milliseconds: 180), child: KeyedSubtree(key: ValueKey(tab), child: pages[tab]))),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.fitness_center_outlined), selectedIcon: Icon(Icons.fitness_center), label: 'Training'),
          NavigationDestination(icon: Icon(Icons.restaurant_outlined), selectedIcon: Icon(Icons.restaurant), label: 'Nutrition'),
          NavigationDestination(icon: Icon(Icons.insights_outlined), selectedIcon: Icon(Icons.insights), label: 'Progress'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
