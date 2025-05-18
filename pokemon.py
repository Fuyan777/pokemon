import pygame
import sys
import random
import time
import os

# 初期化
pygame.init()
SCALE = 3  # スケール倍率
WIDTH, HEIGHT = 160 * SCALE, 144 * SCALE  # 3倍スケールに変更
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ポケモン風ゲーム")
clock = pygame.time.Clock()

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 220, 220)  # 薄いグレー追加
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# 日本語フォントを設定（伸ばし棒対応版）
def get_font(size):
    # macOSの場合はフォントパスを直接指定する方法を試す
    if sys.platform == 'darwin':  # macOS
        try:
            # まず、macOSの標準的な日本語フォントパスを直接試す
            font_paths = [
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',  # Catalina以降
                '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc',
                '/System/Library/Fonts/Hiragino Sans GB.ttc',
                '/System/Library/Fonts/AppleGothic.ttf',
                '/Library/Fonts/Osaka.ttf'
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
        default_font.render(test_text, True, BLACK)
        return default_font
    except:
        # 最終手段
        return pygame.font.SysFont(None, size)

# プレイヤークラス
class Player:
    def __init__(self):
        self.x = 80 * SCALE  # 画面中央あたりに調整
        self.y = 70 * SCALE
        self.speed = 3 * SCALE  # 移動速度もスケールに合わせる
        self.width = 20 * SCALE  # サイズをスケールに合わせる
        self.height = 20 * SCALE
        self.direction = "down"
        self.pokemon = [Pokemon("ヒトカゲ", "火", 20, ["ひのこ", "ひっかく"], [10, 5])]
        # プレイヤー画像を読み込む
        try:
            self.image = pygame.image.load("img/red_front.png")
            # 画像サイズを調整
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            # 画像が読み込めない場合はNoneを設定
            self.image = None
            print("プレイヤー画像の読み込みに失敗しました")

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
            
        # 画面外に出ないようにする
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))

    def draw(self):
        if self.image:
            # 画像があれば描画
            screen.blit(self.image, (self.x, self.y))
            
            # 向きを表示（オプション）
            if self.direction == "up":
                pygame.draw.polygon(screen, RED, [(self.x + 20, self.y - 10), (self.x + 10, self.y), (self.x + 30, self.y)])
            elif self.direction == "down":
                pygame.draw.polygon(screen, RED, [(self.x + 20, self.y + self.height + 10), (self.x + 10, self.y + self.height), (self.x + 30, self.y + self.height)])
            elif self.direction == "left":
                pygame.draw.polygon(screen, RED, [(self.x - 10, self.y + 20), (self.x, self.y + 10), (self.x, self.y + 30)])
            elif self.direction == "right":
                pygame.draw.polygon(screen, RED, [(self.x + self.width + 10, self.y + 20), (self.x + self.width, self.y + 10), (self.x + self.width, self.y + 30)])
        else:
            # 画像がなければ元の四角形で表示
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
            # 向きを示す三角形を描画
            if self.direction == "up":
                pygame.draw.polygon(screen, WHITE, [(self.x + 20, self.y - 10), (self.x + 10, self.y), (self.x + 30, self.y)])
            elif self.direction == "down":
                pygame.draw.polygon(screen, WHITE, [(self.x + 20, self.y + self.height + 10), (self.x + 10, self.y + self.height), (self.x + 30, self.y + self.height)])
            elif self.direction == "left":
                pygame.draw.polygon(screen, WHITE, [(self.x - 10, self.y + 20), (self.x, self.y + 10), (self.x, self.y + 30)])
            elif self.direction == "right":
                pygame.draw.polygon(screen, WHITE, [(self.x + self.width + 10, self.y + 20), (self.x + self.width, self.y + 10), (self.x + self.width, self.y + 30)])

# ポケモンクラス
class Pokemon:
    def __init__(self, name, type, hp, moves, damages):
        self.name = name
        self.type = type
        self.max_hp = hp
        self.hp = hp
        self.moves = moves
        self.damages = damages

