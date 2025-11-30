import 'package:flutter/material.dart';
import 'api_service.dart';
import 'models.dart';

import 'game_info_widget.dart';

class GameWidget extends StatefulWidget {
  final StartGameRequest startGameRequest;
  final VoidCallback onStopGame;
  final ApiService? apiService;

  const GameWidget({
    super.key,
    required this.startGameRequest,
    required this.onStopGame,
    this.apiService,
  });

  @override
  State<GameWidget> createState() => _GameWidgetState();
}

class _GameWidgetState extends State<GameWidget> {
  late final ApiService _apiService;
  BoardState? _boardState;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? ApiService();
    _startGame();
  }

  Future<void> _startGame() async {
    try {
      final boardState = await _apiService.startGame(widget.startGameRequest);
      setState(() {
        _boardState = boardState;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _makeMove(int row, int col) async {
    if (_boardState == null || _boardState!.gameOver || _isLoading) return;

    // Check if it's human's turn
    if (_boardState!.currentPlayer != widget.startGameRequest.humanPlayerSymbol) {
      return;
    }

    // Check if cell is empty
    if (_boardState!.board[row][col] != " ") return;

    setState(() {
      _isLoading = true;
    });

    try {
      final newState = await _apiService.makeMove(MoveRequest(row: row, col: col));
      setState(() {
        _boardState = newState;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          GameInfoWidget(startGameRequest: widget.startGameRequest),
          const SizedBox(height: 20),
          _buildBoard(),
          const SizedBox(height: 10),
          _buildStatusText(),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text('Error: $_errorMessage', style: const TextStyle(color: Colors.red)),
            ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                onPressed: _startGame, // Enabled to restart game
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                  backgroundColor: const Color(0xFF808080),
                  foregroundColor: Colors.black,
                  disabledBackgroundColor: const Color(0xFF808080),
                  disabledForegroundColor: Colors.black,
                  textStyle: const TextStyle(
                    fontSize: 16, 
                    fontWeight: FontWeight.bold,
                    fontFamily: 'Arial',
                  ),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(0)),
                ),
                child: const Text('ゲーム開始'),
              ),
              const SizedBox(width: 20),
              ElevatedButton(
                onPressed: widget.onStopGame,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                  backgroundColor: const Color(0xFF808080),
                  foregroundColor: Colors.black,
                  textStyle: const TextStyle(
                    fontSize: 12,
                    fontFamily: 'Arial',
                  ),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(0)),
                ),
                child: const Text('ゲーム中断'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusText() {
    if (_boardState == null) return const SizedBox.shrink();

    String text;
    Color color = Colors.yellow;

    if (_boardState!.gameOver) {
      if (_boardState!.winner == 'draw') {
        text = "引き分けです！";
      } else if (_boardState!.winner != null) {
        text = "${_boardState!.winner}の勝ちです！";
      } else {
        text = "ゲーム終了";
      }
    } else {
      // In gui.py, status is not shown during game, only result at the end.
      // But showing current player is helpful.
      // gui.py hides result_label during game.
      return const SizedBox(height: 30); // Placeholder to keep layout stable
    }

    return Text(
      text,
      style: TextStyle(
        fontSize: 20, 
        fontWeight: FontWeight.bold, 
        color: color,
        fontFamily: 'Arial',
      ),
    );
  }

  Widget _buildBoard() {
    if (_boardState == null) return const SizedBox(width: 300, height: 300);

    return Container(
      width: 300,
      height: 300,
      color: const Color(0xFF333333), // Background matches parent
      child: CustomPaint(
        painter: BoardPainter(
          boardState: _boardState!,
          winnerLine: _boardState!.winnerLine,
        ),
        child: GridView.builder(
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
          ),
          itemCount: 9,
          itemBuilder: (context, index) {
            int row = index ~/ 3;
            int col = index % 3;
            return GestureDetector(
              onTap: () => _makeMove(row, col),
              child: Container(
                color: Colors.transparent, // Important for hit testing
              ),
            );
          },
        ),
      ),
    );
  }
}

class BoardPainter extends CustomPainter {
  final BoardState boardState;
  final List<List<int>>? winnerLine;

  BoardPainter({required this.boardState, this.winnerLine});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..strokeWidth = 2;

    final cellWidth = size.width / 3;
    final cellHeight = size.height / 3;

    // Highlight winner cells (Yellow background)
    if (winnerLine != null) {
      final highlightPaint = Paint()
        ..color = Colors.yellow
        ..style = PaintingStyle.fill;

      for (var point in winnerLine!) {
        int row = point[0];
        int col = point[1];
        canvas.drawRect(
          Rect.fromLTWH(col * cellWidth, row * cellHeight, cellWidth, cellHeight),
          highlightPaint,
        );
      }
    }

    // Draw grid lines
    for (int i = 1; i < 3; i++) {
      canvas.drawLine(Offset(cellWidth * i, 0), Offset(cellWidth * i, size.height), paint);
      canvas.drawLine(Offset(0, cellHeight * i), Offset(size.width, cellHeight * i), paint);
    }

    // Draw X and O
    for (int row = 0; row < 3; row++) {
      for (int col = 0; col < 3; col++) {
        final symbol = boardState.board[row][col];
        if (symbol == 'X') {
          _drawX(canvas, row, col, cellWidth, cellHeight);
        } else if (symbol == 'O') {
          _drawO(canvas, row, col, cellWidth, cellHeight);
        }
      }
    }
  }

  void _drawX(Canvas canvas, int row, int col, double cellWidth, double cellHeight) {
    final paint = Paint()
      ..color = Colors.red
      ..strokeWidth = 5; // Matched width from python
    final padding = 20.0;
    final x1 = col * cellWidth + padding;
    final y1 = row * cellHeight + padding;
    final x2 = (col + 1) * cellWidth - padding;
    final y2 = (row + 1) * cellHeight - padding;

    canvas.drawLine(Offset(x1, y1), Offset(x2, y2), paint);
    canvas.drawLine(Offset(x2, y1), Offset(x1, y2), paint);
  }

  void _drawO(Canvas canvas, int row, int col, double cellWidth, double cellHeight) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 5 // Matched width from python
      ..style = PaintingStyle.stroke;
    final padding = 20.0;
    final centerX = col * cellWidth + cellWidth / 2;
    final centerY = row * cellHeight + cellHeight / 2;
    final radius = (cellWidth - padding * 2) / 2;

    canvas.drawCircle(Offset(centerX, centerY), radius, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
