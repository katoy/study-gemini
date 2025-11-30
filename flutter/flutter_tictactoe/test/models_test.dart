import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  group('StartGameRequest', () {
    test('toJson returns correct map', () {
      final request = StartGameRequest(
        humanPlayerSymbol: 'X',
        playerXType: 'Human',
        playerOType: 'Random',
      );

      final json = request.toJson();

      expect(json, {
        'human_player_symbol': 'X',
        'player_x_type': 'Human',
        'player_o_type': 'Random',
      });
    });
  });

  group('BoardState', () {
    test('fromJson creates correct object', () {
      final json = {
        'board': [
          ['X', '', ''],
          ['', 'O', ''],
          ['', '', '']
        ],
        'current_player': 'X',
        'winner': null,
        'winner_line': null,
        'game_over': false,
      };

      final boardState = BoardState.fromJson(json);

      expect(boardState.board, [
        ['X', '', ''],
        ['', 'O', ''],
        ['', '', '']
      ]);
      expect(boardState.currentPlayer, 'X');
      expect(boardState.winner, null);
      expect(boardState.winnerLine, null);
      expect(boardState.gameOver, false);
    });

    test('fromJson handles winner and winnerLine', () {
      final json = {
        'board': [
          ['X', 'X', 'X'],
          ['O', 'O', ''],
          ['', '', '']
        ],
        'current_player': 'O',
        'winner': 'X',
        'winner_line': [
          [0, 0],
          [0, 1],
          [0, 2]
        ],
        'game_over': true,
      };

      final boardState = BoardState.fromJson(json);

      expect(boardState.winner, 'X');
      expect(boardState.winnerLine, [
        [0, 0],
        [0, 1],
        [0, 2]
      ]);
      expect(boardState.gameOver, true);
    });
  });

  group('MoveRequest', () {
    test('toJson returns correct map', () {
      final request = MoveRequest(row: 1, col: 2);
      final json = request.toJson();
      expect(json, {'row': 1, 'col': 2});
    });
  });
}
