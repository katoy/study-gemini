# Rust CUI Client

これは、三目並べAIプロジェクトの一部であるRust製のCUI（Character User Interface）クライアントです。FastAPIサーバーと連携し、コマンドラインを通じてAIと三目並べをプレイできます。

## 目次

- [Rust CUI Client](#rust-cui-client)
  - [目次](#目次)
  - [概要](#概要)
  - [ビルド方法](#ビルド方法)
  - [実行方法](#実行方法)
  - [テスト](#テスト)
  - [カバレッジ計測](#カバレッジ計測)
  - [Lintチェック](#lintチェック)

## 概要

このクライアントはRustで実装されており、Python製のFastAPIサーバーと通信します。ユーザーはコンソールを通じて手を指定し、ゲームの進行をテキストで確認できます。

## ファイル構成

以下は、`rust/CUI`ディレクトリ内の主要なファイルとディレクトリです。

```
.
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── display.rs
│   ├── game_client.rs
│   └── models.rs
├── tests/
│   ├── display_test.rs
│   ├── game_client_test.rs
│   ├── main_test.rs
│   └── models_test.rs
└── README.md
```

## ビルド方法

プロジェクトのルートディレクトリで以下のコマンドを実行し、Rust CUIクライアントをビルドします。

```bash
cd rust/CUI
cargo build
```

## 実行方法

クライアントを実行する前に、FastAPIサーバーが起動していることを確認してください。サーバーの起動方法については、[プロジェクトのメインREADME.md](../../README.md)を参照してください。

ビルド後、以下のコマンドでクライアントを実行できます。

```bash
cd rust/CUI
cargo run
```

クライアントアプリケーションは、空いているマスに1から9の数字を表示します。この数字を入力することで、そのマスに手を進めることができます。

## テスト

Rustコードのテストは `cargo test` を使って実行します。`rust/CUI` ディレクトリでコマンドを実行してください。

```bash
cd rust/CUI
cargo test
```

## カバレッジ計測

Rustコードのカバレッジを測定するには `cargo-llvm-cov` を使用します。事前にインストールが必要です。

```bash
cargo install cargo-llvm-cov
```

カバレッジを測定するには、`rust/CUI` ディレクトリで以下のコマンドを実行します。

#### コンソールでの確認

```bash
cd rust/CUI
cargo llvm-cov --text
```

#### HTMLレポートの生成

```bash
cd rust/CUI
cargo llvm-cov --html
open target/llvm-cov/html/index.html # macOSの場合
```

## Lintチェック

Rustコードの品質を保つために、`cargo clippy` を使用してLintチェックを行います。

```bash
cd rust/CUI
cargo clippy
```
