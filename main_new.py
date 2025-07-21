import pyxel
import random
import math

class HanafudaTetris:
    def __init__(self):
        # 画面サイズ
        self.WIDTH = 256
        self.HEIGHT = 240
        
        # ゲームフィールド設定
        self.FIELD_WIDTH = 8
        self.FIELD_HEIGHT = 6  # 高さを調整
        self.CARD_WIDTH = 20   # 新しい画像サイズ
        self.CARD_HEIGHT = 32  # 新しい画像サイズ
        self.FIELD_X = (self.WIDTH - self.FIELD_WIDTH * self.CARD_WIDTH) // 2
        self.FIELD_Y = 30
        
        # ゲーム状態
        self.game_state = "title"  # title, playing, game_over
        self.score = 0
        self.combo = 0
        self.bonus_time = 0
        self.pause_time = 0
        self.spawn_delay = 0
        self.spawn_delay = 0  # 新しい花札生成の遅延時間
        
        # タイトル画面用のアニメーション
        self.title_animation_frame = 0
        self.title_demo_cards = self.generate_demo_cards()
        
        # フィールド（0は空、1-48は花札の種類）
        self.field = [[0 for _ in range(self.FIELD_WIDTH)] for _ in range(self.FIELD_HEIGHT)]
        
        # 落下中の花札
        self.falling_card = None
        self.falling_x = self.FIELD_WIDTH // 2
        self.falling_y = 0
        self.drop_timer = 0
        self.drop_speed = 60  # フレーム数
        
        # 花札データ（月ごとに4枚ずつ）
        self.hanafuda_data = self.create_hanafuda_data()
        
        # 次の花札
        self.next_card = random.randint(1, 48)
        
        # 演出用
        self.effect_particles = []
        
        # Pyxelを初期化
        pyxel.init(self.WIDTH, self.HEIGHT, title="Hanafuda Tetris")
        
        # リソースファイルを読み込み（新しいファイル名）
        pyxel.load("my_resource.pyxres")
        
        # 花札の色データを設定
        self.setup_colors()
        
        pyxel.run(self.update, self.draw)
    
    def generate_demo_cards(self):
        """タイトル画面用のデモカード配置を生成"""
        demo_cards = []
        # いくつかのランダムな花札を配置
        for _ in range(12):
            demo_cards.append({
                'x': random.randint(0, self.WIDTH - self.CARD_WIDTH),
                'y': random.randint(0, self.HEIGHT - self.CARD_HEIGHT),
                'card_id': random.randint(1, 48),
                'rotation': random.uniform(0, 360),
                'scale': random.uniform(0.5, 1.5)
            })
        return demo_cards
    
    def setup_colors(self):
        """花札用の色パレットを設定"""
        # 基本的な色設定（Pyxelの16色パレット使用）
        self.colors = {
            '春': 8,   # 赤
            '夏': 11,  # 緑
            '秋': 10,  # 黄
            '冬': 12,  # 青
            '光': 7,   # 白
            '短': 9,   # オレンジ
            '種': 3,   # 紫
            'カス': 6   # グレー
        }
    
    def create_hanafuda_data(self):
        """花札データを作成"""
        # 月ごとの花札（1月=1-4, 2月=5-8, ...）
        data = {}
        for month in range(1, 13):
            for card in range(1, 5):
                card_id = (month - 1) * 4 + card
                data[card_id] = {
                    'month': month,
                    'type': self.get_card_type(month, card),
                    'color': self.get_card_color(month, card)
                }
        return data
    
    def get_card_type(self, month, card):
        """カードタイプを取得"""
        # 光札（ひかりふだ）
        if (month == 1 and card == 1) or (month == 3 and card == 1) or \
           (month == 8 and card == 1) or (month == 11 and card == 1) or \
           (month == 12 and card == 1):
            return "光"
        # 短冊（たんざく）
        elif card == 2:
            return "短"
        # 種札（たねふだ）
        elif card == 3:
            return "種"
        # カス札
        else:
            return "カス"
    
    def get_card_color(self, month, card):
        """カードの色を取得"""
        # 赤短
        if month in [1, 2, 3] and card == 2:
            return "赤"
        # 青短
        elif month in [6, 9, 10] and card == 2:
            return "青"
        else:
            return "通常"
    
    def get_card_season_color(self, month):
        """季節による色を取得"""
        if month <= 3:
            return '春'
        elif month <= 6:
            return '夏'
        elif month <= 9:
            return '秋'
        else:
            return '冬'
    
    def get_card_image_pos(self, card_id):
        """カードIDから画像位置を取得（新しい配置方式）"""
        # card_id: 1-48
        # 1-4: 1月, 5-8: 2月, ...
        month = ((card_id - 1) // 4) + 1
        card_in_month = ((card_id - 1) % 4) + 1
        
        # 新しい配置方式での座標計算
        # 1月1枚目(0,0),2枚目(20,0),3枚目(40,0),4枚目(60,0)
        # 2月1枚目(80,0),2枚目(100,0),3枚目(120,0),4枚目(140,0)
        # 3月1枚目(0,32),2枚目(20,32),3枚目(40,32),4枚目(60,32)
        # 4月1枚目(80,32),2枚目(100,32),3枚目(120,32),4枚目(140,32)
        
        # 行と列の計算
        row = (month - 1) // 2  # 2月ごとに行が変わる
        col_offset = ((month - 1) % 2) * 4  # 奇数月は0、偶数月は4列目から
        
        # 座標計算
        x = (col_offset + card_in_month - 1) * 20
        y = row * 32
        
        # 全てイメージバンク0に配置
        bank = 0
        
        return bank, x, y
    
    def start_game(self):
        """ゲームを開始"""
        self.game_state = "playing"
        self.score = 0
        self.combo = 0
        self.bonus_time = 0
        self.pause_time = 0
        self.spawn_delay = 0
        self.field = [[0 for _ in range(self.FIELD_WIDTH)] for _ in range(self.FIELD_HEIGHT)]
        self.drop_timer = 0
        self.drop_speed = 60
        self.effect_particles = []
        self.next_card = random.randint(1, 48)
        self.spawn_new_card()
        pyxel.playm(0, )
    
    def spawn_new_card(self):
        """新しい花札を生成"""
        self.falling_card = self.next_card
        self.falling_x = self.FIELD_WIDTH // 2
        self.falling_y = 0
        self.next_card = random.randint(1, 48)
        
        # ゲームオーバーチェック
        if self.field[0][self.falling_x] != 0:
            self.game_state = "game_over"
            pyxel.play(1, 0)
    
    def update(self):
        if self.game_state == "title":
            self.update_title()
        elif self.game_state == "playing":
            self.update_game()
        elif self.game_state == "game_over":
            self.update_game_over()
    
    def update_title(self):
        """タイトル画面の更新"""
        self.title_animation_frame += 1
        
        # デモカードのアニメーション
        for card in self.title_demo_cards:
            card['rotation'] += 0.5
            card['x'] += math.sin(self.title_animation_frame * 0.01 + card['card_id']) * 0.2
            card['y'] += math.cos(self.title_animation_frame * 0.01 + card['card_id']) * 0.2
            
            # 画面外に出たら反対側に移動
            if card['x'] < -self.CARD_WIDTH:
                card['x'] = self.WIDTH
            elif card['x'] > self.WIDTH:
                card['x'] = -self.CARD_WIDTH
            if card['y'] < -self.CARD_HEIGHT:
                card['y'] = self.HEIGHT
            elif card['y'] > self.HEIGHT:
                card['y'] = -self.CARD_HEIGHT
        
        # 入力処理
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.start_game()
    
    def update_game(self):
        # ボーナスタイム・一時停止時間・生成遅延時間の更新
        if self.bonus_time > 0:
            self.bonus_time -= 1
        if self.pause_time > 0:
            self.pause_time -= 1
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            # 生成遅延が終了したら新しい花札を生成
            if self.spawn_delay == 0 and self.falling_card is None:
                self.spawn_new_card()
        
        # 入力処理（一時停止中や生成遅延中は入力を制限）
        if self.pause_time <= 0 and self.spawn_delay <= 0:
            self.handle_input()
        
        # 花札の落下処理（一時停止中や生成遅延中は落下しない）
        if self.pause_time <= 0 and self.spawn_delay <= 0:
            self.drop_timer += 1
            if self.drop_timer >= self.drop_speed:
                self.drop_card()
                self.drop_timer = 0
        
        # 演出パーティクルの更新
        self.update_particles()
        
        # 落下速度の調整
        self.drop_speed = max(10, 60 - self.score // 1000)
    
    def handle_input(self):
        """入力処理"""
        # 左右移動
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) and self.falling_x > 0:
            if self.can_move(self.falling_x - 1, self.falling_y):
                self.falling_x -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) and self.falling_x < self.FIELD_WIDTH - 1:
            if self.can_move(self.falling_x + 1, self.falling_y):
                self.falling_x += 1
        
        # 高速落下
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):# or pyxel.btn(pyxel.KEY_DOWN):
            self.drop_timer = self.drop_speed
        
        # リスタート
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.restart_game()
    
    def can_move(self, x, y):
        """移動可能かチェック"""
        if x < 0 or x >= self.FIELD_WIDTH or y >= self.FIELD_HEIGHT:
            return False
        if y < 0:
            return True
        return self.field[y][x] == 0
    
    def drop_card(self):
        """花札を1マス下に落とす"""
        if self.can_move(self.falling_x, self.falling_y + 1):
            self.falling_y += 1
        else:
            # 花札を固定
            self.field[self.falling_y][self.falling_x] = self.falling_card
            pyxel.play(3, 5)
            
            # 消去チェック
            self.check_and_remove_cards()
            
            # 新しい花札を生成（0.5秒の遅延付き）
            self.spawn_delay = 30  # 60fps × 0.5秒 = 30フレーム
            self.falling_card = None  # 一時的に落下中の花札を無効化
    
    def find_connected_cards(self, start_x, start_y, target_month, visited):
        """指定された月の花札で連結された領域を探索（フラッドフィル）"""
        # 範囲外チェック
        if (start_x < 0 or start_x >= self.FIELD_WIDTH or 
            start_y < 0 or start_y >= self.FIELD_HEIGHT):
            return []
        
        # 既に訪問済みかチェック
        if (start_x, start_y) in visited:
            return []
        
        # 空のマスまたは異なる月の花札はスキップ
        if self.field[start_y][start_x] == 0:
            return []
        
        card_month = self.hanafuda_data[self.field[start_y][start_x]]['month']
        if card_month != target_month:
            return []
        
        # 現在の位置を訪問済みに追加
        visited.add((start_x, start_y))
        connected = [(start_x, start_y)]
        
        # 4方向（上下左右）を探索
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = start_x + dx, start_y + dy
            connected.extend(self.find_connected_cards(new_x, new_y, target_month, visited))
        
        return connected
    
    def check_and_remove_cards(self):
        """花札の消去チェック（縦横連結判定）"""
        removed = False
        combo_multiplier = 1
        
        while True:
            to_remove = set()
            visited = set()
            
            # 全てのマスをチェック
            for y in range(self.FIELD_HEIGHT):
                for x in range(self.FIELD_WIDTH):
                    if self.field[y][x] != 0 and (x, y) not in visited:
                        card_month = self.hanafuda_data[self.field[y][x]]['month']
                        
                        # 連結された同じ月の花札を探索
                        connected = self.find_connected_cards(x, y, card_month, visited)
                        
                        # 3枚以上連結されていれば消去対象に追加
                        if len(connected) >= 3:
                            to_remove.update(connected)
            
            # 特殊役のチェック
            special_removes = self.check_special_combinations()
            to_remove.update(special_removes)
            
            if not to_remove:
                break
            
            # 花札を消去
            points = self.calculate_points(to_remove)
            self.score += points * combo_multiplier * (2 if self.bonus_time > 0 else 1)
            pyxel.play(3, 4)
            
            # 演出パーティクルを生成
            for x, y in to_remove:
                self.create_particles(x, y)
                self.field[y][x] = 0
            
            # 花札を落下
            self.drop_cards()
            
            # コンボ倍率を増加
            combo_multiplier *= 2
            removed = True
        
        if removed:
            self.combo += 1
            # 花札消去時に1秒間の一時停止を設定
            self.pause_time = 30  # 30fps × 1秒 = 30フレーム
        else:
            self.combo = 0
    
    def check_special_combinations(self):
        """特殊役のチェック"""
        to_remove = set()
        special_bonus = 0
        
        # フィールド上の全ての花札を収集
        cards_on_field = {}  # card_id -> [(x, y), ...]
        for y in range(self.FIELD_HEIGHT):
            for x in range(self.FIELD_WIDTH):
                if self.field[y][x] != 0:
                    card_id = self.field[y][x]
                    if card_id not in cards_on_field:
                        cards_on_field[card_id] = []
                    cards_on_field[card_id].append((x, y))
        
        # 光札の位置を取得
        hikari_cards = {}  # month -> [(x, y), ...]
        for card_id, positions in cards_on_field.items():
            month = ((card_id - 1) // 4) + 1
            card_in_month = ((card_id - 1) % 4) + 1
            if card_in_month == 1:  # 各月の1枚目
                hikari_cards[month] = positions
        
        # 五光チェック（1月1枚目＋3月1枚目＋8月1枚目＋11月1枚目＋12月1枚目）
        goko_months = [1, 3, 8, 11, 12]
        goko_positions = []
        for month in goko_months:
            if month in hikari_cards:
                goko_positions.extend(hikari_cards[month])
        
        if len(goko_positions) >= 5:
            to_remove.update(goko_positions)
            special_bonus += 3000
        
        # 雨四光チェック（11月1枚目(必須)＋1月1枚目or3月1枚目or8月1枚目or12月1枚目から3枚）
        elif 11 in hikari_cards:
            ame_shiko_positions = hikari_cards[11][:]
            ame_shiko_months = [1, 3, 8, 12]
            for month in ame_shiko_months:
                if month in hikari_cards:
                    ame_shiko_positions.extend(hikari_cards[month])
            
            if len(ame_shiko_positions) >= 4:
                to_remove.update(ame_shiko_positions)
                special_bonus += 1500
        
        # 四光チェック（1月1枚目or3月1枚目or8月1枚目or12月1枚目の4枚）
        elif len(goko_positions) >= 4:
            to_remove.update(goko_positions)
            special_bonus += 1200
        
        # 三光チェック（1月1枚目or3月1枚目or8月1枚目or12月1枚目から3枚）
        elif len(goko_positions) >= 3:
            to_remove.update(goko_positions)
            special_bonus += 800
        
        # 猪鹿蝶チェック（6月1枚目＋7月1枚目＋10月1枚目）
        inoshikacho_months = [6, 7, 10]
        inoshikacho_positions = []
        inoshikacho_found = True
        for month in inoshikacho_months:
            if month in hikari_cards:
                inoshikacho_positions.extend(hikari_cards[month])
            else:
                inoshikacho_found = False
                break
        
        if inoshikacho_found and len(inoshikacho_positions) >= 3:
            to_remove.update(inoshikacho_positions)
            special_bonus += 1000
        
        # 花見で一杯チェック（3月1枚目＋9月1枚目）
        hanami_months = [3, 9]
        hanami_positions = []
        hanami_found = True
        for month in hanami_months:
            if month in hikari_cards:
                hanami_positions.extend(hikari_cards[month])
            else:
                hanami_found = False
                break
        
        if hanami_found and len(hanami_positions) >= 2:
            to_remove.update(hanami_positions)
            special_bonus += 400
        
        # 月見で一杯チェック（8月1枚目＋9月1枚目）
        tsukimi_months = [8, 9]
        tsukimi_positions = []
        tsukimi_found = True
        for month in tsukimi_months:
            if month in hikari_cards:
                tsukimi_positions.extend(hikari_cards[month])
            else:
                tsukimi_found = False
                break
        
        if tsukimi_found and len(tsukimi_positions) >= 2:
            to_remove.update(tsukimi_positions)
            special_bonus += 400
        
        # 青短・赤短のチェック
        blue_tan = []
        red_tan = []
        
        for y in range(self.FIELD_HEIGHT):
            for x in range(self.FIELD_WIDTH):
                if self.field[y][x] != 0:
                    card_data = self.hanafuda_data[self.field[y][x]]
                    if card_data['type'] == '短' and card_data['color'] == '青':
                        blue_tan.append((x, y))
                    elif card_data['type'] == '短' and card_data['color'] == '赤':
                        red_tan.append((x, y))
        
        if len(blue_tan) >= 3:
            to_remove.update(blue_tan)
            special_bonus += 500
        if len(red_tan) >= 3:
            to_remove.update(red_tan)
            special_bonus += 500
        
        # 特殊役ボーナスをスコアに加算
        if special_bonus > 0:
            self.score += special_bonus * (2 if self.bonus_time > 0 else 1)
            # 特殊役達成時はボーナスタイムを追加
            self.bonus_time += 300  # 5秒間
        
        return to_remove
    
    def calculate_points(self, removed_positions):
        """得点計算"""
        count = len(removed_positions)
        
        # 基本得点
        if count == 3:
            return 100
        elif count == 4:
            return 200
        elif count >= 5:
            return 300
        
        return 0
    
    def drop_cards(self):
        """花札を重力で落下"""
        for x in range(self.FIELD_WIDTH):
            # 下から上へスキャン
            write_y = self.FIELD_HEIGHT - 1
            for read_y in range(self.FIELD_HEIGHT - 1, -1, -1):
                if self.field[read_y][x] != 0:
                    self.field[write_y][x] = self.field[read_y][x]
                    if write_y != read_y:
                        self.field[read_y][x] = 0
                    write_y -= 1
    
    def create_particles(self, x, y):
        """パーティクル生成"""
        for _ in range(5):
            self.effect_particles.append({
                'x': x * self.CARD_WIDTH + self.FIELD_X + self.CARD_WIDTH // 2,
                'y': y * self.CARD_HEIGHT + self.FIELD_Y + self.CARD_HEIGHT // 2,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'life': 30,
                'max_life': 30
            })
    
    def update_particles(self):
        """パーティクル更新"""
        for particle in self.effect_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # 重力
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.effect_particles.remove(particle)
    
    def update_game_over(self):
        """ゲームオーバー時の更新"""
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.restart_game()
            #pyxel.playm(0, )
    
    def restart_game(self):
        """ゲームリスタート"""
        self.game_state = "title"
        self.score = 0
        self.combo = 0
        self.bonus_time = 0
        self.pause_time = 0
        self.field = [[0 for _ in range(self.FIELD_WIDTH)] for _ in range(self.FIELD_HEIGHT)]
        self.drop_timer = 0
        self.drop_speed = 60
        self.effect_particles = []
        self.next_card = random.randint(1, 48)
        self.spawn_new_card()
        #pyxel.playm(0, )
    
    def draw(self):
        pyxel.cls(0)
        
        if self.game_state == "title":
            self.draw_title()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "game_over":
            self.draw_game_over()
    
    def draw_title(self):
        """タイトル画面を描画"""
        # 背景のデモカード（薄く表示）
        for card in self.title_demo_cards:
            bank, img_x, img_y = self.get_card_image_pos(card['card_id'])
            # 薄く表示するため、透明度を下げる（グレーアウト）
            pyxel.blt(int(card['x']), int(card['y']), bank, img_x, img_y, 
                     self.CARD_WIDTH, self.CARD_HEIGHT, 0)
        
        # タイトルロゴ
        title_color = pyxel.frame_count % 16 #14 if (self.title_animation_frame // 30) % 2 == 0 else 10
        pyxel.text(self.WIDTH // 2 - 20, 60, "HANAFUDA", title_color)
        pyxel.text(self.WIDTH // 2 - 16, 75, "TETRIS", title_color)
        
        # サブタイトル
        pyxel.text(self.WIDTH // 2 - 45, 100, "Japanese Card Puzzle", 7)
        
        # 説明文
        instructions = [
            "Match 3+ cards of same month",
            "Special combos for bonus!",
            "",
            "Controls:",
            "L/R: Move   DOWN: Drop",
            "Enter or A: Restart",
            "",
            "Press Enter or A to Start"
        ]
        
        start_y = 130
        for i, text in enumerate(instructions):
            color = 7 if text != "" else 0
            if "Press Enter" in text:
                # 点滅効果
                color = 14 if (self.title_animation_frame // 20) % 2 == 0 else 6
            pyxel.text(self.WIDTH // 2 - len(text) * 2, start_y + i * 8, text, color)
        
        # 特殊役の説明（小さく）
        special_info = [
            "Special Combos:",
            "Hikari(5): 3000pts",
            "Inoshikacho: 1000pts",
            "Hanami/Tsukimi: 400pts"
        ]
        
        for i, text in enumerate(special_info):
            color = 6 if i == 0 else 5
            pyxel.text(5, 200 + i * 8, text, color)
        
        # クレジット表示
        pyxel.text(190, 217, "(V)1.4", 7)
        pyxel.text(190, 225, "(C)2025 Saizo", 7)

    def draw_game(self):
        """ゲーム画面描画"""
        # フィールドの枠
        pyxel.rectb(self.FIELD_X - 1, self.FIELD_Y - 1, 
                   self.FIELD_WIDTH * self.CARD_WIDTH + 2, 
                   self.FIELD_HEIGHT * self.CARD_HEIGHT + 2, 7)
        
        # フィールドの花札
        for y in range(self.FIELD_HEIGHT):
            for x in range(self.FIELD_WIDTH):
                if self.field[y][x] != 0:
                    self.draw_card(x, y, self.field[y][x])
        
        # 落下中の花札
        if self.falling_card is not None:
            self.draw_card(self.falling_x, self.falling_y, self.falling_card)
        
        # パーティクル描画
        for particle in self.effect_particles:
            alpha = particle['life'] / particle['max_life']
            color = 14 if alpha > 0.5 else 6
            pyxel.pset(int(particle['x']), int(particle['y']), color)
        
        # UI描画
        self.draw_ui()
    
    def draw_card(self, x, y, card_id):
        """花札を描画"""
        screen_x = self.FIELD_X + x * self.CARD_WIDTH
        screen_y = self.FIELD_Y + y * self.CARD_HEIGHT
        
        # 画像位置を取得
        bank, img_x, img_y = self.get_card_image_pos(card_id)
        
        # 花札画像を描画
        pyxel.blt(screen_x, screen_y, bank, img_x, img_y, 
                 self.CARD_WIDTH, self.CARD_HEIGHT, 0)
        
        # デバッグ用：月数を表示
        if pyxel.btn(pyxel.KEY_D):
            month = self.hanafuda_data[card_id]['month']
            pyxel.text(screen_x + 2, screen_y + 2, str(month), 7)
    
    def draw_ui(self):
        """UI描画"""
        # スコア
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        
        # コンボ
        if self.combo > 0:
            color = 14 if self.combo < 5 else 8
            pyxel.text(5, 15, f"COMBO: {self.combo}", color)
        
        # ボーナスタイム
        if self.bonus_time > 0:
            color = 14 if (self.bonus_time // 10) % 2 == 0 else 8
            pyxel.text(5, 25, "BONUS TIME", color)
        
        # 次の花札表示
        pyxel.text(self.WIDTH - 40, 5, "NEXT:", 7)
        if self.next_card:
            bank, img_x, img_y = self.get_card_image_pos(self.next_card)
            pyxel.blt(self.WIDTH - 40, 15, bank, img_x, img_y, 
                     self.CARD_WIDTH, self.CARD_HEIGHT, 0)
            
            # 次の花札の月を表示
            month = self.hanafuda_data[self.next_card]['month']
            card_type = self.hanafuda_data[self.next_card]['type']
            pyxel.text(self.WIDTH - 40, 50, f"Month: {month}", 7)
            #pyxel.text(self.WIDTH - 40, 60, f"Type: {card_type}", 7)
        
        # 操作説明
        controls = [
            "L/R: Move",
            "DOWN: Drop",
            "Enter or A: Reset"
        ]
        
        for i, text in enumerate(controls):
            pyxel.text(5, self.HEIGHT - 30 + i * 8, text, 6)
        
        # 一時停止中の表示
        if self.pause_time > 0:
            color = pyxel.frame_count % 16 #14 if (self.bonus_time // 10) % 2 == 0 else 8
            pyxel.text(self.WIDTH // 2 - 10, self.HEIGHT // 2, "NICE!", color)
    
    def draw_game_over(self):
        """ゲームオーバー画面描画"""
        # 背景を暗く
        pyxel.cls(0)
        
        # ゲームオーバーメッセージ
        pyxel.text(self.WIDTH // 2 - 35, self.HEIGHT // 2 - 20, "GAME OVER", 8)
        pyxel.text(self.WIDTH // 2 - 30, self.HEIGHT // 2 - 5, f"SCORE: {self.score}", 7)
        pyxel.text(self.WIDTH // 2 - 30, self.HEIGHT // 2 + 5, f"COMBO: {self.combo}", 7)
        
        # リスタート案内
        color = 14 if (pyxel.frame_count // 30) % 2 == 0 else 6
        pyxel.text(self.WIDTH // 2 - 40, self.HEIGHT // 2 + 20, "Press Enter or A to Restart", color)
        
        # 最終成績
        achievements = []
        if self.score >= 10000:
            achievements.append("Fantastic!")
        elif self.score >= 5000:
            achievements.append("Excellent!")
        elif self.score >= 1000:
            achievements.append("Good!")
        
        if self.combo >= 10:
            achievements.append("Combo Master!")
        
        for i, achievement in enumerate(achievements):
            pyxel.text(self.WIDTH // 2 - len(achievement) * 2, 
                      self.HEIGHT // 2 + 35 + i * 8, achievement, 10)

# ゲーム実行
if __name__ == "__main__":
    HanafudaTetris()