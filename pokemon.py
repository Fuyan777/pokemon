import pygame
import sys
import random
import time
import os

# 初期化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ポケモン風ゲーム")
clock = pygame.time.Clock()

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
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
        self.x = 400
        self.y = 300
        self.speed = 5
        self.width = 40
        self.height = 40
        self.direction = "down"
        self.pokemon = [Pokemon("ヒトカゲ", "火", 20, ["ひのこ", "ひっかく"], [10, 5])]
        # プレイヤー画像を読み込む
        try:
            self.image = pygame.image.load("red_front.png")
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
                self.image = pygame.image.load("zenigame.png")
            elif self.pokemon.name == "ピカチュウ":
                self.image = pygame.image.load("pikachu.png")
            elif self.pokemon.name == "フシギダネ":
                self.image = pygame.image.load("hushigidane.png")
            elif self.pokemon.name == "イーブイ":
                self.image = pygame.image.load("eevee.png")
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
    
    def __init__(self):
        self.state = self.FIELD
        self.battle_timer = 0
        self.wild_pokemon = None
        self.battle_message = ""
        self.player_turn = True
        self.selected_move = 0

# フィールドを描画
def draw_field():
    # 草むらエリアを描画（下半分）
    pygame.draw.rect(screen, GREEN, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    
    # 道を描画
    pygame.draw.rect(screen, (210, 180, 140), (WIDTH // 4, 0, WIDTH // 2, HEIGHT))

# バトル画面を描画
def draw_battle_screen(player, wild_pokemon, state):
    # バトル背景
    screen.fill((220, 220, 220))
    
    # 野生のポケモン情報
    pygame.draw.rect(screen, WHITE, (50, 50, 300, 100))
    font = get_font(30)
    text = font.render(f"{wild_pokemon.pokemon.name} Lv.5", True, BLACK)
    screen.blit(text, (70, 60))
    text = font.render(f"HP: {wild_pokemon.pokemon.hp}/{wild_pokemon.pokemon.max_hp}", True, BLACK)
    screen.blit(text, (70, 100))
    
    # 野生のポケモン画像を描画
    if wild_pokemon.image:
        screen.blit(wild_pokemon.image, (500, 50))
    
    # プレイヤーのポケモン情報
    pygame.draw.rect(screen, WHITE, (450, 300, 300, 100))
    text = font.render(f"{player.pokemon[0].name} Lv.5", True, BLACK)
    screen.blit(text, (470, 310))
    text = font.render(f"HP: {player.pokemon[0].hp}/{player.pokemon[0].max_hp}", True, BLACK)
    screen.blit(text, (470, 350))
    
    # プレイヤーのポケモン画像を描画
    try:
        hitokage_image = pygame.image.load("hitokage.png")
        hitokage_image = pygame.transform.scale(hitokage_image, (120, 120))
        screen.blit(hitokage_image, (50, 300))
    except pygame.error:
        print("ヒトカゲの画像の読み込みに失敗しました")
    
    # コマンドメニュー
    pygame.draw.rect(screen, WHITE, (50, 420, 700, 150))
    
    # バトルメッセージを先に描画（コマンドメニューの中に表示）
    font_message = get_font(24)  # メッセージ用に少し小さいフォント
    text = font_message.render(state.battle_message, True, BLACK)
    screen.blit(text, (100, 430))  # メッセージを上部に表示
    
    if state.player_turn:
        # 技選択メニュー
        for i, move in enumerate(player.pokemon[0].moves):
            if i == state.selected_move:
                pygame.draw.rect(screen, (200, 200, 255), (80 + i * 350, 490, 300, 40))
            text = font.render(move, True, BLACK)
            screen.blit(text, (100 + i * 350, 500))

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
                
            if game_state.state == GameState.BATTLE and game_state.player_turn:
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
                        # HPが0未満にならないように調整
                        game_state.wild_pokemon.pokemon.hp = max(0, game_state.wild_pokemon.pokemon.hp)
                        game_state.battle_message = format_damage_message(player.pokemon[0].name, move_name, damage)
                        game_state.player_turn = False
                        game_state.battle_timer = pygame.time.get_ticks()
        
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
                        steps_since_last_encounter = 0
                        
        elif game_state.state == GameState.BATTLE:
            # 敵のターン処理
            if not game_state.player_turn and pygame.time.get_ticks() - game_state.battle_timer > 2000:
                # 野生ポケモンのHPが0以下ならバトル終了
                if game_state.wild_pokemon.pokemon.hp <= 0:
                    game_state.battle_message = f"野生の{game_state.wild_pokemon.pokemon.name}を倒した！"
                    pygame.time.delay(2000)
                    game_state.state = GameState.FIELD
                else:
                    # 敵の攻撃
                    enemy_move_index = random.randint(0, len(game_state.wild_pokemon.pokemon.moves) - 1)
                    enemy_move = game_state.wild_pokemon.pokemon.moves[enemy_move_index]
                    enemy_damage = game_state.wild_pokemon.pokemon.damages[enemy_move_index]
                    player.pokemon[0].hp -= enemy_damage
                    # HPが0未満にならないように調整
                    player.pokemon[0].hp = max(0, player.pokemon[0].hp)
                    game_state.battle_message = format_damage_message(
                        f"野生の{game_state.wild_pokemon.pokemon.name}", enemy_move, enemy_damage)
                    
                    # プレイヤーのポケモンのHPが0以下ならバトル終了
                    if player.pokemon[0].hp <= 0:
                        player.pokemon[0].hp = 0
                        game_state.battle_message = f"{player.pokemon[0].name}は倒れた！"
                        pygame.time.delay(2000)
                        # HP回復して再開
                        player.pokemon[0].hp = player.pokemon[0].max_hp
                        game_state.state = GameState.FIELD
                    else:
                        game_state.player_turn = True
                        
                game_state.battle_timer = pygame.time.get_ticks()
        
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