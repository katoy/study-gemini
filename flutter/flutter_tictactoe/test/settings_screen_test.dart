import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_tictactoe/settings_screen.dart';
import 'package:flutter_tictactoe/models.dart';
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

  testWidgets('SettingsWidget displays correct UI elements', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (request) {},
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle(); // Wait for future to complete

    expect(find.text('プレイヤーの順番'), findsOneWidget);
    expect(find.text('あなた（先手）'), findsOneWidget);
    expect(find.text('マシン（先手）'), findsOneWidget);
    expect(find.text('対戦エージェント'), findsOneWidget);
    expect(find.text('ゲーム開始'), findsOneWidget);
    expect(find.text('ゲーム中断'), findsOneWidget);
  });

  testWidgets('SettingsWidget calls onStartGame when start button pressed', (WidgetTester tester) async {
    StartGameRequest? request;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {
            request = req;
          },
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(request, isNotNull);
    expect(request!.humanPlayerSymbol, 'X');
    expect(request!.playerXType, 'Human');
    expect(request!.playerOType, 'Random');
  });

  testWidgets('SettingsWidget allows selecting O (second)', (WidgetTester tester) async {
    StartGameRequest? request;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {
            request = req;
          },
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Tap O radio button (find by value)
    final oRadio = find.byWidgetPredicate(
      (widget) => widget is Radio<String> && widget.value == 'O'
    );
    await tester.tap(oRadio);
    await tester.pump();

    // Tap start button
    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(request, isNotNull);
    expect(request!.humanPlayerSymbol, 'O');
    expect(request!.playerXType, 'Random');
    expect(request!.playerOType, 'Human');
  });

  testWidgets('SettingsWidget allows selecting different agents', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {},
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Verify dropdown exists and has options
    expect(find.byType(DropdownButton<String>), findsOneWidget);
    
    // Tap dropdown to open
    await tester.tap(find.byType(DropdownButton<String>));
    await tester.pumpAndSettle();

    // Verify all agent options are available
    expect(find.text('Random').hitTestable(), findsWidgets);
    expect(find.text('Minimax').hitTestable(), findsOneWidget);
    expect(find.text('Database').hitTestable(), findsOneWidget);
    expect(find.text('Perfect').hitTestable(), findsOneWidget);
    expect(find.text('QLearning').hitTestable(), findsOneWidget);
  });

  testWidgets('SettingsWidget allows selecting X (first) after selecting O', (WidgetTester tester) async {
    StartGameRequest? request;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {
            request = req;
          },
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // First select O
    final oRadio = find.byWidgetPredicate(
      (widget) => widget is Radio<String> && widget.value == 'O'
    );
    await tester.tap(oRadio);
    await tester.pump();

    // Then select X back
    final xRadio = find.byWidgetPredicate(
      (widget) => widget is Radio<String> && widget.value == 'X'
    );
    await tester.tap(xRadio);
    await tester.pump();

    // Tap start button
    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(request, isNotNull);
    expect(request!.humanPlayerSymbol, 'X');
  });

  testWidgets('SettingsWidget allows changing agent type', (WidgetTester tester) async {
    StartGameRequest? request;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {
            request = req;
          },
          apiService: mockApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Open dropdown
    await tester.tap(find.byType(DropdownButton<String>));
    await tester.pumpAndSettle();

    // Select Minimax
    await tester.tap(find.text('Minimax').last);
    await tester.pumpAndSettle();

    // Tap start button
    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(request, isNotNull);
    expect(request!.playerOType, 'Minimax');
  });

  testWidgets('SettingsWidget handles error when fetching agents', (WidgetTester tester) async {
    final errorApiService = FakeErrorApiService();
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {},
          apiService: errorApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Should still show default 'Random'
    expect(find.text('Random').hitTestable(), findsOneWidget);
    // Should not crash
  });

  testWidgets('SettingsWidget updates selected agent when Random not in list', (WidgetTester tester) async {
    final customApiService = FakeCustomApiService();
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(
          onStartGame: (req) {},
          apiService: customApiService,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Should show first agent from custom list (Minimax)
    expect(find.text('Minimax').hitTestable(), findsOneWidget);
  });
}

class FakeErrorApiService extends ApiService {
  @override
  Future<List<String>> getAvailableAgents() async {
    throw Exception('Network error');
  }
}

class FakeCustomApiService extends ApiService {
  @override
  Future<List<String>> getAvailableAgents() async {
    return ['Minimax', 'Database', 'Perfect'];
  }
}
