"""
プロンプト処理モジュール
プロンプト文字列の処理を行う機能を提供します。
"""

def build_prompt(prompt_template, clipboard_text):
    """
    プロンプトテンプレート内の${clipboard}をクリップボードの内容で置換します。
    
    Args:
        prompt_template (str): プロンプトテンプレート文字列
        clipboard_text (str): クリップボードの内容
        
    Returns:
        str: 組み立てられたプロンプト文字列
    """
    # JSON内の\nを実際の改行に変換するため、一度評価する
    prompt_template = prompt_template.replace('\\n', '\n')
    return prompt_template.replace('${clipboard}', clipboard_text)
