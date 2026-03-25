import math
import time

class App:
    def __init__(self):
        self.set_time = 0         # セットした合計秒数
        self.remaining_seconds = 0 # 残り秒数
        self.active = False        # タイマー動作中か
        self.last_update = 0
        self.alarm_playing = False # アラーム鳴動中か

    def get_html_layout(self):
        """
        タイマー専用UI。
        時間追加ボタン、スタート/ストップ、リセット。
        """
        html = f'''
            <div style="text-align: center; background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                
                <!-- デジタル時計表示 -->
                <div id="timer-digital" style="font-size: 3.5rem; font-weight: bold; color: #2c3e50; font-family: monospace; letter-spacing: 2px; margin-bottom: 20px;">
                    {self.format_time(self.remaining_seconds)}
                </div>

                <!-- 時間追加ボタン -->
                <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                    <button onclick="addTimerTime(3600)" style="flex:1; padding: 15px; font-size: 1.2rem; background: #95a5a6; color: white; border: none; border-radius: 10px; cursor: pointer; -webkit-tap-highlight-color: transparent;">+1h</button>
                    <button onclick="addTimerTime(60)" style="flex:1; padding: 15px; font-size: 1.2rem; background: #95a5a6; color: white; border: none; border-radius: 10px; cursor: pointer; -webkit-tap-highlight-color: transparent;">+1m</button>
                    <button onclick="addTimerTime(1)" style="flex:1; padding: 15px; font-size: 1.2rem; background: #95a5a6; color: white; border: none; border-radius: 10px; cursor: pointer; -webkit-tap-highlight-color: transparent;">+1s</button>
                </div>

                <!-- メイン操作ボタン -->
                <div style="display: flex; gap: 10px;">
                    <button id="btn-start-stop" onclick="toggleTimerActive()" style="flex:2; padding: 18px; font-size: 1.3rem; background: #27ae60; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; -webkit-tap-highlight-color: transparent;">
                        START
                    </button>
                    <button onclick="resetTimer()" style="flex:1; padding: 18px; font-size: 1.1rem; background: #bdc3c7; color: #333; border: none; border-radius: 12px; cursor: pointer; -webkit-tap-highlight-color: transparent;">
                        Reset
                    </button>
                </div>

                <!-- アラーム停止ボタン -->
                <button id="btn-alarm-stop" onclick="stopAlarmEffect()" style="display:none; width:100%; margin-top:15px; padding: 20px; font-size: 1.4rem; background: #e74c3c; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; animation: pulse 1s infinite; -webkit-tap-highlight-color: transparent;">
                    STOP ALARM
                </button>

                <input type="hidden" id="timer_data_sync" value="0">
            </div>

            <style>
                @keyframes pulse {{
                    0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }}
                    70% {{ transform: scale(1.05); box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }}
                    100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }}
                }}
            </style>

            <script>
                function jsFormatTime(totalSeconds) {{
                    const h = Math.floor(totalSeconds / 3600);
                    const m = Math.floor((totalSeconds % 3600) / 60);
                    const s = totalSeconds % 60;
                    return [h, m, s].map(v => v.toString().padStart(2, '0')).join(':');
                }}

                window.currentJsSeconds = 0;

                if(!window.timerAlarmAudio) {{
                    window.timerAlarmAudio = new Audio('./timer_project/alarm.mp3');
                    window.timerAlarmAudio.loop = true;
                }}

                window.addTimerTime = function(seconds) {{
                    if(window.timerAlarmAudio && !window.timerAlarmAudio.paused) return;
                    
                    window.currentJsSeconds += seconds;
                    document.getElementById("timer-digital").innerText = jsFormatTime(window.currentJsSeconds);
                    
                    const input = document.getElementById('timer_data_sync');
                    input.value = "add:" + seconds;
                    updateProjectData();
                    if (typeof render === 'function') render();
                }}

                window.toggleTimerActive = function() {{
                    if(window.timerAlarmAudio) {{
                        window.timerAlarmAudio.play().then(() => {{ window.timerAlarmAudio.pause(); }}).catch(e => {{}});
                    }}
                    const input = document.getElementById('timer_data_sync');
                    input.value = "toggle";
                    updateProjectData();
                    
                    // ボタンの表示を即座に切り替える（UX向上）
                    const btn = document.getElementById("btn-start-stop");
                    if (btn.innerText === "START") {{
                        btn.innerText = "STOP";
                        btn.style.background = "#e67e22";
                        if (typeof animate === 'function') animate();
                    }} else {{
                        btn.innerText = "START";
                        btn.style.background = "#27ae60";
                    }}
                }}

                window.resetTimer = function() {{
                    window.currentJsSeconds = 0;
                    const input = document.getElementById('timer_data_sync');
                    input.value = "reset";
                    updateProjectData();
                    document.getElementById("timer-digital").innerText = "00:00:00";
                    document.getElementById("timer-digital").style.color = "#2c3e50";
                    
                    const btn = document.getElementById("btn-start-stop");
                    btn.innerText = "START";
                    btn.style.background = "#27ae60";
                    
                    if (typeof render === 'function') render();
                }}

                window.playAlarmEffect = function() {{
                    if(window.timerAlarmAudio) {{
                        window.timerAlarmAudio.currentTime = 0;
                        window.timerAlarmAudio.play().catch(e => console.log("Audio Error:", e));
                    }}
                    document.getElementById('btn-alarm-stop').style.display = 'block';
                    document.getElementById('timer-digital').style.color = '#e74c3c';
                }}

                window.stopAlarmEffect = function() {{
                    if(window.timerAlarmAudio) {{
                        window.timerAlarmAudio.pause();
                        window.timerAlarmAudio.currentTime = 0;
                    }}
                    document.getElementById('btn-alarm-stop').style.display = 'none';
                    document.getElementById('timer-digital').style.color = '#2c3e50';
                    const input = document.getElementById('timer_data_sync');
                    input.value = "alarm_stop";
                    updateProjectData();
                    if (typeof render === 'function') render();
                }}
            </script>
        '''
        return html

    def set_data(self, data):
        command = data.get("timer_data_sync", "")
        
        if command.startswith("add:"):
            if not self.active and not self.alarm_playing:
                sec = int(command.split(":")[1])
                self.set_time += sec
                self.remaining_seconds = self.set_time

        elif command == "toggle":
            if self.remaining_seconds > 0 and not self.alarm_playing:
                self.active = not self.active
                if self.active:
                    self.last_update = time.time()

        elif command == "reset":
            self.active = False
            self.set_time = 0
            self.remaining_seconds = 0
            self.alarm_playing = False
            
        elif command == "alarm_stop":
            self.alarm_playing = False

    def on_click(self):
        import js
        js.toggleTimerActive()

    def update(self):
        if self.active and self.remaining_seconds > 0:
            now = time.time()
            dt = now - self.last_update
            self.remaining_seconds -= dt
            self.last_update = now
            
            if self.remaining_seconds <= 0:
                self.remaining_seconds = 0
                self.active = False
                self.trigger_alarm()
            
            import js
            js.window.currentJsSeconds = int(self.remaining_seconds)
            self.update_html_display()

    def update_html_display(self):
        import js
        try:
            js.document.getElementById("timer-digital").innerText = self.format_time(self.remaining_seconds)
            btn = js.document.getElementById("btn-start-stop")
            # Python側の状態に合わせてボタンを確定させる
            if self.active:
                btn.innerText = "STOP"
                btn.style.background = "#e67e22"
            else:
                btn.innerText = "START"
                btn.style.background = "#27ae60"
        except:
            pass

    def trigger_alarm(self):
        self.alarm_playing = True
        import js
        js.playAlarmEffect()

    def format_time(self, seconds):
        s = max(0, int(seconds))
        h = s // 3600
        m = (s % 3600) // 60
        s = s % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def get_draw_data(self):
        draw_data = []
        draw_data.append({
            "type": "arc", "color": "#ecf0f1", "radius": 180, 
            "start": 0, "end": 2 * math.pi, "x_off": 0, "y_off": 0
        })
        ratio = 0
        if self.set_time > 0:
            ratio = self.remaining_seconds / self.set_time
        
        color = "#3498db"
        if self.alarm_playing:
            color = "#e74c3c" if int(time.time() * 5) % 2 == 0 else "white"
            
        if ratio > 0 or self.alarm_playing:
            end_angle = -math.pi/2 + (2 * math.pi * ratio)
            if self.alarm_playing: end_angle = 1.5 * math.pi
            draw_data.append({
                "type": "arc", "color": color, "radius": 180, 
                "start": -math.pi/2, "end": end_angle, 
                "x_off": 0, "y_off": 0
            })
        draw_data.append({
            "type": "arc", "color": "white", "radius": 160, 
            "start": 0, "end": 2 * math.pi, "x_off": 0, "y_off": 0
        })
        return draw_data

    def is_finished(self):
        return not self.active and not self.alarm_playing