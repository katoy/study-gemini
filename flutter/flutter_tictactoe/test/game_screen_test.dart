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
}
