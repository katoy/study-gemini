# 三目並べゲーム (Tic Tac Toe)

このプロジェクトは、Python で作成された GUI ベースの三目並べゲームです。プレイヤーは先手または後手を選択でき、対戦相手には複数の思考エージェント（ランダム・Minimax・データベース・完全・Q学習）から選択できます。

---

## 特徴

- GUIベースの直感的操作: Tkinter を使用したシンプルで使いやすいインターフェース。
- 多彩な思考エージェント:
  - ランダムエージェント: 空いているマスからランダムに手を選びます。
  - Minimaxエージェント: 完全な Minimax アルゴリズムに基づき、最適な手を選びます（非常に強い！）。
  - Databaseエージェント: 事前に Minimax で全局面を解析し、SQLite データベースに保存した手を参照します（超高速！）。
  - Perfectエージェント: 全局面に対する最適な手を事前に計算し、JSONファイルに保存したデータから参照します（超高速 + 完全なMinimaxの強さ！）。
  - QLearningエージェント: 強化学習（Q学習）を用いて学習するエージェント。学習回数を重ねるごとに強くなります。
- 先手・後手の選択: プレイヤーは先手（X）または後手（O）を選択できます。
- リスタート機能: ゲームを中断し、設定を保持したまま再開できます。
- 黒板風の盤面デザイン: 視覚的にわかりやすい盤面デザイン。
- 勝利ラインのハイライト: 勝敗が決まった際に、勝利ラインをハイライト表示します。
- 充実したテストコード: 信頼性の高い実装を保証するテストコード。
- Q学習エージェントの学習機能: Q学習エージェントを学習させることができます。

---

## 実行方法

1. Python のインストール
   - Python 3.10 以上を推奨します。

2. データベースと完全エージェント用データの作成（初回のみ）

   コマンド: python3 create_database.py

   このコマンドにより、以下のファイルが生成されます。
   - tictactoe.db: 全局面に対する最善手を含む SQLite データベース。
   - perfect_moves.json: 完全エージェントが使用する、すべての局面に対する最善手の JSON データ。

3. Q学習エージェントの学習（任意）

   コマンド: python3 train_q_learning.py --episodes 10000

   このコマンドにより、q_table.json が生成されます。
   - --episodes: 学習回数を指定します（デフォルトは 10000）。
   - --continue_training: 学習済みの q_table.json から学習を再開する場合に指定します。

   例：学習回数を 5000 回に設定し、学習を再開する場合

   コマンド: python3 train_q_learning.py --episodes 5000 --continue_training

4. ゲームの起動

   コマンド: python3 main.py

---

## ディレクトリ構成

.
├── agents/
│   ├── base_agent.py        # エージェント共通基底クラス
│   ├── random_agent.py      # ランダムエージェント
│   ├── minimax_agent.py     # Minimax エージェント
│   ├── database_agent.py    # SQLite データベースエージェント
│   ├── perfect_agent.py     # 完全エージェント
│   └── q_learning_agent.py  # Q学習エージェント
├── tests/                   # ユニットテスト一式
├── gui.py                   # GUI管理クラス
├── settings_ui.py           # 設定画面（先手/後手、エージェント選択）
├── game_info_ui.py          # プレイヤー情報の表示UI
├── board_drawer.py          # 盤面描画クラス
├── game_logic.py            # ゲームロジック（勝敗判定など）
├── create_database.py       # 全局面をMinimaxで解析しSQLiteとJSONに保存するスクリプト
├── main.py                  # アプリ起動スクリプト
├── train_q_learning.py      # Q学習エージェントを学習させるスクリプト
├── q_table.json             # Q学習エージェントが学習した結果を保存するファイル
├── perfect_moves.json       # 完全エージェントが使用する、すべての局面に対する最善手のJSONデータ
├── tictactoe.db             # 全局面に対する最善手を含む SQLite DB
└── README.md                # 本ドキュメント

---

## データベーススキーマ

Database エージェントが使用する SQLite データベース（tictactoe.db）のスキーマは以下の通りです。

CREATE TABLE tictactoe (
    board TEXT PRIMARY KEY,     -- 盤面（例: "XOXOX    "）
    best_move INTEGER,          -- 最善の手（0〜8, -1は終了局面）
    result TEXT                 -- 結果（"X", "O", "draw", "continue"）
);

各カラムの説明：

- board: 9 マスの盤面を左上から右下へ順に文字列化したもの（例: "XOX O X  "）。
- best_move: 勝敗が決していない場合の最適な手。0〜8 の数字でマスを表します。
- result: ゲームの結果。
    - X または O: 勝者。
    - draw: 引き分け。
    - continue: ゲーム継続中。
    - -1: 既に勝敗が決まっており、手を打つ必要がないことを示す。

---

## エージェント比較

| エージェント     | 思考内容           | 特徴                               |
| :--------------- | :----------------- | :--------------------------------- |
| ランダム         | 空きマスを選ぶ     | 弱いが高速                         |
| Minimax          | 先読みによる最適戦略 | 強いがやや低速                     |
| Database         | DBに保存された手   | 非常に高速 + 完全なMinimaxの強さ |
| Perfect          | JSONに保存された手 | 非常に高速 + 完全なMinimaxの強さ |
| QLearning        | 強化学習           | 学習回数に応じて強くなる           |

---

## テスト実行

コマンド: python3 -m unittest discover

または、個別のテストファイルを実行する場合：

コマンド: python3 tests/test_minimax_agent.py

---

## テストカバレッジ計測

コマンド: python3 -m coverage run -m unittest discover -s tests
コマンド: python3 -m coverage report

---

## 使用ライブラリ

- tkinter：GUI描画
- sqlite3：局面データ保存
- json: JSONファイル読み書き
- tqdm: プログレスバー表示
- argparse: コマンドライン引数解析
- numpy: 数値計算
- unittest: ユニットテスト

---

## 今後の課題・拡張案

- 対人戦モードの実装
- ネット対戦機能の追加
- 盤面サイズの可変対応（例：4×4、5×5）
- 勝率ログの保存と学習機能の強化

---

## ライセンス

MIT License

---

## 開発者メモ

- データベース（tictactoe.db）に登録された局面は、すべて create_database.py によって自動生成されています。
- best_move = -1 は、勝敗が決した局面（もう手を打つ必要がない）を意味します。
- 完全エージェント（Perfectエージェント）が使用する perfect_moves.json は、create_database.py によって自動生成されます。
- Q学習エージェントが使用する q_table.json は、train_q_learning.py によって自動生成されます。
