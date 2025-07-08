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
        self.last_tile_x = None
        self.last_tile_y = None
    
    def update_field_state(self, player_moved, player, current_map):
        """フィールド状態を更新"""
        if player_moved:
            player_center_x = player.x + player.width / 2
            player_center_y = player.y + player.height / 2
            
            # 現在のタイル座標を計算
            if current_map:
                current_tile_x = int(player_center_x / current_map.scaled_tile_width)
                current_tile_y = int(player_center_y / current_map.scaled_tile_height)
                
                # タイルが変わった場合のみ処理
                if (self.last_tile_x != current_tile_x or self.last_tile_y != current_tile_y):
                    self.last_tile_x = current_tile_x
                    self.last_tile_y = current_tile_y
                    
                    # 草むらにいる場合のみステップ数をカウント
                    if current_map.is_on_grassy(player_center_x, player_center_y):
                        self.steps_since_last_encounter += 1
                        
                        # 野生ポケモン遭遇チェック
                        if self._should_check_encounter():
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