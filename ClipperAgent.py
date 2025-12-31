"""
LLM Clipperメインアプリケーション (ClipperAgent)
クリップボードの内容を取得し、指定されたプロンプトと組み合わせてLLM APIで処理し、
結果をクリップボードに格納します。
"""

import sys
import argparse
import logging
import time

from clipper_agent.clipboard import get_clipboard_text, set_clipboard_text
from clipper_agent.settings import get_prompt, load_settings
from clipper_agent.prompt import build_prompt
from clipper_agent.gemini_api import generate_text
from clipper_agent.notification import show_notification
from clipper_agent.logging_utils import setup_logging

def main():
    logger = setup_logging()
    print("ClipperAgentを起動しました")

    parser = argparse.ArgumentParser(description='LLM Clipper: クリップボードの内容をLLMで処理するツール')
    parser.add_argument('prompt_name', nargs='?', help='使用するプロンプト名')
    args = parser.parse_args()

    prompt_name = args.prompt_name

    try:
        # プロンプト名が指定されていない場合はデフォルトプロンプトを使用
        if not prompt_name:
            settings = load_settings()
            default_prompt_name = settings.get('default_prompt_name')
            if not default_prompt_name:
                error_msg = "プロンプト名が指定されておらず、デフォルトプロンプトも設定されていません。"
                logger.error(error_msg)
                show_notification("エラー", error_msg)
                print(f"エラー: {error_msg}")
                print("使用法: ClipperAgent.exe \"プロンプト名\"")
                sys.exit(1)
            prompt_name = default_prompt_name
            print(f"デフォルトプロンプト '{prompt_name}' を使用します")
            
        # クリップボードからテキストを取得
        clipboard_text = get_clipboard_text()
        print(f"クリップボードからテキストを取得しました ({len(clipboard_text)} 文字)")

        # 指定されたプロンプト名のプロンプト情報を取得
        prompt_info = get_prompt(prompt_name)
        prompt_template = prompt_info.get('content') or prompt_info.get('text', '')
        model_id = prompt_info.get('model', 'gemini-pro')
        print(f"プロンプト '{prompt_name}' を読み込みました（モデル: {model_id}）")

        # プロンプトを組み立て
        final_prompt = build_prompt(prompt_template, clipboard_text)
        print("プロンプトを組み立てました")

        # LLM APIでテキスト生成
        print(f"Gemini API ({model_id}) にリクエストを送信します")
        start_time = time.time()
        generated_text = generate_text(final_prompt, model_id)
        elapsed_time = time.time() - start_time
        print(f"APIからの応答を受信しました（処理時間: {elapsed_time:.2f}秒）")

        # 生成されたテキストをクリップボードに設定
        set_clipboard_text(generated_text)
        print("生成されたテキストをクリップボードに設定しました")

        # 通知
        success_msg = f"'{prompt_name}'の結果をクリップボードにコピーしました"
        show_notification("処理完了", success_msg)
        print(success_msg)

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"値エラー: {error_msg}")
        show_notification("エラー", error_msg)
        print(f"エラー: {error_msg}")
        sys.exit(1)
    except FileNotFoundError as e:
        error_msg = str(e)
        logger.error(f"ファイル not found エラー: {error_msg}")
        show_notification("エラー", error_msg)
        print(f"エラー: {error_msg}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"予期しないエラーが発生しました: {str(e)}"
        logger.error(error_msg, exc_info=True)
        show_notification("エラー", error_msg)
        print(f"エラー: {error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
