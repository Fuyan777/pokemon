import pygame
import sys
import random

# モジュールのインポート
from src.entities.entities import GameConfig, Player, WildPokemon, NPC
from src.managers.font_manager import FontManager
from src.managers.resource_manager import ResourceManager
from src.managers.battle_manager import BattleManager, GameState
from src.systems.ui_renderer import FieldRenderer, BattleRenderer
from src.managers.input_manager import InputManager
from src.systems.animation_system import AnimationSystem
from src.systems.map_system import TiledMap, SingleMap
from src.managers.map_transition_manager import MapTransitionManager
from src.systems.player_movement import PlayerMovement
from src.managers.game_state_manager import GameStateManager

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
        self.tmx_map = TiledMap()  # 結合マップを初期化
        
        # 責任分離されたマネージャークラス
        self.map_transition_manager = MapTransitionManager()
        self.player_movement = PlayerMovement(self.player)
        self.game_state_manager = GameStateManager()
        
        # ゲーム状態
        self.running = True
        
        # スプライトグループ
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wild_pokemon_group = pygame.sprite.Group()
        
        self.all_sprites.add(self.player)
        self.player_group.add(self.player)
        
        # NPCの初期化
        self.npcs = {}
        self._initialize_npcs()

    def _initialize_npcs(self):
        """各マップのNPCを初期化"""
        # labマップのNPC
        self.npcs["lab"] = []
        
        # okdを配置（位置は16x16のタイル座標 * スケール）
        okd_x = 5 * GameConfig.TILE_SIZE * GameConfig.SCALE
        okd_y = 8 * GameConfig.TILE_SIZE * GameConfig.SCALE
        okd = NPC(self.resource_manager, "okd", okd_x, okd_y, GameConfig.OKD_IMG)
        self.npcs["lab"].append(okd)
        
        # rivalを配置
        rival_x = 3 * GameConfig.TILE_SIZE * GameConfig.SCALE
        rival_y = 6 * GameConfig.TILE_SIZE * GameConfig.SCALE
        rival = NPC(self.resource_manager, "rival", rival_x, rival_y, GameConfig.RIVAL_IMG)
        self.npcs["lab"].append(rival)

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # デバッグモード切り替え（Dキー）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                current_map = self.map_transition_manager.get_current_map(self.tmx_map)
                current_map.toggle_debug_mode()
            
            if self.battle_manager.state == GameState.BATTLE:
                if not self.input_manager.handle_battle_input([event], self.battle_manager, self.player):
                    self.running = False

    def update_field(self):
        """フィールド状態の更新"""
        if self.battle_manager.state == GameState.FIELD:
            # 現在のマップを取得
            current_map = self.map_transition_manager.get_current_map(self.tmx_map)
            
            # プレイヤー移動処理
            keys = pygame.key.get_pressed()
            player_moved = self.player_movement.handle_input(keys, current_map)
            
            if player_moved:
                # マップ遷移チェック
                player_center_x, player_center_y = self.player.get_center_position()
                
                transition_target = self.map_transition_manager.check_transition_trigger(
                    self.tmx_map, player_center_x, player_center_y
                )
                
                if transition_target:
                    self.map_transition_manager.transition_to_map(transition_target, self.player)
                    return
                
                # ゲーム状態更新（エンカウントチェック含む）
                encounter_triggered = self.game_state_manager.update_field_state(
                    player_moved, self.player, current_map
                )
                
                if encounter_triggered:
                    self._start_battle()
    
    
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
        # 現在のマップを取得
        current_map = self.map_transition_manager.get_current_map(self.tmx_map)
        
        # 背景マップを描画し、オフセットを取得
        map_offset_x, map_offset_y = self.field_renderer.draw_field(self.player, current_map)
        
        # プレイヤーの位置を確認
        player_center_x, player_center_y = self.player.get_center_position()
        is_on_grass = current_map.is_on_grassy(player_center_x, player_center_y)
        
        if is_on_grass:
            # 草むらにいる場合：プレイヤーの下半身のみ描画
            self.player.draw_lower_only(self.screen, map_offset_x, map_offset_y)
        
        # 草むら上部レイヤーを描画（top）
        current_map.draw_grassy_top(self.screen, map_offset_x, map_offset_y)
        
        # 草むら下部レイヤーを描画（bottom）
        current_map.draw_grassy_bottom(self.screen, map_offset_x, map_offset_y)
        # 前景レイヤー（rock等）を描画
        current_map.draw_foreground(self.screen, map_offset_x, map_offset_y)
        
        # NPCを描画
        if self.map_transition_manager.is_single_map() and self.map_transition_manager.single_map:
            # 単体マップの場合、マップ名から決定
            if hasattr(self.map_transition_manager.single_map, 'tmx_data'):
                # labマップの場合はNPCを描画
                current_map.draw_npcs(self.screen, self.npcs["lab"], map_offset_x, map_offset_y)
        
        if is_on_grass:
            # 草むらにいる場合：プレイヤーの上部スプライトを最上位に描画
            self.player.draw_upper_only(self.screen, map_offset_x, map_offset_y)
        else:
            # 草むらにいない場合：プレイヤー全体を最前面に描画
            self.player.draw(self.screen, map_offset_x, map_offset_y)
        
        # デバッグ情報を最上位に描画
        current_map.draw_debug_info(self.screen, player_center_x, player_center_y, map_offset_x, map_offset_y, 
                                  self.game_state_manager.steps_since_last_encounter)
    
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
