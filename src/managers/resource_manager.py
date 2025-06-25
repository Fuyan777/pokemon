import pygame

class ResourceManager:
    """リソース管理クラス - 画像の読み込みとキャッシュを担当"""
    
    def __init__(self):
        self._image_cache = {}
    
    def load_image(self, path, size=None):
        """
        画像を読み込んでキャッシュする
        
        Args:
            path: 画像ファイルのパス
            size: リサイズする場合のサイズ (width, height) のタプル
            
        Returns:
            pygame.Surface: 読み込まれた画像
        """
        cache_key = f"{path}_{size}" if size else path
        
        if cache_key not in self._image_cache:
            image = pygame.image.load(path)
            if size:
                image = pygame.transform.scale(image, size)
            self._image_cache[cache_key] = image
        
        return self._image_cache[cache_key]
    
    def clear_cache(self):
        """キャッシュをクリアする"""
        self._image_cache.clear()
    
    def get_cache_info(self):
        """デバッグ用: キャッシュ情報を取得"""
        return {
            'cached_images': len(self._image_cache),
            'cache_keys': list(self._image_cache.keys())
        }