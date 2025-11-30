class StartGameRequest {
  final String humanPlayerSymbol;
  final String playerXType;
  final String playerOType;

  StartGameRequest({
    required this.humanPlayerSymbol,
    required this.playerXType,
    required this.playerOType,
  });

  Map<String, dynamic> toJson() {
    return {
      'human_player_symbol': humanPlayerSymbol,
      'player_x_type': playerXType,
      'player_o_type': playerOType,
    };
  }
}

class BoardState {
  final List<List<String>> board;
  final String currentPlayer;
  final String? winner;
  final List<List<int>>? winnerLine;
  final bool gameOver;

  BoardState({
    required this.board,
    required this.currentPlayer,
    this.winner,
    this.winnerLine,
    required this.gameOver,
  });

  factory BoardState.fromJson(Map<String, dynamic> json) {
    var boardList = (json['board'] as List)
        .map((row) => (row as List).map((e) => e as String).toList())
        .toList();

    List<List<int>>? winnerLineList;
    if (json['winner_line'] != null) {
      winnerLineList = (json['winner_line'] as List)
          .map((point) => (point as List).map((e) => e as int).toList())
          .toList();
    }

    return BoardState(
      board: boardList,
      currentPlayer: json['current_player'],
      winner: json['winner'],
      winnerLine: winnerLineList,
      gameOver: json['game_over'],
    );
  }
}

class MoveRequest {
  final int row;
  final int col;

  MoveRequest({required this.row, required this.col});

  Map<String, dynamic> toJson() {
    return {
      'row': row,
      'col': col,
    };
  }
}
