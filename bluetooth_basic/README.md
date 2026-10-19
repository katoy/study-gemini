# Raspberry Pi Zero と ESP32 を使用した Bluetooth SPP 通信の基本例

このプロジェクトは、Raspberry Pi Zero (クライアント) と ESP32 (サーバー) の間で Bluetooth Serial Port Profile (SPP) 通信を行うための基本的な例を提供します。ESP32 から Raspberry Pi Zero へリクエストを送信し、Raspberry Pi Zero から応答を受け取ることを目的としています。複数の ESP32 デバイスが Raspberry Pi Zero に接続できる設計になっています。

**注意:** このプロジェクトでは Bluetooth Low Energy (BLE) ではなく、Classic Bluetooth (レガシー Bluetooth) の SPP を使用します。

## プロジェクト構成

```
bluetooth_basic/
├── esp32_arduino_sketch/
│   └── esp32_bluetooth_spp.ino   # ESP32 用の Bluetooth SPP サーバー スケッチ
└── rpi_zero_python_client/
    └── bluetooth_client_manager.py # Raspberry Pi Zero 用の Bluetooth SPP クライアント スクリプト
```

## 各コンポーネントの説明

### 1. ESP32 Arduino スケッチ (`esp32_arduino_sketch/esp32_bluetooth_spp.ino`)

*   **機能:** Bluetooth SPP サーバーとして動作し, "ESP32_SPP_SERVER_01" という名前でサービスを広告します。
*   **通信:** クライアント (Raspberry Pi Zero) からの接続を受け入れ, データを受信します。
    *   受信したメッセージが `request_time` で始まる場合, 現在の稼働時間 (ミリ秒) を応答します。
    *   それ以外のメッセージの場合, 受信したメッセージをエコーバックします。
*   **デバイス名:** 必要に応じて `deviceName` を変更し, 複数の ESP32 を区別できます。

### 2. Raspberry Pi Zero Python クライアント (`rpi_zero_python_client/bluetooth_client_manager.py`)

*   **機能:** PyBluez ライブラリを使用して, 指定された MAC アドレスを持つ複数の ESP32 SPP サーバーにクライアントとして接続します。
*   **通信:** 各 ESP32 に対して個別のスレッドを立ち上げ, 定期的に `request_time_X` のようなメッセージを送信し, ESP32 からの応答を受信して表示します。
*   **設定:** 接続したい ESP32 の MAC アドレスを `ESP32_DEVICES_TO_CONNECT` リストに設定する必要があります。

## セットアップ手順

### 1. ESP32 の準備

1.  **Arduino IDE のインストール:** 
    *   Arduino IDE をインストールし, ESP32 ボードのサポートを追加します。
        *   `ファイル` -> `環境設定` -> `追加のボードマネージャのURL` に `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` を追加します。
        *   `ツール` -> `ボード` -> `ボードマネージャ` で `esp32` を検索し, インストールします。
    *   `ツール` -> `ボード` -> `ESP32 Arduino` から, 使用している ESP32 ボードを選択します (例: `ESP32 Dev Module`)。
2.  **スケッチの書き込み:** 
    *   `esp32_arduino_sketch/esp32_bluetooth_spp.ino` ファイルを Arduino IDE で開きます。
    *   ESP32 ボードを USB ケーブルでコンピューターに接続し, `ツール` -> `ポート` から適切なシリアルポートを選択します。
    *   スケッチをコンパイルし, ESP32 に書き込みます。
3.  **MAC アドレスの確認:** 
    *   書き込み後, `ツール` -> `シリアルモニター` を開き, ボーレートを `115200` に設定します。
    *   ESP32 が起動すると, シリアルモニターにデバイス名と MAC アドレスが表示されます。この MAC アドレスを控えてください。

### 2. Raspberry Pi Zero の準備

1.  **Raspberry Pi OS のインストール:** 
    *   Raspberry Pi Imager ツールを使って, microSD カードに Raspberry Pi OS Lite (64-bit) または Raspberry Pi OS with desktop (64-bit) を書き込みます。
    *   **重要:** Imager で OS を書き込む際に, SSH を有効にし, Wi-Fi を設定し, ユーザー名とパスワードを設定しておくことを強く推奨します。これにより, ヘッドレス (モニターなし) でセットアップを進めることができます。
2.  **Raspberry Pi Zero へのアクセス:** 
    *   microSD カードを Raspberry Pi Zero に挿入し, 電源を入れます。
    *   SSH が有効になっていれば, 別のコンピューターから `ssh <ユーザー名>@raspberrypi.local` で接続できます。
