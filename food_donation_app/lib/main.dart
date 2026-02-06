import 'package:flutter/material.dart';
import 'package:food_donation_app/screens/donor_input_screen.dart';

void main() {
  runApp(const FoodDonationApp());
}

class FoodDonationApp extends StatelessWidget {
  const FoodDonationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Food Donation App',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.green,
          brightness: Brightness.light,
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.black, fontSize: 16, fontFamily: 'sans-serif'),
          bodyMedium: TextStyle(color: Colors.black, fontSize: 14, fontFamily: 'sans-serif'),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Food Donation App'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialStatePageRoute(builder: (context) => const DonorInputScreen()),
            );
          },
          child: const Text('Go to Donate Food Screen'),
        ),
      ),
    );
  }
}

// Minimalist PageRoute to handle navigation without extra imports if needed
class MaterialStatePageRoute<T> extends MaterialPageRoute<T> {
  MaterialStatePageRoute({required super.builder});
}
