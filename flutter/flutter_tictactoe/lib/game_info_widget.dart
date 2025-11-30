import 'package:flutter/material.dart';
import 'models.dart';

class GameInfoWidget extends StatelessWidget {
  final StartGameRequest startGameRequest;

  const GameInfoWidget({super.key, required this.startGameRequest});

  @override
  Widget build(BuildContext context) {
    final isHumanFirst = startGameRequest.humanPlayerSymbol == 'X';
    final playerText = isHumanFirst ? "先手: あなた" : "後手: あなた";
    
    final agentName = isHumanFirst 
        ? startGameRequest.playerOType 
        : startGameRequest.playerXType;
    final agentText = "エージェント: $agentName";

    const textStyle = TextStyle(
      color: Color(0xFFEEEEEE),
      fontSize: 12,
      fontWeight: FontWeight.bold,
      fontFamily: 'Arial',
    );

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      color: const Color(0xFF333333),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(playerText, style: textStyle),
          const SizedBox(width: 20),
          Text(agentText, style: textStyle),
        ],
      ),
    );
  }
}
