# CLAUDE.md（日本語訳）

このファイルは、このリポジトリでClaude Code（claude.ai/code）がコードを扱う際のガイダンスを提供します。

## 開発コマンド

### ゲームの実行
```bash
python3 pokemon.py
```

### 依存関係の確認
```bash
python3 -c "import pygame; print('pygame version:', pygame.version.ver)"
python3 -c "import pytmx; print('pytmx imported successfully')"
```

### 必要な依存パッケージ
- pygame（v2.6.1以上で動作確認済み）
- pytmx（TMXマップファイル対応用）

## アーキテクチャ概要

このプロジェクトはPythonとpygameで作られたポケモン風ゲームです。コードベースは単一責任の原則に従い、9つの専門モジュールで明確に責務を分離しています。

### コアアーキテクチャパターン
- **GameEngine**（pokemon.py）：メインループとシステム統合
- **マネージャークラス**：各ドメイン（フォント、リソース、バトル等）を担当
- **エンティティクラス**：ゲームオブジェクト（ポケモン、プレイヤー、野生ポケモン）
- **レンダラークラス**：UI描画をフィールド・バトルごとに分離

### 主なモジュール

**pokemon.py** - エントリーポイント兼メインエンジン
- 全マネージャークラスの初期化
- イベント処理・更新・描画を含むメインループ
- フィールドとバトル状態の制御

**entities.py** - ゲームデータ構造
- `GameConfig`：全体設定定数
- `Pokemon`, `Player`, `WildPokemon`：主要ゲームエンティティ

**battle_manager.py** - バトルシステムロジック
- `GameState`：ゲーム進行用の状態定数
- `BattleManager`：ターン制バトル、ダメージ計算

**map_system.py** - TMXマップ管理
- `TiledMap`：TMXマップの読み込み・描画
- 衝突判定・歩行可能エリア管理

**ui_renderer.py** - 描画処理の分離
- `FieldRenderer`：フィールドUI
- `BattleRenderer`：バトル画面UI・アニメーション

**resource_manager.py** - アセット管理
- 画像の一元的な読み込みとキャッシュ
- メモリ効率の良いリソース管理

**font_manager.py** - 日本語フォント対応
- クロスプラットフォームなフォント読み込み（macOS/Windows/Linux）
- フォントキャッシュシステム

**input_manager.py** - 入力管理
- フィールド・バトルで入力コンテキストを分離
- デバッグキー対応

**animation_system.py** - ビジュアルエフェクト
- アニメーション基盤クラス
- 炎エフェクトやバトルアニメーション

### マップシステム
- マップはTMX形式（pokemon_road_1.tmx）を使用
- Tiledタイルセット対応（pokemon_tileset.tsx/.png）
- レイヤー単位で描画（背景、障害物、草むら）

## 開発ガイドライン

### コードスタイル（.github/copilot-instructions.mdより）
- 変更は必要最小限に
- 単一責任の原則を守る
- 分かりやすい変数名・メソッド名を使う
- 意図が明確になる箇所のみコメントを追加
- 共通処理はメソッド・クラスに切り出す
- 破壊的変更は避ける

### ファイル構成
- 新しいポケモン：entities.pyに追加
- 新しいアニメーション：animation_system.pyに追加
- 新しいUI要素：ui_renderer.pyに追加
- 新しいリソース：resource_manager.py経由で読み込み
- 設定変更：entities.pyのGameConfigを更新

### ゲーム状態管理
ゲームはステートマシンパターンを採用：
- `GameState.FIELD`：フィールド移動・探索
- `GameState.BATTLE`：ターン制バトル
- バトルのサブ状態：COMMAND → SELECT → MESSAGE → ANIMATION

### リソース読み込み
全画像はResourceManager経由で読み込み
- メモリ効率化
- 重複読み込み防止
- アセット管理の一元化