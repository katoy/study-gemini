# BLE Pico Server (MicroPython)

このプロジェクトは、Pythonで実装されたオリジナル版の `ble_server` をRaspberry Pi Pico W上で動作するMicroPythonに移植したものです。
Raspberry Pi Pico WをBLE Centralデバイスとして機能させ、micro:bit (BLE Peripheral) との間でBluetooth Low Energy (BLE) 経由でTic-Tac-Toeゲームの通信を行います。

## 目次
- [BLE Pico Server (MicroPython)](#ble-pico-server-micropython)
  - [目次](#目次)
  - [機能](#機能)
  - [ディレクトリ構造](#ディレクトリ構造)
  - [セットアップとデプロイ](#セットアップとデプロイ)
    - [前提条件](#前提条件)
    - [Pico Wへのデプロイ](#pico-wへのデプロイ)
      - [Thonny IDEの使用](#thonny-ideの使用)
      - [ampyツールの使用 (CLI)](#ampyツールの使用-cli)
  - [micro:bit側の準備](#microbit側の準備)
  - [使い方](#使い方)
  - [技術的詳細と考慮事項](#技術的詳細と考慮事項)

## 機能

*   **BLE Central機能**: Raspberry Pi Pico WがBLE Centralとして動作し、Nordic UART Service (NUS) をアドバタイズするmicro:bitをスキャン、接続します。
*   **Tic-Tac-Toeゲームロジック**: 受信したコマンドに基づきTic-Tac-Toeゲームの状態を管理します。
*   **AI対戦**: シンプルなRandom AIエージェントを搭載し、プレイヤーと対戦します。
*   **通信プロトコル**: micro:bitとの間で定義された文字列ベースのプロトコルでゲーム情報を送受信します。

## ディレクトリ構造

```
ble_pico_server/
├── main.py              # Pico W側のBLE Centralロジック、ゲームアダプターとの連携
├── game_adapter.py      # MicroPython向けに調整されたゲームロジックとAIとのインターフェース
├── tic_tac_toe.py       # コアとなるTic-Tac-Toeゲームロジック
└── agents/
    ├── __init__.py      # Pythonパッケージの初期化ファイル (空で可)
    ├── base_agent.py    # AIエージェントの基底クラス
    └── random_agent.py  # ランダムな手を選択するAIエージェント
```

## セットアップとデプロイ

### 前提条件

*   **Raspberry Pi Pico W**: MicroPythonファームウェアが書き込まれている必要があります。
*   **micro:bit (v2推奨)**: BLE PeripheralとしてNUSサービスをアドバタイズするプログラムが書き込まれている必要があります。

### Pico Wへのデプロイ

以下のいずれかの方法で、`ble_pico_server`ディレクトリ内のすべてのファイルをPico Wにアップロードします。

#### Thonny IDEの使用

1.  Thonny IDEをインストールし、Raspberry Pi Pico Wに接続します。
2.  Thonnyの「ファイル」メニューから「MicroPythonデバイスへファイルをアップロード」を選択します。
3.  `ble_pico_server`ディレクトリ内のすべてのファイルとフォルダ（`main.py`, `game_adapter.py`, `tic_tac_toe.py`, `agents/`）をPico Wのファイルシステムにアップロードします。`agents`ディレクトリはPico W上でもディレクトリとして作成する必要があります。
4.  `main.py`がPico Wのリセット時に自動的に実行されるように設定されていることを確認してください。

#### ampyツールの使用 (CLI)

`ampy`は、MicroPythonデバイスのファイルシステムを操作するためのコマンドラインツールです。

1.  `ampy`をインストールします: `pip install adafruit-ampy`
2.  Pico Wのシリアルポートを特定します (例: `/dev/ttyACM0` on Linux/macOS, `COMx` on Windows)。
3.  以下のコマンドを実行してファイルをアップロードします:

    ```bash
    # ble_pico_server ディレクトリを作成
    ampy --port /dev/ttyACM0 mkdir ble_pico_server

    # ファイルをアップロード
    ampy --port /dev/ttyACM0 put ble_pico_server/main.py ble_pico_server/main.py
    ampy --port /dev/ttyACM0 put ble_pico_server/game_adapter.py ble_pico_server/game_adapter.py
    ampy --port /dev/ttyACM0 put ble_pico_server/tic_tac_toe.py ble_pico_server/tic_tac_toe.py

    # agents ディレクトリを作成
    ampy --port /dev/ttyACM0 mkdir ble_pico_server/agents

    # agents ディレクトリ内のファイルをアップロード
    ampy --port /dev/ttyACM0 put ble_pico_server/agents/__init__.py ble_pico_server/agents/__init__.py
    ampy --port /dev/ttyACM0 put ble_pico_server/agents/base_agent.py ble_pico_server/agents/base_agent.py
    ampy --port /dev/ttyACM0 put ble_pico_server/agents/random_agent.py ble_pico_server/agents/random_agent.py
    ```

## micro:bit側の準備

micro:bit側のプログラムは、Pico Wが期待する以下の文字列プロトコルで通信するように実装されている必要があります。

**Pico W (Central) から micro:bit (Peripheral) へのコマンド** (Pico Wがmicro:bitに書き込む)

*   `START:<HUMAN_SYMBOL>`: 新しいゲームを開始します。`HUMAN_SYMBOL`は 'X' (プレイヤー先攻) または 'O' (AI先攻)。例: "START:X"
*   `MOVE:<MOVE_INDEX>:<HUMAN_SYMBOL>:<BOARD_STATE>`: プレイヤーが手番を打ちます。`MOVE_INDEX`は0-8のマス番号、`HUMAN_SYMBOL`はプレイヤーの記号、`BOARD_STATE`は9文字の盤面文字列 (例: "X.O....")。例: "MOVE:4:X:X.O...."
*   `RESET`: ゲームをリセットします。

**micro:bit (Peripheral) から Pico W (Central) への応答** (Pico Wがmicro:bitからの通知を受信する)

*   `<BOARD_STATE>:<GAME_RESULT>:<WIN_LINE>`: ゲームの状態を示す応答です。
    *   `BOARD_STATE`: 更新された9文字の盤面文字列。
    *   `GAME_RESULT`: 'ONGOING' (続行中), 'WIN' (プレイヤー勝利), 'LOSE' (AI勝利), 'DRAW' (引き分け)。
    *   `WIN_LINE`: 勝利ラインのマス番号をコンマで区切った文字列 (例: "0,4,8")。勝敗が決まっていない場合は空文字列。

## 使い方

1.  上記の手順でPico Wにファイルをデプロイします。
2.  micro:bitに適切なBLE Peripheralプログラムを書き込みます。
3.  Pico Wとmicro:bitの両方をリセット（または電源を入れ直す）します。
4.  Pico Wは自動的にmicro:bitをスキャンし、接続を試みます。接続が確立されると、Pico WのLEDが点灯します。
5.  micro:bit側でゲームを開始するコマンドを送信します (例: ボタンを押して "START:X" を送信)。
6.  Pico Wはこれに応答し、ゲームが進行します。Pico Wのシリアルモニターでデバッグ出力とゲームの進行状況を確認できます。

## 技術的詳細と考慮事項

*   **BLE IRQと同期処理**: MicroPythonのBLEイベントはIRQ (割り込み) コンテキストで処理されます。`main.py`では、このIRQハンドラ内で`GameAdapter`のロジックを同期的に呼び出しています。IRQ内で長時間かかる処理は避けるべきですが、現在のTic-Tac-ToeロジックとRandom AIは比較的軽量であるため、問題は少ないと想定されます。より複雑なAIや処理が必要な場合は、`uasyncio`を使用した非同期処理への移行を検討する必要があります。
*   **メモリ使用量**: Raspberry Pi Pico Wのメモリは限られているため、特にAIエージェントの設計には注意が必要です。現在のRandom AIは非常に軽量です。将来的にMinimaxやQ-LearningのようなAIを導入する場合、メモリフットプリントと計算コストを慎重に評価し、必要に応じて最適化（例: Qテーブルの部分的なロードや事前計算）を行う必要があります。
*   **エラーハンドリング**: 通信エラーや無効なコマンドに対する基本的なエラーハンドリングは含まれていますが、堅牢性を高めるためにはさらなる強化が必要です。