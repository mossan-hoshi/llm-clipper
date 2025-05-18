"""
クリップボード操作モジュール
クリップボードからテキストデータを取得したり、クリップボードにテキストを設定する機能を提供します。
"""

import pyperclip

def get_clipboard_text():
    """
    クリップボードからテキストデータを取得します。
    
    Returns:
        str: クリップボードの内容（テキスト形式）
        
    Raises:
        ValueError: クリップボードが空、またはテキストでない場合
    """
    try:
        text = pyperclip.paste()
        if not text:
            raise ValueError("クリップボードが空です。")
        return text
    except Exception as e:
        raise ValueError(f"クリップボードからテキストを取得できませんでした: {str(e)}")

def set_clipboard_text(text):
    """
    クリップボードにテキストデータを設定します。
    
    Args:
        text (str): クリップボードに設定するテキスト
        
    Raises:
        ValueError: クリップボードへの書き込みに失敗した場合
    """
    try:
        pyperclip.copy(text)
    except Exception as e:
        raise ValueError(f"クリップボードにテキストを設定できませんでした: {str(e)}")
