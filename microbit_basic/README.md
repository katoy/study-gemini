# micro:bit BLE サンプルプロジェクト

## 概要

このプロジェクトは、micro:bit を使用した Bluetooth Low Energy (BLE) 通信のサンプルを提供します。Python スクリプトと micro:bit (MakeCode) スクリプトが含まれており、micro:bit と他のデバイス間での BLE 通信の基本的な実装を示します。

## 目次

- [micro:bit BLE サンプルプロジェクト](#microbit-ble-サンプルプロジェクト)
  - [概要](#概要)
  - [目次](#目次)
  - [ファイル説明](#ファイル説明)
  - [使用方法](#使用方法)
    - [1. micro:bit の準備](#1-microbit-の準備)
    - [2. Python スクリプトの実行](#2-python-スクリプトの実行)
  - [mac 側の動作](#mac-側の動作)
  - [プログラムの動作](#プログラムの動作)
  - [通信表](#通信表)

## ファイル説明

- `micro_bit.js`:
  - micro:bit 用の MakeCode プロジェクトです。
  - Bluetooth UART サービスを初期化し、有効にします。
  - 接続時と切断時に異なるアイコン (Yes/No) を表示します。
  - A ボタンで "A"、B ボタンで "B"、同時押しで "A+B" を送信します。
  - 起動時にハートアイコンを表示します。

- `ble_scanner_all.py`:
  - BLE デバイスをスキャンし、検出したデバイス情報を表示します。

- `connet_microbit.py`:
  - micro:bit と BLE で接続し、UART 通信を行います。

## 使用方法

### 1. micro:bit の準備

1. `micro_bit.js` の内容を MakeCode エディタに貼り付け、プロジェクトをインポートします。
2. コンパイルして生成された `.hex` ファイルを micro:bit に書き込みます。

### 2. Python スクリプトの実行

- `ble_scanner_all.py` を実行して近隣の BLE デバイスをスキャンします。
- `connet_microbit.py` を実行して micro:bit と接続し、BLE UART 通信を開始します。

## mac 側の動作

- Python 3.10 以上が必要です。`pip install bleak` で依存パッケージをインストールしてください。
- `ble_scanner_all.py` はデバイス名・アドバイズデータ・RSSI を端末に表示します。
- `connet_microbit.py` は `bleak` を使用し、接続時に `Connected`、切断時に `Disconnected` と表示します。受信文字列はリアルタイムで標準出力に出力され、Ctrl+C で終了できます。

## プログラムの動作

- `micro_bit.js` は BLE UART を初期化し、ボタン操作に応じて文字列を送信します。
- `ble_scanner_all.py` は周囲の BLE デバイスをスキャンし情報を表示します。
- `connet_microbit.py` は micro:bit と接続し、UART でデータの送受信を行います。接続時に LED が緑、切断時に赤に変わります。

## 通信表

| ボタン操作   | mac への送信文字 | mac から返される文字 | micro:bit の表示                |
| ------------ | ---------------- | -------------------- | ------------------------------- |
| A ボタン単体 | "A"              | "a"                  | "a" が micro:bit に表示されます |
| B ボタン単体 | "B"              | "b"                  | "b" が micro:bit に表示されます |
| A+B 同時押し | "A+B"            | "c"                  | "c" が micro:bit に表示されます |
