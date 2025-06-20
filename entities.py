import pygame
import random
from resource_manager import ResourceManager

class GameConfig:
    """ゲーム全体の設定を管理するクラス"""
    # 画面設定
    SCALE = 3                        # スケール倍率
    BASE_WIDTH = 160
    BASE_HEIGHT = 144
    WIDTH = BASE_WIDTH * SCALE       # 画面幅
    HEIGHT = BASE_HEIGHT * SCALE     # 画面高さ
    FPS = 60                         # フレームレート
    
    # 色定義
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (220, 220, 220)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 200, 0)
    SKY_BLUE = (135, 206, 235)       # 空色
    ROAD_COLOR = (210, 180, 140)     # 道の色

    # 戦闘関連
    ENCOUNTER_RATE = 0.1             # 野生ポケモン遭遇率
    STEPS_BEFORE_ENCOUNTER = 10      # 遭遇までの最小ステップ数
    MESSAGE_DISPLAY_SPEED = 50       # メッセージ表示速度（ミリ秒）
    MESSAGE_WAIT_TIME = 2000         # メッセージ表示後の待機時間（ミリ秒）
    BATTLE_END_WAIT_TIME = 4000      # バトル終了後の待機時間（ミリ秒）
    HP_ANIMATION_SPEED = 0.1         # HPバー減少アニメーションの速度
    
    # スキルアニメーション関連
    SKILL_ANIMATION_DURATION = 1500  # スキルアニメーション表示時間（ミリ秒）
    FIRE_ANIMATION_SPEED = 100       # 炎アニメーションの速度（ミリ秒）
    
    # 画像のパス
    IMG_DIR = "img/"
    HP_BAR_IMG = IMG_DIR + "hp.png"
    ENEMY_FRAME_IMG = IMG_DIR + "enemy_info_frame.png"
    MY_FRAME_IMG = IMG_DIR + "my_info_frame.png"
    MESSAGE_ALL_IMG = IMG_DIR + "message_all.png"
    MESSAGE_HALF_IMG = IMG_DIR + "message_half.png"
    MESSAGE_HALF_MIDDLE_IMG = IMG_DIR + "message_half_middle.png"
    MESSAGE_HALF_SEPARATE_IMG = IMG_DIR + "message_half_separate.png"
    
    # キャラクター画像
    PLAYER_SPRITE_IMG = IMG_DIR + "pokemon_player_red_sprite.png"
    HITOKAGE_IMG = IMG_DIR + "hitokage.png"
    
    # スキル画像
    FIRE_SMALL_IMG = IMG_DIR + "fire_small.png"
    FIRE_BIG_IMG = IMG_DIR + "fire_big.png"
    
    # ポケモン画像マップ
    POKEMON_IMG_MAP = {
        "ゼニガメ": IMG_DIR + "zenigame.png",
        "ピカチュウ": IMG_DIR + "pikachu.png",
        "フシギダネ": IMG_DIR + "hushigidane.png",
        "イーブイ": IMG_DIR + "eevee.png",
        "ヒトカゲ": IMG_DIR + "hitokage.png"
    }
    
    # マップファイル
    MAP_FILE = "pokemon_road_1.tmx"
    
    # タイル設定
    TILE_SIZE = 16                  # 1タイルのピクセル数
    MAP_WIDTH = 20                  # マップの横タイル数
    MAP_HEIGHT = 36                 # マップの縦タイル数
    
    # タイル当たり判定設定
    WALKABLE_TILE_IDS = [3, 6]         # 歩行可能なタイルIDのリスト

class Pokemon:
    """ポケモンクラス - ポケモンの基本情報を管理"""
    
    def __init__(self, name, type, hp, moves, damages, move_types=None, move_pp=None):
        self.name = name
        self.type = type
        self.max_hp = hp
        self.hp = hp
        self.display_hp = hp  # 表示用HP（アニメーション用）
        self.moves = moves
        self.damages = damages
        # 技タイプのデフォルト設定（指定がない場合はポケモンと同じタイプ）
        self.move_types = move_types if move_types else [type] * len(moves)
        # PPのデフォルト設定（指定がない場合は10）
        self.move_pp = move_pp if move_pp else [[10, 10] for _ in moves]  # [現在PP, 最大PP]

