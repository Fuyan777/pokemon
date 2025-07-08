"""
会話システムモジュール
NPCとの会話を管理する
"""

import pygame
from src.entities.entities import GameConfig


class DialogueManager:
    """会話システムを管理するクラス"""
    
    def __init__(self, resource_manager, font_manager):
        self.resource_manager = resource_manager
        self.font_manager = font_manager
        self.is_active = False
        self.current_dialogue = []
        self.current_index = 0
        self.current_text = ""
        self.text_timer = 0
        self.char_index = 0
        self.text_speed = 50  # ミリ秒
        
        # メッセージ背景画像を読み込み
        self.message_bg = self.resource_manager.load_image(GameConfig.MESSAGE_ALL_IMG)
        
    def start_dialogue(self, dialogue_text_list):
        """会話を開始"""
        if not dialogue_text_list:
            return
            
        self.current_dialogue = dialogue_text_list
        self.current_index = 0
        self.current_text = ""
        self.char_index = 0
        self.text_timer = 0
        self.is_active = True
        
    def update(self, dt):
        """会話システムの更新"""
        if not self.is_active or not self.current_dialogue:
            return
            
        # テキストアニメーション
        if self.char_index < len(self.current_dialogue[self.current_index]):
            self.text_timer += dt
            if self.text_timer >= self.text_speed:
                self.current_text += self.current_dialogue[self.current_index][self.char_index]
                self.char_index += 1
                self.text_timer = 0
        
    def handle_input(self, event):
        """入力処理"""
        if not self.is_active:
            return False
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            # テキストアニメーション中の場合は即座に全文表示
            if self.char_index < len(self.current_dialogue[self.current_index]):
                self.current_text = self.current_dialogue[self.current_index]
                self.char_index = len(self.current_dialogue[self.current_index])
                return True
            
            # 次のメッセージに進む
            self.current_index += 1
            
            if self.current_index >= len(self.current_dialogue):
                # 会話終了
                self.end_dialogue()
                return True
            else:
                # 次のメッセージを準備
                self.current_text = ""
                self.char_index = 0
                self.text_timer = 0
                return True
                
        return False
        
    def end_dialogue(self):
        """会話を終了"""
        self.is_active = False
        self.current_dialogue = []
        self.current_index = 0
        self.current_text = ""
        self.char_index = 0
        
    def draw(self, screen):
        """会話を描画"""
        if not self.is_active or not self.current_dialogue:
            return
            
        # メッセージ背景を描画
        bg_width = self.message_bg.get_width() * GameConfig.SCALE
        bg_height = self.message_bg.get_height() * GameConfig.SCALE
        bg_x = (GameConfig.WIDTH - bg_width) // 2
        bg_y = GameConfig.HEIGHT - bg_height
        
        scaled_bg = pygame.transform.scale(self.message_bg, (bg_width, bg_height))
        screen.blit(scaled_bg, (bg_x, bg_y))
        
        # テキストを描画
        if self.current_text:
            font = self.font_manager.get_font(16)
            
            # テキストを行に分割
            lines = self._wrap_text(self.current_text, bg_width - 40, font)
            
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (0, 0, 0))
                text_x = bg_x + 20
                text_y = bg_y + 20 + i * 20
                screen.blit(text_surface, (text_x, text_y))
                
        # 続行インジケーター（テキスト表示完了時）
        if self.char_index >= len(self.current_dialogue[self.current_index]):
            # 下向き三角形を描画
            triangle_size = 18
            triangle_x = bg_x + bg_width - triangle_size - 30
            triangle_y = bg_y + bg_height - triangle_size - 30
            
            triangle_points = [
                (triangle_x + triangle_size // 2, triangle_y + triangle_size),  # 下の頂点
                (triangle_x, triangle_y),  # 左上
                (triangle_x + triangle_size, triangle_y)  # 右上
            ]
            
            pygame.draw.polygon(screen, (50, 50, 50), triangle_points)
    
    def _wrap_text(self, text, max_width, font):
        """テキストを指定幅で折り返し"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word if not current_line else current_line + " " + word
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return lines