"""
設定ファイル操作モジュール
settings.jsonからプロンプト情報を読み込む機能を提供します。
"""

import json
import os
import logging
from pathlib import Path

# アプリケーションデータディレクトリパス
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'ClipperAgent')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json')

def get_settings():
    """
    settings.jsonから設定を読み込みます。
    
    Returns:
        dict: 設定データ
        
    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合
        json.JSONDecodeError: 設定ファイルの形式が不正な場合
    """
    try:
        if not os.path.exists(SETTINGS_FILE):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {SETTINGS_FILE}")
            
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            return settings
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"設定ファイルの形式が不正です: {str(e)}", e.doc, e.pos)
    except Exception as e:
        raise Exception(f"設定ファイルの読み込みに失敗しました: {str(e)}")

def get_prompt(prompt_name):
    """
    指定されたプロンプト名に対応するプロンプト情報を取得します。
    
    Args:
        prompt_name (str): プロンプト名
        
    Returns:
        dict: プロンプト情報（プロンプト名、プロンプト本文、モデルIDなど）
        
    Raises:
        ValueError: 指定されたプロンプト名が存在しない場合
    """
    settings = get_settings()

    prompts = settings.get('prompts', [])
    for prompt in prompts:
        if prompt.get('name') == prompt_name:
            # 後方互換性: textキーが存在する場合はcontentとして扱う
            if 'content' not in prompt and 'text' in prompt:
                prompt['content'] = prompt.get('text')
            return prompt

    raise ValueError(f"指定されたプロンプト '{prompt_name}' が見つかりません。")
