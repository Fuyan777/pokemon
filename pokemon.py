import pygame
import sys
import random
import time
import os
import pytmx  # TMXファイルを読み込むためのライブラリ

# ゲーム定数
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
    PLAYER_IMG = IMG_DIR + "red_front.png"
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

# 初期化
pygame.init()
screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
pygame.display.set_caption("ポケモン風ゲーム")
clock = pygame.time.Clock()

# 画像キャッシュ - 同じ画像の重複読み込みを防ぐ
image_cache = {}

def load_image(path, size=None):
    """画像を読み込んでキャッシュする関数"""
    if path not in image_cache:
        image_cache[path] = pygame.image.load(path)
    
    image = image_cache[path]
    if size:
        image = pygame.transform.scale(image, size)
    
    return image

# 日本語フォントを設定（伸ばし棒対応版）
def get_font(size, font_weight='W5'):
    # macOSの場合はフォントパスを直接指定する方法を試す
    if sys.platform == 'darwin':  # macOS
        try:
            # まず、macOSの標準的な日本語フォントパスを直接試す
            if font_weight == 'W8':
                font_paths = [
                    '/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc',  # W6フォント
                ]
            else:  # デフォルトはW5
                font_paths = [
                    '/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc',  # Catalina以降
                ]
            
            for path in font_paths:
                if os.path.exists(path):
                    return pygame.font.Font(path, size)
                    
            # 上記のパスでフォントが見つからない場合は、フォント名で試す
            font_names = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'AppleGothic', 'Osaka']
            for font_name in font_names:
                if font_name.lower() in [f.lower() for f in pygame.font.get_fonts()]:
                    return pygame.font.SysFont(font_name, size)
        except:
            print("Warning: Error loading direct font path, falling back to SysFont")
    
    # Windowsの場合や上記の方法で失敗した場合はSysFontを使う
    font_names = [
        'MS Gothic', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP',  # Windows/Linux
        'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'AppleGothic', 'Osaka'  # macOS
    ]
    
    # フォント名のリストから使えるフォントを探す
    available_fonts = pygame.font.get_fonts()
    for font_name in font_names:
        if font_name.lower() in [f.lower() for f in available_fonts]:
            return pygame.font.SysFont(font_name, size)
        
        # match_fontでも試す
        matched_font = pygame.font.match_font(font_name)
        if matched_font:
            return pygame.font.Font(matched_font, size)
    
    # すべて失敗した場合は代替手段として既定のフォントを使用
    print("Warning: No suitable Japanese font found. Text may not display correctly.")
    
    # フォールバック: シフトJISエンコードを使ってデフォルトフォントを試す
    try:
        default_font = pygame.font.SysFont(None, size)
        # フォントがレンダリングできるか簡単なテスト
        test_text = "テスト"
        default_font.render(test_text, True, GameConfig.BLACK)
        return default_font
    except:
        # 最終手段
        return pygame.font.SysFont(None, size)

# ポケモンクラス
class Pokemon:
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

# プレイヤークラス
class Player:
    def __init__(self):
        self.x = 80 * GameConfig.SCALE  # 画面中央あたりに調整
        self.y = 70 * GameConfig.SCALE
        self.speed = 3 * GameConfig.SCALE  # 移動速度もスケールに合わせる
        self.width = 20 * GameConfig.SCALE  # サイズをスケールに合わせる
        self.height = 20 * GameConfig.SCALE
        self.direction = "down"
        # 技の詳細情報を追加：タイプとPP
        self.pokemon = [Pokemon("ヒトカゲ", "ほのお", 20, 
                               ["ひのこ", "ひっかく"], 
                               [10, 5], 
                               ["ほのお", "ノーマル"],  # 技のタイプ
                               [[25, 25], [35, 35]])]  # PP [現在値, 最大値]
        # プレイヤー画像を読み込む
        self.image = load_image(GameConfig.PLAYER_IMG, (self.width, self.height))

    def move(self, keys, tmx_map=None):
        new_x, new_y = self.x, self.y
        
        if keys[pygame.K_LEFT]:
            new_x -= self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
            self.direction = "right"
        if keys[pygame.K_UP]:
            new_y -= self.speed
            self.direction = "up"
        if keys[pygame.K_DOWN]:
            new_y += self.speed
            self.direction = "down"
    
        # TMXマップがある場合は衝突判定を行う
        if tmx_map:
            # 移動先がマップ内で歩行可能かチェック
            if tmx_map.is_walkable(new_x + self.width/2, new_y + self.height/2):
                # マップ範囲内に制限する
                self.x = max(0, min(tmx_map.scaled_map_width - self.width, new_x))
                self.y = max(0, min(tmx_map.scaled_map_height - self.height, new_y))
            # マップの端に達したかどうかをチェックせず、常にマップの範囲内に収める
        else:
            # TMXマップがない場合は単純に移動し、画面内に制限
            self.x = max(0, min(GameConfig.WIDTH - self.width, new_x))
            self.y = max(0, min(GameConfig.HEIGHT - self.height, new_y))

    def draw(self, map_offset_x=0, map_offset_y=0):
        # オフセットを適用した位置に描画
        screen_x = self.x + map_offset_x
        screen_y = self.y + map_offset_y
        
        # 画像を描画
        screen.blit(self.image, (screen_x, screen_y))

# 野生のポケモンクラス
class WildPokemon:
    def __init__(self):
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
        self.image = load_image(image_path, (120, 120))

