import math
import random
import js
from pyodide.ffi import create_proxy

class App:
    def __init__(self):
        self.items = ["ラーメン", "パスタ", "牛丼", "カレー", "寿司"]
        self.base_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6"]
        self.angle = 0
        self.speed = 0
        self.friction = 0.985
        self.active = False
        self.winner = ""
        self._setup_done = False

    def get_html_layout(self):
        items_text = "\n".join(self.items)
        return f'''
            <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; text-align: center; font-family: sans-serif;">
                <div id="result-box" style="margin-bottom: 20px; padding: 15px; background: #fff5f5; border-radius: 10px; border: 2px dashed #e74c3c;">
                    <div style="font-size: 0.8rem; color: #999; margin-bottom: 5px;">当選結果:</div>
                    <div id="result-text" style="font-size: 1.8rem; font-weight: bold; color: #e74c3c; min-height: 1.2em;">READY</div>
                </div>

                <button id="spin-button" style="width: 100%; padding: 20px; background: #e74c3c; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; font-size: 1.5rem; box-shadow: 0 4px 0 #c0392b; margin-bottom: 20px; transition: transform 0.1s;">
                    START!!
                </button>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

                <p style="margin-bottom: 8px; font-weight: bold; color: #555; font-size: 0.9rem;">ルーレット項目編集 (改行区切り)</p>
                <textarea id="items_input" rows="5" style="width: 100%; border: 1px solid #ccc; padding: 10px; border-radius: 8px; font-family: inherit; font-size: 14px; margin-bottom: 10px;">{items_text}</textarea>
                
                <button onclick="window.updateProjectData()" style="width: 100%; padding: 10px; background: #3498db; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.9rem;">
                    設定を反映
                </button>
            </div>
        '''

    def on_click(self):
        """スタートボタンが押された時の処理"""
        if not self.active:
            # 回転パラメータの設定
            self.speed = random.uniform(0.3, 0.45)
            self.active = True
            self.winner = ""
            # JSで直接「回転中」に書き換える
            el = js.document.getElementById("result-text")
            if el: el.innerText = "回転中..."

    def set_data(self, data):
        """「設定を反映」ボタンが押された時の処理"""
        if "items_input" in data:
            self.items = [x.strip() for x in data["items_input"].split('\n') if x.strip()]
            self.angle = 0
            self.speed = 0
            self.active = False
            self.winner = ""
            el = js.document.getElementById("result-text")
            if el: el.innerText = "READY"

    def update(self):
        # 初回のみボタンにイベントを登録（Run Actionの代わり）
        if not self._setup_done:
            btn = js.document.getElementById("spin-button")
            if btn:
                btn.onclick = create_proxy(lambda e: self.on_click())
                self._setup_done = True

        # 回転アニメーション
        if self.active:
            self.angle += self.speed
            self.speed *= self.friction
            if self.speed < 0.002:
                self.speed = 0
                self.active = False
                self.calc_winner()

    def calc_winner(self):
        num = len(self.items)
        if num == 0: return
        step = (2 * math.pi) / num
        # 針の位置(真上)にある項目を計算
        normalized_angle = (1.5 * math.pi - (self.angle % (2 * math.pi))) % (2 * math.pi)
        idx = int(normalized_angle / step)
        self.winner = self.items[idx % num]
        
        # JSを直接叩いて結果を表示
        el = js.document.getElementById("result-text")
        if el: el.innerText = self.winner

    def get_draw_data(self):
        draw_data = []
        num = len(self.items)
        if num == 0: return []
        step = (2 * math.pi) / num
        
        for i in range(num):
            a = self.angle + (i * step)
            draw_data.append({
                "type": "arc", 
                "color": self.base_colors[i % len(self.base_colors)], 
                "radius": 200, "start": a, "end": a + step, 
                "x_off": 0, "y_off": 0
            })
            # 項目名の描画
            draw_data.append({
                "type": "text", "text": self.items[i], 
                "angle": a + step/2, "x": 130, "y": 8, 
                "color": "white", "x_off": 0, "y_off": 0
            })
        
        # センターサークルと矢印
        draw_data.append({"type": "arc", "color": "white", "radius": 40, "start": 0, "end": 2 * math.pi, "x_off": 0, "y_off": 0})
        draw_data.append({"type": "text", "text": "▼", "angle": 0, "x": 0, "y": -210, "color": "#e74c3c", "x_off": 0, "y_off": 0})
            
        return draw_data

    def is_finished(self):
        # 常に監視を続けるためFalseを返す（またはアニメーション中か初期化中か）
        return False