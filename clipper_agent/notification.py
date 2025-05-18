"""
デスクトップ通知モジュール
デスクトップ通知を表示する機能を提供します。
"""

import platform
from plyer import notification

def show_notification(title, message, timeout=5):
    """
    デスクトップ通知を表示します。
    
    Args:
        title (str): 通知のタイトル
        message (str): 通知のメッセージ
        timeout (int): 通知の表示時間（秒）
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="LLM Clipper",
            timeout=timeout
        )
    except Exception as e:
        # 通知の表示に失敗しても処理を続行
        print(f"通知の表示に失敗しました: {str(e)}")
