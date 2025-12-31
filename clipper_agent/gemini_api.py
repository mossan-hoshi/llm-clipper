"""
Gemini API連携モジュール
Gemini APIとの通信を行う機能を提供します。
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from clipper_agent.settings import get_project_root, get_app_data_dir

def load_api_settings():
    """
    .envファイルからAPI設定を読み込みます。
    
    Returns:
        tuple: (API_KEY, AVAILABLE_MODELS)
        
    Raises:
        ValueError: APIキーが設定されていない場合
    """
    # .envファイルの検索と読み込み
    # まず実行ファイル(またはプロジェクトルート)と同じディレクトリを確認
    env_path = get_project_root() / '.env'
    if not env_path.exists():
        # 次にユーザーのアプリケーションデータディレクトリを確認
        app_data_dir = get_app_data_dir()
        env_path = app_data_dir / '.env'
        if not env_path.exists():
            raise FileNotFoundError(f".envファイルが見つかりません。APIキーを設定してください。")
    
    # .envファイル読み込み
    load_dotenv(env_path)
    
    # APIキー取得
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
    
    # 利用可能なモデル一覧取得（オプション）
    available_models = os.getenv('AVAILABLE_MODELS', 'gemini-pro,gemini-1.5-flash').split(',')
    
    return api_key, available_models

def generate_text(prompt, model_id='gemini-pro'):
    """
    Gemini APIを使用してテキスト生成を行います。
    
    Args:
        prompt (str): プロンプト文字列
        model_id (str): 使用するモデルのID
        
    Returns:
        str: 生成されたテキスト
        
    Raises:
        ValueError: API呼び出しに失敗した場合
    """
    try:
        # API設定の読み込み
        api_key, _ = load_api_settings()
        
        # Gemini APIの初期化
        genai.configure(api_key=api_key)
        
        # モデルの取得
        model = genai.GenerativeModel(model_id)
        
        # テキスト生成リクエスト
        response = model.generate_content(prompt)
        
        # 結果のテキストを返す
        return response.text
        
    except Exception as e:
        raise ValueError(f"Gemini APIの呼び出しに失敗しました: {str(e)}")
