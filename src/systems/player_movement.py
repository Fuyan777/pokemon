"""
プレイヤー移動管理モジュール
単一責任の原則：プレイヤーの移動処理のみを担当
"""

import pygame
from src.entities.entities import GameConfig


class PlayerMovement:
    """プレイヤーの移動処理を管理するクラス"""
    
    def __init__(self, player):
        self.player = player
        self.collision_checker = CollisionChecker()
    
    def handle_input(self, keys, current_map, npcs=None):
        """入力に基づいてプレイヤーを移動させる"""
        moved = False
        direction_changed = False
        
        # 斜め移動を防ぐため、1つの方向のみ処理
        if keys[pygame.K_UP]:
            moved = self._attempt_move(0, -self.player.speed, "up", current_map, npcs)
            direction_changed = True
        elif keys[pygame.K_DOWN]:
            moved = self._attempt_move(0, self.player.speed, "down", current_map, npcs)
            direction_changed = True
        elif keys[pygame.K_LEFT]:
            moved = self._attempt_move(-self.player.speed, 0, "left", current_map, npcs)
            direction_changed = True
        elif keys[pygame.K_RIGHT]:
            moved = self._attempt_move(self.player.speed, 0, "right", current_map, npcs)
            direction_changed = True
        
        # 移動状態とアニメーションを更新
        self.player.is_moving = moved
        
        if direction_changed or moved:
            self.player.update_animation()
        
        # スプライト位置を更新
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y
        
        return moved
    
    def _attempt_move(self, dx, dy, direction, current_map, npcs=None):
        """指定された方向への移動を試行"""
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        # 方向を更新（移動できなくても向きは変える）
        self.player.direction = direction
        
        # 衝突判定をチェック
        if current_map and not self.collision_checker.can_move_to(
            self.player, new_x, new_y, current_map, npcs
        ):
            return False
        
        # 移動実行
        old_x, old_y = self.player.x, self.player.y
        
        if current_map:
            # マップ範囲内に制限
            self.player.x = max(0, min(current_map.scaled_map_width - self.player.width, new_x))
            self.player.y = max(0, min(current_map.scaled_map_height - self.player.height, new_y))
        else:
            # 画面内に制限
            self.player.x = max(0, min(GameConfig.WIDTH - self.player.width, new_x))
            self.player.y = max(0, min(GameConfig.HEIGHT - self.player.height, new_y))
        
        return old_x != self.player.x or old_y != self.player.y


class CollisionChecker:
    """衝突判定を管理するクラス"""
    
    def can_move_to(self, player, new_x, new_y, current_map, npcs=None):
        """指定された位置に移動可能かチェック"""
        collision_points = self._get_collision_points(player, new_x, new_y)
        
        # マップとの衝突をチェック
        for point_x, point_y in collision_points:
            if not current_map.is_walkable(point_x, point_y):
                return False
        
        # NPCとの衝突をチェック
        if npcs and current_map.check_npc_collision(player.x, player.y, npcs, new_x, new_y):
            return False
        
        return True
    
    def _get_collision_points(self, player, x, y):
        """プレイヤーの当たり判定ポイントを取得"""
        margin = 6 * GameConfig.SCALE
        
        return [
            (x + margin, y + margin),  # 左上
            (x + player.width - margin, y + margin),  # 右上
            (x + margin, y + player.height - margin),  # 左下
            (x + player.width - margin, y + player.height - margin),  # 右下
        ]