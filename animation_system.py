import pygame
from entities import GameConfig

class AnimationSystem:
    """アニメーションシステム - バトルエフェクトのアニメーション管理"""
    
    def __init__(self):
        self.active_animations = []
    
    def create_fire_animation(self, target_pos, duration=GameConfig.SKILL_ANIMATION_DURATION):
        """炎アニメーションを作成"""
        animation = FireAnimation(target_pos, duration)
        self.active_animations.append(animation)
        return animation
    
    def update(self, dt):
        """アニメーションを更新"""
        # 完了したアニメーションを削除
        self.active_animations = [anim for anim in self.active_animations if anim.update(dt)]
    
    def render(self, screen, resource_manager):
        """アニメーションを描画"""
        for animation in self.active_animations:
            animation.render(screen, resource_manager)
    
    def has_active_animations(self):
        """アクティブなアニメーションがあるかチェック"""
        return len(self.active_animations) > 0

class Animation:
    """アニメーションの基底クラス"""
    
    def __init__(self, duration):
        self.duration = duration
        self.elapsed_time = 0
        self.is_finished = False
    
    def update(self, dt):
        """アニメーションを更新 - 継続中の場合はTrueを返す"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.is_finished = True
            return False
        return True
    
    def render(self, screen, resource_manager):
        """アニメーションを描画 - サブクラスで実装"""
        pass

class FireAnimation(Animation):
    """炎のアニメーション"""
    
    def __init__(self, target_pos, duration):
        super().__init__(duration)
        self.target_pos = target_pos
        self.frame = 0
        self.frame_timer = 0
        self.use_big_fire = False
        self.positions = self._calculate_positions()
    
    def _calculate_positions(self):
        """3点移動の位置を計算"""
        center_x, center_y = self.target_pos
        offsets = [
            (-20 * GameConfig.SCALE, 0),  # 左側
            (20 * GameConfig.SCALE, 0),   # 右側
            (0, 0)                        # 中央
        ]
        return [(center_x + off_x, center_y + off_y) for off_x, off_y in offsets]
    
    def update(self, dt):
        """炎アニメーションの更新"""
        if not super().update(dt):
            return False
        
        self.frame_timer += dt
        if self.frame_timer >= GameConfig.FIRE_ANIMATION_SPEED:
            if self.use_big_fire:
                # 次の位置へ移動
                self.frame = (self.frame + 1) % 3
                self.use_big_fire = False
            else:
                # 大きい炎に切り替え
                self.use_big_fire = True
            self.frame_timer = 0
        
        return True
    
    def render(self, screen, resource_manager):
        """炎アニメーションの描画"""
        if self.is_finished:
            return
        
        # 現在の位置を取得
        current_pos = self.positions[self.frame]
        
        # 炎の画像を描画
        fire_img_path = GameConfig.FIRE_BIG_IMG if self.use_big_fire else GameConfig.FIRE_SMALL_IMG
        fire_size = (16 * GameConfig.SCALE, 16 * GameConfig.SCALE)
        fire_img = resource_manager.load_image(fire_img_path, fire_size)
        
        # 炎画像を描画（中央揃え）
        fire_rect = fire_img.get_rect(center=current_pos)
        screen.blit(fire_img, fire_rect)