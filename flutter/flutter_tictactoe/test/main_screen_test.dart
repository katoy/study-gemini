import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_tictactoe/main_screen.dart';
import 'package:flutter_tictactoe/settings_screen.dart';
import 'package:flutter_tictactoe/game_screen.dart';
import 'package:flutter_tictactoe/api_service.dart';

class FakeApiService extends ApiService {
  @override
  Future<List<String>> getAvailableAgents() async {
    return ['Random', 'Minimax', 'Database', 'Perfect', 'QLearning'];
  }
}

void main() {
  late FakeApiService mockApiService;

  setUp(() {
    mockApiService = FakeApiService();
  });

  testWidgets('MainScreen shows SettingsWidget initially', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: MainScreen(),
    ));
    await tester.pumpAndSettle(); // Wait for async operations

    expect(find.byType(SettingsWidget), findsOneWidget);
    expect(find.byType(GameWidget), findsNothing);
  });

  testWidgets('MainScreen switches to GameWidget when game starts', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: MainScreen(),
    ));
    await tester.pumpAndSettle(); // Wait for SettingsWidget to load

    // Tap start button in settings
    await tester.tap(find.text('ゲーム開始'));
    await tester.pumpAndSettle(); // Wait for state change and rebuild

    expect(find.byType(SettingsWidget), findsNothing);
    expect(find.byType(GameWidget), findsOneWidget);
  });

  testWidgets('MainScreen switches back to SettingsWidget when game stops', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: MainScreen(),
    ));
    await tester.pumpAndSettle(); // Wait for initial load

    // Start game
    await tester.tap(find.text('ゲーム開始'));
    await tester.pumpAndSettle(); // Wait for game to start

    // Verify game screen is shown
    expect(find.byType(GameWidget), findsOneWidget);

    // Tap stop button in game
    await tester.tap(find.text('ゲーム中断'));
    await tester.pumpAndSettle(); // Wait for state change

    // Verify settings screen is shown again
    expect(find.byType(SettingsWidget), findsOneWidget);
    expect(find.byType(GameWidget), findsNothing);
  });
}
