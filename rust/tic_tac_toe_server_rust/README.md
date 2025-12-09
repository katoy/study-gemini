# Tic-Tac-Toe Server in Rust

## 目次

- [概要](#概要)
- [機能](#機能)
- [ファイル構造](#ファイル構造)
- [環境設定](#環境設定)
- [実行方法](#実行方法)
- [APIエンドポイント](#apiエンドポイント)
- [テスト](#テスト)
- [カバレッジ計測](#カバレッジ計測)
- [Lintチェックとフォーマット](#lintチェックとフォーマット)

## 概要

このプロジェクトは、Rustで実装された三目並べ（Tic-Tac-Toe）ゲームのバックエンドサーバーです。Actix-webフレームワークを使用しており、RESTful APIを通じてゲームの状態管理を行います。AIエージェントとの対戦も可能です。

## 機能

-   人間対AI、またはAI対AIの三目並べゲーム
-   シンプルなRESTful APIを通じたゲームの操作
-   利用可能なAIエージェントのリスト取得 (例: `Human`, `Random`)
-   OpenAPI (Swagger) によるAPIドキュメントの自動生成

## ファイル構造

プロジェクトの主要なファイルとディレクトリは以下の通りです。

-   `Cargo.toml`: Rustプロジェクトの設定ファイル。依存関係やパッケージ情報が含まれます。
-   `Cargo.lock`: 依存関係の正確なバージョンを記録するロックファイルです。
-   `src/`: ソースコードディレクトリ
    -   `main.rs`: アプリケーションのエントリーポイント。
    -   `lib.rs`: ライブラリクレートのエントリーポイント。ブートストラップロジックやルーティング設定を含みます。
    -   `server.rs`: Actix-webサーバーのエンドポイントハンドラやゲーム管理ロジック。
    -   `game_logic.rs`: 三目並べのコアロジック（ボード状態、手の実行、勝敗判定）。
    -   `agents.rs`: AIエージェントの定義と実装。
    -   `schemas.rs`: APIのリクエスト/レスポンス用データ構造（スキーマ）。
-   `tests/`: 統合テストディレクトリ
    -   `agents_test.rs`: エージェント関連のテスト。
    -   `game_logic_test.rs`: ゲームロジック関連のテスト。
    -   `schemas_test.rs`: スキーマ関連のテスト。
    -   `server_test.rs`: サーバーエンドポイントのテスト。
-   `openapi.json`: アプリケーション起動時に自動生成されるOpenAPIドキュメント。
-   `target/`: コンパイル生成物が格納されるディレクトリ（Git管理対象外）。

## 環境設定

本プロジェクトを実行するには、[Rust](https://www.rust-lang.org/tools/install) がインストールされている必要があります。

1.  **Rustのインストール:**
    公式ドキュメントに従い、`rustup` を使用してインストールしてください。

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

    インストール後、環境変数を反映させます。

    ```bash
    source "$HOME/.cargo/env"
    ```

2.  **ビルド:**
    プロジェクトディレクトリで以下を実行します。

    ```bash
    cd rust/tic_tac_toe_server_rust
    cargo build
    ```

## 実行方法

サーバーを起動するには、以下のコマンドを実行します。

```bash
cargo run
```

サーバーはデフォルトで `http://127.0.0.1:8000` でリッスンします。

## APIエンドポイント

| メソッド | エンドポイント   | 説明                      | リクエストボディ (例)                                                                 |
| :------- | :--------------- | :------------------------ | :------------------------------------------------------------------------------------ |
| `POST`   | `/game/start`    | 新しいゲームを開始        | `{"player_x_type": "Human", "player_o_type": "Random", "human_player_symbol": "X"}` |
| `GET`    | `/game/status`   | 現在のゲームの状態を取得  | なし                                                                                  |
| `POST`   | `/game/move`     | プレイヤーの移動を実行    | `{"row": 0, "col": 0}`                                                                |
| `GET`    | `/agents`        | 利用可能なエージェント一覧 | なし                                                                                  |

### APIドキュメント (Swagger UI)

サーバー起動中、以下のURLでAPIドキュメントを参照・テストできます。

-   **Swagger UI:** `http://127.0.0.1:8000/swagger-ui/`
-   **OpenAPI JSON:** `http://127.0.0.1:8000/api-docs/openapi.json`

また、サーバー起動時にルートディレクトリに `openapi.json` ファイルが生成されます。

## テスト

Rustコードのテストは以下のコマンドで実行します。

```bash
cargo test
```

## カバレッジ計測

コードカバレッジを測定するには `cargo-llvm-cov` を使用します。

1.  **ツールのインストール:**

    ```bash
    rustup component add llvm-tools-preview
    cargo install cargo-llvm-cov
    ```

2.  **計測の実行:**

    コンソールにサマリーを表示する場合:
    ```bash
    cargo llvm-cov report --summary-only
    ```

    ファイルごとの詳細なカバレッジをコンソールに表示する場合:
    ```bash
    cargo llvm-cov --text
    ```

    HTMLレポートを生成する場合:
    ```bash
    cargo llvm-cov --html
    open target/llvm-cov/html/index.html # macOSの場合
    ```

    HTMLレポートを生成する場合:
    ```bash
    cargo llvm-cov --html
    open target/llvm-cov/html/index.html # macOSの場合
    ```

## Lintチェックとフォーマット

コード品質を維持するために、Clippyとrustfmtを使用します。

### Lintチェック (Clippy)

```bash
cargo clippy
```

### コードフォーマット

コードスタイルをチェック・修正します。

```bash
cargo fmt --check  # チェックのみ
cargo fmt          # 自動修正
```