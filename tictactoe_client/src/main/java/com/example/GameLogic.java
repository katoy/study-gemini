package com.example;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class GameLogic {

    private HttpService httpService;
    private String SERVER_URL = "http://127.0.0.1:8000";

    // Game State
    private String gameState = "SETTINGS"; // "SETTINGS", "GAME", "GAME_OVER"
    private JSONObject boardState;
    private String[] availableAgents = {"Human", "Random", "Minimax"};
    private String playerXType = "Human";
    private String playerOType = "Random";
    private String humanPlayerSymbol = "X";
    private String moveToMakeJson;

    public GameLogic(HttpService httpService) {
        this.httpService = httpService;
    }

    // Getters for game state
    public String getGameState() {
        return gameState;
    }

    public JSONObject getBoardState() {
        return boardState;
    }

    public String[] getAvailableAgents() {
        return availableAgents;
    }

    public String getPlayerXType() {
        return playerXType;
    }

    public String getPlayerOType() {
        return playerOType;
    }

    public String getHumanPlayerSymbol() {
        return humanPlayerSymbol;
    }

    public void setPlayerXType(String playerXType) {
        this.playerXType = playerXType;
    }

    public void setPlayerOType(String playerOType) {
        this.playerOType = playerOType;
    }

    public void setHumanPlayerSymbol(String humanPlayerSymbol) {
        this.humanPlayerSymbol = humanPlayerSymbol;
    }

    public void setMoveToMakeJson(JSONObject moveData) {
        this.moveToMakeJson = moveData.toString();
    }

    // Game logic and server communication methods
    public void fetchAvailableAgents() throws Exception {
        String response = httpService.httpGet(SERVER_URL + "/agents");
        JSONObject json = new JSONObject(response);
        JSONArray agentsArray = json.getJSONArray("agents");
        List<String> agentList = new ArrayList<>();
        for (int i = 0; i < agentsArray.length(); i++) {
            agentList.add(agentsArray.getString(i));
        }
        this.availableAgents = agentList.toArray(new String[0]);
    }

    public void startGame() throws Exception {
        JSONObject requestBody = new JSONObject();
        requestBody.put("player_x_type", playerXType);
        requestBody.put("player_o_type", playerOType);
        requestBody.put("human_player_symbol", humanPlayerSymbol);

        String response = httpService.httpPost(SERVER_URL + "/game/start", requestBody.toString());
        this.boardState = new JSONObject(response);
        this.gameState = "GAME";
    }

    public void makeMove() throws Exception {
        String response = httpService.httpPost(SERVER_URL + "/game/move", moveToMakeJson);
        this.boardState = new JSONObject(response);

        // AIのターンもサーバーが処理してくれるので、ステータスを更新する
        // 人間の手に対するレスポンスに、AIが打った後の盤面が含まれている
        String responseAfterAI = httpService.httpGet(SERVER_URL + "/game/status");
        this.boardState = new JSONObject(responseAfterAI);
    }

    // State transitions
    public void setGameState(String newState) {
        this.gameState = newState;
    }

    public boolean isGameOver() {
        return boardState != null && boardState.has("game_over") && boardState.getBoolean("game_over");
    }

    public String getWinner() {
        if (boardState != null && boardState.has("winner")) {
            return boardState.getString("winner");
        }
        return null;
    }
}
