package com.example;

import processing.core.PApplet;
import processing.core.PFont;
import processing.data.JSONArray; // Still needed for drawing board
import processing.data.JSONObject; // Still needed for drawing board

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class TicTacToeClient extends PApplet {

    // --- Services ---
    private HttpService httpService;
    private GameLogic gameLogic;

    PFont japaneseFont; // 日本語フォント

    // --- UI要素 ---
    Button startButton;
    Button resetButton; // This is not used but kept for now.
    Button stopButton;
    Button backToSettingsButton;
    Button rematchButton;
    DropDown playerXDropdown;
    DropDown playerODropdown;
    RadioButton radioX, radioO;

    public static void main(String[] args) {
        PApplet.main("com.example.TicTacToeClient");
    }

    @Override
    public void settings() {
        size(400, 500);
    }

    @Override
    public void setup() {
        println("システムのフォントから直接 'Osaka-Mono' を読み込みます...");
        try {
            japaneseFont = createFont("Osaka-Mono", 20);
            if (japaneseFont == null) {
                throw new Exception("createFontがnullを返しました。");
            }
            println("フォントの準備が完了しました。");
        } catch (Exception e) {
            println("警告: 'Osaka-Mono' の生成に失敗しました。");
            println("原因: " + e.getMessage());
            println("デフォルトフォント (Arial) を使用します。");
            japaneseFont = createFont("Arial", 20);
        }

        // --- Servicesの初期化 ---
        httpService = new HttpService();
        gameLogic = new GameLogic(httpService);

        // --- UIの初期化 ---
        startButton = new Button(this, "ゲーム開始", 150, 450, 100, 40, japaneseFont);
        stopButton = new Button(this, "ゲーム中断", width - 110, height - 45, 100, 40, japaneseFont);
        backToSettingsButton = new Button(this, "設定に戻る", width / 4 - 50, height - 50, 100, 40, japaneseFont);
        rematchButton = new Button(this, "再戦", width * 3 / 4 - 50, height - 50, 100, 40, japaneseFont);

        // 利用可能なエージェントリストをサーバーから非同期で取得
        // thread("fetchAvailableAgents"); の代わりに Runnable を使用
        new Thread(() -> {
            try {
                gameLogic.fetchAvailableAgents();
                // UIアップデートはイベントディスパッチスレッドで行う必要がある
                // Processingの場合、setup()内では直接UIを更新しても問題ないことが多い
                // ただし、draw()やmousePressed()以外でUIを直接変更するのは避けるべき
                // ここではavailableAgentsがGameLogicに移動したので、UI側のDropdownのoptionsを更新する必要がある
                String[] agents = gameLogic.getAvailableAgents();
                playerXDropdown = new DropDown(this, 50, 150, 150, 30, "Player X:", agents, japaneseFont);
                playerODropdown = new DropDown(this, 50, 250, 150, 30, "Player O:", agents, japaneseFont);
            } catch (Exception e) {
                println("エージェントリストの取得に失敗: " + e.getMessage());
            }
        }).start();


        radioX = new RadioButton(this, "あなたが X", 50, 350, true, japaneseFont);
        radioO = new RadioButton(this, "あなたが O", 200, 350, false, japaneseFont);
    }

    @Override
    public void draw() {
        background(240);

        // gameState は gameLogic から取得する
        String currentGameState = gameLogic.getGameState();

        if (currentGameState.equals("SETTINGS")) {
            drawSettingsScreen();
        } else if (currentGameState.equals("GAME") || currentGameState.equals("GAME_OVER")) {
            drawGameScreen();
        }
    }

    @Override
    public void mousePressed() {
        String currentGameState = gameLogic.getGameState();

        if (currentGameState.equals("SETTINGS")) {
            if (startButton.isClicked()) {
                // 選択された設定をgameLogicに設定
                gameLogic.setPlayerXType(playerXDropdown.getSelected());
                gameLogic.setPlayerOType(playerODropdown.getSelected());
                gameLogic.setHumanPlayerSymbol(radioX.isSelected ? "X" : "O");

                // ゲーム開始リクエストをgameLogicに依頼
                new Thread(() -> {
                    try {
                        gameLogic.startGame();
                    } catch (Exception e) {
                        println("ゲームの開始に失敗: " + e.getMessage());
                    }
                }).start();
            }
            playerXDropdown.handleMousePress();
            playerODropdown.handleMousePress();

            if (radioX.isClicked()) {
                radioX.isSelected = true;
                radioO.isSelected = false;
            }
            if (radioO.isClicked()) {
                radioO.isSelected = true;
                radioX.isSelected = false;
            }
        } else if (currentGameState.equals("GAME")) {
            if (stopButton.isClicked()) {
                gameLogic.setGameState("SETTINGS"); // GameLogicのメソッドで状態を変更
                return;
            }
            // ボードクリック処理
            int col = floor(mouseX / (float) (width / 3.0));
            int row = floor(mouseY / (float) (width / 3.0));
            if (row < 3 && col < 3) {
                // ProcessingのJSONObjectをorg.json.JSONObjectに変換
                org.json.JSONObject moveData = new org.json.JSONObject();
                moveData.put("row", row);
                moveData.put("col", col);
                gameLogic.setMoveToMakeJson(moveData); // GameLogicに移動情報を設定

                new Thread(() -> {
                    try {
                        gameLogic.makeMove();
                    } catch (Exception e) {
                        println("手の送信に失敗: " + e.getMessage());
                    }
                }).start();
            }
        } else if (currentGameState.equals("GAME_OVER")) {
            if (backToSettingsButton.isClicked()) {
                gameLogic.setGameState("SETTINGS");
            }
            if (rematchButton.isClicked()) {
                new Thread(() -> {
                    try {
                        gameLogic.startGame();
                    } catch (Exception e) {
                        println("ゲームの開始に失敗: " + e.getMessage());
                    }
                }).start();
            }
        }
    }

    // --- 画面描画 ---

    public void drawSettingsScreen() {
        textFont(japaneseFont); // フォント適用
        textSize(32);
        textAlign(CENTER, CENTER);
        fill(0);
        text("三目並べ設定", width / 2, 50);

        startButton.draw();
        // playerXDropdownとplayerODropdownはsetup()で初期化されるため、ここでは描画のみ
        if (playerXDropdown != null) playerXDropdown.draw();
        if (playerODropdown != null) playerODropdown.draw();
        radioX.draw();
        radioO.draw();

        // 展開されているドロップダウンメニューを最前面に描画
        if (playerXDropdown != null && playerXDropdown.expanded) {
            playerXDropdown.drawExpandedOptions();
        }
        if (playerODropdown != null && playerODropdown.expanded) {
            playerODropdown.drawExpandedOptions();
        }
    }

    public void drawGameScreen() {
        background(240);
        // gameLogic.isGameOver() を使用
        if (!gameLogic.isGameOver()) {
            stopButton.draw();
        }
        drawBoard(); // 1. ボードの線を描画
        // boardState は gameLogic から取得する
        org.json.JSONObject currentBoardState = gameLogic.getBoardState();
        if (currentBoardState != null) {
            // ゲームオーバー状態なら、勝利ラインを先に描画
            if (currentBoardState.has("game_over") && currentBoardState.getBoolean("game_over")) {
                drawWinnerLine(currentBoardState); // org.json.JSONObject を渡す
            }
            // org.json.JSONArray に変換して渡す
            drawMarks(new processing.data.JSONArray(currentBoardState.getJSONArray("board").toString())); // ProcessingのJSONArrayに戻す
            
            // 4. メッセージを描画
            if (currentBoardState.has("game_over") && currentBoardState.getBoolean("game_over")) {
                gameLogic.setGameState("GAME_OVER"); // GameLogicで状態を更新
                drawGameOver(currentBoardState); // org.json.JSONObject を渡す
            } else {
                textFont(japaneseFont);
                textSize(16); // 少しフォントを小さくする
                textAlign(CENTER, CENTER);
                fill(0);

                // エージェント表示
                String agentInfo = "X: " + gameLogic.getPlayerXType() + "  vs  O: " + gameLogic.getPlayerOType();
                text(agentInfo, width / 2, width + 20);

                // 現在のプレイヤー表示
                textSize(20);
                text("現在のプレイヤー: " + currentBoardState.getString("current_player"), width / 2, width + 45);
            }
        }
    }

    // drawWinnerLine と drawGameOver は org.json.JSONObject を受け取るように修正
    public void drawWinnerLine(org.json.JSONObject currentBoardState) {
        // winner_lineが存在し、nullではなく、要素が空でないことを確認
        if (currentBoardState.has("winner_line") && !currentBoardState.isNull("winner_line")) {
            org.json.JSONArray winnerLine = currentBoardState.getJSONArray("winner_line"); // org.json.JSONArray
            if (winnerLine.length() > 0) {
                fill(255, 255, 0, 150); // 黄色、半透明
                noStroke();
                float cellSide = width / 3.0f;

                for (int i = 0; i < winnerLine.length(); i++) { // .length()
                    org.json.JSONArray cell = winnerLine.getJSONArray(i);
                    int row = cell.getInt(0);
                    int col = cell.getInt(1);
                    float x = col * cellSide;
                    float y = row * cellSide;
                    rect(x, y, cellSide, cellSide);
                }
            }
        }
    }

    public void drawBoard() {
        stroke(0);
        strokeWeight(2);
        float boardSide = width; // ボードの1辺の長さをウィンドウ幅に合わせる (400px)

        // 縦線
        line(boardSide / 3, 0, boardSide / 3, boardSide);
        line(boardSide * 2 / 3, 0, boardSide * 2 / 3, boardSide);

        // 横線
        line(0, boardSide / 3, boardSide, boardSide / 3);
        line(0, boardSide * 2 / 3, boardSide, boardSide * 2 / 3);
    }

    // drawMarks は Processing の JSONArray を受け取るため、drawGameScreen で変換する
    public void drawMarks(processing.data.JSONArray board) {
        float cellSide = width / 3.0f; // セルの1辺の長さ

        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                String mark = board.getJSONArray(i).getString(j);
                float x = j * cellSide + cellSide / 2;
                float y = i * cellSide + cellSide / 2; // y座標もcellSide基準に

                if (mark.equals("X")) {
                    stroke(255, 0, 0);
                    strokeWeight(5);
                    line(x - 30, y - 30, x + 30, y + 30);
                    line(x + 30, y - 30, x - 30, y + 30);
                } else if (mark.equals("O")) {
                    stroke(0, 0, 255);
                    strokeWeight(5);
                    noFill();
                    ellipse(x, y, 60, 60);
                }
            }
        }
    }

    public void drawGameOver(org.json.JSONObject currentBoardState) {
        textFont(japaneseFont); // フォント適用
        textSize(36);
        fill(255, 0, 0);
        textAlign(CENTER, CENTER);
        String winner = gameLogic.getWinner(); // GameLogicからwinnerを取得
        if (winner != null && winner.equals("draw")) {
            text("引き分け！", width / 2, width + 20); // 引き分けの場合
        } else if (winner != null && !winner.equals("null")) {
            text(winner + " の勝ち！", width / 2, width + 20); // X か O の勝ち
        } else {
            text("引き分け！", width / 2, width + 20); // Fallback (念のため)
        }

        // ボタンの描画
        backToSettingsButton.draw();
        rematchButton.draw();
    }
}