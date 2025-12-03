// TicTacToeClient.pde

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

// --- 状態管理 ---
String SERVER_URL = "http://127.0.0.1:8000";
String gameState = "SETTINGS"; // "SETTINGS", "GAME", "GAME_OVER"
JSONObject boardState;
String[] availableAgents = {"Human", "Random", "Minimax"}; // 初期値、後にサーバーから取得
String playerXType = "Human";
String playerOType = "Random";
String humanPlayerSymbol = "X";
String moveToMakeJson;

PFont japaneseFont; // 日本語フォント

// --- UI要素 ---
Button startButton;
DropDown playerXDropdown;
DropDown playerODropdown;
RadioButton radioX, radioO;

void setup() {
  size(400, 500);

  println("システムのフォントから直接 'Osaka-Mono' を読み込みます...");
  try {
    // ファイルからロードするのではなく、毎回直接フォントを生成する
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
  
  // --- UIの初期化 ---
  startButton = new Button("ゲーム開始", 150, 450, 100, 40);
  
  String[] agentOptions = availableAgents;
  playerXDropdown = new DropDown(50, 150, 150, 30, "Player X:", agentOptions);
  playerODropdown = new DropDown(50, 250, 150, 30, "Player O:", agentOptions);
  
  radioX = new RadioButton("あなたが X", 50, 350, true);
  radioO = new RadioButton("あなたが O", 200, 350, false);

  // 利用可能なエージェントリストをサーバーから非同期で取得
  thread("fetchAvailableAgents");
}

void draw() {
  background(240);
  
  if (gameState.equals("SETTINGS")) {
    drawSettingsScreen();
  } else if (gameState.equals("GAME") || gameState.equals("GAME_OVER")) {
    drawGameScreen();
  }
}

void mousePressed() {
  if (gameState.equals("SETTINGS")) {
    if (startButton.isClicked()) {
      // 選択された設定を取得
      playerXType = playerXDropdown.getSelected();
      playerOType = playerODropdown.getSelected();
      humanPlayerSymbol = radioX.isSelected ? "X" : "O";
      
      // ゲーム開始リクエストを送信
      thread("startGame");
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
  } else if (gameState.equals("GAME")) {
    // ボードクリック処理
    int col = floor(mouseX / (width / 3.0));
    int row = floor(mouseY / (width / 3.0));
    if (row < 3 && col < 3) {
      JSONObject moveData = new JSONObject();
      moveData.setInt("row", row);
      moveData.setInt("col", col);
      moveToMakeJson = moveData.toString();
      thread("makeMove");
    }
  } else if (gameState.equals("GAME_OVER")) {
      // 設定画面に戻るボタン (y=450 to 490)
      if (mouseX > 100 && mouseX < 300 && mouseY > height - 50 && mouseY < height - 10) {
          gameState = "SETTINGS";
      }
  }
}

// --- 画面描画 ---

void drawSettingsScreen() {
  textFont(japaneseFont); // フォント適用
  textSize(32);
  textAlign(CENTER, CENTER);
  fill(0);
  text("三目並べ設定", width/2, 50);
  
  startButton.draw();
  playerXDropdown.draw();
  playerODropdown.draw();
  radioX.draw();
  radioO.draw();

  // 展開されているドロップダウンメニューを最前面に描画
  if (playerXDropdown.expanded) {
    playerXDropdown.drawExpandedOptions();
  }
  if (playerODropdown.expanded) {
    playerODropdown.drawExpandedOptions();
  }
}

void drawGameScreen() {
    drawBoard(); // 1. ボードの線を描画
    if (boardState != null) {
        // ゲームオーバー状態なら、勝利ラインを先に描画
        if (boardState.getBoolean("game_over")) {
            drawWinnerLine(); // 2. 勝利ラインのハイライト
        }
        drawMarks(boardState.getJSONArray("board")); // 3. X/Oマークを描画

        // 4. メッセージを描画
        if (boardState.getBoolean("game_over")) {
            gameState = "GAME_OVER";
            drawGameOver();
        } else {
            textFont(japaneseFont);
            textSize(20);
            textAlign(CENTER, CENTER);
            fill(0);
            text("現在のプレイヤー: " + boardState.getString("current_player"), width / 2, width + 25);
        }
    }
}

void drawWinnerLine() {
  // winner_lineが存在し、nullではなく、要素が空でないことを確認
  if (boardState.hasKey("winner_line") && !boardState.isNull("winner_line")) {
    JSONArray winnerLine = boardState.getJSONArray("winner_line");
    if (winnerLine.size() > 0) {
      fill(255, 255, 0, 150); // 黄色、半透明
      noStroke();
      float cellSide = width / 3.0;

      for (int i = 0; i < winnerLine.size(); i++) {
        JSONArray cell = winnerLine.getJSONArray(i);
        int row = cell.getInt(0);
        int col = cell.getInt(1);
        float x = col * cellSide;
        float y = row * cellSide;
        rect(x, y, cellSide, cellSide);
      }
    }
  }
}

void drawBoard() {
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

void drawMarks(JSONArray board) {
    float cellSide = width / 3.0; // セルの1辺の長さ
    
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


void drawGameOver() {
    textFont(japaneseFont); // フォント適用
    textSize(36);
    fill(255, 0, 0);
    textAlign(CENTER, CENTER);
    String winner = boardState.getString("winner");
    if (winner != null && !winner.equals("null")) {
        text(winner + " の勝ち！", width / 2, width + 20); // y=420
    } else {
        text("引き分け！", width/2, width + 20); // y=420
    }
    
    // 設定画面に戻るボタン
    fill(0, 100, 200);
    rect(100, height - 50, 200, 40); // y=450, height=40
    fill(255);
    textFont(japaneseFont); // フォント適用
    textSize(20);
    text("設定に戻る", width/2, height - 30); // y=470
}


// --- サーバー通信 (非同期) ---

void fetchAvailableAgents() {
  try {
    String response = httpGet(SERVER_URL + "/agents");
    JSONObject json = parseJSONObject(response);
    JSONArray agentsArray = json.getJSONArray("agents");
    availableAgents = new String[agentsArray.size()];
    for (int i = 0; i < agentsArray.size(); i++) {
      availableAgents[i] = agentsArray.getString(i);
    }
    // ドロップダウンの選択肢を更新
    playerXDropdown.options = availableAgents;
    playerODropdown.options = availableAgents;
  } catch (Exception e) {
    println("エージェントリストの取得に失敗: " + e.getMessage());
  }
}

void startGame() {
  try {
    JSONObject requestBody = new JSONObject();
    requestBody.setString("player_x_type", playerXType);
    requestBody.setString("player_o_type", playerOType);
    requestBody.setString("human_player_symbol", humanPlayerSymbol);

    String response = httpPost(SERVER_URL + "/game/start", requestBody.toString());
    boardState = parseJSONObject(response);
    gameState = "GAME";
  } catch (Exception e) {
    println("ゲームの開始に失敗: " + e.getMessage());
  }
}

void makeMove() {
  String moveDataJson = moveToMakeJson;
  try {
    String response = httpPost(SERVER_URL + "/game/move", moveDataJson);
    boardState = parseJSONObject(response);
    
    // AIのターンもサーバーが処理してくれるので、ステータスを更新する
    // 人間の手に対するレスポンスに、AIが打った後の盤面が含まれている
    String responseAfterAI = httpGet(SERVER_URL + "/game/status");
    boardState = parseJSONObject(responseAfterAI);
    
  } catch (Exception e) {
    println("手の送信に失敗: " + e.getMessage());
  }
}


// --- HTTPヘルパー関数 ---
String httpGet(String url) throws Exception {
    HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
    conn.setRequestMethod("GET");
    conn.setRequestProperty("Accept-Charset", "UTF-8");
    return readResponse(conn);
}

String httpPost(String url, String jsonBody) throws Exception {
    HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
    conn.setRequestMethod("POST");
    conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
    conn.setDoOutput(true);
    try(OutputStream os = conn.getOutputStream()) {
        byte[] input = jsonBody.getBytes("UTF-8");
        os.write(input, 0, input.length);           
    }
    return readResponse(conn);
}

String readResponse(HttpURLConnection conn) throws Exception {
    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
    String inputLine;
    StringBuffer content = new StringBuffer();
    while ((inputLine = in.readLine()) != null) {
        content.append(inputLine);
    }
    in.close();
    conn.disconnect();
    return content.toString();
}


// --- UIコンポーネントクラス ---

class Button {
  String label;
  float x, y, w, h;
  Button(String label, float x, float y, float w, float h) {
    this.label = label;
    this.x = x; this.y = y; this.w = w; this.h = h;
  }
  
  void draw() {
    fill(200);
    rect(x, y, w, h);
    fill(0);
    textAlign(CENTER, CENTER);
    textFont(japaneseFont, 16); // フォント適用
    text(label, x + w/2, y + h/2);
  }
  
  boolean isClicked() {
    return mousePressed && mouseX > x && mouseX < x + w && mouseY > y && mouseY < y + h;
  }
}

class DropDown {
  float x, y, w, h;
  String label;
  String[] options;
  boolean expanded = false;
  String selected;
  
  DropDown(float x, float y, float w, float h, String label, String[] options) {
    this.x = x; this.y = y; this.w = w; this.h = h;
    this.label = label;
    this.options = options;
    if (options.length > 0) {
      this.selected = options[0];
    } else {
      this.selected = "";
    }
  }
  
  String getSelected() { return selected; }
  
  void handleMousePress() {
    if (mouseX > x && mouseX < x + w && mouseY > y && mouseY < y + h) {
      expanded = !expanded;
    } else if (expanded) {
      for (int i = 0; i < options.length; i++) {
        if (mouseX > x && mouseX < x + w && mouseY > y + h * (i + 1) && mouseY < y + h * (i + 2)) {
          selected = options[i];
          expanded = false;
          return;
        }
      }
      expanded = false;
    }
  }
  
  void draw() {
    // Label
    textFont(japaneseFont); // フォント適用
    fill(0);
    textAlign(LEFT, CENTER);
    textSize(16);
    text(label, x, y - 20);

    // Dropdown box
    fill(255);
    stroke(0);
    rect(x, y, w, h);
    fill(0);
    textAlign(LEFT, CENTER);
    text(selected, x + 10, y + h/2);

    // Arrow
    fill(0);
    triangle(x + w - 20, y + h/2 - 5, x + w - 10, y + h/2 - 5, x + w - 15, y + h/2 + 5);

    // 展開された選択肢の描画は drawExpandedOptions() に移動
  }

  void drawExpandedOptions() {
    if (expanded) {
      for (int i = 0; i < options.length; i++) {
        fill(255); // 不透明な白に変更
        stroke(0);
        rect(x, y + h * (i + 1), w, h);
        fill(0);
        textFont(japaneseFont); // フォント適用
        text(options[i], x + 10, y + h * (i + 1) + h/2);
      }
    }
  }
}

class RadioButton {
  String label;
  float x, y;
  boolean isSelected;
  
  RadioButton(String label, float x, float y, boolean isSelected) {
    this.label = label;
    this.x = x;
    this.y = y;
    this.isSelected = isSelected;
  }
  
  void draw() {
    stroke(0);
    fill(isSelected ? 0 : 255);
    ellipse(x, y, 20, 20);
    fill(0);
    textAlign(LEFT, CENTER);
    textFont(japaneseFont, 16); // フォント適用
    text(label, x + 15, y);
  }
  
  boolean isClicked() {
    return mousePressed && dist(mouseX, mouseY, x, y) < 10;
  }
}