# 野生のポケモンクラス
class WildPokemon:
    def __init__(self):
        pokemon_options = [
            ("ゼニガメ", "水", 18, ["みずでっぽう", "たいあたり"], [9, 5]),
            ("フシギダネ", "草", 19, ["はっぱカッター", "たいあたり"], [8, 5]),
            ("ピカチュウ", "電気", 15, ["でんきショック", "たいあたり"], [12, 5]),
            ("イーブイ", "ノーマル", 17, ["たいあたり", "すなかけ"], [7, 3])
        ]
        choice = random.choice(pokemon_options)
        self.pokemon = Pokemon(choice[0], choice[1], choice[2], choice[3], choice[4])
        
        # ポケモンの画像を読み込む
        try:
            if self.pokemon.name == "ゼニガメ":
                self.image = pygame.image.load("img/zenigame.png")
            elif self.pokemon.name == "ピカチュウ":
                self.image = pygame.image.load("img/pikachu.png")
            elif self.pokemon.name == "フシギダネ":
                self.image = pygame.image.load("img/hushigidane.png")
            elif self.pokemon.name == "イーブイ":
                self.image = pygame.image.load("img/eevee.png")
            else:
                # その他のポケモンの場合、デフォルト画像を使用するか、他の画像を用意する
                self.image = None
            
            # 画像がある場合はサイズを調整
            if self.image:
                self.image = pygame.transform.scale(self.image, (120, 120))
        except pygame.error:
            self.image = None
            print(f"{self.pokemon.name}の画像の読み込みに失敗しました")

# ゲームステートクラス
class GameState:
    FIELD = 0
    BATTLE = 1
    BATTLE_SELECT = 0  # 技選択中
    BATTLE_MESSAGE = 1  # メッセージ表示中

    def __init__(self):
        self.state = self.FIELD
        self.battle_timer = 0
        self.wild_pokemon = None
        self.battle_message = ""
        self.player_turn = True
        self.selected_move = 0
        self.battle_state = self.BATTLE_SELECT  # 追加
        self.battle_end_flag = False  # 追加
        # テキスト表示用の変数
        self.displayed_chars = 0  # 現在表示している文字数
        self.char_display_timer = 0  # 文字表示用タイマー
        self.full_message_displayed = False  # メッセージがすべて表示されたかどうか