class Player(pygame.sprite.Sprite):
    """プレイヤークラス - プレイヤーキャラクターの制御を担当"""
    
    def __init__(self, resource_manager: ResourceManager):
        super().__init__()
        self.resource_manager = resource_manager

        map_width_px = GameConfig.MAP_WIDTH * GameConfig.TILE_SIZE * GameConfig.SCALE
        map_height_px = GameConfig.MAP_HEIGHT * GameConfig.TILE_SIZE * GameConfig.SCALE
        
        self.width = 20 * GameConfig.SCALE  # サイズをスケールに合わせる
        self.height = 20 * GameConfig.SCALE
        
        # 中央位置の計算（プレイヤーの幅を考慮）
        self.x = (map_width_px / 2) - (self.width / 2)
        # 下部位置の計算（プレイヤーの高さを考慮し、少し余裕を持たせる）
        self.y = map_height_px - self.height - (4 * GameConfig.TILE_SIZE * GameConfig.SCALE)
        
        self.speed = 3 * GameConfig.SCALE  # 移動速度もスケールに合わせる
        self.direction = "down"
        
        # アニメーション関連
        self.animation_frame = 0  # 現在のアニメーションフレーム
        self.animation_timer = 0  # アニメーションタイマー
        self.is_moving = False    # 移動中かどうか
        
        # 技の詳細情報を追加：タイプとPP
        self.pokemon = [Pokemon("ヒトカゲ", "ほのお", 20, 
                               ["ひのこ", "ひっかく"], 
                               [10, 5], 
                               ["ほのお", "ノーマル"],  # 技のタイプ
                               [[25, 25], [35, 35]])]  # PP [現在値, 最大値]
        
        # スプライトシートを読み込む
        self.sprite_sheet = self.resource_manager.load_image(GameConfig.PLAYER_SPRITE_IMG)
        
        # スプライトのサイズ（スプライトシートでの1フレームのサイズ）
        self.sprite_width = 16  # スプライトシートでの1フレームの幅
        self.sprite_height = 16  # スプライトシートでの1フレームの高さ
        
        # 初期画像を設定
        self.image = self.get_sprite_frame(self.direction, 0)
        
        # スプライト用のrectを設定
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_sprite_frame(self, direction, frame):
        """指定された方向とフレームのスプライトを切り出す"""
        # 実際のスプライト位置とフレームのマッピング
        if direction == "down":
            row = 0
            col = frame  # 0, 1, 2
        elif direction == "left":
            # 左向きは[1][0]と[1][1]を使用
            row = 1
            col = 0 if frame == 0 else 1 if frame == 1 else 0  # frame 2も0に戻す
        elif direction == "right":
            # 右向きは左向きを反転
            row = 1
            col = 0 if frame == 0 else 1 if frame == 1 else 0  # frame 2も0に戻す
        elif direction == "up":
            # 上向きは[1][2]と[2][0]を使用
            if frame == 0:
                row = 1
                col = 2
            elif frame == 1:
                row = 2
                col = 0
            else:  # frame == 2
                row = 1
                col = 2
        else:
            row = 0
            col = frame
        
        # スプライトシートから切り出す
        sprite_rect = pygame.Rect(
            col * self.sprite_width,
            row * self.sprite_height,
            self.sprite_width,
            self.sprite_height
        )
        
        # 切り出したスプライトを作成
        sprite = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), sprite_rect)
        
        # 右向きの場合は左右反転
        if direction == "right":
            sprite = pygame.transform.flip(sprite, True, False)
        
        # ゲームのスケールに合わせてリサイズ
        scaled_sprite = pygame.transform.scale(sprite, (self.width, self.height))
        
        return scaled_sprite

    def move(self, keys, tmx_map=None):
        """プレイヤーの移動処理"""
        moved = False
        
        # 斜め移動を防ぐため、1つの方向のみ処理（優先順位: 上下 > 左右）
        if keys[pygame.K_UP]:
            if self._try_move(0, -self.speed, "up", tmx_map):
                moved = True
        elif keys[pygame.K_DOWN]:
            if self._try_move(0, self.speed, "down", tmx_map):
                moved = True
        elif keys[pygame.K_LEFT]:
            if self._try_move(-self.speed, 0, "left", tmx_map):
                moved = True
        elif keys[pygame.K_RIGHT]:
            if self._try_move(self.speed, 0, "right", tmx_map):
                moved = True
        
        # 移動状態を更新
        self.is_moving = moved
        
        # アニメーション更新
        self.update_animation()
        
        # rectの位置を更新
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _try_move(self, dx, dy, direction, tmx_map):
        """指定された方向への移動を試行する"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # TMXマップがある場合は衝突判定を行う
        if tmx_map:
            # プレイヤーの当たり判定ポイントを複数チェック
            collision_points = self._get_collision_points(new_x, new_y)
            
            # すべての当たり判定ポイントが歩行可能かチェック
            for point_x, point_y in collision_points:
                if not tmx_map.is_walkable(point_x, point_y):
                    return False
            
            # マップ範囲内に制限する
            old_x, old_y = self.x, self.y
            self.x = max(0, min(tmx_map.scaled_map_width - self.width, new_x))
            self.y = max(0, min(tmx_map.scaled_map_height - self.height, new_y))
            
            # 方向を更新
            self.direction = direction
            
            # 実際に移動したかチェック
            return old_x != self.x or old_y != self.y
        else:
            # TMXマップがない場合は単純に移動し、画面内に制限
            old_x, old_y = self.x, self.y
            self.x = max(0, min(GameConfig.WIDTH - self.width, new_x))
            self.y = max(0, min(GameConfig.HEIGHT - self.height, new_y))
            self.direction = direction
            return old_x != self.x or old_y != self.y
    
    def _get_collision_points(self, x, y):
        """プレイヤーの当たり判定ポイントを取得する"""
        # プレイヤーの四隅と中心、さらに各辺の中点をチェック
        margin = 2 * GameConfig.SCALE  # 少しマージンを取る
        points = [
            # 四隅
            (x + margin, y + margin),  # 左上
            (x + self.width - margin, y + margin),  # 右上
            (x + margin, y + self.height - margin),  # 左下
            (x + self.width - margin, y + self.height - margin),  # 右下
            # 各辺の中点
            (x + self.width/2, y + margin),  # 上辺中央
            (x + self.width/2, y + self.height - margin),  # 下辺中央
            (x + margin, y + self.height/2),  # 左辺中央
            (x + self.width - margin, y + self.height/2),  # 右辺中央
            # 中心
            (x + self.width/2, y + self.height/2)  # 中心
        ]
        return points
    
    def update_animation(self):
        """アニメーションフレームを更新"""
        current_time = pygame.time.get_ticks()
        
        if self.is_moving:
            # 移動中は歩行アニメーション
            if current_time - self.animation_timer > 200:  # 200ms間隔でフレーム変更
                self.animation_frame = (self.animation_frame + 1) % 3  # 0, 1, 2をループ
                # フレーム1, 2の場合は歩行アニメーション
                if self.animation_frame == 0:
                    frame = 0  # 正面
                elif self.animation_frame == 1:
                    frame = 1  # 歩行1
                else:  # self.animation_frame == 2
                    frame = 2  # 歩行2
                
                self.image = self.get_sprite_frame(self.direction, frame)
                self.animation_timer = current_time
        else:
            # 停止中は正面向きのフレーム
            self.animation_frame = 0
            self.image = self.get_sprite_frame(self.direction, 0)

    def draw(self, screen, map_offset_x=0, map_offset_y=0):
        """プレイヤーを描画"""
        # オフセットを適用した位置に描画
        screen_x = self.x + map_offset_x
        screen_y = self.y + map_offset_y
        
        # 画像を描画
        screen.blit(self.image, (screen_x, screen_y))

class WildPokemon(pygame.sprite.Sprite):
    """野生ポケモンクラス - 野生ポケモンの生成と管理"""
    
    def __init__(self, resource_manager: ResourceManager):
        super().__init__()
        self.resource_manager = resource_manager
        
        pokemon_options = [
            ("ゼニガメ", "みず", 18, ["みずでっぽう", "たいあたり"], [9, 5]),
            ("フシギダネ", "くさ", 19, ["はっぱカッター", "たいあたり"], [8, 5]),
            ("ピカチュウ", "でんき", 15, ["でんきショック", "たいあたり"], [12, 5]),
            ("イーブイ", "ノーマル", 17, ["たいあたり", "すなかけ"], [7, 3])
        ]
        choice = random.choice(pokemon_options)
        self.pokemon = Pokemon(choice[0], choice[1], choice[2], choice[3], choice[4])
        
        # ポケモンの画像を読み込む
        image_path = GameConfig.POKEMON_IMG_MAP.get(self.pokemon.name, GameConfig.POKEMON_IMG_MAP["ピカチュウ"])
        self.image = self.resource_manager.load_image(image_path, (120, 120))
        # スプライト用のrectを設定（位置は固定）
        self.rect = pygame.Rect(90 * GameConfig.SCALE, -10, 50 * GameConfig.SCALE, 50 * GameConfig.SCALE)