import math
import random

class App:
    def __init__(self):
        self.items = ["ラーメン", "パスタ", "牛丼", "カレー", "寿司"]
        self.base_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6"]
        self.angle = 0
        self.speed = 0
        self.friction = 0.985
        self.active = False
        self.winner = ""
        self.is_new_result = False # 結果が新しくなったかどうかのフラグ

    def get_html_layout(self):
        items_text = "\n".join(self.items)
        # HTML側に id="result-text" を持たせる
        html = '''
            <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; text-align: center;">
                <p style="margin-bottom: 8px; font-weight: bold; color: #555;">ルーレット項目編集 (改行区切り)</p>
                <textarea id="items_input" rows="5" style="width: 100%; border: 1px solid #ccc; padding: 10px; border-radius: 8px; font-family: inherit; font-size: 14px;">[[ITEMS]]</textarea>
                
                <button onclick="updateProjectData()" style="margin-top: 10px; width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    設定を反映
                </button>
                
                <div id="result-box" style="margin-top: 20px; padding: 15px; background: #fff5f5; border-radius: 10px; border: 2px dashed #e74c3c;">
                    <div style="font-size: 0.8rem; color: #999; margin-bottom: 5px;">当選結果:</div>
                    <div id="result-text" style="font-size: 1.8rem; font-weight: bold; color: #e74c3c; min-height: 1.2em;">READY</div>
                </div>
            </div>
        '''
        return html.replace("[[ITEMS]]", items_text)

    def set_data(self, data):
        if "items_input" in data:
            self.items = [x.strip() for x in data["items_input"].split('\n') if x.strip()]
            self.angle = 0
            self.speed = 0
            self.active = False
            self.winner = ""

    def on_click(self):
        if not self.active:
            self.speed = random.uniform(0.35, 0.55)
            self.active = True
            self.winner = ""
            # JSで「回転中」に書き換える（プラットフォーム経由ではなく直接操作）
            import js
            js.document.getElementById("result-text").innerText = "回転中..."

    def update(self):
        if self.active:
            self.angle += self.speed
            self.speed *= self.friction
            if self.speed < 0.002:
                self.speed = 0
                self.active = False
                self.calc_winner()

    def calc_winner(self):
        num = len(self.items)
        step = (2 * math.pi) / num
        normalized_angle = (1.5 * math.pi - (self.angle % (2 * math.pi))) % (2 * math.pi)
        idx = int(normalized_angle / step)
        self.winner = self.items[idx % num]
        
        # 【重要】計算が終わった瞬間に、JavaScriptを叩いてHTMLを更新する
        import js
        js.document.getElementById("result-text").innerText = self.winner

    def get_draw_data(self):
        draw_data = []
        num = len(self.items)
        if num == 0: return []
        step = (2 * math.pi) / num
        
        for i in range(num):
            a = self.angle + (i * step)
            draw_data.append({"type": "arc", "color": self.base_colors[i % len(self.base_colors)], "radius": 200, "start": a, "end": a + step, "x_off": 0, "y_off": 0})
            draw_data.append({"type": "text", "text": self.items[i], "angle": a + step/2, "x": 130, "y": 8, "color": "white", "x_off": 0, "y_off": 0})
        
        # センターサークルと矢印
        draw_data.append({"type": "arc", "color": "white", "radius": 50, "start": 0, "end": 2 * math.pi, "x_off": 0, "y_off": 0})
        draw_data.append({"type": "text", "text": "▼", "angle": 0, "x": 0, "y": -210, "color": "#e74c3c", "x_off": 0, "y_off": 0})

        # 停止時に中央にも表示
        if not self.active and self.speed == 0 and self.winner:
            draw_data.append({"type": "text", "text": self.winner, "angle": 0, "x": 0, "y": 10, "color": "#e74c3c", "x_off": 0, "y_off": 0})
            
        return draw_data

    def is_finished(self):
        return not self.active and self.speed == 0