import math
import random

class App:
    def __init__(self):
        self.dices = [1]
        self.rolling = False
        self.roll_count = 0
        self.target_rolls = 15
        self.total = 1
        # --- ここでダイスの大きさを一括管理 ---
        self.dice_size = 100  # 80から100に大きくしました

    def get_html_layout(self):
        count = len(self.dices)
        html = '''
            <div style="text-align: center; background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd;">
                <div style="margin-bottom: 15px;">
                    <button onclick="changeDice(-1)" style="width:40px; height:40px; cursor:pointer;">-</button>
                    <span style="font-size: 20px; margin: 0 15px; font-weight: bold;">
                        ダイスの数: <span id="dice_num_display">[[COUNT]]</span>
                    </span>
                    <button onclick="changeDice(1)" style="width:40px; height:40px; cursor:pointer;">+</button>
                </div>
                <input type="hidden" id="dice_count_val" value="[[COUNT]]">
                
                <div id="result-box" style="margin-top: 15px; padding: 15px; background: #f0f7ff; border-radius: 10px; border: 2px dashed #3498db;">
                    <div style="font-size: 0.9rem; color: #7f8c8d;">合計値:</div>
                    <div id="dice-result" style="font-size: 2.2rem; font-weight: bold; color: #2980b9;">[[TOTAL]]</div>
                </div>
            </div>
            <script>
                window.changeDice = function(delta) {
                    const input = document.getElementById('dice_count_val');
                    let val = parseInt(input.value) + delta;
                    if (val < 1) val = 1; if (val > 12) val = 12;
                    input.value = val;
                    document.getElementById('dice_num_display').innerText = val;
                    updateProjectData();
                }
            </script>
        '''
        return html.replace("[[COUNT]]", str(count)).replace("[[TOTAL]]", str(self.total))

    def set_data(self, data):
        if "dice_count_val" in data:
            target = int(data["dice_count_val"])
            while len(self.dices) < target: self.dices.append(random.randint(1, 6))
            while len(self.dices) > target: self.dices.pop()
            self.update_total_display()

    def on_click(self):
        if not self.rolling:
            self.rolling = True
            self.roll_count = 0
            import js
            js.document.getElementById("dice-result").innerText = "ROLLING..."

    def update(self):
        if self.rolling:
            self.dices = [random.randint(1, 6) for _ in self.dices]
            self.roll_count += 1
            if self.roll_count >= self.target_rolls:
                self.rolling = False
                self.update_total_display()

    def update_total_display(self):
        self.total = sum(self.dices)
        import js
        js.document.getElementById("dice-result").innerText = str(self.total)

    def get_draw_data(self):
        draw_data = []
        cols = 4
        size = self.dice_size  # この数値を変更するだけで全体の大きさが変わります
        gap = 25
        
        for i, val in enumerate(self.dices):
            row = i // cols
            col = i % cols
            x = (col - (min(len(self.dices), cols)-1)/2) * (size + gap)
            y = (row - ((len(self.dices)-1)//cols)/2) * (size + gap)

            # 1. ダイスの外枠 (四角形描画命令)
            draw_data.append({
                "type": "rect", 
                "color": "black", 
                "width": size, 
                "height": size, 
                "lineWidth": 3,
                "x_off": x, "y_off": y
            })
            
            # 2. ダイスの背景（白）
            draw_data.append({
                "type": "arc", "color": "white", "radius": size/2 - 2, 
                "start": 0, "end": 2 * math.pi, "x_off": x, "y_off": y
            })

            # 3. 出目の数値
            draw_data.append({
                "type": "text", "text": str(val), "angle": 0, "x": 0, "y": size/8, 
                "color": "#e74c3c" if val == 1 else "#2c3e50", "x_off": x, "y_off": y
            })
            
        return draw_data

    def is_finished(self):
        return not self.rolling