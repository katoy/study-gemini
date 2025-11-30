import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_tictactoe/api_service.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  group('ApiService', () {
    test('startGame returns BoardState on success', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [['', '', ''], ['', '', ''], ['', '', '']],
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

      final result = await apiService.startGame(request);

      expect(result, isA<BoardState>());
      expect(result.currentPlayer, 'X');
    });

    test('startGame throws exception on failure', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);
      final request = StartGameRequest(
        humanPlayerSymbol: 'X',
        playerXType: 'Human',
        playerOType: 'Random',
      );

      expect(apiService.startGame(request), throwsException);
    });

    test('makeMove returns BoardState on success', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [['X', '', ''], ['', '', ''], ['', '', '']],
          'current_player': 'O',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      });

      final apiService = ApiService(client: client);
      final request = MoveRequest(row: 0, col: 0);

      final result = await apiService.makeMove(request);

      expect(result.board[0][0], 'X');
      expect(result.currentPlayer, 'O');
    });

    test('makeMove throws exception on failure', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);
      final request = MoveRequest(row: 0, col: 0);

      expect(apiService.makeMove(request), throwsException);
    });

    test('getGameStatus returns BoardState on success', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({
          'board': [['X', 'O', ''], ['', '', ''], ['', '', '']],
          'current_player': 'X',
          'winner': null,
          'winner_line': null,
          'game_over': false,
        }), 200);
      });

      final apiService = ApiService(client: client);
      final result = await apiService.getGameStatus();

      expect(result.board[0][0], 'X');
      expect(result.board[0][1], 'O');
      expect(result.currentPlayer, 'X');
    });

    test('getGameStatus throws exception on failure', () async {
      final client = MockClient((request) async {
        return http.Response('Error', 500);
      });

      final apiService = ApiService(client: client);

      expect(apiService.getGameStatus(), throwsException);
    });
  });
}
