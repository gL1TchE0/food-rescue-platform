import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'screens/dashboard_screen.dart';
import 'config/api_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Auto-login for testing - get token and save it
  await _autoLogin();
  
  runApp(const FoodRescueNgoApp());
}

/// Auto-login with test credentials for development
Future<void> _autoLogin() async {
  try {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': 'hope@foundation.org',
        'password': 'password123',
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final token = data['access_token'];
      print('🔑 Received token from login: ${token.substring(0, 15)}... (${token.length} chars)');
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', token);
      print('✅ Auto-login successful! Token saved.');
    } else {
      print('❌ Auto-login failed: ${response.body}');
    }
  } catch (e) {
    print('❌ Auto-login error: $e');
  }
}

class FoodRescueNgoApp extends StatelessWidget {
  const FoodRescueNgoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Food Rescue - NGO',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.green,
        primaryColor: const Color(0xFF4CAF50),
        scaffoldBackgroundColor: Colors.grey.shade100,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4CAF50),
          primary: const Color(0xFF4CAF50),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF4CAF50),
          foregroundColor: Colors.white,
          elevation: 2,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF4CAF50),
            foregroundColor: Colors.white,
          ),
        ),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
    );
  }
}
