import 'package:flutter/material.dart';
import 'models.dart';

class SettingsWidget extends StatefulWidget {
  final Function(StartGameRequest) onStartGame;

  const SettingsWidget({super.key, required this.onStartGame});

  @override
  State<SettingsWidget> createState() => _SettingsWidgetState();
}

class _SettingsWidgetState extends State<SettingsWidget> {
  String _selectedHumanSymbol = 'X';
  String _selectedAgentType = 'Random';

  final List<String> _agentTypes = [
    'Random',
    'Minimax',
    'Database',
    'Perfect',
    'QLearning',
  ];

  void _startGame() {
    String playerXType;
    String playerOType;

    if (_selectedHumanSymbol == 'X') {
      playerXType = 'Human';
      playerOType = _selectedAgentType;
    } else {
      playerXType = _selectedAgentType;
      playerOType = 'Human';
    }

    final request = StartGameRequest(
      humanPlayerSymbol: _selectedHumanSymbol,
      playerXType: playerXType,
      playerOType: playerOType,
    );

    widget.onStartGame(request);
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        padding: const EdgeInsets.all(20.0),
        constraints: const BoxConstraints(maxWidth: 400),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildLabelFrame(
              title: 'プレイヤーの順番',
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildRadioBtn('あなた（先手）', 'X', _selectedHumanSymbol, (val) {
                    setState(() => _selectedHumanSymbol = val!);
                  }),
                  const SizedBox(width: 20),
                  _buildRadioBtn('マシン（先手）', 'O', _selectedHumanSymbol, (val) {
                    setState(() => _selectedHumanSymbol = val!);
                  }),
                ],
              ),
            ),
            const SizedBox(height: 20),
            _buildLabelFrame(
              title: '対戦エージェント',
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _selectedAgentType,
                    isExpanded: true,
                    items: _agentTypes.map((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                    onChanged: (newValue) {
                      setState(() {
                        _selectedAgentType = newValue!;
                      });
                    },
                  ),
                ),
              ),
            ),
            const SizedBox(height: 40),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _startGame,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                    backgroundColor: const Color(0xFF808080),
                    foregroundColor: Colors.black,
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
                  onPressed: null, // Disabled in settings view
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                    backgroundColor: const Color(0xFF808080),
                    foregroundColor: Colors.black,
                    disabledBackgroundColor: const Color(0xFF808080),
                    disabledForegroundColor: Colors.black,
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
      ),
    );
  }

  Widget _buildLabelFrame({required String title, required Widget child}) {
    return InputDecorator(
      decoration: InputDecoration(
        labelText: title,
        labelStyle: const TextStyle(
          color: Color(0xFFEEEEEE),
          fontSize: 14, // Matched python font size
          fontWeight: FontWeight.bold,
          fontFamily: 'Arial',
        ),
        enabledBorder: OutlineInputBorder(
          borderSide: const BorderSide(color: Colors.grey),
          borderRadius: BorderRadius.circular(2), // Less rounded
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      ),
      child: child,
    );
  }

  Widget _buildRadioBtn(
      String label, String value, String groupValue, Function(String?) onChanged) {
    return Row(
      children: [
        Radio<String>(
          value: value,
          groupValue: groupValue,
          onChanged: onChanged,
          fillColor: WidgetStateProperty.all(const Color(0xFFEEEEEE)),
          activeColor: const Color(0xFF555555), // Matched selectcolor
        ),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFFEEEEEE), 
            fontWeight: FontWeight.bold,
            fontSize: 12,
            fontFamily: 'Arial',
          ),
        ),
      ],
    );
  }
}
