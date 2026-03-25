import math
import time

class App:
    def __init__(self):
        self.start_time = 0
        self.elapsed_seconds = 0
        self.active = False
        self.is_paused = True
        self.bell_minutes = [8, 10, 12]
        self.bell_settings = [m * 60 for m in self.bell_minutes]
        self.bell_fired = [False] * len(self.bell_settings)

    def get_html_layout(self):
        return f'''
            <div style="text-align: center; background: #1a1a1a; color: white; padding: 25px; border-radius: 20px; font-family: sans-serif;">
                <h2 style="margin: 0 0 15px 0; color: #95a5a6; font-size: 1.2rem;">CONFERENCE TIMER</h2>
                
                <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; background: #2c3e50; padding: 15px; border-radius: 12px;">
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-size: 0.7rem; color: #bdc3c7;">1st (min)</span>
                        <input type="number" id="bell1" value="{self.bell_minutes[0]}" onchange="updateProjectData()" style="width: 50px; padding: 5px; border-radius: 5px; border: none; text-align: center;">
                    </div>
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-size: 0.7rem; color: #bdc3c7;">2nd (min)</span>
                        <input type="number" id="bell2" value="{self.bell_minutes[1]}" onchange="updateProjectData()" style="width: 50px; padding: 5px; border-radius: 5px; border: none; text-align: center;">
                    </div>
                    <div style="display: flex; flex-direction: column;">
                        <span style="font-size: 0.7rem; color: #bdc3c7;">3rd (min)</span>
                        <input type="number" id="bell3" value="{self.bell_minutes[2]}" onchange="updateProjectData()" style="width: 50px; padding: 5px; border-radius: 5px; border: none; text-align: center;">
                    </div>
                </div>

                <div id="display-time" style="font-size: 8rem; font-family: monospace; font-weight: bold; margin: 10px 0; line-height: 1;">
                    00:00
                </div>

                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button id="btn-toggle" onclick="toggleTimer()" style="flex: 2; padding: 20px; font-size: 1.5rem; background: #27ae60; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold;">
                        START
                    </button>
                    <button onclick="resetTimer()" style="flex: 1; padding: 20px; font-size: 1.2rem; background: #c0392b; color: white; border: none; border-radius: 12px; cursor: pointer;">
                        RESET
                    </button>
                </div>
                <input type="hidden" id="timer_sync" value="">
            </div>

            <script>
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                function playBell(count) {{
                    for(let i=0; i<count; i++) {{
                        setTimeout(() => {{
                            const osc = audioCtx.createOscillator();
                            const gain = audioCtx.createGain();
                            osc.type = "sine";
                            osc.frequency.setValueAtTime(1000, audioCtx.currentTime);
                            gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.2);
                            osc.connect(gain);
                            gain.connect(audioCtx.destination);
                            osc.start();
                            osc.stop(audioCtx.currentTime + 1.2);
                        }}, i * 700);
                    }}
                }}

                window.toggleTimer = function() {{
                    if (audioCtx.state === 'suspended') audioCtx.resume();
                    const input = document.getElementById('timer_sync');
                    const btn = document.getElementById("btn-toggle");
                    if (btn.innerText === "START") {{
                        input.value = "start";
                        btn.innerText = "STOP";
                        btn.style.background = "#e67e22";
                    }} else {{
                        input.value = "stop";
                        btn.innerText = "START";
                        btn.style.background = "#27ae60";
                    }}
                    updateProjectData();
                }};

                window.resetTimer = function() {{
                    document.getElementById('timer_sync').value = "reset";
                    updateProjectData();
                    const btn = document.getElementById("btn-toggle");
                    btn.innerText = "START";
                    btn.style.background = "#27ae60";
                    document.getElementById("display-time").style.color = "white";
                }};

                window.fireBell = function(count) {{ playBell(count); }};
            </script>
        '''

    def set_data(self, data):
        try:
            m1 = float(data.get("bell1", 8))
            m2 = float(data.get("bell2", 10))
            m3 = float(data.get("bell3", 12))
            self.bell_minutes = [m1, m2, m3]
            self.bell_settings = [m * 60 for m in self.bell_minutes]
        except: pass

        val = data.get("timer_sync", "")
        if val == "start":
            self.active = True
            self.is_paused = False
            self.start_time = time.time() - self.elapsed_seconds
        elif val == "stop":
            self.active = False
            self.is_paused = True
        elif val == "reset":
            self.elapsed_seconds = 0
            self.active = False
            self.is_paused = True
            self.bell_fired = [False] * len(self.bell_settings)
        data["timer_sync"] = ""

    def update(self):
        if self.active and not self.is_paused:
            self.elapsed_seconds = time.time() - self.start_time
            self.check_bells()
        self.update_ui_state()

    def check_bells(self):
        import js
        for i, target_time in enumerate(self.bell_settings):
            if self.elapsed_seconds >= target_time and not self.bell_fired[i]:
                js.fireBell(i + 1)
                self.bell_fired[i] = True

    def update_ui_state(self):
        import js
        display = self.format_min_sec(self.elapsed_seconds)
        try:
            el = js.document.getElementById("display-time")
            el.innerText = display
            if self.elapsed_seconds >= self.bell_settings[1]:
                el.style.color = "#e74c3c"
            elif self.elapsed_seconds >= self.bell_settings[0]:
                el.style.color = "#f1c40f"
            else:
                el.style.color = "white"
        except: pass

    def format_min_sec(self, seconds):
        s = int(seconds)
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"

    def get_draw_data(self):
        draw_data = []
        ratio = min(1.0, self.elapsed_seconds / max(1, self.bell_settings[1]))
        color = "#27ae60"
        if self.elapsed_seconds >= self.bell_settings[1]: color = "#e74c3c"
        elif self.elapsed_seconds >= self.bell_settings[0]: color = "#f1c40f"
        draw_data.append({"type": "arc", "color": "#333", "radius": 180, "start": 0, "end": 2*math.pi, "x_off": 0, "y_off": 0})
        draw_data.append({"type": "arc", "color": color, "radius": 180, "start": -math.pi/2, "end": -math.pi/2 + 2*math.pi*ratio, "x_off": 0, "y_off": 0})
        draw_data.append({"type": "arc", "color": "#1a1a1a", "radius": 165, "start": 0, "end": 2*math.pi, "x_off": 0, "y_off": 0})
        return draw_data

    def is_finished(self): return False
    def on_click(self): pass

# --- 自動実行用スクリプト ---
import js
def auto_run():
    # ページ内のRun Actionボタンを探して押す
    btn = js.document.querySelector("button") # 一番最初のボタン（通常はRun Action）
    # セレクタをより厳密にするなら: "button[style*='background: rgb(231, 76, 60)']" など
    if btn and "Run" in btn.innerText:
        btn.click()
    else:
        js.setTimeout(js.create_proxy(auto_run), 300)

auto_run()
