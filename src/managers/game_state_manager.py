"""
ゲーム状態管理モジュール
単一責任の原則：ゲーム状態の管理のみを担当
"""

from src.entities.entities import GameConfig


class GameStateManager:
    """ゲーム状態を管理するクラス"""
    
    def __init__(self):
        self.steps_since_last_encounter = 0
        self.encounter_checker = EncounterChecker()
    
    def update_field_state(self, player_moved, player, current_map):
        """フィールド状態を更新"""
        if player_moved:
            self.steps_since_last_encounter += 1
            
            # 野生ポケモン遭遇チェック
            if self._should_check_encounter():
                player_center_x = player.x + player.width / 2
                player_center_y = player.y + player.height / 2
                
                if self.encounter_checker.should_encounter(
                    player_center_x, player_center_y, current_map
                ):
                    self.steps_since_last_encounter = 0
                    return True  # エンカウント発生
        
        return False
    
    def _should_check_encounter(self):
        """エンカウントチェックを行うべきかどうか"""
        return self.steps_since_last_encounter >= GameConfig.STEPS_BEFORE_ENCOUNTER


class EncounterChecker:
    """野生ポケモンとの遭遇判定を管理するクラス"""
    
    def should_encounter(self, player_x, player_y, current_map):
        """野生ポケモンとの遭遇判定"""
        # 草むらにいるかチェック
        if current_map and current_map.is_on_grassy(player_x, player_y):
            import random
            return random.random() < GameConfig.ENCOUNTER_RATE
        
        return False