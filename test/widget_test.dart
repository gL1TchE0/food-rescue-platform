// Basic Flutter widget test for Food Rescue NGO app

import 'package:flutter_test/flutter_test.dart';

import 'package:food_rescue_ngo/main.dart';

void main() {
  testWidgets('App loads and shows title', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const FoodRescueNgoApp());

    // Verify that the app bar title is shown
    expect(find.text('Available Donations'), findsOneWidget);
  });
}
