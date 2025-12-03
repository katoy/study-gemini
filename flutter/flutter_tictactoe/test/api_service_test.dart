import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_tictactoe/api_service.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  group('ApiService', () {
    test('startGame returns BoardState on 200', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'X',
          'game_over': false
        }), 200);
      });

      final apiService = ApiService(client: client);
      final request = StartGameRequest(humanPlayerSymbol: 'X', playerXType: 'Human', playerOType: 'Random');
      final result = await apiService.startGame(request);

      expect(result, isA<BoardState>());
      expect(result.currentPlayer, 'X');
    });

    test('startGame throws Exception on non-200', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);
      final request = StartGameRequest(humanPlayerSymbol: 'X', playerXType: 'Human', playerOType: 'Random');

      expect(() => apiService.startGame(request), throwsException);
    });

    test('getGameStatus returns BoardState on 200', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'X',
          'game_over': false
        }), 200);
      });

      final apiService = ApiService(client: client);
      final result = await apiService.getGameStatus();

      expect(result, isA<BoardState>());
    });

    test('getGameStatus throws Exception on non-200', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);

      expect(() => apiService.getGameStatus(), throwsException);
    });

    test('makeMove returns BoardState on 200', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [['X', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
          'current_player': 'O',
          'game_over': false
        }), 200);
      });

      final apiService = ApiService(client: client);
      final result = await apiService.makeMove(MoveRequest(row: 0, col: 0));

      expect(result, isA<BoardState>());
      expect(result.board[0][0], 'X');
    });

    test('makeMove throws Exception on non-200', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);

      expect(() => apiService.makeMove(MoveRequest(row: 0, col: 0)), throwsException);
    });

    test('getAvailableAgents returns list on 200', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({'agents': ['Random', 'Minimax']}), 200);
      });

      final apiService = ApiService(client: client);
      final result = await apiService.getAvailableAgents();

      expect(result, ['Random', 'Minimax']);
    });

    test('getAvailableAgents throws Exception on non-200', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);

      expect(() => apiService.getAvailableAgents(), throwsException);
    });
  });
}
