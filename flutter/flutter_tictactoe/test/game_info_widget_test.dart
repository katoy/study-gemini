import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_tictactoe/game_info_widget.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  testWidgets('GameInfoWidget displays correct info for Human vs Random', (WidgetTester tester) async {
    final request = StartGameRequest(
      humanPlayerSymbol: 'X',
      playerXType: 'Human',
      playerOType: 'Random',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameInfoWidget(startGameRequest: request),
      ),
    ));

    expect(find.text('先手: あなた'), findsOneWidget);
    expect(find.text('エージェント: Random'), findsOneWidget);
  });

  testWidgets('GameInfoWidget displays correct info for Random vs Human', (WidgetTester tester) async {
    final request = StartGameRequest(
      humanPlayerSymbol: 'O',
      playerXType: 'Random',
      playerOType: 'Human',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: GameInfoWidget(startGameRequest: request),
      ),
    ));

    expect(find.text('後手: あなた'), findsOneWidget);
    expect(find.text('エージェント: Random'), findsOneWidget);
  });
}
