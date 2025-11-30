import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_tictactoe/game_screen.dart';
import 'package:flutter_tictactoe/api_service.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  testWidgets('GameWidget loads and displays board', (WidgetTester tester) async {
    final client = MockClient((request) async {
      if (request.url.path == '/game/start') {
        return http.Response(jsonEncode({
          'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'X',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      }
      return http.Response('Not Found', 404);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    // Wait for future to complete
    await tester.pump();

    expect(find.byWidgetPredicate((widget) => widget is CustomPaint && widget.painter is BoardPainter), findsOneWidget);
    expect(find.text('ゲーム中断'), findsOneWidget);
  });

  testWidgets('GameWidget displays error message on API failure', (WidgetTester tester) async {
    final client = MockClient((request) async {
      return http.Response('Server Error', 500);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();

    expect(find.textContaining('Error'), findsOneWidget);
  });

  testWidgets('GameWidget displays winner message when game ends with win', (WidgetTester tester) async {
    final client = MockClient((request) async {
      return http.Response(jsonEncode({
        'board': [['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']],
        'current_player': 'X',
        'winner': 'X',
        'winner_line': [[0, 0], [0, 1], [0, 2]],
        'game_over': true,
      }), 200);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();

    expect(find.text('Xの勝ちです！'), findsOneWidget);
  });

  testWidgets('GameWidget displays draw message when game ends in draw', (WidgetTester tester) async {
    final client = MockClient((request) async {
      return http.Response(jsonEncode({
        'board': [['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']],
        'current_player': 'X',
        'winner': 'draw',
        'winner_line': null,
        'game_over': true,
      }), 200);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();

    expect(find.text('引き分けです！'), findsOneWidget);
  });

  testWidgets('GameWidget can restart game', (WidgetTester tester) async {
    int callCount = 0;
    final client = MockClient((request) async {
      callCount++;
      return http.Response(jsonEncode({
        'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
        'current_player': 'X',
        'winner': null,
        'winner_line': null,
        'game_over': false,
      }), 200);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();
    expect(callCount, 1);

    // Tap restart button
    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(callCount, 2); // Game restarted
  });

  testWidgets('GameWidget handles move error gracefully', (WidgetTester tester) async {
    int callCount = 0;
    final client = MockClient((request) async {
      callCount++;
      if (callCount == 1) {
        // First call: startGame succeeds
        return http.Response(jsonEncode({
          'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'X',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      } else {
        // Second call: makeMove fails
        return http.Response('Move Error', 500);
      }
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();

    // Tap a cell to make a move
    await tester.tap(find.byType(GestureDetector).first);
    await tester.pump();

    // Error message should be displayed
    expect(find.textContaining('Error'), findsOneWidget);
  });

  testWidgets('GameWidget ignores clicks when game is over', (WidgetTester tester) async {
    final client = MockClient((request) async {
      return http.Response(jsonEncode({
        'board': [['X', 'X', 'X'], ['O', 'O', ' '], [' ', ' ', ' ']],
        'current_player': 'X',
        'winner': 'X',
        'winner_line': [[0, 0], [0, 1], [0, 2]],
        'game_over': true,
      }), 200);
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();

    // Try to tap a cell - should be ignored
    await tester.tap(find.byType(GestureDetector).at(5));
    await tester.pump();

    // Winner message should still be displayed
    expect(find.text('Xの勝ちです！'), findsOneWidget);
  });

  testWidgets('GameWidget successfully makes a move and updates board', (WidgetTester tester) async {
    int callCount = 0;
    final client = MockClient((request) async {
      callCount++;
      if (callCount == 1) {
        // First call: startGame
        return http.Response(jsonEncode({
          'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'X',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      } else {
        // Second call: makeMove succeeds
        return http.Response(jsonEncode({
          'board': [['X', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'O',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      }
    });

    final apiService = ApiService(client: client);
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameWidget(
          startGameRequest: request,
          onStopGame: () {},
          apiService: apiService,
        ),
      ),
    ));

    await tester.pump();
    expect(callCount, 1);

    // Tap a cell to make a move
    await tester.tap(find.byType(GestureDetector).first);
    await tester.pump();

    expect(callCount, 2); // Move was made
  });
}
