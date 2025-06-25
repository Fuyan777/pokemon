# CLAUDE.md（日本語訳）

このファイルは、このリポジトリでClaude Code（claude.ai/code）がコードを扱う際のガイダンスを提供します。

## 開発コマンド

### ゲームの実行
```bash
python3 main.py
```

### 依存関係の確認
```bash
python3 -c "import pygame; print('pygame version:', pygame.version.ver)"
python3 -c "import pytmx; print('pytmx imported successfully')"
```

### 必要な依存パッケージ
- pygame（v2.6.1以上で動作確認済み）
- pytmx（TMXマップファイル対応用）

## プロジェクト構造

```
pokemon/
├── main.py                          # エントリーポイント
├── CLAUDE.md                        # 開発ガイドライン
├── README.md
├── src/                            # ソースコード
│   ├── core/                       # コアシステム
│   │   └── game_engine.py          # メインゲームエンジン
│   ├── entities/                   # ゲームエンティティ
│   │   └── entities.py             # プレイヤー、ポケモン、設定クラス
│   ├── managers/                   # 各種マネージャー
│   │   ├── battle_manager.py       # バトルシステム管理
│   │   ├── font_manager.py         # フォント管理
│   │   ├── game_state_manager.py   # ゲーム状態管理
│   │   ├── input_manager.py        # 入力管理
│   │   ├── map_transition_manager.py # マップ遷移管理
│   │   └── resource_manager.py     # リソース管理
│   └── systems/                    # システム機能
│       ├── animation_system.py     # アニメーションシステム
│       ├── map_system.py           # マップシステム
│       ├── player_movement.py      # プレイヤー移動システム
│       └── ui_renderer.py          # UI描画システム
└── assets/                         # ゲームアセット
    ├── images/                     # 画像ファイル
    ├── maps/                       # TMXマップファイル
    ├── tilesets/                   # タイルセットファイル
    └── fonts/                      # フォントファイル（予定）
```

## アーキテクチャ概要

このプロジェクトはPythonとpygameで作られたポケモン風ゲームです。単一責任の原則に従い、モジュラーアーキテクチャで責務を明確に分離しています。

### コアアーキテクチャパターン
- **GameEngine**：メインループとシステム統合
- **Managers**：各ドメインの専門管理（フォント、リソース、バトル等）
- **Systems**：機能システム（マップ、アニメーション、UI等）
- **Entities**：ゲームオブジェクト（ポケモン、プレイヤー、野生ポケモン）

### コアモジュール

**src/core/game_engine.py** - メインゲームエンジン
- 全マネージャーとシステムの初期化
- イベント処理・更新・描画を含むメインループ
- フィールドとバトル状態の制御

**src/entities/entities.py** - ゲームエンティティ
- `GameConfig`：全体設定定数（遭遇率3%等）
- `Pokemon`, `Player`, `WildPokemon`：主要ゲームオブジェクト

### マネージャー系

**src/managers/battle_manager.py** - バトルシステム
- `GameState`：ゲーム進行用の状態管理
- `BattleManager`：ターン制バトル、ダメージ計算

**src/managers/map_transition_manager.py** - マップ遷移
- 複数マップ間の遷移管理
- プレイヤー位置の保存・復元

**src/managers/resource_manager.py** - アセット管理
- 画像の一元的な読み込みとキャッシュ
- メモリ効率の良いリソース管理

**src/managers/font_manager.py** - フォント管理
- クロスプラットフォームなフォント読み込み
- フォントキャッシュシステム

**src/managers/input_manager.py** - 入力管理
- フィールド・バトルで入力コンテキストを分離

**src/managers/game_state_manager.py** - ゲーム状態管理
- ゲーム全体の状態遷移管理

### システム系

**src/systems/map_system.py** - マップシステム
- `TiledMap`（結合マップ）、`SingleMap`：TMXマップの読み込み・描画
- 衝突判定・歩行可能エリア管理
- ドア相互作用システム

**src/systems/ui_renderer.py** - 描画システム
- `FieldRenderer`：フィールドUI描画
- `BattleRenderer`：バトル画面UI・アニメーション描画

**src/systems/player_movement.py** - プレイヤー移動
- 移動ロジックの処理
- 衝突判定との連携

**src/systems/animation_system.py** - アニメーション
- アニメーション基盤クラス
- 炎エフェクトやバトルアニメーション

### マップシステム
- 複数TMXマップの結合表示（pokemon_road_1.tmx + pokemon_town.tmx）
- 単体マップ表示（pokemon_tileset_okd_lab.tmx）
- Tiledタイルセット対応
- レイヤー単位で描画（背景、障害物、草むら上下）
- マップ間遷移システム（town ⇔ lab）

## 開発ガイドライン

### コードスタイル（.github/copilot-instructions.mdより）
- 変更は必要最小限に
- 単一責任の原則を守る
- 分かりやすい変数名・メソッド名を使う
- 意図が明確になる箇所のみコメントを追加
- 共通処理はメソッド・クラスに切り出す
- 破壊的変更は避ける

### ファイル構成
- 新しいポケモン：src/entities/entities.pyに追加
- 新しいアニメーション：src/systems/animation_system.pyに追加
- 新しいUI要素：src/systems/ui_renderer.pyに追加
- 新しいリソース：src/managers/resource_manager.py経由で読み込み
- 設定変更：src/entities/entities.pyのGameConfigを更新
- 新しいマップ：assets/maps/に配置、GameConfig.MAP_FILESに登録

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