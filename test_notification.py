"""
通知機能のテストスクリプト
"""

import time
from clipper_agent.notification import show_notification

def test_notification():
    print("通知テスト開始...")
    
    # 成功通知のテスト
    show_notification(
        "処理成功", 
        "プロンプト「日本語翻訳」の結果をクリップボードにコピーしました。",
        timeout=5
    )
    
    time.sleep(2)  # 少し待って2つ目の通知を表示
    
    # エラー通知のテスト
    show_notification(
        "エラー発生", 
        "APIとの通信中にエラーが発生しました。\nネットワーク接続を確認してください。",
        timeout=7
    )
    
    print("通知が表示されました。数秒後に自動的に閉じます。")
    
    # メインスレッドを維持するために少し待機
    time.sleep(3)
    print("テスト完了")

if __name__ == "__main__":
    test_notification()
