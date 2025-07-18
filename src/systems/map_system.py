import pygame
import pytmx
from src.entities.entities import GameConfig
from src.managers.font_manager import FontManager

class CombinedMap:
    """複数のTMXマップを結合して管理するクラス"""
    
    def __init__(self):
        try:
            # 各マップを読み込む
            self.maps = {}
            for map_name, filename in GameConfig.MAP_FILES.items():
                self.maps[map_name] = pytmx.load_pygame(filename)
            
            # タイルサイズ
            self.tile_width = GameConfig.TILE_SIZE
            self.tile_height = GameConfig.TILE_SIZE
            
            # 結合マップのサイズ（道マップの下に町マップを配置）
            road_width, road_height = GameConfig.MAP_SIZES["road"]
            town_width, town_height = GameConfig.MAP_SIZES["town"]
            
            self.map_width = max(road_width, town_width)  # 横幅は最大値
            self.map_height = road_height + town_height   # 縦は合計
            
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


class SingleMap:
    """単体TMXマップを読み込み描画するクラス"""
    
    def __init__(self, map_name):
        try:
            # 指定されたマップを読み込む
            filename = GameConfig.MAP_FILES[map_name]
            self.tmx_data = pytmx.load_pygame(filename)
            
            # タイルサイズ
            self.tile_width = GameConfig.TILE_SIZE
            self.tile_height = GameConfig.TILE_SIZE
            
            # マップサイズ
            self.map_width, self.map_height = GameConfig.MAP_SIZES[map_name]
            
            # ピクセル単位のマップサイズ
            self.width = self.map_width * self.tile_width
            self.height = self.map_height * self.tile_height
            
            # スケーリングサイズを計算
            self.scaled_tile_width = self.tile_width * GameConfig.SCALE
            self.scaled_tile_height = self.tile_height * GameConfig.SCALE
            
            # スケーリング後のマップサイズ
            self.scaled_map_width = int(self.width * GameConfig.SCALE)
            self.scaled_map_height = int(self.height * GameConfig.SCALE)
            
            # デバッグモード
            self.debug_mode = False
            self.font_manager = FontManager()
            
            # マップ画像を作成
            self.create_map_surface()
        except Exception as e:
            print(f"マップの読み込みに失敗しました: {e}")
    
    def create_map_surface(self):
        """マップ全体をサーフェスに描画"""
        # 各レイヤー用のサーフェスを作成
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((0, 0, 0, 0))
        
        self.obstacles_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.obstacles_surface.fill((0, 0, 0, 0))
        
        self.grassy_bottom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.grassy_bottom_surface.fill((0, 0, 0, 0))
        
        self.grassy_top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.grassy_top_surface.fill((0, 0, 0, 0))
        
        # レイヤーごとに適切なサーフェスに描画
        for layer in self.tmx_data.visible_layers:
            if not hasattr(layer, 'data'):
                continue
                
            # 描画先のサーフェスを決定
            if layer.name == 'obstacles':
                target_surface = self.obstacles_surface
            elif layer.name == 'object':
                target_surface = self.obstacles_surface  # objectレイヤーも障害物として扱う
            elif layer.name == 'grassy_bottom':
                target_surface = self.grassy_bottom_surface
            elif layer.name == 'grassy_top':
                target_surface = self.grassy_top_surface
            else:  # 'background'またはその他のレイヤー
                target_surface = self.background_surface
            
            for x, y, gid in layer:
                if gid:
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
        
        self.scaled_grassy_bottom = pygame.transform.scale(
            self.grassy_bottom_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_grassy_top = pygame.transform.scale(
            self.grassy_top_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
    
    # draw系メソッドを継承用に追加
    def draw(self, screen, center_x, center_y):
        """プレイヤーを中心にマップを描画"""
        screen_center_x = GameConfig.WIDTH // 2
        screen_center_y = GameConfig.HEIGHT // 2
        
        x_offset = screen_center_x - center_x
        y_offset = screen_center_y - center_y
        
        if self.scaled_map_width < GameConfig.WIDTH:
            x_offset = (GameConfig.WIDTH - self.scaled_map_width) // 2
        else:
            x_offset = min(0, x_offset)
            if self.scaled_map_width + x_offset < GameConfig.WIDTH:
                x_offset = GameConfig.WIDTH - self.scaled_map_width
    
        if self.scaled_map_height < GameConfig.HEIGHT:
            y_offset = (GameConfig.HEIGHT - self.scaled_map_height) // 2
        else:
            y_offset = min(0, y_offset)
            if self.scaled_map_height + y_offset < GameConfig.HEIGHT:
                y_offset = GameConfig.HEIGHT - self.scaled_map_height
        
        screen.blit(self.scaled_background, (x_offset, y_offset))
        return x_offset, y_offset
    
    def draw_foreground(self, screen, offset_x, offset_y):
        screen.blit(self.scaled_obstacles, (offset_x, offset_y))
    
    def draw_grassy_bottom(self, screen, offset_x, offset_y):
        screen.blit(self.scaled_grassy_bottom, (offset_x, offset_y))
    
    def draw_grassy_top(self, screen, offset_x, offset_y):
        screen.blit(self.scaled_grassy_top, (offset_x, offset_y))
    
    def draw_npcs(self, screen, npcs, offset_x, offset_y):
        """NPCを描画"""
        for npc in npcs:
            npc.draw(screen, offset_x, offset_y)
    
    def check_npc_collision(self, player_x, player_y, npcs, new_x, new_y):
        """指定した座標でNPCとの衝突をチェック（現在位置から新しい位置への移動をチェック）"""
        new_player_rect = pygame.Rect(new_x, new_y, 20 * GameConfig.SCALE, 20 * GameConfig.SCALE)
        current_player_rect = pygame.Rect(player_x, player_y, 20 * GameConfig.SCALE, 20 * GameConfig.SCALE)
        
        for npc in npcs:
            # 非表示のNPCとは衝突しない
            if not npc.visible:
                continue
                
            npc_rect = pygame.Rect(npc.x, npc.y, npc.width, npc.height)
            
            # 現在位置でNPCと重なっている場合は、NPCから離れる方向の移動を許可
            if current_player_rect.colliderect(npc_rect):
                # NPCから離れる方向かどうかをチェック
                current_distance = self._get_distance_squared(
                    current_player_rect.centerx, current_player_rect.centery,
                    npc_rect.centerx, npc_rect.centery
                )
                new_distance = self._get_distance_squared(
                    new_player_rect.centerx, new_player_rect.centery,
                    npc_rect.centerx, npc_rect.centery
                )
                
                # 離れる方向の移動は許可
                if new_distance >= current_distance:
                    continue
            
            # 新しい位置でNPCと衝突する場合は移動を禁止
            if new_player_rect.colliderect(npc_rect):
                return True
        
        return False
    
    def _get_distance_squared(self, x1, y1, x2, y2):
        """2点間の距離の二乗を計算（平方根計算を避けるため）"""
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy
    
    def toggle_debug_mode(self):
        """デバッグモードの切り替え"""
        self.debug_mode = not self.debug_mode
    
    def draw_debug_info(self, screen, player_x, player_y, offset_x, offset_y, steps_since_encounter=0):
        """デバッグ情報を描画"""
        if not self.debug_mode:
            return
        
        # タイル座標を計算
        tile_x = int(player_x / self.scaled_tile_width)
        tile_y = int(player_y / self.scaled_tile_height)
        
        # 草むらにいるかチェック
        is_on_grass = self.is_on_grassy(player_x, player_y)
        
        # デバッグ情報を表示
        debug_text = [
            f"Player: ({int(player_x)}, {int(player_y)})",
            f"Tile: ({tile_x}, {tile_y})",
            f"Map: {self.map_width}x{self.map_height}",
            f"Scaled Tile: {self.scaled_tile_width}x{self.scaled_tile_height}",
            f"On Grass: {is_on_grass}",
            f"Steps: {steps_since_encounter}/10"
        ]
        
        # 背景描画
        for i, text in enumerate(debug_text):
            y_pos = 10 + i * 20
            text_surface = self.font_manager.get_font(14).render(text, True, (255, 255, 255))
            bg_rect = pygame.Rect(5, y_pos - 2, text_surface.get_width() + 10, text_surface.get_height() + 4)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            screen.blit(text_surface, (10, y_pos))
        
        # タイルグリッドを描画
        self.draw_tile_grid(screen, offset_x, offset_y)
    
    def draw_tile_grid(self, screen, offset_x, offset_y):
        """タイルグリッドを描画"""
        if not self.debug_mode:
            return
        
        # グリッド線の色
        grid_color = (255, 0, 0, 128)
        
        # 画面に表示される範囲のタイルを計算
        start_x = max(0, int(-offset_x / self.scaled_tile_width))
        start_y = max(0, int(-offset_y / self.scaled_tile_height))
        end_x = min(self.map_width, int((-offset_x + GameConfig.WIDTH) / self.scaled_tile_width) + 1)
        end_y = min(self.map_height, int((-offset_y + GameConfig.HEIGHT) / self.scaled_tile_height) + 1)
        
        # 縦線を描画
        for x in range(start_x, end_x + 1):
            screen_x = x * self.scaled_tile_width + offset_x
            if 0 <= screen_x <= GameConfig.WIDTH:
                pygame.draw.line(screen, grid_color, 
                               (screen_x, max(0, offset_y)), 
                               (screen_x, min(GameConfig.HEIGHT, self.scaled_map_height + offset_y)))
        
        # 横線を描画
        for y in range(start_y, end_y + 1):
            screen_y = y * self.scaled_tile_height + offset_y
            if 0 <= screen_y <= GameConfig.HEIGHT:
                pygame.draw.line(screen, grid_color, 
                               (max(0, offset_x), screen_y), 
                               (min(GameConfig.WIDTH, self.scaled_map_width + offset_x), screen_y))
        
        # タイル座標を表示
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                screen_x = x * self.scaled_tile_width + offset_x + 5
                screen_y = y * self.scaled_tile_height + offset_y + 5
                
                if (0 <= screen_x <= GameConfig.WIDTH - 30 and 
                    0 <= screen_y <= GameConfig.HEIGHT - 15):
                    coord_text = f"{x},{y}"
                    text_surface = self.font_manager.get_font(10).render(coord_text, True, (255, 255, 0))
                    screen.blit(text_surface, (screen_x, screen_y))
    
    def is_walkable(self, x, y):
        """指定した座標が歩行可能かどうかを判定"""
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        if tile_x < 0 or tile_x >= self.map_width or tile_y < 0 or tile_y >= self.map_height:
            return False
        
        try:
            obstacles_layer = self.tmx_data.get_layer_by_name('obstacles')
            if obstacles_layer and hasattr(obstacles_layer, 'data'):
                gid = obstacles_layer.data[tile_y][tile_x]
                if gid > 0:
                    return False
            
            # objectレイヤーもチェック
            object_layer = self.tmx_data.get_layer_by_name('object')
            if object_layer and hasattr(object_layer, 'data'):
                gid = object_layer.data[tile_y][tile_x]
                if gid > 0:
                    return False
        except (ValueError, AttributeError, KeyError):
            pass
                    
        return True
    
    def is_on_grassy(self, x, y):
        """指定した座標が草むらの上かどうかを判定"""
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        if tile_x < 0 or tile_x >= self.map_width or tile_y < 0 or tile_y >= self.map_height:
            return False
        
        try:
            grassy_bottom_layer = self.tmx_data.get_layer_by_name('grassy_bottom')
            if grassy_bottom_layer and hasattr(grassy_bottom_layer, 'data'):
                gid = grassy_bottom_layer.data[tile_y][tile_x]
                if gid > 0:
                    return True
        except (ValueError, AttributeError, KeyError):
            pass
                    
        return False

class TiledMap(CombinedMap):
    """TMXマップを読み込み描画するクラス（後方互換性のため継承）"""
    
    def __init__(self):
        super().__init__()
        self.debug_mode = False
        self.font_manager = FontManager()
    
    def create_map_surface(self):
        """結合マップ全体をサーフェスに描画"""
        # 各レイヤー用のサーフェスを作成
        self.background_surface = pygame.Surface((self.width, self.height))
        self.background_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        self.obstacles_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.obstacles_surface.fill((0, 0, 0, 0))  # 透明で初期化
    
        self.grassy_bottom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.grassy_bottom_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        self.grassy_top_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.grassy_top_surface.fill((0, 0, 0, 0))  # 透明で初期化
        
        # 各マップを結合描画
        road_height = GameConfig.MAP_SIZES["road"][1]
        
        # 道マップ（上部）を描画
        self._draw_map_to_surface("road", 0, 0)
        
        # 町マップ（下部）を描画
        self._draw_map_to_surface("town", 0, road_height)
    
    def _draw_map_to_surface(self, map_name, offset_x, offset_y):
        """指定されたマップを指定位置に描画"""
        tmx_data = self.maps[map_name]
        
        for layer in tmx_data.visible_layers:
            if not hasattr(layer, 'data'):
                continue
                
            # 描画先のサーフェスを決定
            if layer.name == 'obstacles':
                target_surface = self.obstacles_surface
            elif layer.name == 'grassy_bottom':
                target_surface = self.grassy_bottom_surface
            elif layer.name == 'grassy_top':
                target_surface = self.grassy_top_surface
            else:  # 'background'またはその他のレイヤー
                target_surface = self.background_surface
            
            for x, y, gid in layer:
                # gidが0の場合はタイルなし
                if gid:
                    # タイルを取得して描画
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        draw_x = (x + offset_x) * self.tile_width
                        draw_y = (y + offset_y) * self.tile_height
                        target_surface.blit(tile, (draw_x, draw_y))
        
        # 各レイヤーをスケーリング
        self.scaled_background = pygame.transform.scale(
            self.background_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_obstacles = pygame.transform.scale(
            self.obstacles_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_grassy_bottom = pygame.transform.scale(
            self.grassy_bottom_surface, 
            (int(self.width * GameConfig.SCALE), int(self.height * GameConfig.SCALE))
        )
        
        self.scaled_grassy_top = pygame.transform.scale(
            self.grassy_top_surface, 
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
        
        # オフセット値を返す（プレイヤー描画位置の計算とレイヤー描画に使用）
        return x_offset, y_offset
    
    def draw_foreground(self, screen, offset_x, offset_y):
        """障害物レイヤー（obstacles）を描画"""
        # 障害物レイヤーを後から描画
        screen.blit(self.scaled_obstacles, (offset_x, offset_y))
    
    def draw_grassy_bottom(self, screen, offset_x, offset_y):
        """草むら下部レイヤー（grassy_bottom）を描画"""
        # 草むら下部レイヤーをプレイヤーの後に描画
        screen.blit(self.scaled_grassy_bottom, (offset_x, offset_y))
    
    def draw_grassy_top(self, screen, offset_x, offset_y):
        """草むら上部レイヤー（grassy_top）を描画"""
        # 草むら上部レイヤーをプレイヤーの前に描画
        screen.blit(self.scaled_grassy_top, (offset_x, offset_y))
    
    def draw_npcs(self, screen, npcs, offset_x, offset_y):
        """NPCを描画"""
        for npc in npcs:
            npc.draw(screen, offset_x, offset_y)
    
    def check_npc_collision(self, player_x, player_y, npcs, new_x, new_y):
        """指定した座標でNPCとの衝突をチェック（現在位置から新しい位置への移動をチェック）"""
        new_player_rect = pygame.Rect(new_x, new_y, 20 * GameConfig.SCALE, 20 * GameConfig.SCALE)
        current_player_rect = pygame.Rect(player_x, player_y, 20 * GameConfig.SCALE, 20 * GameConfig.SCALE)
        
        for npc in npcs:
            # 非表示のNPCとは衝突しない
            if not npc.visible:
                continue
                
            npc_rect = pygame.Rect(npc.x, npc.y, npc.width, npc.height)
            
            # 現在位置でNPCと重なっている場合は、NPCから離れる方向の移動を許可
            if current_player_rect.colliderect(npc_rect):
                # NPCから離れる方向かどうかをチェック
                current_distance = self._get_distance_squared(
                    current_player_rect.centerx, current_player_rect.centery,
                    npc_rect.centerx, npc_rect.centery
                )
                new_distance = self._get_distance_squared(
                    new_player_rect.centerx, new_player_rect.centery,
                    npc_rect.centerx, npc_rect.centery
                )
                
                # 離れる方向の移動は許可
                if new_distance >= current_distance:
                    continue
            
            # 新しい位置でNPCと衝突する場合は移動を禁止
            if new_player_rect.colliderect(npc_rect):
                return True
        
        return False
    
    def _get_distance_squared(self, x1, y1, x2, y2):
        """2点間の距離の二乗を計算（平方根計算を避けるため）"""
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy
        
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
        if tile_x < 0 or tile_x >= self.map_width or tile_y < 0 or tile_y >= self.map_height:
            return False
        
        # どのマップエリアにいるかを判定
        road_height = GameConfig.MAP_SIZES["road"][1]
        
        if tile_y < road_height:
            # 道マップエリア
            tmx_data = self.maps["road"]
            local_tile_y = tile_y
        else:
            # 町マップエリア
            tmx_data = self.maps["town"]
            local_tile_y = tile_y - road_height
        
        # 該当するマップの範囲内かチェック
        if tile_x >= tmx_data.width or local_tile_y >= tmx_data.height:
            return False
        
        # obstaclesレイヤーをチェック
        try:
            obstacles_layer = tmx_data.get_layer_by_name('obstacles')
            if obstacles_layer and hasattr(obstacles_layer, 'data'):
                gid = obstacles_layer.data[local_tile_y][tile_x]
                # このレイヤーにタイルがあれば歩行不可
                if gid > 0:
                    return False
        except (ValueError, AttributeError, KeyError):
            # レイヤーが存在しない場合は無視
            pass
        
        # objectレイヤーもチェック（町マップの場合のみ）
        if tile_y >= road_height:  # 町マップエリア
            try:
                object_layer = tmx_data.get_layer_by_name('object')
                if object_layer and hasattr(object_layer, 'data'):
                    gid = object_layer.data[local_tile_y][tile_x]
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
        if tile_x < 0 or tile_x >= self.map_width or tile_y < 0 or tile_y >= self.map_height:
            return False
        
        # どのマップエリアにいるかを判定
        road_height = GameConfig.MAP_SIZES["road"][1]
        
        if tile_y < road_height:
            # 道マップエリア
            tmx_data = self.maps["road"]
            local_tile_y = tile_y
        else:
            # 町マップエリア
            tmx_data = self.maps["town"]
            local_tile_y = tile_y - road_height
        
        # 該当するマップの範囲内かチェック
        if tile_x >= tmx_data.width or local_tile_y >= tmx_data.height:
            return False
        
        # grassy_bottomレイヤーをチェック
        try:
            grassy_bottom_layer = tmx_data.get_layer_by_name('grassy_bottom')
            if grassy_bottom_layer and hasattr(grassy_bottom_layer, 'data'):
                gid = grassy_bottom_layer.data[local_tile_y][tile_x]
                # このレイヤーにタイルがあれば草むら
                if gid > 0:
                    return True
        except (ValueError, AttributeError, KeyError):
            # レイヤーが存在しない場合は無視
            pass
                    
        # デフォルトは草むらではない
        return False
    
    def check_door_interaction(self, x, y):
        """指定した座標でドアとの相互作用をチェック"""
        # タイル座標に変換
        tile_x = int(x / self.scaled_tile_width)
        tile_y = int(y / self.scaled_tile_height)
        
        # マップ範囲外ならドアなし
        if tile_x < 0 or tile_x >= self.map_width or tile_y < 0 or tile_y >= self.map_height:
            return None
        
        # どのマップエリアにいるかを判定
        road_height = GameConfig.MAP_SIZES["road"][1]
        
        if tile_y < road_height:
            # 道マップエリア - ドアなし
            return None
        else:
            # 町マップエリア
            local_tile_y = tile_y - road_height
            
            # 特定の位置でのみlabマップへの移動を許可
            if tile_x == 12 and local_tile_y == 11:
                return "lab"
        
        return None
    
    def toggle_debug_mode(self):
        """デバッグモードの切り替え"""
        self.debug_mode = not self.debug_mode
    
    def draw_debug_info(self, screen, player_x, player_y, offset_x, offset_y, steps_since_encounter=0):
        """デバッグ情報を描画"""
        if not self.debug_mode:
            return
        
        # タイル座標を計算
        tile_x = int(player_x / self.scaled_tile_width)
        tile_y = int(player_y / self.scaled_tile_height)
        
        # 草むらにいるかチェック
        is_on_grass = self.is_on_grassy(player_x, player_y)
        
        # デバッグ情報を表示
        debug_text = [
            f"Player: ({int(player_x)}, {int(player_y)})",
            f"Tile: ({tile_x}, {tile_y})",
            f"Map: {self.map_width}x{self.map_height}",
            f"Scaled Tile: {self.scaled_tile_width}x{self.scaled_tile_height}",
            f"On Grass: {is_on_grass}",
            f"Steps: {steps_since_encounter}/10"
        ]
        
        # 背景描画
        for i, text in enumerate(debug_text):
            y_pos = 10 + i * 20
            text_surface = self.font_manager.get_font(14).render(text, True, (255, 255, 255))
            bg_rect = pygame.Rect(5, y_pos - 2, text_surface.get_width() + 10, text_surface.get_height() + 4)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            screen.blit(text_surface, (10, y_pos))
        
        # タイルグリッドを描画
        self.draw_tile_grid(screen, offset_x, offset_y)
    
    def draw_tile_grid(self, screen, offset_x, offset_y):
        """タイルグリッドを描画"""
        if not self.debug_mode:
            return
        
        # グリッド線の色
        grid_color = (255, 0, 0, 128)
        
        # 画面に表示される範囲のタイルを計算
        start_x = max(0, int(-offset_x / self.scaled_tile_width))
        start_y = max(0, int(-offset_y / self.scaled_tile_height))
        end_x = min(self.map_width, int((-offset_x + GameConfig.WIDTH) / self.scaled_tile_width) + 1)
        end_y = min(self.map_height, int((-offset_y + GameConfig.HEIGHT) / self.scaled_tile_height) + 1)
        
        # 縦線を描画
        for x in range(start_x, end_x + 1):
            screen_x = x * self.scaled_tile_width + offset_x
            if 0 <= screen_x <= GameConfig.WIDTH:
                pygame.draw.line(screen, grid_color, 
                               (screen_x, max(0, offset_y)), 
                               (screen_x, min(GameConfig.HEIGHT, self.scaled_map_height + offset_y)))
        
        # 横線を描画
        for y in range(start_y, end_y + 1):
            screen_y = y * self.scaled_tile_height + offset_y
            if 0 <= screen_y <= GameConfig.HEIGHT:
                pygame.draw.line(screen, grid_color, 
                               (max(0, offset_x), screen_y), 
                               (min(GameConfig.WIDTH, self.scaled_map_width + offset_x), screen_y))
        
        # タイル座標を表示
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                screen_x = x * self.scaled_tile_width + offset_x + 5
                screen_y = y * self.scaled_tile_height + offset_y + 5
                
                if (0 <= screen_x <= GameConfig.WIDTH - 30 and 
                    0 <= screen_y <= GameConfig.HEIGHT - 15):
                    coord_text = f"{x},{y}"
                    text_surface = self.font_manager.get_font(10).render(coord_text, True, (255, 255, 0))
                    screen.blit(text_surface, (screen_x, screen_y))
    
    def get_available_layers(self):
        """利用可能なTMXレイヤーのリストを返す（デバッグ用）"""
        layers = []
        if hasattr(self.tmx_data, 'visible_layers'):
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, 'name'):
                    layers.append(layer.name)
        return layers