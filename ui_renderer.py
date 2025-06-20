import pygame
from entities import GameConfig
from font_manager import FontManager
from resource_manager import ResourceManager
from battle_manager import GameState

class UIRenderer:
    """UI描画の基底クラス"""
    
    def __init__(self, screen, font_manager: FontManager, resource_manager: ResourceManager):
        self.screen = screen
        self.font_manager = font_manager
        self.resource_manager = resource_manager

class FieldRenderer(UIRenderer):
    """フィールド画面の描画を担当"""
    
    def draw_field(self, player, tmx_map):
        """フィールドを描画し、オフセットを返す"""
        # マップを描画し、描画時のオフセットを取得
        offset_x, offset_y = tmx_map.draw(self.screen, player.x + player.width // 2, player.y + player.height // 2)
        return offset_x, offset_y

class BattleRenderer(UIRenderer):
    """バトル画面の描画を担当"""
    
    def draw_battle_screen(self, player, wild_pokemon, battle_manager):
        """バトル画面全体を描画"""
        # バトル背景
        self.screen.fill(GameConfig.WHITE)
        
        # 共通で使う値
        info_width = 60 * GameConfig.SCALE
        
        # 各要素を描画する
        self.draw_wild_pokemon_info(wild_pokemon)
        self.draw_player_pokemon_info(player, info_width)
        
        # メッセージ枠は常に表示
        self.draw_battle_message(battle_manager, player)
        
        # アニメーション状態なら炎アニメーションも描画
        if battle_manager.battle_state == GameState.BATTLE_ANIMATION:
            self.draw_fire_animation(battle_manager, wild_pokemon)
    
    def draw_wild_pokemon_info(self, wild_pokemon):
        """野生ポケモンの情報を描画"""
        # 配置座標
        info_x = 5 * GameConfig.SCALE
        info_y = 5 * GameConfig.SCALE

        info_width = 80 * GameConfig.SCALE
        # 情報フレーム画像を表示
        enemy_info_frame = self.resource_manager.load_image(GameConfig.ENEMY_FRAME_IMG, (info_width, 25 * GameConfig.SCALE))
        self.screen.blit(enemy_info_frame, (info_x - 2 * GameConfig.SCALE, info_y))
        
        # ポケモン名を表示
        font = self.font_manager.get_font(15)
        info_pokemon_name_x = 11 * GameConfig.SCALE
        info_pokemon_name_y = 9 * GameConfig.SCALE
        text = font.render(f"{wild_pokemon.pokemon.name} Lv.5", True, GameConfig.BLACK)
        self.screen.blit(text, (info_pokemon_name_x, info_pokemon_name_y))
        
        # HPラベルを表示（太字）
        font_hp_label = self.font_manager.get_font(12, font_weight='W8')
        hp_label_text = "HP:"
        hp_label = font_hp_label.render(hp_label_text, True, GameConfig.BLACK)
        
        # HPバーを描画
        hp_back_x = 10 * GameConfig.SCALE
        hp_back_y = info_pokemon_name_y + 18
        self.screen.blit(hp_label, (hp_back_x - 5, hp_back_y + 3))
        self.draw_hp_bar(hp_back_x + hp_label.get_width() + 3, hp_back_y, wild_pokemon.pokemon, False)
        
        # ポケモン画像を描画
        image = pygame.transform.scale(wild_pokemon.image, (50 * GameConfig.SCALE, 50 * GameConfig.SCALE))
        self.screen.blit(image, (90 * GameConfig.SCALE, -10))
    
    def draw_player_pokemon_info(self, player, info_width):
        """プレイヤーのポケモン情報を描画"""
        # 配置座標
        player_info_x = 85 * GameConfig.SCALE
        player_info_y = 65 * GameConfig.SCALE
        
        # 情報フレーム画像を表示
        my_info_frame = self.resource_manager.load_image(GameConfig.MY_FRAME_IMG, (info_width + 5 * GameConfig.SCALE, 25 * GameConfig.SCALE))
        self.screen.blit(my_info_frame, (player_info_x - 2 * GameConfig.SCALE, player_info_y))
        
        # ポケモン名を表示
        font = self.font_manager.get_font(15)
        player_hp_text_x = 90 * GameConfig.SCALE
        text = font.render(f"{player.pokemon[0].name} Lv.5", True, GameConfig.BLACK)
        self.screen.blit(text, (player_hp_text_x + 30, player_info_y + 3 * GameConfig.SCALE))
        
        # HPラベルを表示（太字）
        font_hp_label = self.font_manager.get_font(12, font_weight='W8')
        hp_label_text = "HP:"
        hp_label = font_hp_label.render(hp_label_text, True, GameConfig.BLACK)
        
        # HPバーを描画
        hp_bar_x = player_hp_text_x  # 名前と同じX座標を使用
        hp_bar_y = player_info_y + 25
        self.screen.blit(hp_label, (hp_bar_x - 5, hp_bar_y + 2))
        self.draw_hp_bar(hp_bar_x + hp_label.get_width() + 3, hp_bar_y, player.pokemon[0], True)
        
        # HP数値表示（太字）
        font_hp = self.font_manager.get_font(15)
        hp_text_p = f"{int(player.pokemon[0].display_hp)}/{player.pokemon[0].max_hp}"
        text_hp_p = font_hp.render(hp_text_p, True, GameConfig.BLACK)
        # テキストの幅を取得してHP数値を中央に配置
        text_width = text_hp_p.get_width()
        hp_bar_width = 40 * GameConfig.SCALE
        hp_bar_x_adjusted = hp_bar_x + hp_label.get_width() + 3
        centered_x = hp_bar_x_adjusted + (hp_bar_width - text_width) // 2
        self.screen.blit(text_hp_p, (centered_x, hp_bar_y + 21))
        
        # プレイヤーのポケモン画像を描画
        hitokage_image = self.resource_manager.load_image(GameConfig.HITOKAGE_IMG, (40 * GameConfig.SCALE, 40 * GameConfig.SCALE))
        self.screen.blit(hitokage_image, (20 * GameConfig.SCALE, 56 * GameConfig.SCALE))
    
    def draw_hp_bar(self, x, y, pokemon, is_player=False):
        """HPバーを描画する"""
        # 共通の設定
        hp_image = self.resource_manager.load_image(GameConfig.HP_BAR_IMG)
        hp_unit_height = 4 * GameConfig.SCALE
        hp_unit_width = 40 * GameConfig.SCALE
        hp_image_scaled = pygame.transform.scale(hp_image, (hp_unit_width, hp_unit_height))
        
        # HPの計算
        hp_inner_width = (40 - 1.5) * GameConfig.SCALE
        hp_ratio = max(0, pokemon.display_hp / pokemon.max_hp)
        
        # HPバーを描画
        if hp_ratio > 0:
            hp_bar_width = int(hp_inner_width * hp_ratio)
            
            # HP残量に応じて色を変える
            if hp_ratio > 0.5:
                bar_color = GameConfig.GREEN
            elif hp_ratio > 0.2:
                bar_color = GameConfig.YELLOW
            else:
                bar_color = GameConfig.RED

            bar_y_offset = 2 if is_player else 3
            pygame.draw.rect(self.screen, bar_color, (x + GameConfig.SCALE * 2, y + bar_y_offset * GameConfig.SCALE, hp_bar_width, hp_unit_height))
        
        self.screen.blit(hp_image_scaled, (x + GameConfig.SCALE, y + (2 if is_player else 3) * GameConfig.SCALE))
        
        return hp_ratio
    
    def draw_battle_message(self, battle_manager, player):
        """バトルメッセージを描画"""
        if battle_manager.battle_state == GameState.BATTLE_MESSAGE or battle_manager.battle_state == GameState.BATTLE_ANIMATION:
            message_image = self.resource_manager.load_image(GameConfig.MESSAGE_ALL_IMG, (GameConfig.WIDTH, 49 * GameConfig.SCALE))
            self.screen.blit(message_image, (0, GameConfig.HEIGHT - 49 * GameConfig.SCALE))
            font_message = self.font_manager.get_font(14)
            
            # 現在表示すべき文字列を取得
            displayed_text = battle_manager.get_displayed_message()
            
            text = font_message.render(displayed_text, True, GameConfig.BLACK)
            self.screen.blit(text, (10 * GameConfig.SCALE, GameConfig.HEIGHT - 49 * GameConfig.SCALE + 10 * GameConfig.SCALE))
        elif battle_manager.battle_state == GameState.BATTLE_COMMAND:
            self.draw_command_selection(battle_manager)
        elif battle_manager.battle_state == GameState.BATTLE_SELECT:
            self.draw_move_selection(battle_manager, player)
    
    def draw_command_selection(self, battle_manager):
        """コマンド選択画面を描画"""
        # message_halfを使ってコマンド選択画面を表示
        message_image = self.resource_manager.load_image(GameConfig.MESSAGE_HALF_IMG, (GameConfig.WIDTH, 49 * GameConfig.SCALE))
        self.screen.blit(message_image, (0, GameConfig.HEIGHT - 49 * GameConfig.SCALE))
        
        commands = ["たたかう", "どうぐ", "ポケモン", "にげる"]
        font_commands = self.font_manager.get_font(14)
        
        # 2x2のグリッドでコマンドを右半分に配置
        for i, command in enumerate(commands):
            # 右側画面の左半分のコマンド（たたかう、ポケモン）
            if i % 2 == 0:
                x = GameConfig.WIDTH // 2 + 10 * GameConfig.SCALE
            # 右側画面の右半分のコマンド（どうぐ、にげる）
            else:
                x = GameConfig.WIDTH // 2 + GameConfig.WIDTH // 4 + 5 * GameConfig.SCALE
                
            # 上段のコマンド（たたかう、どうぐ）
            if i < 2:
                y = GameConfig.HEIGHT - 49 * GameConfig.SCALE + 10 * GameConfig.SCALE
            # 下段のコマンド（ポケモン、にげる）
            else:
                y = GameConfig.HEIGHT - 49 * GameConfig.SCALE + 30 * GameConfig.SCALE
                
            # 現在選択されているコマンドには▶︎を表示
            if i == battle_manager.selected_command:
                mark = font_commands.render("▶︎", True, GameConfig.BLACK)
                self.screen.blit(mark, (x - 7 * GameConfig.SCALE, y))
                
            text = font_commands.render(command, True, GameConfig.BLACK)
            self.screen.blit(text, (x, y))
    
    def draw_move_selection(self, battle_manager, player):
        """技選択画面を描画"""
        # 共通サイズの設定
        message_width = GameConfig.WIDTH // 2
        message_height = 70 * GameConfig.SCALE
        
        # message_half_middleを使用して左下に配置
        left_message_image = self.resource_manager.load_image(GameConfig.MESSAGE_HALF_MIDDLE_IMG, (message_width, message_height))
        self.screen.blit(left_message_image, (0, GameConfig.HEIGHT - message_height))
        
        # message_half_separateを使用して右下に配置
        right_message_image = self.resource_manager.load_image(GameConfig.MESSAGE_HALF_SEPARATE_IMG, (88 * GameConfig.SCALE, 48 * GameConfig.SCALE))
        self.screen.blit(right_message_image, (72 * GameConfig.SCALE, GameConfig.HEIGHT - 48 * GameConfig.SCALE))
        
        font_moves = self.font_manager.get_font(14)
        
        for i, move in enumerate(player.pokemon[0].moves):
            # マークとテキストの位置を計算（左側に表示）
            mark_x = 10 * GameConfig.SCALE
            text_x = 17 * GameConfig.SCALE
            text_y = GameConfig.HEIGHT - message_height + 10 * GameConfig.SCALE + i * 10 * GameConfig.SCALE
            
            # 選択中の技には▶︎マークを表示
            if i == battle_manager.selected_move:
                mark = font_moves.render("▶︎", True, GameConfig.BLACK)
                self.screen.blit(mark, (mark_x, text_y))
                
            # 技名を表示
            text = font_moves.render(move, True, GameConfig.BLACK)
            self.screen.blit(text, (text_x, text_y))
        
        # 右側メッセージボックスに選択した技の詳細情報を表示
        if len(player.pokemon[0].moves) > 0:
            # 選択中の技のタイプとPPを表示
            sel_move_idx = battle_manager.selected_move
            move_type = player.pokemon[0].move_types[sel_move_idx]
            current_pp = player.pokemon[0].move_pp[sel_move_idx][0]
            max_pp = player.pokemon[0].move_pp[sel_move_idx][1]
            
            # わざタイプを表示 - 中央に配置
            type_text = font_moves.render(f"わざタイプ / {move_type}", True, GameConfig.BLACK)
            type_text_width = type_text.get_width()
            # 右側メッセージボックスの中心を計算（右側の表示エリアの中央に）
            right_box_center_x = 72 * GameConfig.SCALE + (88 * GameConfig.SCALE) // 2
            # テキストの位置を中央揃えに
            type_text_x = right_box_center_x - type_text_width // 2
            self.screen.blit(type_text, (type_text_x, GameConfig.HEIGHT - 22 * GameConfig.SCALE))
            
            # PPを表示 - 中央に配置
            pp_text = font_moves.render(f"PP {current_pp}/{max_pp}", True, GameConfig.BLACK)
            pp_text_width = pp_text.get_width()
            pp_text_x = right_box_center_x - pp_text_width // 2
            self.screen.blit(pp_text, (pp_text_x, GameConfig.HEIGHT - 32 * GameConfig.SCALE))
    
    def draw_fire_animation(self, battle_manager, wild_pokemon):
        """炎のアニメーション描画"""
        current_time = pygame.time.get_ticks()
        
        # アニメーション開始からの経過時間
        elapsed_time = current_time - battle_manager.animation_start_time
        
        # アニメーション表示時間を超えていたらアニメーション終了
        if elapsed_time > GameConfig.SKILL_ANIMATION_DURATION:
            # メッセージ表示状態に切り替え
            battle_manager.battle_state = GameState.BATTLE_MESSAGE
            battle_manager.battle_timer = current_time
            return
        
        # アニメーションフレームの更新
        if current_time - battle_manager.animation_timer > GameConfig.FIRE_ANIMATION_SPEED:
            # 同じ位置で大小切り替え、または次の位置へ移動
            if battle_manager.use_big_fire:  # 大きい炎を表示中なら
                # 次の位置へ移動
                battle_manager.animation_frame = (battle_manager.animation_frame + 1) % 3  # 3点移動（左→右→中央）
                battle_manager.use_big_fire = False  # 小さい炎から開始
            else:
                # 同じ位置で大きい炎に切り替え
                battle_manager.use_big_fire = True
                
            battle_manager.animation_timer = current_time
        
        # 敵ポケモンの実際の表示位置を基準に3点移動位置を計算
        # ポケモン画像の表示位置（draw_wild_pokemon_info関数と同じ座標を使用）
        enemy_pos_x = 90 * GameConfig.SCALE  # ポケモン画像のX座標
        enemy_width = 50 * GameConfig.SCALE  # ポケモン画像の幅
        enemy_height = 50 * GameConfig.SCALE  # ポケモン画像の高さ
        
        # 敵ポケモンの中心位置
        enemy_center_x = enemy_pos_x + enemy_width / 2
        
        # アニメーションポイント（同じ高さでの3点移動）
        if not battle_manager.animation_pos:
            # 初期化（最初の呼び出し時のみ）
            # 敵ポケモンの中心Yより少し上の位置を炎の高さとする
            fire_height = enemy_height
            # 移動順序を設定: 左側→右側→中央
            offsets = [
                (-20, 0),  # 左側
                (20, 0),   # 右側
                (0, 0)     # 中央
            ]
            for off_x, off_y in offsets:
                pos_x = enemy_center_x + off_x * GameConfig.SCALE
                pos_y = fire_height
                battle_manager.animation_pos.append((pos_x, pos_y))
        
        # 現在のフレームの位置を取得
        current_pos = battle_manager.animation_pos[battle_manager.animation_frame]
        
        # 炎の画像を描画
        fire_img_path = GameConfig.FIRE_BIG_IMG if battle_manager.use_big_fire else GameConfig.FIRE_SMALL_IMG
        fire_size = (16 * GameConfig.SCALE) if battle_manager.use_big_fire else (16 * GameConfig.SCALE)
        fire_img = self.resource_manager.load_image(fire_img_path, (fire_size, fire_size))
        
        # 炎画像を描画
        self.screen.blit(fire_img, (current_pos[0] - fire_size//2, current_pos[1] - fire_size//2))