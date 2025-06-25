import pygame
import sys
import os

class FontManager:
    """フォント管理クラス - 日本語フォントの読み込みと管理を担当"""
    
    def __init__(self):
        self._font_cache = {}
    
    def get_font(self, size, font_weight='W5'):
        """
        指定されたサイズと重みのフォントを取得する
        
        Args:
            size: フォントサイズ
            font_weight: フォントの重み ('W5' または 'W8')
            
        Returns:
            pygame.font.Font: フォントオブジェクト
        """
        cache_key = f"{size}_{font_weight}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        font = self._load_japanese_font(size, font_weight)
        self._font_cache[cache_key] = font
        return font
    
    def _load_japanese_font(self, size, font_weight='W5'):
        """
        日本語フォントを読み込む
        
        Args:
            size: フォントサイズ
            font_weight: フォントの重み
            
        Returns:
            pygame.font.Font: 読み込まれたフォント
        """
        # macOSの場合はフォントパスを直接指定する方法を試す
        if sys.platform == 'darwin':  # macOS
            try:
                # まず、macOSの標準的な日本語フォントパスを直接試す
                if font_weight == 'W8':
                    font_paths = [
                        '/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc',  # W8フォント
                    ]
                else:  # デフォルトはW5
                    font_paths = [
                        '/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc',  # Catalina以降
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
            default_font.render(test_text, True, (0, 0, 0))
            return default_font
        except:
            # 最終手段
            return pygame.font.SysFont(None, size)