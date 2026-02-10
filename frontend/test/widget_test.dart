import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:foodrescue_dispatcher/main.dart';

void main() {
  testWidgets('App smoke test - renders SurplusSync', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: FoodRescueApp(),
      ),
    );

    // Verify the app launches (splash screen shows SurplusSync)
    expect(find.text('SurplusSync'), findsOneWidget);
  });
}
