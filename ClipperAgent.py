"""
LLM Clipperメインアプリケーション (ClipperAgent)
クリップボードの内容を取得し、指定されたプロンプトと組み合わせて処理します。
"""

import sys
import argparse
import logging

from clipper_agent.clipboard import get_clipboard_text
from clipper_agent.settings import get_prompt
from clipper_agent.prompt import build_prompt

def main():
    """
    メインエントリーポイント
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='LLM Clipper: クリップボードの内容をLLMで処理するツール')
    parser.add_argument('prompt_name', nargs='?', help='使用するプロンプト名')
    args = parser.parse_args()
    
    prompt_name = args.prompt_name
    
    try:
        from clipper_agent.settings import get_settings
        
        # プロンプト名が指定されていない場合はデフォルトプロンプトを使用
        if not prompt_name:
            settings = get_settings()
            default_prompt_name = settings.get('default_prompt_name')
            if not default_prompt_name:
                print("エラー: プロンプト名が指定されておらず、デフォルトプロンプトも設定されていません。")
                print("使用法: ClipperAgent.exe \"プロンプト名\"")
                sys.exit(1)
            prompt_name = default_prompt_name
            print(f"デフォルトプロンプト '{prompt_name}' を使用します。")
            
        # クリップボードからテキストを取得
        clipboard_text = get_clipboard_text()
        
        # 指定されたプロンプト名のプロンプト情報を取得
        prompt_info = get_prompt(prompt_name)
        prompt_template = prompt_info.get('content', '')
        model_id = prompt_info.get('model', 'gemini-pro')
        
        # プロンプトを組み立て
        final_prompt = build_prompt(prompt_template, clipboard_text)
        
        # 組み立てられたプロンプトを出力（動作確認用）
        print(f"プロンプト名: {prompt_name}")
        print(f"使用モデル: {model_id}")
        print("組み立てられたプロンプト:")
        print("=" * 50)
        print(final_prompt)
        print("=" * 50)
        
    except ValueError as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
