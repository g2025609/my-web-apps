import math
import time
import js
from pyodide.ffi import create_proxy

class App:
    def __init__(self):
        # 内部状態
        self.start_time = 0
        self.elapsed_seconds = 0
        self.is_active = False
        self.bell_minutes = [8, 10, 12]
        self.bell_fired = [False, False, False]
        self._setup_done = False

    def get_html_layout(self):
        return f'''
            <div id="conf-timer-root" style="text-align: center; background: #1a1a1a; color: white; padding: 30px 20px; border-radius: 30px; font-family: sans-serif; width: 100%; box-shadow: 0 20px 50px rgba(0,0,0,0.5); box-sizing: border-box;">
                <h2 style="margin: 0 0 20px 0; color: #95a5a6; font-size: 1.2rem; letter-spacing: 2px;">CONFERENCE TIMER</h2>
                
                <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;">
                    <div style="background: #2c3e50; padding: 10px; border-radius: 12px; width: 75px;">
                        <div style="font-size: 0.7rem; color: #bdc3c7; margin-bottom: 5px;">1st Bell</div>
                        <input type="number" id="inp-bell1" value="{self.bell_minutes[0]}" style="width: 100%; background: #000; color: #fff; border: 1px solid #555; text-align: center; font-size: 1rem; border-radius: 5px;">
                    </div>
                    <div style="background: #2c3e50; padding: 10px; border-radius: 12px; width: 75px;">
                        <div style="font-size: 0.7rem; color: #bdc3c7; margin-bottom: 5px;">2nd Bell</div>
                        <input type="number" id="inp-bell2" value="{self.bell_minutes[1]}" style="width: 100%; background: #000; color: #fff; border: 1px solid #555; text-align: center; font-size: 1rem; border-radius: 5px;">
                    </div>
                    <div style="background: #2c3e50; padding: 10px; border-radius: 12px; width: 75px;">
                        <div style="font-size: 0.7rem; color: #bdc3c7; margin-bottom: 5px;">3rd Bell</div>
                        <input type="number" id="inp-bell3" value="{self.bell_minutes[2]}" style="width: 100%; background: #000; color: #fff; border: 1px solid #555; text-align: center; font-size: 1rem; border-radius: 5px;">
                    </div>
                </div>

                <!-- フォントサイズを調整し、はみ出しを防止 -->
                <div id="timer-display" style="font-size: 6.5rem; font-family: 'Courier New', monospace; font-weight: bold; margin: 15px 0; line-height: 1.1; text-shadow: 0 0 20px rgba(255,255,255,0.1); letter-spacing: -2px;">00:00</div>

                <div style="display: flex; gap: 15px; margin-top: 20px;">
                    <button id="btn-main-toggle" style="flex: 2; padding: 18px; font-size: 1.5rem; background: #27ae60; color: white; border: none; border-radius: 15px; cursor: pointer; font-weight: bold; transition: 0.2s;">START</button>
                    <button id="btn-main-reset" style="flex: 1; padding: 18px; font-size: 1.2rem; background: #c0392b; color: white; border: none; border-radius: 15px; cursor: pointer; opacity: 0.9;">RESET</button>
                </div>
            </div>
        '''

    def _trigger_bell_sound(self, count):
        js.window.eval(f"""
            (function() {{
                if (!window.A_CTX) window.A_CTX = new (window.AudioContext || window.webkitAudioContext)();
                if (window.A_CTX.state === 'suspended') window.A_CTX.resume();
                for(let i=0; i<{count}; i++) {{
                    setTimeout(() => {{
                        const o = window.A_CTX.createOscillator();
                        const g = window.A_CTX.createGain();
                        o.type = "sine"; o.frequency.setValueAtTime(1000, window.A_CTX.currentTime);
                        g.gain.setValueAtTime(0.3, window.A_CTX.currentTime);
                        g.gain.exponentialRampToValueAtTime(0.001, window.A_CTX.currentTime + 1.2);
                        o.connect(g); g.connect(window.A_CTX.destination);
                        o.start(); o.stop(window.A_CTX.currentTime + 1.2);
                    }}, i * 700);
                }}
            }})();
        """)

    def update(self):
        # ボタンへのイベント登録
        if not self._setup_done:
            t_btn = js.document.getElementById("btn-main-toggle")
            r_btn = js.document.getElementById("btn-main-reset")
            if t_btn and r_btn:
                def toggle_click(e):
                    if not self.is_active:
                        self.is_active = True
                        self.start_time = time.time() - self.elapsed_seconds
                        t_btn.innerText = "STOP"
                        t_btn.style.background = "#e67e22"
                        js.window.eval("if(window.A_CTX) window.A_CTX.resume();")
                    else:
                        self.is_active = False
                        t_btn.innerText = "START"
                        t_btn.style.background = "#27ae60"

                def reset_click(e):
                    self.is_active = False
                    self.elapsed_seconds = 0
                    self.bell_fired = [False] * 3
                    t_btn.innerText = "START"
                    t_btn.style.background = "#27ae60"
                    # 表示も即座にリセット
                    disp = js.document.getElementById("timer-display")
                    if disp: 
                        disp.innerText = "00:00"
                        disp.style.color = "white"

                t_btn.onclick = create_proxy(toggle_click)
                r_btn.onclick = create_proxy(reset_click)
                self._setup_done = True

        # タイマー進行とベル判定
        if self.is_active:
            self.elapsed_seconds = time.time() - self.start_time
            
            try:
                b_settings = [
                    float(js.document.getElementById("inp-bell1").value) * 60,
                    float(js.document.getElementById("inp-bell2").value) * 60,
                    float(js.document.getElementById("inp-bell3").value) * 60
                ]
            except: b_settings = [480, 600, 720]

            for i, target in enumerate(b_settings):
                if self.elapsed_seconds >= target and not self.bell_fired[i]:
                    self._trigger_bell_sound(i + 1)
                    self.bell_fired[i] = True

        # 表示の更新
        s = int(self.elapsed_seconds)
        time_text = f"{s // 60:02d}:{s % 60:02d}"
        display_el = js.document.getElementById("timer-display")
        
        if display_el:
            display_el.innerText = time_text
            try:
                limit = float(js.document.getElementById("inp-bell2").value) * 60
                warning = float(js.document.getElementById("inp-bell1").value) * 60
                if self.elapsed_seconds >= limit: display_el.style.color = "#e74c3c"
                elif self.elapsed_seconds >= warning: display_el.style.color = "#f1c40f"
                else: display_el.style.color = "white"
            except: pass

    def get_draw_data(self):
        # 画面背景の進捗サークル
        try:
            limit = float(js.document.getElementById("inp-bell2").value) * 60
            ratio = min(1.0, self.elapsed_seconds / max(1, limit))
        except: ratio = 0
        
        color = "#27ae60"
        if ratio >= 1.0: color = "#e74c3c"
        elif ratio >= 0.8: color = "#f1c40f"
        
        return [
            {"type": "arc", "color": "#333", "radius": 180, "start": 0, "end": 2*math.pi, "x_off": 0, "y_off": 0},
            {"type": "arc", "color": color, "radius": 180, "start": -math.pi/2, "end": -math.pi/2 + 2*math.pi*ratio, "x_off": 0, "y_off": 0},
            {"type": "arc", "color": "#1a1a1a", "radius": 165, "start": 0, "end": 2*math.pi, "x_off": 0, "y_off": 0}
        ]

    def set_data(self, data): pass
    def is_finished(self): return False
    def on_click(self): pass