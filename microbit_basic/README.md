# micro:bit BLE サンプルプロジェクト

## 概要

このプロジェクトは、micro:bit を使用した Bluetooth Low Energy (BLE) 通信のサンプルを提供します。Python スクリプトと micro:bit (MakeCode) スクリプトが含まれており、micro:bit と他のデバイス間での BLE 通信の基本的な実装を示します。

## 目次

- [概要](#概要)
- [ファイル説明](#ファイル説明)
- [使用方法](#使用方法)
  - [1. micro:bit の準備](#1-microbit-の準備)
  - [2. Python スクリプトの実行)


## ファイル説明

-   `micro_bit.js`:
    -   micro:bit 用の MakeCode プロジェクトです。
    -   Bluetooth UART サービスを初期化し、有効にします。
    -   Bluetooth 接続時と切断時に異なるアイコン (Yes/No) を表示します。
    -   micro:bit の A ボタンが押されると "A" という文字列を、B ボタンが押されると "B" という文字列を Bluetooth UART 経由で送信します。
    -   起動時にハートアイコンを表示します。

-   `ble_scanner_all.py`:
    -   BLE デバイスをスキャンし、検出したデバイスの情報を表示する Python スクリプトです。
    -   周囲の BLE デバイスを探索する際に使用できます。

-   `connet_microbit.py`:
    -   micro:bit と Bluetooth で接続し、UART 通信を行うための Python スクリプトです。
    -   `micro_bit.js` が書き込まれた micro:bit と連携して動作します。

## 使用方法

### 1. micro:bit の準備

1.  `micro_bit.js` の内容を MakeCode エディタにコピー＆ペーストするか、プロジェクトをインポートします。
2.  プロジェクトをコンパイルし、生成された `.hex` ファイルを micro:bit に書き込みます。

### 2. Python スクリプトの実行

-   `ble_scanner_all.py` を実行して、近くの BLE デバイスをスキャンできます。
-   `connet_microbit.py` を実行して、`micro_bit.js` が書き込まれた micro:bit と接続し、BLE UART 通信を開始できます。