# ゲームステートクラス
class GameState:
    FIELD = 0
    BATTLE = 1
    BATTLE_COMMAND = 0  # コマンド選択（たたかう、どうぐ、ポケモン、にげる）
    BATTLE_SELECT = 1   # 技選択
    BATTLE_MESSAGE = 2  # メッセージ表示
    BATTLE_ANIMATION = 3  # 技アニメーション表示

    def __init__(self):
        self.state = self.FIELD
        self.battle_timer = 0
        self.wild_pokemon = None
        self.battle_message = ""
        self.player_turn = True
        self.selected_move = 0
        self.selected_command = 0  # 選択中のコマンド（0: たたかう, 1: どうぐ, 2: ポケモン, 3: にげる）
        self.battle_state = self.BATTLE_COMMAND  # 初期状態をコマンド選択に変更
        self.battle_end_flag = False
        # テキスト表示用の変数
        self.displayed_chars = 0  # 現在表示している文字数
        self.char_display_timer = 0  # 文字表示用タイマー
        self.full_message_displayed = False  # メッセージがすべて表示されたかどうか
        # ダメージ情報を一時保存
        self.pending_damage = 0    # 待機中のダメージ量
        self.damage_target = None  # ダメージを受ける対象（"player" または "enemy"）
        
        # 技アニメーション用の変数
        self.animation_start_time = 0  # アニメーション開始時間
        self.current_move_name = ""  # 現在使用中の技名
        self.animation_pos = []  # アニメーション位置リスト（3点移動用）
        self.animation_frame = 0  # アニメーションフレーム
        self.animation_timer = 0  # アニメーション用タイマー
        self.use_big_fire = False  # 大きい炎を使用するかどうか

