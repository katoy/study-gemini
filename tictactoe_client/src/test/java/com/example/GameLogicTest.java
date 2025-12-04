package com.example;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class GameLogicTest {

    @Mock
    private HttpService httpService; // HttpServiceをモック化

    @InjectMocks
    private GameLogic gameLogic; // モックを注入するGameLogicインスタンス

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this); // モックを初期化
    }

    @Test
    void testFetchAvailableAgents() throws Exception {
        // モックの振る舞いを定義
        String mockResponse = "{\"agents\":[\"Human\",\"Minimax\",\"Random\"]}";
        when(httpService.httpGet(anyString())).thenReturn(mockResponse);

        // テスト対象のメソッドを呼び出す
        gameLogic.fetchAvailableAgents();

        // 結果を検証
        String[] expectedAgents = {"Human", "Minimax", "Random"};
        assertArrayEquals(expectedAgents, gameLogic.getAvailableAgents(), "Available agents should be fetched correctly");
        verify(httpService, times(1)).httpGet("http://127.0.0.1:8000/agents"); // httpGetが呼ばれたことを確認
    }

    @Test
    void testStartGame() throws Exception {
        // モックの振る舞いを定義
        String mockStartGameResponse = "{\"board\":[[\" \",\" \",\" \"],[\" \",\" \",\" \"],[\" \",\" \",\" \"]],\"current_player\":\"X\",\"game_over\":false}";
        when(httpService.httpPost(eq("http://127.0.0.1:8000/game/start"), anyString())).thenReturn(mockStartGameResponse);

        // GameLogicの状態を設定
        gameLogic.setPlayerXType("Human");
        gameLogic.setPlayerOType("Random");
        gameLogic.setHumanPlayerSymbol("X");

        // テスト対象のメソッドを呼び出す
        gameLogic.startGame();

        // 結果を検証
        assertEquals("GAME", gameLogic.getGameState(), "Game state should be GAME");
        assertNotNull(gameLogic.getBoardState(), "Board state should not be null");
        assertEquals("X", gameLogic.getBoardState().getString("current_player"), "Current player should be X");
        verify(httpService, times(1)).httpPost(eq("http://127.0.0.1:8000/game/start"), anyString());
    }

    @Test
    void testMakeMove() throws Exception {
        // ゲーム開始状態をシミュレート
        String mockStartGameResponse = "{\"board\":[[\" \",\" \",\" \"],[\" \",\" \",\" \"],[\" \",\" \",\" \"]],\"current_player\":\"X\",\"game_over\":false}";
        when(httpService.httpPost(eq("http://127.0.0.1:8000/game/start"), anyString())).thenReturn(mockStartGameResponse);
        gameLogic.setPlayerXType("Human");
        gameLogic.setPlayerOType("Random");
        gameLogic.setHumanPlayerSymbol("X");
        gameLogic.startGame(); // boardStateが設定される

        // モックの振る舞いを定義
        String mockMoveResponse = "{\"board\":[[\"X\",\" \",\" \"],[\" \",\" \",\" \"],[\" \",\" \",\" \"]],\"current_player\":\"O\",\"game_over\":false}";
        String mockStatusResponse = "{\"board\":[[\"X\",\" \",\" \"],[\" \",\" \",\" \"],[\" \",\" \",\" \"]],\"current_player\":\"O\",\"game_over\":false}"; // AIの後の状態も同じと仮定
        when(httpService.httpPost(eq("http://127.0.0.1:8000/game/move"), anyString())).thenReturn(mockMoveResponse);
        when(httpService.httpGet(eq("http://127.0.0.1:8000/game/status"))).thenReturn(mockStatusResponse);

        // テスト対象のメソッドを呼び出す
        JSONObject moveData = new JSONObject();
        moveData.put("row", 0);
        moveData.put("col", 0);
        gameLogic.setMoveToMakeJson(moveData);
        gameLogic.makeMove();

        // 結果を検証
        assertNotNull(gameLogic.getBoardState(), "Board state should not be null after move");
        assertEquals("O", gameLogic.getBoardState().getString("current_player"), "Current player should change to O");
        assertEquals("X", gameLogic.getBoardState().getJSONArray("board").getJSONArray(0).getString(0), "Move should be reflected on board");
        verify(httpService, times(1)).httpPost(eq("http://127.0.0.1:8000/game/move"), anyString());
        verify(httpService, times(1)).httpGet("http://127.0.0.1:8000/game/status");
    }

    @Test
    void testIsGameOver() throws Exception {
        // ゲームオーバー状態をシミュレートするBoardState
        String gameOverResponse = "{\"board\":[[\"X\",\"X\",\"X\"],[\" \",\" \",\" \"],[\" \",\" \",\" \"]],\"current_player\":\"O\",\"game_over\":true,\"winner\":\"X\"}";
        when(httpService.httpPost(eq("http://127.0.0.1:8000/game/start"), anyString())).thenReturn(gameOverResponse);

        gameLogic.setPlayerXType("Human");
        gameLogic.setPlayerOType("Random");
        gameLogic.setHumanPlayerSymbol("X");
        gameLogic.startGame(); // boardStateが設定される

        assertTrue(gameLogic.isGameOver(), "Game should be over");
        assertEquals("X", gameLogic.getWinner(), "Winner should be X");
    }

    @Test
    void testGetWinnerDraw() throws Exception {
        // 引き分け状態をシミュレートするBoardState
        String drawResponse = "{\"board\":[[\"X\",\"O\",\"X\"],[\"O\",\"X\",\"O\"],[\"O\",\"X\",\"O\"]],\"current_player\":\"X\",\"game_over\":true,\"winner\":\"draw\"}";
        when(httpService.httpPost(eq("http://127.0.0.1:8000/game/start"), anyString())).thenReturn(drawResponse);

        gameLogic.setPlayerXType("Human");
        gameLogic.setPlayerOType("Random");
        gameLogic.setHumanPlayerSymbol("X");
        gameLogic.startGame();

        assertTrue(gameLogic.isGameOver(), "Game should be over");
        assertEquals("draw", gameLogic.getWinner(), "Winner should be 'draw'");
    }
}
