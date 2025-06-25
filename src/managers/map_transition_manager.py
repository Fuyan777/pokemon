"""
マップ遷移管理モジュール
単一責任の原則：マップ間の遷移処理のみを担当
"""

from src.entities.entities import GameConfig
from src.systems.map_system import SingleMap


class MapTransitionManager:
    """マップ遷移を管理するクラス"""
    
    def __init__(self):
        self.previous_position = None
        self.current_map_type = "combined"  # "combined" または "single"
        self.single_map = None
    
    def check_transition_trigger(self, tmx_map, player_x, player_y):
        """遷移トリガーをチェックし、遷移先を返す"""
        if self.current_map_type == "combined":
            return tmx_map.check_door_interaction(player_x, player_y)
        else:
            # 単体マップでの出口チェック
            tile_x = int(player_x / (GameConfig.TILE_SIZE * GameConfig.SCALE))
            tile_y = int(player_y / (GameConfig.TILE_SIZE * GameConfig.SCALE))
            
            if (tile_x == 4 and tile_y == 11) or (tile_x == 5 and tile_y == 11):
                return "return_to_previous"
        
        return None
    
    def transition_to_map(self, map_name, player):
        """指定されたマップに遷移する"""
        try:
            if map_name == "lab":
                self._transition_to_lab(player)
            elif map_name == "return_to_previous":
                self._return_to_previous_map(player)
            else:
                print(f"Unknown map transition: {map_name}")
        except Exception as e:
            print(f"Error during map transition: {e}")
            # エラー時は遷移をキャンセル
    
    def _transition_to_lab(self, player):
        """labマップに遷移"""
        # 現在の位置を記録
        self.previous_position = (player.x, player.y)
        
        # labマップに遷移
        self.single_map = SingleMap("lab")
        self.current_map_type = "single"
        
        # プレイヤーを入り口に配置
        lab_width, lab_height = GameConfig.MAP_SIZES["lab"]
        new_x = (lab_width * GameConfig.TILE_SIZE * GameConfig.SCALE / 2) - (player.width / 2)
        new_y = (lab_height - 1) * GameConfig.TILE_SIZE * GameConfig.SCALE - player.height
        player.set_position(new_x, new_y)
    
    def _return_to_previous_map(self, player):
        """前のマップに戻る"""
        if self.previous_position:
            # 結合マップに戻る
            self.current_map_type = "combined"
            self.single_map = None
            
            # 記録された位置に復帰
            player.set_position(*self.previous_position)
            self.previous_position = None
    
    def get_current_map(self, combined_map):
        """現在のマップオブジェクトを取得"""
        if self.current_map_type == "single":
            return self.single_map
        else:
            return combined_map
    
    def is_single_map(self):
        """単体マップかどうかを判定"""
        return self.current_map_type == "single"