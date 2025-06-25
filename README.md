# 概要

ほぼAIが作ったポケモン風ゲームです。

- 言語：Python
- ライブラリ：pygame

## プロジェクト構成

```
pokemon/
├── main.py                 # エントリーポイント
├── CLAUDE.md              # 開発ガイドライン
├── README.md              # このファイル
├── src/                   # ソースコード
│   ├── core/              # コアシステム
│   │   └── game_engine.py # メインゲームエンジン
│   ├── entities/          # ゲームエンティティ
│   │   └── entities.py    # プレイヤー、ポケモン、設定クラス
│   ├── managers/          # 各種マネージャー
│   │   ├── battle_manager.py
│   │   ├── font_manager.py
│   │   ├── game_state_manager.py
│   │   ├── input_manager.py
│   │   ├── map_transition_manager.py
│   │   └── resource_manager.py
│   └── systems/           # システム機能
│       ├── animation_system.py
│       ├── map_system.py
│       ├── player_movement.py
│       └── ui_renderer.py
└── assets/                # ゲームアセット
    ├── images/            # 画像ファイル
    │   ├── *.png         # スプライト、UI画像
    │   └── img_usage.md  # 画像使用方法
    ├── maps/              # マップファイル
    │   └── *.tmx         # Tiledマップファイル
    ├── tilesets/          # タイルセット
    │   ├── *.tsx         # Tiledタイルセットファイル
    │   └── *.png         # タイルセット画像
    └── fonts/             # フォントファイル（今後追加予定）
```

## 実行方法

```bash
python3 main.py
```

## 開発コマンド

### 依存関係の確認
```bash
python3 -c "import pygame; print('pygame version:', pygame.version.ver)"
python3 -c "import pytmx; print('pytmx imported successfully')"
```

### 必要な依存パッケージ
- pygame（v2.6.1以上で動作確認済み）
- pytmx（TMXマップファイル対応用）

## アーキテクチャ

このプロジェクトは単一責任の原則に従い、各コンポーネントが明確な責任を持つよう設計されています：

- **GameEngine**: メインループとシステム統合
- **Managers**: 各ドメインの管理（フォント、リソース、バトル等）
- **Systems**: 機能システム（マップ、アニメーション、UI等）
- **Entities**: ゲームオブジェクト（ポケモン、プレイヤー）

詳細な開発ガイドラインは`CLAUDE.md`を参照してください。