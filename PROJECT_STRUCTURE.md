# ポケモン風ゲーム プロジェクト構成

## 概要
このプロジェクトは、単一責任の原則と読みやすさを重視してリファクタリングされたポケモン風ゲームです。元の巨大な単一ファイルから、責任が明確に分離された複数のモジュールに分割されています。

## フォルダ構成

```
pokemon/
├── README.md                    # プロジェクトの説明
├── PROJECT_STRUCTURE.md        # このファイル（プロジェクト構成説明）
├── pokemon.py                   # メインゲームファイル（エントリーポイント）
├── entities.py                  # ゲームエンティティ（Pokemon, Player, WildPokemon）
├── font_manager.py              # フォント管理システム
├── resource_manager.py          # リソース（画像）管理システム
├── battle_manager.py            # バトルシステム管理
├── ui_renderer.py               # UI描画システム
├── input_manager.py             # 入力処理システム
├── animation_system.py          # アニメーション管理システム
├── map_system.py                # マップシステム
├── pokemon_road_1.tmx           # マップデータファイル
└── img/                         # 画像リソースフォルダ
```

## モジュール詳細

### 1. pokemon.py
**責任**: ゲーム全体の制御とエントリーポイント
- `GameEngine`: メインゲームループと全体制御
- 各種マネージャーの初期化と統合
- イベント処理、状態更新、描画の統合

### 2. entities.py
**責任**: ゲーム内エンティティの定義
- `GameConfig`: ゲーム設定の定数管理
- `Pokemon`: ポケモンの基本データ構造
- `Player`: プレイヤーキャラクターの制御
- `WildPokemon`: 野生ポケモンの生成と管理

### 3. font_manager.py
**責任**: フォント管理
- `FontManager`: 日本語フォントの読み込みと管理
- プラットフォーム対応（macOS/Windows/Linux）
- フォントキャッシュ機能

### 4. resource_manager.py
**責任**: リソース管理
- `ResourceManager`: 画像の読み込みとキャッシュ
- メモリ効率的なリソース管理
- 重複読み込みの防止

### 5. battle_manager.py
**責任**: バトルシステム管理
- `GameState`: ゲーム状態の定数定義
- `BattleManager`: バトルロジックと状態管理
- 技の実行、ダメージ計算、ターン管理
- メッセージ表示制御

### 6. ui_renderer.py
**責任**: UI描画
- `UIRenderer`: 描画の基底クラス
- `FieldRenderer`: フィールド画面の描画
- `BattleRenderer`: バトル画面の描画
- HPバー、メニュー、アニメーション描画

### 7. input_manager.py
**責任**: 入力処理
- `InputManager`: キーボード入力の処理
- フィールドとバトルでの入力分離
- デバッグ機能の入力処理

### 8. animation_system.py
**責任**: アニメーション管理
- `AnimationSystem`: アニメーション全体の管理
- `Animation`: アニメーションの基底クラス
- `FireAnimation`: 炎エフェクトのアニメーション

### 9. map_system.py
**責任**: マップシステム
- `TiledMap`: TMXマップファイルの読み込みと描画
- 衝突判定、歩行可能性判定
- レイヤー管理（背景、障害物、草むら）

## 設計原則

### 単一責任の原則（SRP）
各クラスとモジュールは1つの明確な責任を持ちます：
- フォント管理はfont_managerのみ
- リソース管理はresource_managerのみ
- バトルロジックはbattle_managerのみ

### 依存関係の管理
- 上位レベル（GameEngine）が下位レベル（各Manager）に依存
- 各Managerは独立性を保ち、相互依存を最小化
- 設定はGameConfigクラスで一元管理

### 拡張性
- 新しいポケモンの追加：entitiesに追加
- 新しいアニメーション：animation_systemに追加
- 新しいUI：ui_rendererに追加

## 使用方法

### ゲームの起動
```bash
python pokemon.py
```

### 依存関係
- pygame
- pytmx（TMXマップファイル用）

### 開発時のポイント
1. 新機能追加時は適切なモジュールに配置
2. 共通設定はGameConfigに追加
3. リソース追加時はresource_managerを通す
4. UI変更時はui_rendererを修正

## リファクタリング前後の比較

### リファクタリング前
- 1つの巨大ファイル（1250+ 行）
- 全ての機能が混在
- 保守性・拡張性が低い

### リファクタリング後
- 9つの専門モジュール
- 各モジュール100-400行程度
- 明確な責任分離
- 高い保守性・拡張性

## 今後の改善案

1. **テストの追加**: 各モジュールに対応するテストファイル
2. **設定ファイル**: GameConfigを外部ファイル化
3. **ログシステム**: デバッグとエラー追跡用
4. **セーブシステム**: ゲーム進行状況の保存
5. **サウンドシステム**: 音楽・効果音の管理

この構成により、コードの理解・保守・拡張が大幅に改善されています。