# フィールドを描画
def draw_field():
    # 草むらエリアを描画（下半分）
    pygame.draw.rect(screen, GREEN, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    
    # 道を描画
    pygame.draw.rect(screen, (210, 180, 140), (WIDTH // 4, 0, WIDTH // 2, HEIGHT))

def draw_battle_screen(player, wild_pokemon, state):
    # バトル背景
    screen.fill(WHITE)

    # 野生のポケモン情報（左上）
    info_width = 60 * SCALE
    pygame.draw.rect(screen, LIGHT_GRAY, (5 * SCALE, 5 * SCALE, info_width, 25 * SCALE))
    font = get_font(15)
    text = font.render(f"{wild_pokemon.pokemon.name} Lv.5", True, BLACK)

    info_pokemon_name_x = 10 * SCALE
    info_pokemon_name_y = 8 * SCALE
    screen.blit(text, (info_pokemon_name_x, info_pokemon_name_y))

    # HPバー（野生ポケモン）
    pygame.draw.rect(screen, LIGHT_GRAY, (5 * SCALE, 30 * SCALE, info_width, 10 * SCALE))
    hp_ratio = max(0, wild_pokemon.pokemon.hp / wild_pokemon.pokemon.max_hp)
    pygame.draw.rect(screen, GREEN, (5 * SCALE, 30 * SCALE, int(info_width * hp_ratio), 10 * SCALE))

    # HP数値表示
    font_hp = get_font(15)
    hp_text = f"{wild_pokemon.pokemon.hp}/{wild_pokemon.pokemon.max_hp}"
    text_hp = font_hp.render(hp_text, True, BLACK)
    screen.blit(text_hp, (info_pokemon_name_x, info_pokemon_name_y + 20))

    # 野生のポケモン画像を描画
    if wild_pokemon.image:
        image = pygame.transform.scale(wild_pokemon.image, (50 * SCALE, 50 * SCALE))
        screen.blit(image, (90 * SCALE, -10))

    # プレイヤーのポケモン情報
    player_info_x = 85 * SCALE
    player_info_y = 55 * SCALE
    pygame.draw.rect(screen, LIGHT_GRAY, (player_info_x, player_info_y, info_width, 25 * SCALE))
    
    player_hp_text_x = 90 * SCALE
    text = font.render(f"{player.pokemon[0].name} Lv.5", True, BLACK)
    screen.blit(text, (player_hp_text_x, player_info_y + 3 * SCALE))

    # HPバー（プレイヤーポケモン）
    hp_bar_y = player_info_y + 25 * SCALE
    pygame.draw.rect(screen, LIGHT_GRAY, (85 * SCALE, hp_bar_y, info_width, 8 * SCALE))
    hp_ratio = max(0, player.pokemon[0].hp / player.pokemon[0].max_hp)
    pygame.draw.rect(screen, GREEN, (85 * SCALE, hp_bar_y, int(info_width * hp_ratio), 8 * SCALE))

    # HP数値表示
    hp_text_p = f"{player.pokemon[0].hp}/{player.pokemon[0].max_hp}"
    text_hp_p = font_hp.render(hp_text_p, True, BLACK)
    screen.blit(text_hp_p, (player_hp_text_x, player_info_y + 30))

    # プレイヤーのポケモン画像を描画
    try:
        hitokage_image = pygame.image.load("img/hitokage.png")
        hitokage_image = pygame.transform.scale(hitokage_image, (40 * SCALE, 40 * SCALE))
        screen.blit(hitokage_image, (20 * SCALE, 56 * SCALE))
    except pygame.error:
        print("ヒトカゲの画像の読み込みに失敗しました")

    # バトルメッセージを表示する場合
    if state.battle_state == GameState.BATTLE_MESSAGE:
        try:
            message_image = pygame.image.load("img/message_all.png")
            message_image = pygame.transform.scale(message_image, (WIDTH, 49 * SCALE))
            screen.blit(message_image, (0, HEIGHT - 49 * SCALE))
        except pygame.error:
            print("message_allの画像の読み込みに失敗しました")
        font_message = get_font(14)
        
        # 1文字ずつ表示する処理
        current_time = pygame.time.get_ticks()
        # 文字表示タイマーが設定されていない場合は初期化
        if state.char_display_timer == 0:
            state.char_display_timer = current_time
            state.displayed_chars = 0
            state.full_message_displayed = False
        
        # 一定時間ごとに表示する文字数を増やす（文字送りの速度調整）
        if not state.full_message_displayed and current_time - state.char_display_timer > 50:  # 50ミリ秒ごとに1文字表示
            state.displayed_chars += 1
            state.char_display_timer = current_time
            
            # 全ての文字を表示したかチェック
            if state.displayed_chars >= len(state.battle_message):
                state.displayed_chars = len(state.battle_message)
                state.full_message_displayed = True
        
        # 現在表示すべき文字列を取得
        displayed_text = state.battle_message[:state.displayed_chars]
        text = font_message.render(displayed_text, True, BLACK)
        screen.blit(text, (10 * SCALE, HEIGHT - 49 * SCALE + 10 * SCALE))
    elif state.battle_state == GameState.BATTLE_SELECT:
        try:
            message_image = pygame.image.load("img/message_half.png")
            message_image = pygame.transform.scale(message_image, (WIDTH, 49 * SCALE))
            screen.blit(message_image, (0, HEIGHT - 49 * SCALE))
        except pygame.error:
            print("message_halfの画像の読み込みに失敗しました")
        font_moves = get_font(14)  # フォントサイズを2アップ
        for i, move in enumerate(player.pokemon[0].moves):
            # まず▶︎マークを表示（選択中の場合のみ）
            mark_x = WIDTH // 2 + 1 * SCALE
            text_x = WIDTH // 2 + 8 * SCALE  # テキストの開始位置を固定
            text_y = HEIGHT - 49 * SCALE + 10 * SCALE + i * 10 * SCALE
            
            if i == state.selected_move:
                mark = font_moves.render("▶︎", True, BLACK)
                screen.blit(mark, (mark_x, text_y))
                
            # 技名を表示（位置を固定）
            text = font_moves.render(move, True, BLACK)
            screen.blit(text, (text_x, text_y))

# メイン関数
def main():
    player = Player()
    game_state = GameState()
    steps_since_last_encounter = 0
    
    # バトル時のメッセージで伸ばし棒を使った文字を表示
    def format_damage_message(pokemon_name, move_name, damage):
        # 'ダメージ'の伸ばし棒がちゃんと表示されるようにするため
        return f"{pokemon_name}の{move_name}! {damage}のダメージ!"
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state.state == GameState.BATTLE:
                # 技選択中
                if game_state.battle_state == GameState.BATTLE_SELECT and game_state.player_turn:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT and game_state.selected_move > 0:
                            game_state.selected_move -= 1
                        elif event.key == pygame.K_RIGHT and game_state.selected_move < len(player.pokemon[0].moves) - 1:
                            game_state.selected_move += 1
                        elif event.key == pygame.K_RETURN:
                            # 技を使用
                            move_index = game_state.selected_move
                            move_name = player.pokemon[0].moves[move_index]
                            damage = player.pokemon[0].damages[move_index]
                            game_state.wild_pokemon.pokemon.hp -= damage
                            game_state.wild_pokemon.pokemon.hp = max(0, game_state.wild_pokemon.pokemon.hp)
                            game_state.battle_message = format_damage_message(player.pokemon[0].name, move_name, damage)
                            game_state.battle_state = GameState.BATTLE_MESSAGE
                            game_state.player_turn = False
                            game_state.battle_timer = pygame.time.get_ticks()
                            # 文字表示をリセット
                            game_state.displayed_chars = 0
                            game_state.char_display_timer = 0
                            game_state.full_message_displayed = False

        # ゲームロジック
        if game_state.state == GameState.FIELD:
            keys = pygame.key.get_pressed()
            old_x, old_y = player.x, player.y
            player.move(keys)
            
            # 移動したかチェック
            if old_x != player.x or old_y != player.y:
                steps_since_last_encounter += 1
                
                # 草むらの中にいるかチェック
                if player.y > HEIGHT // 2:
                    # ランダムエンカウント
                    if steps_since_last_encounter > 10 and random.random() < 0.1:
                        game_state.state = GameState.BATTLE
                        game_state.wild_pokemon = WildPokemon()
                        game_state.battle_message = f"野生の{game_state.wild_pokemon.pokemon.name}が現れた！"
                        game_state.player_turn = True
                        game_state.battle_state = GameState.BATTLE_MESSAGE  # ここで必ずメッセージ状態にする
                        steps_since_last_encounter = 0
                        # 文字表示をリセット
                        game_state.displayed_chars = 0
                        game_state.char_display_timer = 0
                        game_state.full_message_displayed = False
                        # バトル開始メッセージ表示用にタイマーをセット
                        game_state.battle_timer = pygame.time.get_ticks()
                        
        elif game_state.state == GameState.BATTLE:
            # メッセージ自動送り処理
            if game_state.battle_state == GameState.BATTLE_MESSAGE:
                # メッセージが全部表示された場合のみタイマー処理を行う
                if game_state.full_message_displayed:
                    if pygame.time.get_ticks() - game_state.battle_timer > 2000 and not game_state.battle_end_flag:
                        if game_state.player_turn:
                            game_state.battle_state = GameState.BATTLE_SELECT
                        else:
                            # 敵のターン処理
                            if game_state.wild_pokemon.pokemon.hp <= 0:
                                game_state.battle_message = f"野生の{game_state.wild_pokemon.pokemon.name}を倒した！"
                                game_state.battle_timer = pygame.time.get_ticks()  # タイマーをリセット
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                # 4秒後にフィールドに戻るフラグを立てる
                                game_state.battle_end_flag = True
                            else:
                                enemy_move_index = random.randint(0, len(game_state.wild_pokemon.pokemon.moves) - 1)
                                enemy_move = game_state.wild_pokemon.pokemon.moves[enemy_move_index]
                                enemy_damage = game_state.wild_pokemon.pokemon.damages[enemy_move_index]
                                player.pokemon[0].hp -= enemy_damage
                                player.pokemon[0].hp = max(0, player.pokemon[0].hp)
                                game_state.battle_message = format_damage_message(
                                    f"野生の{game_state.wild_pokemon.pokemon.name}", enemy_move, enemy_damage)
                                game_state.battle_timer = pygame.time.get_ticks()
                                # 文字表示をリセット
                                game_state.displayed_chars = 0
                                game_state.char_display_timer = 0
                                game_state.full_message_displayed = False
                                
                                if player.pokemon[0].hp <= 0:
                                    player.pokemon[0].hp = 0
                                    game_state.battle_message = f"{player.pokemon[0].name}は倒れた！"
                                    game_state.battle_timer = pygame.time.get_ticks()  # タイマーをリセット
                                    # 文字表示をリセット
                                    game_state.displayed_chars = 0
                                    game_state.char_display_timer = 0
                                    game_state.full_message_displayed = False
                                    # 4秒後にフィールドに戻るフラグを立てる
                                    game_state.battle_end_flag = True
                                else:
                                    # プレイヤーのポケモンが倒れていなければプレイヤーのターンに戻す
                                    game_state.player_turn = True

            # バトル終了処理
            if game_state.battle_end_flag and pygame.time.get_ticks() - game_state.battle_timer > 4000:
                # 倒れたのがプレイヤーのポケモンなら回復させる
                if player.pokemon[0].hp <= 0:
                    player.pokemon[0].hp = player.pokemon[0].max_hp
                game_state.state = GameState.FIELD
                game_state.battle_end_flag = False
        
        # 描画
        screen.fill((135, 206, 235))  # 空色の背景
        
        if game_state.state == GameState.FIELD:
            draw_field()
            player.draw()
        elif game_state.state == GameState.BATTLE:
            draw_battle_screen(player, game_state.wild_pokemon, game_state)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
