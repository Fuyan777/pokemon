import pygame
import random
from src.entities.entities import GameConfig

class GameState:
    """ゲーム状態の定数定義"""
    FIELD = 0
    BATTLE = 1
    BATTLE_COMMAND = 0  # コマンド選択（たたかう、どうぐ、ポケモン、にげる）
    BATTLE_SELECT = 1   # 技選択
    BATTLE_MESSAGE = 2  # メッセージ表示
    BATTLE_ANIMATION = 3  # 技アニメーション表示

class BattleManager:
    """バトルシステムの管理クラス - 戦闘ロジックを担当"""
    
    def __init__(self):
        self.state = GameState.FIELD
        self.battle_timer = 0
        self.wild_pokemon = None
        self.battle_message = ""
        self.player_turn = True
        self.selected_move = 0
        self.selected_command = 0  # 選択中のコマンド（0: たたかう, 1: どうぐ, 2: ポケモン, 3: にげる）
        self.battle_state = GameState.BATTLE_COMMAND  # 初期状態をコマンド選択に変更
        self.battle_end_flag = False
        
        # テキスト表示用の変数
        self.displayed_chars = 0  # 現在表示している文字数
        self.char_display_timer = 0  # 文字表示用タイマー
        self.full_message_displayed = False  # メッセージがすべて表示されたかどうか
        
        # ダメージ情報を一時保存
        self.pending_damage = 0    # 待機中のダメージ量
        self.damage_target = None  # ダメージを受ける対象（"player" または "enemy"）
        
        # 技アニメーション用の変数
        self.animation_start_time = 0  # アニメーション開始時間
        self.current_move_name = ""  # 現在使用中の技名
        self.animation_pos = []  # アニメーション位置リスト（3点移動用）
        self.animation_frame = 0  # アニメーションフレーム
        self.animation_timer = 0  # アニメーション用タイマー
        self.use_big_fire = False  # 大きい炎を使用するかどうか
    
    def start_battle(self, wild_pokemon):
        """バトルを開始する"""
        self.state = GameState.BATTLE
        self.wild_pokemon = wild_pokemon
        self.battle_message = f"野生の{wild_pokemon.pokemon.name}が現れた！"
        self.player_turn = True
        self.battle_state = GameState.BATTLE_MESSAGE
        self.battle_end_flag = False
        
        # 表示関連のリセット
        self.displayed_chars = 0
        self.char_display_timer = 0
        self.full_message_displayed = False
        self.battle_timer = pygame.time.get_ticks()
    
    def handle_command_input(self, event):
        """コマンド選択時の入力処理"""
        if self.battle_state != GameState.BATTLE_COMMAND or not self.player_turn:
            return
            
        if event.type == pygame.KEYDOWN:
            # 横方向の移動（左右）
            if event.key == pygame.K_LEFT:
                if self.selected_command % 2 == 1:  # 右側から左側へ
                    self.selected_command -= 1
            elif event.key == pygame.K_RIGHT:
                if self.selected_command % 2 == 0:  # 左側から右側へ
                    self.selected_command += 1
            # 縦方向の移動（上下）
            elif event.key == pygame.K_UP:
                if self.selected_command >= 2:  # 下段から上段へ
                    self.selected_command -= 2
            elif event.key == pygame.K_DOWN:
                if self.selected_command < 2:  # 上段から下段へ
                    self.selected_command += 2
            # 決定（Enterキー）
            elif event.key == pygame.K_RETURN:
                if self.selected_command == 0:  # 「たたかう」選択時
                    self.battle_state = GameState.BATTLE_SELECT
                elif self.selected_command == 3:  # 「にげる」選択時
                    self._handle_run_away()
    
    def handle_move_selection_input(self, event, player):
        """技選択時の入力処理"""
        if self.battle_state != GameState.BATTLE_SELECT or not self.player_turn:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.selected_move > 0:
                self.selected_move -= 1
            elif event.key == pygame.K_DOWN and self.selected_move < len(player.pokemon[0].moves) - 1:
                self.selected_move += 1
            elif event.key == pygame.K_ESCAPE:  # ESCキーでコマンド選択に戻る
                self.battle_state = GameState.BATTLE_COMMAND
            elif event.key == pygame.K_RETURN:
                self._execute_player_move(player)
    
    def _handle_run_away(self):
        """逃走処理"""
        self.battle_message = "うまく にげきれた！"
        self.battle_state = GameState.BATTLE_MESSAGE
        self.battle_timer = pygame.time.get_ticks()
        self._reset_message_display()
        self.battle_end_flag = True
    
    def _execute_player_move(self, player):
        """プレイヤーの技実行処理"""
        move_index = self.selected_move
        move_name = player.pokemon[0].moves[move_index]
        damage = player.pokemon[0].damages[move_index]
        
        # PPがあるか確認
        if player.pokemon[0].move_pp[move_index][0] > 0:
            # PPを1減らす
            player.pokemon[0].move_pp[move_index][0] -= 1
            
            # ダメージ情報を保存
            self.pending_damage = damage
            self.damage_target = "enemy"
            # メッセージを設定
            self.battle_message = self._format_damage_message(player.pokemon[0].name, move_name, damage)
            
            # 「ひのこ」の場合はアニメーション表示
            if move_name == "ひのこ" and player.pokemon[0].name == "ヒトカゲ":
                self._start_skill_animation(move_name)
            else:
                # 通常の技はメッセージ表示
                self.battle_state = GameState.BATTLE_MESSAGE
            
            self.player_turn = False
            self.battle_timer = pygame.time.get_ticks()
            self._reset_message_display()
        else:
            # PPが足りない場合のメッセージ
            self.battle_message = f"{move_name}のPPが足りない！"
            self.battle_state = GameState.BATTLE_MESSAGE
            self.battle_timer = pygame.time.get_ticks()
            self._reset_message_display()
            # プレイヤーのターンは続行
            self.pending_damage = 0
    
    def _start_skill_animation(self, move_name):
        """スキルアニメーション開始"""
        self.battle_state = GameState.BATTLE_ANIMATION
        self.current_move_name = move_name
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_timer = pygame.time.get_ticks()
        self.animation_frame = 0
        self.animation_pos = []  # 位置はアニメーション描画時に初期化
        self.use_big_fire = False
    
    def update_battle(self, player):
        """バトル状態の更新"""
        if self.state != GameState.BATTLE:
            return
            
        # メッセージ自動送り処理
        if self.battle_state == GameState.BATTLE_MESSAGE:
            if self.full_message_displayed:
                self._apply_pending_damage(player)
                
                # バトル終了フラグがセットされていない場合のみ次の処理へ
                if self.battle_end_flag:
                    pass  # 終了フラグがセットされていれば何もしない
                elif pygame.time.get_ticks() - self.battle_timer > GameConfig.MESSAGE_WAIT_TIME:
                    if self.player_turn:
                        self.battle_state = GameState.BATTLE_COMMAND
                    else:
                        self._handle_enemy_turn(player)
        
        # バトル終了処理
        if self.battle_end_flag and pygame.time.get_ticks() - self.battle_timer > GameConfig.BATTLE_END_WAIT_TIME:
            self._end_battle(player)
    
    def _apply_pending_damage(self, player):
        """保留中のダメージを適用"""
        if self.pending_damage > 0:
            if self.damage_target == "enemy":
                self.wild_pokemon.pokemon.hp -= self.pending_damage
                self.wild_pokemon.pokemon.hp = max(0, self.wild_pokemon.pokemon.hp)
            elif self.damage_target == "player":
                player.pokemon[0].hp -= self.pending_damage
                player.pokemon[0].hp = max(0, player.pokemon[0].hp)
                # プレイヤーのポケモンが倒れたかチェック
                if player.pokemon[0].hp <= 0:
                    player.pokemon[0].hp = 0
                    self.battle_message = f"{player.pokemon[0].name}は倒れた！"
                    self.battle_timer = pygame.time.get_ticks()
                    self._reset_message_display()
                    self.battle_end_flag = True
            
            self.pending_damage = 0
    
    def _handle_enemy_turn(self, player):
        """敵のターン処理"""
        if self.wild_pokemon.pokemon.hp <= 0:
            self.battle_message = f"野生の{self.wild_pokemon.pokemon.name}を倒した！"
            self.battle_timer = pygame.time.get_ticks()
            self._reset_message_display()
            self.battle_end_flag = True
        else:
            # PPが残っている技をランダムに選ぶ
            available_moves = []
            for i, move in enumerate(self.wild_pokemon.pokemon.moves):
                if self.wild_pokemon.pokemon.move_pp[i][0] > 0:
                    available_moves.append(i)
            
            # 使える技がある場合
            if available_moves:
                enemy_move_index = random.choice(available_moves)
                enemy_move = self.wild_pokemon.pokemon.moves[enemy_move_index]
                enemy_damage = self.wild_pokemon.pokemon.damages[enemy_move_index]
                
                # PPを消費
                self.wild_pokemon.pokemon.move_pp[enemy_move_index][0] -= 1
                
                # ダメージ情報を保存
                self.pending_damage = enemy_damage
                self.damage_target = "player"
                # メッセージを設定
                self.battle_message = self._format_damage_message(
                    f"野生の{self.wild_pokemon.pokemon.name}", enemy_move, enemy_damage)
            
            self.battle_timer = pygame.time.get_ticks()
            self._reset_message_display()
            self.player_turn = True
    
    def _end_battle(self, player):
        """バトル終了処理"""
        # 倒れたのがプレイヤーのポケモンなら回復させる
        if player.pokemon[0].hp <= 0:
            player.pokemon[0].hp = player.pokemon[0].max_hp
            player.pokemon[0].display_hp = player.pokemon[0].max_hp  # 回復時はdisplay_hpも同期
        
        self.state = GameState.FIELD
        self.battle_end_flag = False
    
    def update_hp_animations(self, player):
        """HPアニメーションの更新"""
        if self.state != GameState.BATTLE:
            return
            
        # プレイヤーポケモンのHP
        if player.pokemon[0].display_hp > player.pokemon[0].hp:
            hp_diff = player.pokemon[0].display_hp - player.pokemon[0].hp
            decrease_amount = max(hp_diff * 0.05, GameConfig.HP_ANIMATION_SPEED)
            player.pokemon[0].display_hp -= decrease_amount
            if player.pokemon[0].display_hp < player.pokemon[0].hp:
                player.pokemon[0].display_hp = player.pokemon[0].hp
        
        # 敵ポケモンのHP
        if self.wild_pokemon and self.wild_pokemon.pokemon.display_hp > self.wild_pokemon.pokemon.hp:
            hp_diff = self.wild_pokemon.pokemon.display_hp - self.wild_pokemon.pokemon.hp
            decrease_amount = max(hp_diff * 0.05, GameConfig.HP_ANIMATION_SPEED)
            self.wild_pokemon.pokemon.display_hp -= decrease_amount
            if self.wild_pokemon.pokemon.display_hp < self.wild_pokemon.pokemon.hp:
                self.wild_pokemon.pokemon.display_hp = self.wild_pokemon.pokemon.hp
    
    def update_message_display(self):
        """メッセージ表示の更新"""
        if self.battle_state in [GameState.BATTLE_MESSAGE, GameState.BATTLE_ANIMATION]:
            current_time = pygame.time.get_ticks()
            
            # 文字表示タイマーが設定されていない場合は初期化
            if self.char_display_timer == 0:
                self.char_display_timer = current_time
                self.displayed_chars = 0
                self.full_message_displayed = False
            
            # アニメーション中はテキストをすぐに全て表示
            if self.battle_state == GameState.BATTLE_ANIMATION:
                self.displayed_chars = len(self.battle_message)
                self.full_message_displayed = True
            else:
                # 一定時間ごとに表示する文字数を増やす
                if not self.full_message_displayed and current_time - self.char_display_timer > GameConfig.MESSAGE_DISPLAY_SPEED:
                    self.displayed_chars += 1
                    self.char_display_timer = current_time
                    
                    # 全ての文字を表示したかチェック
                    if self.displayed_chars >= len(self.battle_message):
                        self.displayed_chars = len(self.battle_message)
                        self.full_message_displayed = True
    
    def get_displayed_message(self):
        """現在表示すべきメッセージを取得"""
        return self.battle_message[:self.displayed_chars]
    
    def _reset_message_display(self):
        """メッセージ表示をリセット"""
        self.displayed_chars = 0
        self.char_display_timer = 0
        self.full_message_displayed = False
    
    def _format_damage_message(self, pokemon_name, move_name, damage):
        """ダメージメッセージをフォーマット"""
        return f"{pokemon_name}の{move_name}!"