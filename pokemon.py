import pygame
import sys
import random

# モジュールのインポート
from entities import GameConfig, Player, WildPokemon
from font_manager import FontManager
from resource_manager import ResourceManager
from battle_manager import BattleManager, GameState
from ui_renderer import FieldRenderer, BattleRenderer
from input_manager import InputManager
from animation_system import AnimationSystem
from map_system import TiledMap

class GameEngine:
    """ゲームエンジンクラス - ゲーム全体の制御を担当"""
    
    def __init__(self):
        # Pygame初期化
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("ポケモン風ゲーム")
        self.clock = pygame.time.Clock()
        
        # 管理クラスの初期化
        self.font_manager = FontManager()
        self.resource_manager = ResourceManager()
        self.battle_manager = BattleManager()
        self.input_manager = InputManager()
        self.animation_system = AnimationSystem()
        
        # レンダラーの初期化
        self.field_renderer = FieldRenderer(self.screen, self.font_manager, self.resource_manager)
        self.battle_renderer = BattleRenderer(self.screen, self.font_manager, self.resource_manager)
        
        # ゲームオブジェクトの初期化
        self.player = Player(self.resource_manager)
        self.tmx_map = TiledMap(GameConfig.MAP_FILE)
        
        # ゲーム状態
        self.steps_since_last_encounter = 0
        self.running = True
        
        # スプライトグループ
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wild_pokemon_group = pygame.sprite.Group()
        
        self.all_sprites.add(self.player)
        self.player_group.add(self.player)

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if self.battle_manager.state == GameState.BATTLE:
                if not self.input_manager.handle_battle_input([event], self.battle_manager, self.player):
                    self.running = False

    def update_field(self):
        """フィールド状態の更新"""
        if self.battle_manager.state == GameState.FIELD:
            old_x, old_y = self.player.x, self.player.y
            self.input_manager.handle_field_input(self.player, self.tmx_map)
            
            # 移動したかチェック
            if old_x != self.player.x or old_y != self.player.y:
                self.steps_since_last_encounter += 1
                
                # 草むら（grassy）の中にいるかチェック
                # if self.tmx_map.is_on_grassy(self.player.x + self.player.width/2, self.player.y + self.player.height/2):
                #     # ランダムエンカウント
                #     if self.steps_since_last_encounter > GameConfig.STEPS_BEFORE_ENCOUNTER and random.random() < GameConfig.ENCOUNTER_RATE:
                #         self._start_battle()
    
    def _start_battle(self):
        """バトル開始処理"""
        wild_pokemon = WildPokemon(self.resource_manager)
        self.battle_manager.start_battle(wild_pokemon)
        
        # 野生ポケモンをスプライトグループに追加
        self.all_sprites.add(wild_pokemon)
        self.wild_pokemon_group.add(wild_pokemon)
        
        self.steps_since_last_encounter = 0

    def update_battle(self):
        """バトル状態の更新"""
        if self.battle_manager.state == GameState.BATTLE:
            self.battle_manager.update_battle(self.player)
            self.battle_manager.update_hp_animations(self.player)
            self.battle_manager.update_message_display()
            
            # バトル終了チェック
            if self.battle_manager.state == GameState.FIELD:
                self._end_battle()

    def _end_battle(self):
        """バトル終了処理"""
        # 野生ポケモンをスプライトグループから削除
        if self.battle_manager.wild_pokemon:
            self.all_sprites.remove(self.battle_manager.wild_pokemon)
            self.wild_pokemon_group.remove(self.battle_manager.wild_pokemon)

    def render(self):
        """画面描画処理"""
        self.screen.fill(GameConfig.SKY_BLUE)  # 空色の背景
        
        if self.battle_manager.state == GameState.FIELD:
            self._render_field()
        elif self.battle_manager.state == GameState.BATTLE:
            self._render_battle()
        
        # デバッグ情報の描画（特定のキーが押されたときのみ）
        if self.input_manager.check_debug_keys():
            self._draw_debug_info()
        
        pygame.display.flip()
    
    def _render_field(self):
        """フィールド画面の描画"""
        # 背景マップを描画し、オフセットを取得
        map_offset_x, map_offset_y = self.field_renderer.draw_field(self.player, self.tmx_map)
        # 草むら上部レイヤーを最初に描画（top）
        self.tmx_map.draw_grassy_top(self.screen, map_offset_x, map_offset_y)
        # プレイヤーを描画
        self.player.draw(self.screen, map_offset_x, map_offset_y)
        # 草むら下部レイヤーを描画（bottom）
        self.tmx_map.draw_grassy_bottom(self.screen, map_offset_x, map_offset_y)
        # 前景レイヤー（rock等）を描画
        self.tmx_map.draw_foreground(self.screen, map_offset_x, map_offset_y)
    
    def _render_battle(self):
        """バトル画面の描画"""
        self.battle_renderer.draw_battle_screen(self.player, self.battle_manager.wild_pokemon, self.battle_manager)

    def _draw_debug_info(self):
        """デバッグ情報を描画"""
        # プレイヤーの位置を取得
        player_pos_x = self.player.x + self.player.width/2
        player_pos_y = self.player.y + self.player.height/2
        
        # デバッグ情報を描画
        font = self.font_manager.get_font(10)
        y_offset = 10
        
        # 座標情報
        pos_text = f"座標: ({int(player_pos_x)}, {int(player_pos_y)})"
        text_surface = font.render(pos_text, True, GameConfig.WHITE)
        self.screen.blit(text_surface, (10, y_offset))

    def run(self):
        """メインゲームループ"""
        while self.running:
            # イベント処理
            self.handle_events()
            
            # ゲーム状態更新
            self.update_field()
            self.update_battle()
            
            # アニメーション更新
            dt = self.clock.get_time()
            self.animation_system.update(dt)
            
            # 描画
            self.render()
            
            # フレームレート制御
            self.clock.tick(GameConfig.FPS)

def main():
    """メイン関数"""
    game_engine = GameEngine()
    game_engine.run()
    
    pygame.quit()
    sys.exit()









if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
