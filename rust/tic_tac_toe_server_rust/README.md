# Tic-Tac-Toe Server in Rust

## 目次

- [概要](#概要)
- [ファイル構造](#ファイル構造)
- [機能](#機能)
- [環境設定](#環境設定)
- [実行方法](#実行方法)
- [APIエンドポイント](#apiエンドポイント)
- [テスト](#テスト)
- [カバレッジ](#カバレッジ)

## 概要

このプロジェクトは、Rustで実装された三目並べ（Tic-Tac-Toe）ゲームのバックエンドサーバーです。Actix-webフレームワークを使用しており、AIエージェントとの対戦も可能です。

## ファイル構造

プロジェクトの主要なファイルとディレクトリは以下の通りです。

-   `Cargo.toml`: Rustプロジェクトの設定ファイル。依存関係やパッケージ情報が含まれます。
-   `Cargo.lock`: `Cargo.toml`で指定された依存関係の正確なバージョンを記録します。
-   `src/`: ソースコードを格納するディレクトリです。
    -   `src/main.rs`: アプリケーションのエントリーポイントです。
    -   `src/lib.rs`: ライブラリクレートのエントリーポイントです。アプリケーションのブートストラップロジックやルーティング設定が含まれます。
    -   `src/server.rs`: Actix-webサーバーのエンドポイントハンドラやゲーム管理ロジックが含まれます。
    -   `src/game_logic.rs`: 三目並べゲームのコアロジック（ボードの状態、手の実行、勝者判定など）が含まれます。
    -   `src/agents.rs`: AIエージェントの定義と実装（例: RandomAgent）が含まれます。
    -   `src/schemas.rs`: APIのリクエスト/レスポンスのデータ構造（スキーマ）が定義されています。
-   `tests/`: 統合テストを格納するディレクトリです。
    -   `tests/agents_test.rs`: エージェント関連のテストが含まれます。
    -   `tests/game_logic_test.rs`: ゲームロジック関連のテストが含まれます。
    -   `tests/schemas_test.rs`: スキーマ関連のテストが含まれます。
    -   `tests/server_test.rs`: サーバー関連のテストが含まれます。
-   `openapi.json`: アプリケーション起動時に自動生成されるOpenAPIドキュメントです。
-   `coverage.json`: コードカバレッジの結果ファイルです。
-   `target/`: コンパイルされたバイナリや中間ファイルを格納するディレクトリです（Git管理対象外）。

## 機能

-   人間対AI、またはAI対AIの三目並べゲーム
-   シンプルなRESTful APIを通じてゲームの状態管理と操作
-   利用可能なAIエージェントのリスト取得 (例: `Human`, `Random`)

## 環境設定

本プロジェクトを実行するには、[Rust](https://www.rust-lang.org/tools/install) がインストールされている必要があります。

1.  **Rustのインストール:**
    公式ドキュメントに従って `rustup` を使用してRustをインストールしてください。

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

    インストール後、現在のシェルでPathを設定するために以下のコマンドを実行するか、新しいターミナルを開いてください。

    ```bash
    source "$HOME/.cargo/env"
    ```

2.  **依存関係のビルド:**
    プロジェクトディレクトリに移動し、依存関係をビルドします。

    ```bash
    cd /path/to/tic_tac_toe_server_rust
    cargo build
    ```

## 実行方法

デバッグモードでサーバーを起動するには、以下のコマンドを実行します。

```bash
cargo run
```

サーバーはデフォルトで `http://127.0.0.1:8000` でリッスンします。

## APIエンドポイント

| メソッド | エンドポイント        | 説明                      | リクエストボディ (例)                   | レスポンスボディ (例)                                         |
| :------- | :-------------------- | :------------------------ | :---------------------------------- | :-------------------------------------------------------- |
| `POST`   | `/start_game`         | 新しいゲームを開始        | `{"player_x_type": "Human", "player_o_type": "Random", "human_player_symbol": "X"}` | `{"board": [["_", "_", "_"], ...], "current_player": "X", ...}` |
| `GET`    | `/game_status`        | 現在のゲームの状態を取得  | なし                                | `{"board": [["_", "_", "_"], ...], "current_player": "X", ...}` |
| `POST`   | `/make_move`          | プレイヤーの移動を実行    | `{"row": 0, "col": 0}`              | `{"board": [["X", "_", "_"], ...], "current_player": "O", ...}` |
| `GET`    | `/available_agents`   | 利用可能なエージェントを取得 | なし                                | `{"agents": ["Human", "Random"]}`                         |

## APIドキュメント

このプロジェクトのAPIドキュメントは、OpenAPI 3.0形式で提供されます。

### ファイル出力

`cargo run`でサーバーを起動すると、プロジェクトのルートディレクトリに`openapi.json`ファイルが自動的に生成されます。

### オンライン参照

サーバーが実行されている間は、以下のURLでブラウザからAPIドキュメントを参照できます。

-   **OpenAPI JSON:** `http://127.0.0.1:8000/api-docs/openapi.json`
-   **Swagger UI:** `http://127.0.0.1:8000/swagger-ui/`

## テスト

プロジェクトのテストを実行するには、以下のコマンドを使用します。

```bash
cargo test
```

## カバレッジ

コードカバレッジを生成するには、`cargo llvm-cov` を使用します。まず、`llvm-tools-preview` コンポーネントがインストールされていることを確認してください。

```bash
rustup component add llvm-tools-preview
```

次に、`cargo-llvm-cov` クレートをインストールします。

```bash
cargo install cargo-llvm-cov
```

カバレッジを生成し、レポートを表示するには、以下のコマンドを実行します。

```bash
cargo llvm-cov --html
```

これにより、`target/llvm-cov/html/index.html` にHTMLレポートが生成されます。

ターミナルにカバレッジのサマリーのみを表示したい場合は、以下のコマンドを実行します。

## Lint (Clippy)

コード品質チェックには、Rustの公式linterであるClippyを使用します。

```bash
cargo clippy
```

現在、一部の`MutexGuard`に関する警告が残っていますが、これは`std::sync::Mutex`を非同期コンテキストで使用する際のRustの制限によるもので、アプリケーションの動作には影響ありません。これらの警告は現在許容されています。


```bash
cargo llvm-cov report --summary-only
```

