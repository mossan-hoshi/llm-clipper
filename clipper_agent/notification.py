"""
通知モジュール
非侵入的な通知ウィンドウを表示する機能を提供します。
"""

import platform
import tkinter as tk
import threading
import time
from tkinter import font as tkfont


class NotificationWindow:
    """非侵入的な通知ウィンドウクラス"""

    def __init__(self, title, message, timeout=5):
        """
        通知ウィンドウを初期化します。

        Args:
            title (str): 通知のタイトル
            message (str): 通知のメッセージ
            timeout (int): 通知の表示時間（秒）
        """
        self.title = title
        self.message = message
        self.timeout = timeout
        self.window = None

    def show(self):
        """通知ウィンドウを表示します"""
        # メインスレッドでウィンドウを作成
        self.window = tk.Tk()
        self.window.withdraw()  # 一旦非表示にして設定

        # ウィンドウの設定
        self.window.title("LLM Clipper")
        self.window.attributes("-topmost", True)  # 最前面に表示
        self.window.overrideredirect(True)  # タイトルバーを非表示

        # スタイル設定 - エラー時は黄色背景
        if "エラー" in self.title:
            bg_color = "#ffeb3b"  # 黄色
            fg_color = "#333333"  # 暗いテキスト
            title_color = "#d32f2f"  # 赤いタイトル
        else:
            bg_color = "#2c3e50"  # 通常の青/灰色
            fg_color = "#ecf0f1"  # 明るいテキスト
            title_color = "#3498db"  # 青いタイトル

        # フレームの作成
        frame = tk.Frame(self.window, bg=bg_color, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # タイトルラベル
        title_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        title_label = tk.Label(
            frame,
            text=self.title,
            bg=bg_color,
            fg=title_color,
            font=title_font,
            anchor="w",
            justify="left",
        )
        title_label.pack(fill=tk.X, pady=(0, 5))

        # メッセージラベル
        msg_font = tkfont.Font(family="Helvetica", size=10)
        msg_label = tk.Label(
            frame,
            text=self.message,
            bg=bg_color,
            fg=fg_color,
            font=msg_font,
            anchor="w",
            justify="left",
            wraplength=300,
        )
        msg_label.pack(fill=tk.X)

        # ウィンドウサイズを調整
        self.window.update_idletasks()
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()

        # 画面の右下に配置
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = screen_width - width - 20
        y = screen_height - height - 40

        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # ウィンドウを表示
        self.window.deiconify()

        # フォーカスを奪わないようにする
        self.window.focus_set()
        self.window.focus_force()
        self.window.after(1, lambda: self.window.focus_force())

        # タイムアウト後に閉じるスレッドを開始
        close_thread = threading.Thread(target=self._auto_close)
        close_thread.daemon = True
        close_thread.start()

        # メインループを開始
        self.window.mainloop()

    def _auto_close(self):
        """指定時間後にウィンドウを閉じる"""
        time.sleep(self.timeout)
        try:
            self.window.destroy()
        except:
            pass  # ウィンドウがすでに閉じられている場合


def show_notification(title, message, timeout=5):
    try:
        # 別スレッドで通知を表示
        def show_notification_thread():
            notification = NotificationWindow(title, message, timeout)
            notification.show()

        notification_thread = threading.Thread(target=show_notification_thread)
        notification_thread.daemon = False  # デーモンスレッドからノンデーモンスレッドに変更
        notification_thread.start()
        
        # メインスレッドが終了してもノンデーモンスレッドは実行され続けるため
        # 通知ウィンドウが表示されるまで少し待機
        time.sleep(0.5)
    except Exception as e:
        # 通知の表示に失敗しても処理を続行
        print(f"通知の表示に失敗しました: {str(e)}")
