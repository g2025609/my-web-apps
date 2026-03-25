import math
import random
import js
from pyodide.ffi import create_proxy

class App:
    def __init__(self):
        self.dices = [1]
        self.rolling = False
        self.roll_count = 0
        self.target_rolls = 15
        self.total = 1
        self.dice_size = 100
        self._setup_done = False

    def get_html_layout(self):
        count = len(self.dices)
        return f'''
            <div style="text-align: center; background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; font-family: sans-serif;">
                
                <div id="result-box" style="margin-bottom: 20px; padding: 15px; background: #f0f7ff; border-radius: 10px; border: 2px dashed #3498db;">
                    <div style="font-size: 0.9rem; color: #7f8c8d;">合計値:</div>
                    <div id="dice-result" style="font-size: 2.5rem; font-weight: bold; color: #2980b9;">{self.total}</div>
                </div>

                <button id="roll-button" style="width: 100%; padding: 20px; background: #3498db; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; font-size: 1.5rem; box-shadow: 0 4px 0 #2980b9; margin-bottom: 20px;">
                    サイコロを振る
                </button>

                <div style="background: #f9f9f9; padding: 15px; border-radius: 10px;">
                    <div style="margin-bottom: 5px; font-size: 0.9rem; color: #555;">ダイスの個数</div>
                    <button onclick="window.changeDice(-1)" style="width:45px; height:45px; cursor:pointer; border-radius: 8px; border: 1px solid #ccc; background: white; font-size: 1.2rem;">-</button>
                    <span style="font-size: 20px; margin: 0 20px; font-weight: bold; min-width: 30px; display: inline-block;">
                        <span id="dice_num_display">{count}</span>
                    </span>
                    <button onclick="window.changeDice(1)" style="width:45px; height:45px; cursor:pointer; border-radius: 8px; border: 1px solid #ccc; background: white; font-size: 1.2rem;">+</button>
                </div>
                
                <input type="hidden" id="dice_count_val" value="{count}">
            </div>

            <script>
                // 個数変更時の処理
                window.changeDice = function(delta) {{
                    const input = document.getElementById('dice_count_val');
                    let val = parseInt(input.value) + delta;
                    if (val < 1) val = 1; 
                    if (val > 12) val = 12;
                    input.value = val;
                    document.getElementById('dice_num_display').innerText = val;
                    window.updateProjectData(); // Python側へ通知
                }}
            </script>
        '''

    def on_click(self):
        """サイコロを振るボタンが押された時の処理"""
        if not self.rolling:
            self.rolling = True
            self.roll_count = 0
            el = js.document.getElementById("dice-result")
            if el: el.innerText = "ROLLING..."

    def set_data(self, data):
        """個数変更などが通知された時の処理"""
        if "dice_count_val" in data:
            target = int(data["dice_count_val"])
            while len(self.dices) < target: self.dices.append(random.randint(1, 6))
            while len(self.dices) > target: self.dices.pop()
            self.update_total_display()

    def update(self):
        # ボタンのイベント登録（一度だけ実行）
        if not self._setup_done:
            btn = js.document.getElementById("roll-button")
            if btn:
                btn.onclick = create_proxy(lambda e: self.on_click())
                self._setup_done = True

        if self.rolling:
            # シャッフル中
            self.dices = [random.randint(1, 6) for _ in self.dices]
            self.roll_count += 1
            if self.roll_count >= self.target_rolls:
                self.rolling = False
                self.update_total_display()

    def update_total_display(self):
        self.total = sum(self.dices)
        el = js.document.getElementById("dice-result")
        if el: el.innerText = str(self.total)

    def get_draw_data(self):
        draw_data = []
        cols = 4
        size = self.dice_size
        gap = 25
        
        for i, val in enumerate(self.dices):
            row = i // cols
            col = i % cols
            # 中央揃えのための座標計算
            curr_cols = min(len(self.dices), cols)
            x = (col - (curr_cols-1)/2) * (size + gap)
            y = (row - ((len(self.dices)-1)//cols)/2) * (size + gap)

            # ダイスの外枠
            draw_data.append({
                "type": "rect", "color": "#2c3e50", 
                "width": size, "height": size, "lineWidth": 3,
                "x_off": x, "y_off": y
            })
            
            # 背景
            draw_data.append({
                "type": "arc", "color": "white", "radius": size/2 - 2, 
                "start": 0, "end": 2 * math.pi, "x_off": x, "y_off": y
            })

            # 出目
            draw_data.append({
                "type": "text", "text": str(val), "angle": 0, "x": 0, "y": size/8, 
                "color": "#e74c3c" if val == 1 else "#2c3e50", "x_off": x, "y_off": y
            })
            
        return draw_data

    def is_finished(self):
        return False