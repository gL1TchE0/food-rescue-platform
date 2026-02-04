import 'package:flutter/material.dart';
// import 'package:firebase_core/firebase_core.dart'; // Commented out for Windows desktop
import 'ui/screens/home_screen.dart';

/// M7 Volunteer Logistics App
/// Version: 1.0.0
/// Offline-first, state-authoritative mobile app

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase (commented out for Windows desktop testing)
  // await Firebase.initializeApp();
  
  runApp(const M7VolunteerApp());
}

class M7VolunteerApp extends StatelessWidget {
  const M7VolunteerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'M7 Volunteer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2563EB), // Royal Blue
          brightness: Brightness.light,
        ),
        fontFamily: 'Inter',
        scaffoldBackgroundColor: const Color(0xFFF4F5F7),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2563EB),
          brightness: Brightness.dark,
        ),
        fontFamily: 'Inter',
        scaffoldBackgroundColor: const Color(0xFF121212),
      ),
      themeMode: ThemeMode.system,
      home: const HomeScreen(),
    );
  }
}