# TMXマップを読み込み描画するクラス
class TiledMap:
    def __init__(self, filename):
        try:
            # TMXファイルを読み込む
            self.tmx_data = pytmx.load_pygame(filename)
            # タイルサイズ
            self.tile_width = GameConfig.TILE_SIZE
            self.tile_height = GameConfig.TILE_SIZE
            # マップサイズ（タイル数）
            self.map_width = GameConfig.MAP_WIDTH
            self.map_height = GameConfig.MAP_HEIGHT
            # ピクセル単位のマップサイズ
            self.width = self.map_width * self.tile_width
            self.height = self.map_height * self.tile_height
            # スケーリングサイズを計算
            self.scaled_tile_width = self.tile_width * GameConfig.SCALE
            self.scaled_tile_height = self.tile_height * GameConfig.SCALE
            # スケーリング後のマップサイズ
            self.scaled_map_width = int(self.width * GameConfig.SCALE)
            self.scaled_map_height = int(self.height * GameConfig.SCALE)
            # マップ画像を作成
            self.create_map_surface()
        except Exception as e:
            print(f"マップの読み込みに失敗しました: {e}")
    
    def create_map_surface(self):
        """マップ全体をサーフェスに描画"""
        # 背景のサーフェスを作成（地面や通常レイヤー用）
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        # 前景のサーフェスを作成（rockなどの障害物レイヤー用）
        self.foreground_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.foreground_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        # レイヤーごとに適切なサーフェスに描画
        for layer in self.tmx_data.visible_layers:
            if not hasattr(layer, 'data'):
                continue
                
            # 描画先のサーフェスを決定
            target_surface = self.foreground_surface if layer.name in ['rock', 'collision', 'obstacles'] else self.background_surface
            
            for x, y, gid in layer:
                # gidが0の場合はタイルなし
                if gid:
                    # タイルを取得して描画
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        target_surface.blit(tile, (x * self.tile_width, y * self.tile_height))
        
        # 背景と前景のスケーリングしたサーフェスを作成
        self.scaled_background = pygame.transform.scale(
            self.background_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_foreground = pygame.transform.scale(
            self.foreground_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
    def draw(self, screen, center_x, center_y):
        """プレイヤーを中心にマップを描画"""
        # 画面の中心位置
        screen_center_x = GameConfig.WIDTH // 2
        screen_center_y = GameConfig.HEIGHT // 2
        
        # 描画位置を計算（プレイヤーを中心に）
        x_offset = screen_center_x - center_x
        y_offset = screen_center_y - center_y
        
        # マップが小さい場合は中央に配置
        if self.scaled_map_width < GameConfig.WIDTH:
            x_offset = (GameConfig.WIDTH - self.scaled_map_width) // 2
        else:
            # マップが画面より大きい場合、端の処理を行う
            # 左端の制限（マップの左端が画面の右にはみ出さないように）
            x_offset = min(0, x_offset)
            
            # 右端の制限（マップの右端が画面の左にはみ出さないように）
            if self.scaled_map_width + x_offset < GameConfig.WIDTH:
                x_offset = GameConfig.WIDTH - self.scaled_map_width
        
        # 縦方向も同様に処理
        if self.scaled_map_height < GameConfig.HEIGHT:
            y_offset = (GameConfig.HEIGHT - self.scaled_map_height) // 2
        else:
            # 上端の制限
            y_offset = min(0, y_offset)
            
            # 下端の制限
            if self.scaled_map_height + y_offset < GameConfig.HEIGHT:
                y_offset = GameConfig.HEIGHT - self.scaled_map_height
        
        # 背景レイヤーを描画
        screen.blit(self.scaled_background, (x_offset, y_offset))
        
        # オフセット値を返す（プレイヤー描画位置の計算に使用）
        # これはプレイヤー描画後に、前景レイヤーを描画するための情報として使用
        return x_offset, y_offset
    
    def draw_foreground(self, screen, offset_x, offset_y):
        """前景レイヤー（rockなど）を描画"""
        # 前景レイヤー（障害物など）を後から描画
        screen.blit(self.scaled_foreground, (offset_x, offset_y))
        
    def get_object_layer(self, name):
        """指定した名前のオブジェクトレイヤーを取得"""
        if hasattr(self.tmx_data, 'get_layer_by_name'):
            return self.tmx_data.get_layer_by_name(name)
        return None
    
    def is_walkable(self, x, y):
        """指定した座標が歩行可能かどうかを判定"""
        # タイル座標に変換
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        # マップ範囲外なら歩行不可
        if tile_x < 0 or tile_x >= self.tmx_data.width or tile_y < 0 or tile_y >= self.tmx_data.height:
            return False
        
        # GameConfigで定義された歩行可能なタイルIDのリストを使用
        walkable_tile_ids = GameConfig.WALKABLE_TILE_IDS
        
        # 最初に障害物レイヤーをチェック（rock, collision, obstaclesレイヤー）
        for layer_name in ['rock', 'collision', 'obstacles']:
            try:
                layer = self.tmx_data.get_layer_by_name(layer_name)
                if layer and hasattr(layer, 'data'):
                    gid = layer.data[tile_y][tile_x]
                    # このレイヤーにタイルがあって、歩行可能でなければ歩行不可
                    if gid > 0:
                        return False  # 障害物レイヤーに何かあれば歩行不可
            except (ValueError, AttributeError, KeyError):
                # レイヤーが存在しない場合は無視
                pass
        
        # 背景レイヤーをチェック（backgroundレイヤー）
        try:
            background_layer = self.tmx_data.get_layer_by_name('background')
            if background_layer and hasattr(background_layer, 'data'):
                gid = background_layer.data[tile_y][tile_x]
                # タイルがある場合
                if gid > 0:
                    # GIDがそのままタイルID（TMXファイル内の値）
                    if gid in walkable_tile_ids:
                        return True  # 歩行可能なタイルIDなら通過可能
        except (ValueError, AttributeError, KeyError):
            # backgroundレイヤーが存在しない場合は無視
            pass
                        
        # デフォルトは歩行可能（障害物が無く、特定の制限もない場合）
        return True

# フィールドを描画
def draw_field(player, tmx_map):
    # マップを描画し、描画時のオフセットを取得
    offset_x, offset_y = tmx_map.draw(screen, player.x + player.width // 2, player.y + player.height // 2)
    # オフセットを返す（プレイヤー描画時に使用）
    return offset_x, offset_y

# HPバーを描画する関数
def draw_hp_bar(x, y, pokemon, is_player=False):
    # 共通の設定
    hp_image = load_image(GameConfig.HP_BAR_IMG)
    hp_unit_height = 4 * GameConfig.SCALE
    hp_unit_width = 40 * GameConfig.SCALE
    hp_image_scaled = pygame.transform.scale(hp_image, (hp_unit_width, hp_unit_height))
    
    # HPの計算
    hp_inner_width = (40 - 1.5) * GameConfig.SCALE
    hp_ratio = max(0, pokemon.display_hp / pokemon.max_hp)
    
    # HPバーを描画
    if hp_ratio > 0:
        hp_bar_width = int(hp_inner_width * hp_ratio)
        
        # HP残量に応じて色を変える
        if hp_ratio > 0.5:
            bar_color = GameConfig.GREEN
        elif hp_ratio > 0.2:
            bar_color = GameConfig.YELLOW
        else:
            bar_color = GameConfig.RED

        bar_y_offset = 2 if is_player else 3
        pygame.draw.rect(screen, bar_color, (x + GameConfig.SCALE * 2, y + bar_y_offset * GameConfig.SCALE, hp_bar_width, hp_unit_height))
    
    screen.blit(hp_image_scaled, (x + GameConfig.SCALE, y + (2 if is_player else 3) * GameConfig.SCALE))
    
    return hp_ratio

# 野生ポケモンの情報を描画
def draw_wild_pokemon_info(wild_pokemon):
    # 配置座標
    info_x = 5 * GameConfig.SCALE
    info_y = 5 * GameConfig.SCALE

    info_width = 80 * GameConfig.SCALE
    # 情報フレーム画像を表示
    enemy_info_frame = load_image(GameConfig.ENEMY_FRAME_IMG, (info_width, 25 * GameConfig.SCALE))
    screen.blit(enemy_info_frame, (info_x - 2 * GameConfig.SCALE, info_y))
    
    # ポケモン名を表示
    font = get_font(15)
    info_pokemon_name_x = 11 * GameConfig.SCALE
    info_pokemon_name_y = 9 * GameConfig.SCALE
    text = font.render(f"{wild_pokemon.pokemon.name} Lv.5", True, GameConfig.BLACK)
    screen.blit(text, (info_pokemon_name_x, info_pokemon_name_y))
    
    # HPラベルを表示（太字）
    font_hp_label = get_font(12, font_weight='W8')
    hp_label_text = "HP:"
    hp_label = font_hp_label.render(hp_label_text, True, GameConfig.BLACK)
    
    # HPバーを描画
    hp_back_x = 10 * GameConfig.SCALE
    hp_back_y = info_pokemon_name_y + 18
    screen.blit(hp_label, (hp_back_x - 5, hp_back_y + 3))
    draw_hp_bar(hp_back_x + hp_label.get_width() + 3, hp_back_y, wild_pokemon.pokemon, False)
    
    # ポケモン画像を描画
    image = pygame.transform.scale(wild_pokemon.image, (50 * GameConfig.SCALE, 50 * GameConfig.SCALE))
    screen.blit(image, (90 * GameConfig.SCALE, -10))

# プレイヤーのポケモン情報を描画
def draw_player_pokemon_info(player, info_width):
    # 配置座標
    player_info_x = 85 * GameConfig.SCALE
    player_info_y = 65 * GameConfig.SCALE
    
    # 情報フレーム画像を表示
    my_info_frame = load_image(GameConfig.MY_FRAME_IMG, (info_width + 5 * GameConfig.SCALE, 25 * GameConfig.SCALE))
    screen.blit(my_info_frame, (player_info_x - 2 * GameConfig.SCALE, player_info_y))
    
    # ポケモン名を表示
    font = get_font(15)
    player_hp_text_x = 90 * GameConfig.SCALE
    text = font.render(f"{player.pokemon[0].name} Lv.5", True, GameConfig.BLACK)
    screen.blit(text, (player_hp_text_x + 30, player_info_y + 3 * GameConfig.SCALE))
    
    # HPラベルを表示（太字）
    font_hp_label = get_font(12, font_weight='W8')
    hp_label_text = "HP:"
    hp_label = font_hp_label.render(hp_label_text, True, GameConfig.BLACK)
    
    # HPバーを描画
    hp_bar_x = player_hp_text_x  # 名前と同じX座標を使用
    hp_bar_y = player_info_y + 25
    screen.blit(hp_label, (hp_bar_x - 5, hp_bar_y + 2))
    draw_hp_bar(hp_bar_x + hp_label.get_width() + 3, hp_bar_y, player.pokemon[0], True)
    
    # HP数値表示（太字）
    font_hp = get_font(15)
    hp_text_p = f"{int(player.pokemon[0].display_hp)}/{player.pokemon[0].max_hp}"
    text_hp_p = font_hp.render(hp_text_p, True, GameConfig.BLACK)
    # テキストの幅を取得してHP数値を中央に配置
    text_width = text_hp_p.get_width()
    hp_bar_width = 40 * GameConfig.SCALE
    hp_bar_x_adjusted = hp_bar_x + hp_label.get_width() + 3
    centered_x = hp_bar_x_adjusted + (hp_bar_width - text_width) // 2
    screen.blit(text_hp_p, (centered_x, hp_bar_y + 21))
    
    # プレイヤーのポケモン画像を描画
    hitokage_image = load_image(GameConfig.HITOKAGE_IMG, (40 * GameConfig.SCALE, 40 * GameConfig.SCALE))
    screen.blit(hitokage_image, (20 * GameConfig.SCALE, 56 * GameConfig.SCALE))

# コマンド選択画面を描画
def draw_command_selection(state):
    # message_halfを使ってコマンド選択画面を表示
    message_image = load_image(GameConfig.MESSAGE_HALF_IMG, (GameConfig.WIDTH, 49 * GameConfig.SCALE))
    screen.blit(message_image, (0, GameConfig.HEIGHT - 49 * GameConfig.SCALE))
    
    commands = ["たたかう", "どうぐ", "ポケモン", "にげる"]
    font_commands = get_font(14)
    
    # 2x2のグリッドでコマンドを右半分に配置
    for i, command in enumerate(commands):
        # 右側画面の左半分のコマンド（たたかう、ポケモン）
        if i % 2 == 0:
            x = GameConfig.WIDTH // 2 + 10 * GameConfig.SCALE
        # 右側画面の右半分のコマンド（どうぐ、にげる）
        else:
            x = GameConfig.WIDTH // 2 + GameConfig.WIDTH // 4 + 5 * GameConfig.SCALE
            
        # 上段のコマンド（たたかう、どうぐ）
        if i < 2:
            y = GameConfig.HEIGHT - 49 * GameConfig.SCALE + 10 * GameConfig.SCALE
        # 下段のコマンド（ポケモン、にげる）
        else:
            y = GameConfig.HEIGHT - 49 * GameConfig.SCALE + 30 * GameConfig.SCALE
            
        # 現在選択されているコマンドには▶︎を表示
        if i == state.selected_command:
            mark = font_commands.render("▶︎", True, GameConfig.BLACK)
            screen.blit(mark, (x - 7 * GameConfig.SCALE, y))
            
        text = font_commands.render(command, True, GameConfig.BLACK)
        screen.blit(text, (x, y))

# バトルメッセージを描画
def draw_battle_message(state):
    if state.battle_state == GameState.BATTLE_MESSAGE or state.battle_state == GameState.BATTLE_ANIMATION:
        message_image = load_image(GameConfig.MESSAGE_ALL_IMG, (GameConfig.WIDTH, 49 * GameConfig.SCALE))
        screen.blit(message_image, (0, GameConfig.HEIGHT - 49 * GameConfig.SCALE))
        font_message = get_font(14)
        
        # 1文字ずつ表示する処理
        current_time = pygame.time.get_ticks()
        # 文字表示タイマーが設定されていない場合は初期化
        if state.char_display_timer == 0:
            state.char_display_timer = current_time
            state.displayed_chars = 0
            state.full_message_displayed = False
        
        # アニメーション中はテキストをすぐに全て表示
        if state.battle_state == GameState.BATTLE_ANIMATION:
            displayed_text = state.battle_message
            state.displayed_chars = len(state.battle_message)
            state.full_message_displayed = True
        else:
            # 一定時間ごとに表示する文字数を増やす
            if not state.full_message_displayed and current_time - state.char_display_timer > GameConfig.MESSAGE_DISPLAY_SPEED:
                state.displayed_chars += 1
                state.char_display_timer = current_time
                
                # 全ての文字を表示したかチェック
                if state.displayed_chars >= len(state.battle_message):
                    state.displayed_chars = len(state.battle_message)
                    state.full_message_displayed = True
            
            # 現在表示すべき文字列を取得
            displayed_text = state.battle_message[:state.displayed_chars]
        
        text = font_message.render(displayed_text, True, GameConfig.BLACK)
        screen.blit(text, (10 * GameConfig.SCALE, GameConfig.HEIGHT - 49 * GameConfig.SCALE + 10 * GameConfig.SCALE))
    elif state.battle_state == GameState.BATTLE_COMMAND:
        draw_command_selection(state)
    elif state.battle_state == GameState.BATTLE_SELECT:
        draw_move_selection(state)

# 技選択画面を描画
def draw_move_selection(state):
    # 共通サイズの設定
    message_width = GameConfig.WIDTH // 2
    message_height = 70 * GameConfig.SCALE
    
    # message_half_middleを使用して左下に配置
    left_message_image = load_image(GameConfig.MESSAGE_HALF_MIDDLE_IMG, (message_width, message_height))
    screen.blit(left_message_image, (0, GameConfig.HEIGHT - message_height))
    
    # message_half_separateを使用して右下に配置
    right_message_image = load_image(GameConfig.MESSAGE_HALF_SEPARATE_IMG, (88 * GameConfig.SCALE, 48 * GameConfig.SCALE))
    screen.blit(right_message_image, (72 * GameConfig.SCALE, GameConfig.HEIGHT - 48 * GameConfig.SCALE))
    
    font_moves = get_font(14)
    
    for i, move in enumerate(state.player.pokemon[0].moves):
        # マークとテキストの位置を計算（左側に表示）
        mark_x = 10 * GameConfig.SCALE
        text_x = 17 * GameConfig.SCALE
        text_y = GameConfig.HEIGHT - message_height + 10 * GameConfig.SCALE + i * 10 * GameConfig.SCALE
        
        # 選択中の技には▶︎マークを表示
        if i == state.selected_move:
            mark = font_moves.render("▶︎", True, GameConfig.BLACK)
            screen.blit(mark, (mark_x, text_y))
            
        # 技名を表示
        text = font_moves.render(move, True, GameConfig.BLACK)
        screen.blit(text, (text_x, text_y))
    
    # 右側メッセージボックスに選択した技の詳細情報を表示
    if len(state.player.pokemon[0].moves) > 0:
        # 選択中の技のタイプとPPを表示
        sel_move_idx = state.selected_move
        move_type = state.player.pokemon[0].move_types[sel_move_idx]
        current_pp = state.player.pokemon[0].move_pp[sel_move_idx][0]
        max_pp = state.player.pokemon[0].move_pp[sel_move_idx][1]
        
        # わざタイプを表示 - 中央に配置
        type_text = font_moves.render(f"わざタイプ / {move_type}", True, GameConfig.BLACK)
        type_text_width = type_text.get_width()
        # 右側メッセージボックスの中心を計算（右側の表示エリアの中央に）
        right_box_center_x = 72 * GameConfig.SCALE + (88 * GameConfig.SCALE) // 2
        # テキストの位置を中央揃えに
        type_text_x = right_box_center_x - type_text_width // 2
        screen.blit(type_text, (type_text_x, GameConfig.HEIGHT - 22 * GameConfig.SCALE))
        
        # PPを表示 - 中央に配置
        pp_text = font_moves.render(f"PP {current_pp}/{max_pp}", True, GameConfig.BLACK)
        pp_text_width = pp_text.get_width()
        pp_text_x = right_box_center_x - pp_text_width // 2
        screen.blit(pp_text, (pp_text_x, GameConfig.HEIGHT - 32 * GameConfig.SCALE))

# 炎アニメーションを描画する関数
def draw_fire_animation(state, wild_pokemon):
    """炎のアニメーション描画関数"""
    current_time = pygame.time.get_ticks()
    
    # アニメーション開始からの経過時間
    elapsed_time = current_time - state.animation_start_time
    
    # アニメーション表示時間を超えていたらアニメーション終了
    if elapsed_time > GameConfig.SKILL_ANIMATION_DURATION:
        # メッセージ表示状態に切り替え
        state.battle_state = GameState.BATTLE_MESSAGE
        state.battle_timer = current_time
        return
    
    # アニメーションフレームの更新
    if current_time - state.animation_timer > GameConfig.FIRE_ANIMATION_SPEED:
        # 同じ位置で大小切り替え、または次の位置へ移動
        if state.use_big_fire:  # 大きい炎を表示中なら
            # 次の位置へ移動
            state.animation_frame = (state.animation_frame + 1) % 3  # 3点移動（左→右→中央）
            state.use_big_fire = False  # 小さい炎から開始
        else:
            # 同じ位置で大きい炎に切り替え
            state.use_big_fire = True
            
        state.animation_timer = current_time
    
    # 敵ポケモンの実際の表示位置を基準に3点移動位置を計算
    # ポケモン画像の表示位置（draw_wild_pokemon_info関数と同じ座標を使用）
    enemy_pos_x = 90 * GameConfig.SCALE  # ポケモン画像のX座標
    enemy_width = 50 * GameConfig.SCALE  # ポケモン画像の幅
    enemy_height = 50 * GameConfig.SCALE  # ポケモン画像の高さ
    
    # 敵ポケモンの中心位置
    enemy_center_x = enemy_pos_x + enemy_width / 2
    
    # アニメーションポイント（同じ高さでの3点移動）
    if not state.animation_pos:
        # 初期化（最初の呼び出し時のみ）
        # 敵ポケモンの中心Yより少し上の位置を炎の高さとする
        fire_height = enemy_height
        # 移動順序を設定: 左側→右側→中央
        offsets = [
            (-20, 0),  # 左側
            (20, 0),   # 右側
            (0, 0)     # 中央
        ]
        for off_x, off_y in offsets:
            pos_x = enemy_center_x + off_x * GameConfig.SCALE
            pos_y = fire_height
            state.animation_pos.append((pos_x, pos_y))
    
    # 現在のフレームの位置を取得
    current_pos = state.animation_pos[state.animation_frame]
    
    # 炎の画像を描画
    fire_img_path = GameConfig.FIRE_BIG_IMG if state.use_big_fire else GameConfig.FIRE_SMALL_IMG
    fire_size = (16 * GameConfig.SCALE) if state.use_big_fire else (16 * GameConfig.SCALE)
    fire_img = load_image(fire_img_path, (fire_size, fire_size))
    
    # 炎画像を描画
    screen.blit(fire_img, (current_pos[0] - fire_size//2, current_pos[1] - fire_size//2))

# バトル画面を描画するメイン関数
def draw_battle_screen(player, wild_pokemon, state):
    # バトル背景
    screen.fill(GameConfig.WHITE)
    
    # 共通で使う値
    info_width = 60 * GameConfig.SCALE
    
    # 各要素を描画する
    draw_wild_pokemon_info(wild_pokemon)
    draw_player_pokemon_info(player, info_width)
    
    # stateにplayerを一時的に格納（技選択画面描画で使用）
    state.player = player
    
    # メッセージ枠は常に表示
    draw_battle_message(state)
    
    # アニメーション状態なら炎アニメーションも描画
    if state.battle_state == GameState.BATTLE_ANIMATION:
        draw_fire_animation(state, wild_pokemon)

# デバッグ情報を描画する関数
def draw_debug_info(screen, player, tmx_map):
    """デバッグ情報を描画する関数"""
    # プレイヤーの位置を取得
    player_pos_x = player.x + player.width/2
    player_pos_y = player.y + player.height/2
    
    # プレイヤーの位置のタイルIDを取得
    tile_ids = tmx_map.get_tile_id_at(player_pos_x, player_pos_y)
    
    # デバッグ情報を描画
    font = get_font(10)
    y_offset = 10
    
    # 座標情報
    pos_text = f"座標: ({int(player_pos_x)}, {int(player_pos_y)})"
    text_surface = font.render(pos_text, True, GameConfig.WHITE)
    screen.blit(text_surface, (10, y_offset))
    y_offset += 20
    
    # タイルID情報
    for layer_name, tile_info in tile_ids.items():
        if isinstance(tile_info, dict):
            # 詳細情報がある場合
            gid = tile_info.get('gid', 'N/A')
            raw_gid = tile_info.get('raw_gid', 'N/A')
            tileset = tile_info.get('tileset', 'N/A')
            local_id = tile_info.get('local_id', 'N/A')
            
            # レイヤー情報を表示
            layer_text = f"{layer_name}: GID={gid}, 純粋GID={raw_gid}"
            text_surface = font.render(layer_text, True, GameConfig.WHITE)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 15
            
            # タイルセット情報を表示
            tileset_text = f"  タイルセット={tileset}, ローカルID={local_id}"
            text_surface = font.render(tileset_text, True, GameConfig.WHITE)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20
        else:
            # 従来のシンプル表示（エラーなどの場合）
            id_text = f"{layer_name}: タイルID = {tile_info}"
            text_surface = font.render(id_text, True, GameConfig.WHITE)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20

# メイン関数
def main():
    player = Player()
    game_state = GameState()
    steps_since_last_encounter = 0
    
    # TMXマップを読み込む
    tmx_map = TiledMap(GameConfig.MAP_FILE)
    
    # バトル時のダメージメッセージを生成
    def format_damage_message(pokemon_name, move_name, damage):
        return f"{pokemon_name}の{move_name}!"
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state.state == GameState.BATTLE:
                # コマンド選択中
                if game_state.battle_state == GameState.BATTLE_COMMAND and game_state.player_turn:
                    if event.type == pygame.KEYDOWN:
                        # 横方向の移動（左右）
                        if event.key == pygame.K_LEFT:
                            if game_state.selected_command % 2 == 1:  # 右側から左側へ
                                game_state.selected_command -= 1
                        elif event.key == pygame.K_RIGHT:
                            if game_state.selected_command % 2 == 0:  # 左側から右側へ
                                game_state.selected_command += 1
                        # 縦方向の移動（上下）
                        elif event.key == pygame.K_UP:
                            if game_state.selected_command >= 2:  # 下段から上段へ
                                game_state.selected_command -= 2
                        elif event.key == pygame.K_DOWN:
                            if game_state.selected_command < 2:  # 上段から下段へ
                                game_state.selected_command += 2
                        # 決定（Enterキー）
                        elif event.key == pygame.K_RETURN:
                            if game_state.selected_command == 0:  # 「たたかう」選択時
                                game_state.battle_state = GameState.BATTLE_SELECT
                            elif game_state.selected_command == 3:  # 「にげる」選択時
                                # バトルから逃げるメッセージを表示して、フィールドに戻る
                                game_state.battle_message = "うまく にげきれた！"
                                game_state.battle_state = GameState.BATTLE_MESSAGE
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                game_state.battle_end_flag = True
                
                # 技選択中
                elif game_state.battle_state == GameState.BATTLE_SELECT and game_state.player_turn:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and game_state.selected_move > 0:
                            game_state.selected_move -= 1
                        elif event.key == pygame.K_DOWN and game_state.selected_move < len(player.pokemon[0].moves) - 1:
                            game_state.selected_move += 1
                        elif event.key == pygame.K_ESCAPE:  # ESCキーでコマンド選択に戻る
                            game_state.battle_state = GameState.BATTLE_COMMAND
                        elif event.key == pygame.K_RETURN:
                            # 技を使用（ダメージは後で適用）
                            move_index = game_state.selected_move
                            move_name = player.pokemon[0].moves[move_index]
                            damage = player.pokemon[0].damages[move_index]
                            
                            # PPがあるか確認
                            if player.pokemon[0].move_pp[move_index][0] > 0:
                                # PPを1減らす
                                player.pokemon[0].move_pp[move_index][0] -= 1
                                
                                # ダメージ情報を保存
                                game_state.pending_damage = damage
                                game_state.damage_target = "enemy"
                                # メッセージを設定
                                game_state.battle_message = format_damage_message(player.pokemon[0].name, move_name, damage)
                                
                                # 「ひのこ」の場合はアニメーション表示
                                if move_name == "ひのこ" and player.pokemon[0].name == "ヒトカゲ":
                                    # アニメーション状態に切り替え
                                    game_state.battle_state = GameState.BATTLE_ANIMATION
                                    game_state.current_move_name = move_name
                                    game_state.animation_start_time = pygame.time.get_ticks()
                                    game_state.animation_timer = pygame.time.get_ticks()
                                    game_state.animation_frame = 0
                                    game_state.animation_pos = []  # 位置はdraw_fire_animation内で初期化
                                    game_state.use_big_fire = False
                                else:
                                    # 通常の技はメッセージ表示
                                    game_state.battle_state = GameState.BATTLE_MESSAGE
                                
                                game_state.player_turn = False
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                            else:
                                # PPが足りない場合のメッセージ
                                game_state.battle_message = f"{move_name}のPPが足りない！"
                                game_state.battle_state = GameState.BATTLE_MESSAGE
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                # プレイヤーのターンは続行
                                game_state.pending_damage = 0

        # ゲームロジック
        if game_state.state == GameState.FIELD:
            keys = pygame.key.get_pressed()
            old_x, old_y = player.x, player.y
            player.move(keys, tmx_map)
            
            # 移動したかチェック
            if old_x != player.x or old_y != player.y:
                steps_since_last_encounter += 1
                
                # 草むらの中にいるかチェック
                # if player.y > GameConfig.HEIGHT // 2:
                #     # ランダムエンカウント
                #     if steps_since_last_encounter > GameConfig.STEPS_BEFORE_ENCOUNTER and random.random() < GameConfig.ENCOUNTER_RATE:
                #         game_state.state = GameState.BATTLE
                #         game_state.wild_pokemon = WildPokemon()
                #         game_state.battle_message = f"野生の{game_state.wild_pokemon.pokemon.name}が現れた！"
                #         game_state.player_turn = True
                #         game_state.battle_state = GameState.BATTLE_MESSAGE
                #         steps_since_last_encounter = 0
                #         # 文字表示をリセット
                #         game_state.displayed_chars = 0
                #         game_state.char_display_timer = 0
                #         game_state.full_message_displayed = False
                #         # バトル開始メッセージ表示用にタイマーをセット
                #         game_state.battle_timer = pygame.time.get_ticks()
                        
        elif game_state.state == GameState.BATTLE:
            # メッセージ自動送り処理
            if game_state.battle_state == GameState.BATTLE_MESSAGE:
                # メッセージが全部表示された場合のみタイマー処理を行う
                if game_state.full_message_displayed:
                    # メッセージが完全に表示されたら、保存しておいたダメージを適用
                    if game_state.pending_damage > 0:
                        if game_state.damage_target == "enemy":
                            game_state.wild_pokemon.pokemon.hp -= game_state.pending_damage
                            game_state.wild_pokemon.pokemon.hp = max(0, game_state.wild_pokemon.pokemon.hp)
                        elif game_state.damage_target == "player":
                            player.pokemon[0].hp -= game_state.pending_damage
                            player.pokemon[0].hp = max(0, player.pokemon[0].hp)
                            # プレイヤーのポケモンが倒れたかチェック
                            if player.pokemon[0].hp <= 0:
                                player.pokemon[0].hp = 0
                                game_state.battle_message = f"{player.pokemon[0].name}は倒れた！"
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                # 数秒後にフィールドに戻るフラグを立てる
                                game_state.battle_end_flag = True
                                # ダメージをリセット
                                game_state.pending_damage = 0
                        # 一度だけ適用するようにリセット
                        game_state.pending_damage = 0
                        
                    # バトル終了フラグがセットされていない場合のみ次の処理へ
                    if game_state.battle_end_flag:
                        # 終了フラグがセットされていれば何もしない（「倒れた！」メッセージを表示したまま）
                        pass
                    elif pygame.time.get_ticks() - game_state.battle_timer > GameConfig.MESSAGE_WAIT_TIME:
                        if game_state.player_turn:
                            game_state.battle_state = GameState.BATTLE_COMMAND
                        else:
                            # 敵のターン処理
                            if game_state.wild_pokemon.pokemon.hp <= 0:
                                game_state.battle_message = f"野生の{game_state.wild_pokemon.pokemon.name}を倒した！"
                                game_state.battle_timer = pygame.time.get_ticks()  # タイマーをリセット
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                # 数秒後にフィールドに戻るフラグを立てる
                                game_state.battle_end_flag = True
                            else:
                                # PPが残っている技をランダムに選ぶ
                                available_moves = []
                                for i, move in enumerate(game_state.wild_pokemon.pokemon.moves):
                                    if game_state.wild_pokemon.pokemon.move_pp[i][0] > 0:
                                        available_moves.append(i)
                                
                                # 使える技がある場合
                                if available_moves:
                                    enemy_move_index = random.choice(available_moves)
                                    enemy_move = game_state.wild_pokemon.pokemon.moves[enemy_move_index]
                                    enemy_damage = game_state.wild_pokemon.pokemon.damages[enemy_move_index]
                                    
                                    # PPを消費
                                    game_state.wild_pokemon.pokemon.move_pp[enemy_move_index][0] -= 1
                                    
                                    # ダメージ情報を保存
                                    game_state.pending_damage = enemy_damage
                                    game_state.damage_target = "player"
                                    # メッセージを設定
                                    game_state.battle_message = format_damage_message(
                                        f"野生の{game_state.wild_pokemon.pokemon.name}", enemy_move, enemy_damage)
                                
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                
                                # プレイヤーのターンに戻す
                                game_state.player_turn = True

            # バトル終了処理
            if game_state.battle_end_flag and pygame.time.get_ticks() - game_state.battle_timer > GameConfig.BATTLE_END_WAIT_TIME:
                # 倒れたのがプレイヤーのポケモンなら回復させる
                if player.pokemon[0].hp <= 0:
                    player.pokemon[0].hp = player.pokemon[0].max_hp
                    player.pokemon[0].display_hp = player.pokemon[0].max_hp  # 回復時はdisplay_hpも同期
                game_state.state = GameState.FIELD
                game_state.battle_end_flag = False
        
        # HPアニメーション更新
        if game_state.state == GameState.BATTLE:
            # プレイヤーポケモンのHP
            if player.pokemon[0].display_hp > player.pokemon[0].hp:
                # 現在のHPとの差に比例した減少速度（差が大きいほど速く減少）
                hp_diff = player.pokemon[0].display_hp - player.pokemon[0].hp
                decrease_amount = max(hp_diff * 0.05, GameConfig.HP_ANIMATION_SPEED)
                player.pokemon[0].display_hp -= decrease_amount
                # 減りすぎないようにチェック
                if player.pokemon[0].display_hp < player.pokemon[0].hp:
                    player.pokemon[0].display_hp = player.pokemon[0].hp
            
            # 敵ポケモンのHP
            if game_state.wild_pokemon and game_state.wild_pokemon.pokemon.display_hp > game_state.wild_pokemon.pokemon.hp:
                # 現在のHPとの差に比例した減少速度
                hp_diff = game_state.wild_pokemon.pokemon.display_hp - game_state.wild_pokemon.pokemon.hp
                decrease_amount = max(hp_diff * 0.05, GameConfig.HP_ANIMATION_SPEED)
                game_state.wild_pokemon.pokemon.display_hp -= decrease_amount
                if game_state.wild_pokemon.pokemon.display_hp < game_state.wild_pokemon.pokemon.hp:
                    game_state.wild_pokemon.pokemon.display_hp = game_state.wild_pokemon.pokemon.hp
        
        # 描画
        screen.fill(GameConfig.SKY_BLUE)  # 空色の背景
        
        if game_state.state == GameState.FIELD:
            # 背景マップを描画し、オフセットを取得
            map_offset_x, map_offset_y = draw_field(player, tmx_map)
            # 前景レイヤー（rock等）を描画
            tmx_map.draw_foreground(screen, map_offset_x, map_offset_y)
            # プレイヤーを最後に描画（プレイヤーが最前面になる）
            player.draw(map_offset_x, map_offset_y)
        elif game_state.state == GameState.BATTLE:
            draw_battle_screen(player, game_state.wild_pokemon, game_state)
        
        # デバッグ情報の描画（特定のキーが押されたときのみ）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f]:  # Fキーでデバッグ情報を表示
            draw_debug_info(screen, player, tmx_map)
        
        pygame.display.flip()
        clock.tick(GameConfig.FPS)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
