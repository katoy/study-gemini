import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_tictactoe/settings_screen.dart';
import 'package:flutter_tictactoe/models.dart';

void main() {
  testWidgets('SettingsWidget displays correct UI elements', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SettingsWidget(onStartGame: (request) {}),
      ),
    ));

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
        body: SettingsWidget(onStartGame: (req) {
          request = req;
        }),
      ),
    ));

    await tester.tap(find.text('ゲーム開始'));
    await tester.pump();

    expect(request, isNotNull);
    expect(request!.humanPlayerSymbol, 'X');
    expect(request!.playerXType, 'Human');
    expect(request!.playerOType, 'Random');
  });
}
