import 'package:flutter/material.dart';

import 'package:shared_preferences/shared_preferences.dart';

import 'app_state.dart';
import 'reminders.dart';
import 'screens/guide_screen.dart';
import 'screens/home_screen.dart';
import 'screens/session_screen.dart';
import 'screens/track_screen.dart';
import 'screens/workouts_screen.dart';

final navigatorKey = GlobalKey<NavigatorState>();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await appState.load();
  final reminders = ReminderService.instance;
  reminders.onOpenSession = (id) {
    if (appState.sessionById(id) == null) return;
    navigatorKey.currentState?.push(MaterialPageRoute(builder: (_) => SessionScreen(sessionId: id)));
  };
  try {
    await reminders.init();
  } catch (e) {
    debugPrint('Reminders unavailable: $e');
  }
  runApp(const RacePlanApp());
}

class RacePlanApp extends StatefulWidget {
  const RacePlanApp({super.key});

  @override
  State<RacePlanApp> createState() => _RacePlanAppState();
}

class _RacePlanAppState extends State<RacePlanApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    appState.startAutoSync(); // every 4 minutes while the app is open
    WidgetsBinding.instance.addPostFrameCallback((_) => _afterFirstFrame());
  }

  Future<void> _afterFirstFrame() async {
    final reminders = ReminderService.instance;
    try {
      // Ask for notification permission once, on first launch. Later changes happen in Settings.
      final prefs = await SharedPreferences.getInstance();
      if (prefs.getString('asked_notifications') == null) {
        await prefs.setString('asked_notifications', 'yes');
        await reminders.requestPermissions();
      } else {
        await reminders.refreshPermissionState();
        await reminders.reschedule();
      }
      await reminders.handleLaunch();
    } catch (e) {
      debugPrint('Reminders unavailable: $e');
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    appState.stopAutoSync();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      appState.startAutoSync(); // sync immediately on return, then every 4 minutes
      ReminderService.instance.refreshPermissionState().then((_) => ReminderService.instance.reschedule()).catchError((_) {});
    } else if (state == AppLifecycleState.paused) {
      appState.stopAutoSync();
    }
  }

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF0F7C8C);
    return MaterialApp(
      title: 'Race Plan',
      navigatorKey: navigatorKey,
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark),
      ),
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _tab = 0;

  void goToTab(int i) => setState(() => _tab = i);

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(onOpenWorkouts: () => goToTab(1)),
      const WorkoutsScreen(),
      const TrackScreen(),
      const GuideScreen(),
    ];
    return Scaffold(
      body: IndexedStack(index: _tab, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: goToTab,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.fitness_center_outlined), selectedIcon: Icon(Icons.fitness_center), label: 'Workouts'),
          NavigationDestination(icon: Icon(Icons.edit_note_outlined), selectedIcon: Icon(Icons.edit_note), label: 'Track'),
          NavigationDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: 'Guide'),
        ],
      ),
    );
  }
}
