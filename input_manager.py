import pygame
from battle_manager import GameState

class InputManager:
    """入力処理を管理するクラス - キーボード入力の処理を担当"""
    
    def __init__(self):
        self.keys_pressed = set()
    
    def handle_field_input(self, player, tmx_map):
        """フィールドでの入力処理"""
        keys = pygame.key.get_pressed()
        player.move(keys, tmx_map)
    
    def handle_battle_input(self, events, battle_manager, player):
        """バトルでの入力処理"""
        for event in events:
            if event.type == pygame.QUIT:
                return False
            
            # コマンド選択中の入力処理
            if battle_manager.battle_state == GameState.BATTLE_COMMAND:
                battle_manager.handle_command_input(event)
            
            # 技選択中の入力処理
            elif battle_manager.battle_state == GameState.BATTLE_SELECT:
                battle_manager.handle_move_selection_input(event, player)
        
        return True
    
    def check_debug_keys(self):
        """デバッグキーの状態をチェック"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_f]  # Fキーでデバッグ情報を表示