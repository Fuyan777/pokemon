import pygame
import pytmx
from entities import GameConfig

class TiledMap:
    """TMXマップを読み込み描画するクラス"""
    
    def __init__(self, filename):
        try:
            # TMXファイルを読み込む
            self.tmx_data = pytmx.load_pygame(filename)
            # タイルサイズ
            self.tile_width = GameConfig.TILE_SIZE
            self.tile_height = GameConfig.TILE_SIZE
            # マップサイズ（タイル数）
            self.map_width = GameConfig.MAP_WIDTH
            self.map_height = GameConfig.MAP_HEIGHT
            # ピクセル単位のマップサイズ
            self.width = self.map_width * self.tile_width
            self.height = self.map_height * self.tile_height
            # スケーリングサイズを計算
            self.scaled_tile_width = self.tile_width * GameConfig.SCALE
            self.scaled_tile_height = self.tile_height * GameConfig.SCALE
            # スケーリング後のマップサイズ
            self.scaled_map_width = int(self.width * GameConfig.SCALE)
            self.scaled_map_height = int(self.height * GameConfig.SCALE)
            # マップ画像を作成
            self.create_map_surface()
        except Exception as e:
            print(f"マップの読み込みに失敗しました: {e}")
    
    def create_map_surface(self):
        """マップ全体をサーフェスに描画"""
        # 背景のサーフェスを作成（backgroundレイヤー用）
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        # 障害物のサーフェスを作成（obstaclesレイヤー用）
        self.obstacles_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.obstacles_surface.fill((0, 0, 0, 0))  # 透明で初期化
    
        # 草むらのサーフェスを作成（grassyレイヤー用）
        self.grassy_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.grassy_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        # レイヤーごとに適切なサーフェスに描画
        for layer in self.tmx_data.visible_layers:
            if not hasattr(layer, 'data'):
                continue
                
            # 描画先のサーフェスを決定
            if layer.name == 'obstacles':
                target_surface = self.obstacles_surface
            elif layer.name == 'grassy':
                target_surface = self.grassy_surface
            else:  # 'background'またはその他のレイヤー
                target_surface = self.background_surface
            
            for x, y, gid in layer:
                # gidが0の場合はタイルなし
                if gid:
                    # タイルを取得して描画
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        target_surface.blit(tile, (x * self.tile_width, y * self.tile_height))
        
        # 各レイヤーをスケーリング
        self.scaled_background = pygame.transform.scale(
            self.background_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_obstacles = pygame.transform.scale(
            self.obstacles_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_grassy = pygame.transform.scale(
            self.grassy_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
    def draw(self, screen, center_x, center_y):
        """プレイヤーを中心にマップを描画"""
        # 画面の中心位置
        screen_center_x = GameConfig.WIDTH // 2
        screen_center_y = GameConfig.HEIGHT // 2
        
        # 描画位置を計算（プレイヤーを中心に）
        x_offset = screen_center_x - center_x
        y_offset = screen_center_y - center_y
        
        # マップが小さい場合は中央に配置
        if self.scaled_map_width < GameConfig.WIDTH:
            x_offset = (GameConfig.WIDTH - self.scaled_map_width) // 2
        else:
            # マップが画面より大きい場合、端の処理を行う
            # 左端の制限（マップの左端が画面の右にはみ出さないように）
            x_offset = min(0, x_offset)
            
            # 右端の制限（マップの右端が画面の左にはみ出さないように）
            if self.scaled_map_width + x_offset < GameConfig.WIDTH:
                x_offset = GameConfig.WIDTH - self.scaled_map_width
    
        # 縦方向も同様に処理
        if self.scaled_map_height < GameConfig.HEIGHT:
            y_offset = (GameConfig.HEIGHT - self.scaled_map_height) // 2
        else:
            # 上端の制限
            y_offset = min(0, y_offset)
            
            # 下端の制限
            if self.scaled_map_height + y_offset < GameConfig.HEIGHT:
                y_offset = GameConfig.HEIGHT - self.scaled_map_height
        
        # 背景レイヤーを描画
        screen.blit(self.scaled_background, (x_offset, y_offset))
        
        # 草むらレイヤーを描画
        screen.blit(self.scaled_grassy, (x_offset, y_offset))
        
        # オフセット値を返す（プレイヤー描画位置の計算とレイヤー描画に使用）
        return x_offset, y_offset
    
    def draw_foreground(self, screen, offset_x, offset_y):
        """障害物レイヤー（obstacles）を描画"""
        # 障害物レイヤーを後から描画
        screen.blit(self.scaled_obstacles, (offset_x, offset_y))
        
    def get_object_layer(self, name):
        """指定した名前のオブジェクトレイヤーを取得"""
        if hasattr(self.tmx_data, 'get_layer_by_name'):
            return self.tmx_data.get_layer_by_name(name)
        return None
    
    def is_walkable(self, x, y):
        """指定した座標が歩行可能かどうかを判定"""
        # タイル座標に変換
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        # マップ範囲外なら歩行不可
        if tile_x < 0 or tile_x >= self.tmx_data.width or tile_y < 0 or tile_y >= self.tmx_data.height:
            return False
        
        # obstaclesレイヤーのみチェック
        try:
            obstacles_layer = self.tmx_data.get_layer_by_name('obstacles')
            if obstacles_layer and hasattr(obstacles_layer, 'data'):
                gid = obstacles_layer.data[tile_y][tile_x]
                # このレイヤーにタイルがあれば歩行不可
                if gid > 0:
                    return False
        except (ValueError, AttributeError, KeyError):
            # レイヤーが存在しない場合は無視
            pass
                    
        # デフォルトは歩行可能
        return True
    
    def is_on_grassy(self, x, y):
        """指定した座標が草むらの上かどうかを判定"""
        # タイル座標に変換
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        # マップ範囲外なら草むらではない
        if tile_x < 0 or tile_x >= self.tmx_data.width or tile_y < 0 or tile_y >= self.tmx_data.height:
            return False
        
        # grassyレイヤーをチェック
        try:
            grassy_layer = self.tmx_data.get_layer_by_name('grassy')
            if grassy_layer and hasattr(grassy_layer, 'data'):
                gid = grassy_layer.data[tile_y][tile_x]
                # このレイヤーにタイルがあれば草むら
                if gid > 0:
                    return True
        except (ValueError, AttributeError, KeyError):
            # レイヤーが存在しない場合は無視
            pass
                    
        # デフォルトは草むらではない
        return False
    
    def get_available_layers(self):
        """利用可能なTMXレイヤーのリストを返す（デバッグ用）"""
        layers = []
        if hasattr(self.tmx_data, 'visible_layers'):
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, 'name'):
                    layers.append(layer.name)
        return layers