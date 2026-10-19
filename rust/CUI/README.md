# Rust CUI Client

これは、三目並べAIプロジェクトの一部であるRust製のCUI（Character User Interface）クライアントです。FastAPIサーバーと連携し、コマンドラインを通じてAIと三目並べをプレイできます。

## 目次

- [Rust CUI Client](#rust-cui-client)
  - [目次](#目次)
  - [概要](#概要)
  - [ファイル構成](#ファイル構成)
  - [ビルド方法](#ビルド方法)
  - [実行方法](#実行方法)
  - [テスト](#テスト)
  - [カバレッジ計測](#カバレッジ計測)
  - [Lintチェックとフォーマット](#lintチェックとフォーマット)

## 概要

このクライアントはRustで実装されており、Python製のFastAPIサーバーと通信します。ユーザーはコンソールを通じて手を指定し、ゲームの進行をテキストで確認できます。
主なロジックは `src/lib.rs` に集約されており、高いテストカバレッジを実現しています。

## ファイル構成

以下は、`rust/CUI`ディレクトリ内の主要なファイルとディレクトリです。

```
.
├── Cargo.toml          # Rustプロジェクトの定義ファイル
├── Cargo.lock          # 依存関係のロックファイル
├── src/
│   ├── main.rs         # エントリポイント
│   ├── lib.rs          # アプリケーションのコアロジック
│   ├── display.rs      # 盤面表示ロジック
│   ├── game_client.rs  # サーバー通信クライアント
│   └── models.rs       # データモデル定義
├── tests/              # 統合テスト
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

### コンソールでの確認

```bash
cd rust/CUI
cargo llvm-cov --text
```

### HTMLレポートの生成

```bash
cd rust/CUI
cargo llvm-cov --html
open target/llvm-cov/html/index.html # macOSの場合
```

## Lintチェックとフォーマット

コード品質を維持するために、Clippyとrustfmtを使用します。

### Lintチェック (Clippy)

潜在的なバグや非推奨なコードパターンを検出します。

```bash
cd rust/CUI
cargo clippy
```

### コードフォーマット

コードのスタイルが標準規約に従っているか確認します。

```bash
cd rust/CUI
cargo fmt --check
```

フォーマットを自動修正するには以下を実行します。

```bash
cd rust/CUI
cargo fmt
```