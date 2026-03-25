import js
from pyodide.ffi import create_proxy

class App:
    def __init__(self):
        self.storage_key = "absolute_memo_v6"
        self._is_initialized = False

    def get_html_layout(self):
        # メモ帳本体のHTML
        return f'''
            <div id="memo-pad-container" style="text-align: center; background: #ffffff; padding: 20px; border: 3px solid #333; border-radius: 20px; width: 100%; max-width: 500px; margin: 0 auto 20px auto; box-shadow: 10px 10px 0px #aaa; box-sizing: border-box; font-family: sans-serif;">
                <h2 style="margin: 0 0 10px 0; font-family: monospace; font-size: 1.1rem;">> MEMO_SYSTEM_V6</h2>
                
                <textarea id="memo-input-box" placeholder="ここに書き込んでください..." 
                    style="width: 100%; height: 180px; padding: 15px; border: 2px solid #333; border-radius: 10px; font-size: 16px; box-sizing: border-box; background: #f9f9f9; display: block; margin-bottom: 10px;"></textarea>
                
                <button id="final-save-btn" style="width: 100%; padding: 12px; font-size: 16px; background: #2ecc71; color: white; border: none; border-bottom: 4px solid #27ae60; border-radius: 10px; cursor: pointer; font-weight: bold;">
                    💾 保存する
                </button>
                
                <div id="debug-log" style="margin-top: 8px; font-family: monospace; font-size: 11px; color: #e67e22; min-height: 1.2em;"></div>
            </div>
        '''

    def update(self):
        # 1. 位置の移動と初期設定
        if not self._is_initialized:
            container = js.document.getElementById("memo-pad-container")
            main_area = js.document.getElementById("main")
            title_el = js.document.getElementById("title")

            if container and main_area:
                # キャンバスより上、タイトルのすぐ下に移動させる
                if title_el and title_el.nextSibling:
                    main_area.insertBefore(container, title_el.nextSibling)
                else:
                    main_area.prepend(container)

            target_area = js.document.getElementById("memo-input-box")
            target_btn = js.document.getElementById("final-save-btn")

            if target_area and target_btn:
                # 前回のデータを読み込む
                try:
                    saved = js.window.localStorage.getItem(self.storage_key)
                    if saved is not None:
                        target_area.value = saved
                except:
                    pass

                # 保存ボタンのクリックイベント
                def on_click_save(event):
                    current_text = js.document.getElementById("memo-input-box").value
                    js.window.localStorage.setItem(self.storage_key, current_text)
                    
                    log_el = js.document.getElementById("debug-log")
                    if log_el:
                        log_el.innerText = "SAVED SUCCESSFULLY"
                        js.window.setTimeout(create_proxy(lambda: self._clear_log()), 2000)

                target_btn.onclick = create_proxy(on_click_save)
                self._is_initialized = True

    def _clear_log(self):
        log = js.document.getElementById("debug-log")
        if log: log.innerText = ""

    def on_click(self): pass
    def get_draw_data(self): return []
    def set_data(self, data): pass