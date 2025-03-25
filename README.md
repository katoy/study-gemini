# 三目並べゲーム (Tic Tac Toe)

このプロジェクトは、Python で作成された GUI ベースの三目並べゲームです。プレイヤーは先手または後手を選択でき、対戦相手には複数の思考エージェント（ランダム・Minimax・データベース学習済み）から選択できます。

---

## 特徴

- 🎮 **GUIベースの直感的操作:** Tkinter を使用したシンプルで使いやすいインターフェース。
- 🧠 **思考エージェントの選択:**
  - **ランダムエージェント:** 空いているマスからランダムに選びます。
  - **Minimaxエージェント:** 完全な Minimax アルゴリズムに基づき、最適な手を選びます（強い！）。
  - **Databaseエージェント:** 事前に Minimax で全局面を解析し、SQLite データベースに保存した手を参照します（超高速！）。
- 🔁 **先手・後手の選択可能**
- 🔄 **リスタート機能 & 設定保持**
- 🖌️ **黒板風の盤面デザイン & 勝利ラインのハイライト**
- ✅ **テストコードが充実しており、信頼性の高い実装**

---

## 実行方法

1. **Python をインストール**
    - Python 3.10 以上推奨

2. **データベースの作成（初回のみ）**

    ```bash
    python3 create_database.py
    ```

    これにより、`tictactoe.db`（全局面に対する最善手を含む SQLite DB）が生成されます。

3. **ゲームの起動**

    ```bash
    python3 main.py
    ```

---

## ディレクトリ構成

```
.
├── agents/
│   ├── base_agent.py        # エージェント共通基底クラス
│   ├── random_agent.py      # ランダムエージェント
│   ├── minimax_agent.py     # Minimax エージェント
│   └── database_agent.py    # SQLite データベースエージェント
├── tests/                   # ユニットテスト一式（ファイルはルートに配置されている場合もあり）
├── gui.py                   # GUI管理クラス
├── settings_ui.py           # 設定画面（先手/後手、エージェント選択）
├── game_info_ui.py          # プレイヤー情報の表示UI
├── board_drawer.py          # 盤面描画クラス
├── game_logic.py            # ゲームロジック（勝敗判定など）
├── create_database.py       # 全局面をMinimaxで解析しSQLiteに保存するスクリプト
├── main.py                  # アプリ起動スクリプト
└── README.md                # 本ドキュメント
```

---

## データベーススキーマ

Database エージェントが使用する SQLite データベース（`tictactoe.db`）のスキーマは以下の通りです：

```sql
CREATE TABLE tictactoe (
    board TEXT PRIMARY KEY,     -- 盤面を "XOXOX    " のような文字列で表現
    best_move INTEGER,          -- 次に打つべき最善の手（0〜8, -1は終了局面）
    result TEXT                 -- "X", "O", "draw", または "continue"
);
```

- `board`: 9マスの盤面を左上から右下へ順に文字列化（例: "XOX O X  ")
- `best_move`: 勝敗が決していない場合の最適な手（0〜8）
- `result`: 結果
  - `X` または `O`: 勝者
  - `draw`: 引き分け
  - `continue`: まだ継続中の局面
  - `-1`: 既に勝敗が決まっており、手を打つ必要がない

---

## エージェント比較

| エージェント     | 思考内容           | 特徴                               |
|------------------|--------------------|------------------------------------|
| ランダム         | 空きマスを選ぶ     | 弱いが早い                         |
| Minimax          | 先読み最適戦略     | 強いがやや遅い                     |
| Database         | DBに保存された手   | 非常に高速 + 完全なMinimaxの強さ |

---

## テスト実行（任意）

```bash
python3 -m unittest discover
```

または個別ファイルを指定：

```bash
python3 tests/test_minimax_agent.py
```

## テストカバレッジ(任意)

```
python3 -m coverage run -m unittest discover -s tests
python3 -m coverage report
```
---

## 使用ライブラリ

- `tkinter`：GUI描画
- `sqlite3`：局面データ保存
- `unittest`：テスト

---

## 今後の課題・拡張案

- [ ] 対人戦モード
- [ ] ネット対戦
- [ ] 盤面サイズの可変対応（例：4×4、5×5）
- [ ] 勝率ログ保存・学習

---

## ライセンス

MIT License

---

## 開発者メモ

- データベースに登録された局面は、すべて `create_database.py` にて自動生成されています。
- `best_move = -1` は勝敗が決した局面（もう手を打つ必要なし）を意味します。

