import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';
  final http.Client client;

  ApiService({http.Client? client}) : client = client ?? http.Client();

  Future<BoardState> startGame(StartGameRequest request) async {
    final response = await client.post(
      Uri.parse('$baseUrl/game/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      return BoardState.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to start game: ${response.body}');
    }
  }

  Future<BoardState> getGameStatus() async {
    final response = await client.get(Uri.parse('$baseUrl/game/status'));

    if (response.statusCode == 200) {
      return BoardState.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to get game status: ${response.body}');
    }
  }

  Future<BoardState> makeMove(MoveRequest request) async {
    final response = await client.post(
      Uri.parse('$baseUrl/game/move'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      return BoardState.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to make move: ${response.body}');
    }
  }

  Future<List<String>> getAvailableAgents() async {
    final response = await client.get(Uri.parse('$baseUrl/agents'));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['agents']);
    } else {
      throw Exception('Failed to get available agents: ${response.body}');
    }
  }
}