3.  **システムの更新:** 
    *   SSH 接続後, 以下のコマンドでシステムを最新の状態に更新します。
        ```bash
        sudo apt update
        sudo apt upgrade -y
        ```
4.  **必要なパッケージのインストール:** 
    *   Bluetooth 関連のパッケージと Python 開発ファイルをインストールします。
        ```bash
        sudo apt install bluetooth bluez libbluetooth-dev python3-dev -y
        ```
5.  **PyBluez のインストール:** 
    *   以下のコマンドで PyBluez をインストールします。
        ```bash
        pip install PyBluez
        # pip コマンドがない場合: sudo apt install python3-pip -y
        # pip3 を使用する場合: pip3 install PyBluez
        ```
6.  **Bluetooth サービスの確認:** 
    *   Bluetooth サービスが起動していることを確認します。
        ```bash
        sudo systemctl status bluetooth
        ```
    *   もし起動していなければ, `sudo systemctl start bluetooth` で起動し, `sudo systemctl enable bluetooth` で自動起動を設定します。

## 実行方法

1.  **ESP32 の起動:** 
    *   ESP32 が `esp32_arduino_spp.ino` スケッチで動作していることを確認します。

2.  **`bluetooth_client_manager.py` の設定:** 
    *   Raspberry Pi Zero のファイルシステムに, このリポジトリの `rpi_zero_python_client/` ディレクトリをコピーします。
    *   `rpi_zero_python_client/bluetooth_client_manager.py` ファイルを編集し, `ESP32_DEVICES_TO_CONNECT` リストに, 準備した ESP32 の MAC アドレスを正確に設定します。複数の ESP32 がある場合は, それぞれ追加します。
        ```python
        ESP32_DEVICES_TO_CONNECT = ["XX:XX:XX:XX:XX:XX", "YY:YY:YY:YY:YY:YY"]
        ```

3.  **Python クライアントスクリプトの実行:** 
    *   Raspberry Pi Zero のターミナルで, `bluetooth_client_manager.py` があるディレクトリに移動し, スクリプトを実行します。
        ```bash
        cd rpi_zero_python_client
        python3 bluetooth_client_manager.py
        ```

## トラブルシューティング

*   **接続できない、または Bluetooth エラー:**
    *   **MAC アドレスの確認:** `bluetooth_client_manager.py` の MAC アドレスが正しいか再確認します。コロン (`:`) で区切られていることを確認してください。
    *   **ESP32 の電源とスケッチ:** ESP32 の電源が入っており, 正しいスケッチが書き込まれ, Bluetooth SPP サーバーとして動作しているか確認します。
    *   **Raspberry Pi Zero の Bluetooth:** Raspberry Pi Zero の Bluetooth が有効になっており, `sudo systemctl status bluetooth` でサービスが動作しているか確認します。
    *   **ペアリング:** 初回接続時, Raspberry Pi Zero と ESP32 の間で手動でのペアリングが必要になることがあります。
        *   Raspberry Pi Zero のターミナルで `bluetoothctl` を実行します。
        *   `agent on` -> `default-agent` -> `scan on`
        *   ESP32 (`ESP32_SPP_SERVER_01`など) が見つかったら, その MAC アドレスをメモします。
        *   `pair <ESP32 の MAC アドレス>`
        *   パスキーの入力を求められたら, ESP32 側で指定していない場合は通常 `0000` や `1234` などを使用します。
        *   `connect <ESP32 の MAC アドレス>`
        *   `quit` で `bluetoothctl` を終了します。
    *   **権限の問題:** Python スクリプトを `sudo python3 bluetooth_client_manager.py` で実行してみてください。ただし, セキュリティ上の理由から, 必要最低限の権限で実行するのが理想です。

*   **データが送受信されない:**
    *   **改行コード:** Python スクリプトと ESP32 スケッチの両方で, `readStringUntil('\n')` と `println()` が整合性を持って使われているか確認します。
    *   **バッファサイズ:** 送信するデータが大きすぎる場合, 送受信バッファの制限に引っかかる可能性があります。少量のデータでテストしてください。
    *   **`time.sleep()`:** デバッグ中は `time.sleep()` の値を小さくして, より頻繁に通信するようにしても良いでしょう。

---
この README ファイルは, プロジェクトをセットアップし, 実行するための包括的なガイドとして機能します。

```