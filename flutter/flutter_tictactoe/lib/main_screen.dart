import 'package:flutter/material.dart';
import 'settings_screen.dart';
import 'game_screen.dart';
import 'models.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  bool _isPlaying = false;
  StartGameRequest? _startGameRequest;

  void _startGame(StartGameRequest request) {
    setState(() {
      _startGameRequest = request;
      _isPlaying = true;
    });
  }

  void _stopGame() {
    setState(() {
      _isPlaying = false;
      _startGameRequest = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('三目並べ'),
        backgroundColor: const Color(0xFF333333),
        foregroundColor: Colors.white,
      ),
      backgroundColor: const Color(0xFF333333),
      body: _isPlaying
          ? GameWidget(
              startGameRequest: _startGameRequest!,
              onStopGame: _stopGame,
            )
          : SettingsWidget(
              onStartGame: _startGame,
            ),
    );
  }
}
